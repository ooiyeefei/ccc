#!/usr/bin/env node
/**
 * PreToolUse guard hook for Claude Code (bash-safety-guard plugin).
 *
 * Wired to the `Bash` tool via hooks/hooks.json. Reuses the same
 * `classifyCommand` classifier as the pixtension pi orchestrator (vendored in
 * ./lib/guards.ts) so both enforce identical rules. PreToolUse hooks run
 * regardless of permission mode (including `--dangerously-skip-permissions`),
 * so the gate holds even in autonomous sessions.
 *
 * Contract: exit 0 = allow; exit 2 = block (stderr is fed back to the model).
 * We FAIL CLOSED (exit 2) on any prod-data-loss / credential-leak /
 * catastrophic-rm verdict AND on any parse/classifier error. Non-Bash tools are
 * auto-allowed (this hook is only matched to Bash, but we double-check).
 *
 * Requires Node >= 22 (uses --experimental-strip-types to run TS directly).
 */
import { classifyCommand } from "../lib/guards.ts";

function block(reason: string): never {
	process.stderr.write(`BLOCKED by bash-safety-guard (fail-closed): ${reason}\n`);
	process.exit(2);
}

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
	raw += chunk;
});
process.stdin.on("end", () => {
	let payload: {
		tool_name?: string;
		toolName?: string;
		tool_input?: { command?: string };
		toolInput?: { command?: string };
	};
	try {
		payload = JSON.parse(raw || "{}");
	} catch {
		block("could not parse PreToolUse payload");
	}

	const tool = payload.tool_name ?? payload.toolName ?? "";
	if (tool !== "Bash") process.exit(0);

	const command = payload.tool_input?.command ?? payload.toolInput?.command ?? "";
	let verdict: ReturnType<typeof classifyCommand>;
	try {
		verdict = classifyCommand(String(command));
	} catch (err) {
		block(`classifier error: ${(err as Error).message}`);
	}

	if (verdict.action === "allow") process.exit(0);
	block(`${verdict.category}: ${verdict.reason}\n\nCommand:\n${command}`);
});
