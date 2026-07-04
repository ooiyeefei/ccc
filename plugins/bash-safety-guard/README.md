# bash-safety-guard

A **fail-closed** [Claude Code](https://github.com/anthropics/claude-code) plugin
that guards the `Bash` tool with a `PreToolUse` hook. It blocks genuinely
dangerous commands **before they run** — and, crucially, keeps blocking even
under `--dangerously-skip-permissions`, because PreToolUse hooks run regardless
of permission mode.

Non-Bash tools (Read/Write/Edit/…) are never touched.

## What it blocks

**Production data loss**
- Destructive SQL actually being executed or aimed at prod: `DROP TABLE/DATABASE`, `TRUNCATE`, `DELETE FROM` (via `psql`/`mysql`/`-c`…)
- `convex import --replace` / data-touching convex ops aimed at `--prod`
- `prisma migrate reset`, `prisma db push --accept-data-loss`, `drizzle-kit drop/reset`
- `redis-cli flushall/flushdb`, `dropdb`
- `aws dynamodb delete-table/delete-item`, `aws s3 rb/delete-bucket`, `aws s3 rm --recursive`
- `rm -rf` on database/backup/dump paths
- **Catastrophic `rm -rf`**: `/`, `/*`, `~`, `$HOME`, `.`, `..`, and top-level system dirs (incl. `sudo` / `--no-preserve-root`)

**Credential leaks**
- A secret file (`.env*`, `*.pem`, `id_rsa`, `credentials.json`, service-account keys) sent over the network
- Secrets piped into egress (`cat .env | curl …`) or to a paste/tunnel/webhook sink (`transfer.sh`, `webhook.site`, `ngrok`, …)
- Committing secret files to git

## What it deliberately allows (no false positives)

`git reset`/`checkout`/`clean`/worktree ops, dev servers (`--live`), read-only
`convex data`/`run <fn>`, SQL keywords inside commit messages / `echo` / `grep`,
authenticated API calls (`curl -H "Authorization: Bearer $TOKEN" …`), and
ordinary build cleanup (`rm -rf node_modules dist .next`, `/tmp/...`).

## Install

```bash
/plugin marketplace add ooiyeefei/ccc
/plugin install bash-safety-guard@ccc
```

**Requires Node ≥ 22** on your `PATH` (the hook runs the TypeScript classifier
via `node --experimental-strip-types`).

## How it works

- `hooks/hooks.json` wires `hooks/guard-hook.ts` to `PreToolUse` for the `Bash` matcher.
- The hook reads the tool payload, classifies the command with `lib/guards.ts`,
  and exits `0` (allow) or `2` (block — stderr is fed back to the model).
- It **fails closed**: any dangerous verdict, parse error, or classifier error blocks.

## Notes

- `lib/guards.ts` is the same classifier used by the [pixtension](https://github.com/ooiyeefei/pixtension)
  pi orchestrator, vendored here so the two share one set of rules.
- The classifier is conservative by design: a false positive costs one blocked
  command; a false negative can wipe prod or leak a key.

## License

MIT © ooiyeefei
