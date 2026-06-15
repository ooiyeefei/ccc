# Changelog — uat-testing skill

## 1.4.0
- **Secure, env-var authentication — the agent never types a password into a login
  field.** Interactive credential entry (`browser_fill_form`/`browser_type`/computer
  use) is a security risk and a hard-blocked action for AI agents, so the skill now
  authenticates with a code-driven setup script that reads credentials from a
  **gitignored env file** and saves an authenticated Playwright `storageState` for
  the run to reuse. The secret flows env-file → script → auth field deterministically
  and never passes through the agent's tool calls, context, or output.
  - New template `references/uat-auth-setup.mjs` (`node --env-file=.env.uat uat-auth-setup.mjs`).
  - Rewrote `references/agent-guide.md` → **Auth Handling** with the full pattern,
    mandatory AI-agent security rules (secrets only in a gitignored env file; never
    echo/log/print/screenshot a credential; fail closed on a missing env var — no
    interactive fallback; treat `storageState` as a live secret), and a
    bot-detection fallback (headed mode / user-exported session).
  - Updated `SKILL.md` Phase 2 (request creds via env file, not chat) and Phase 4
    (run the auth script, reuse the saved session), and the README.
  - Verified: the script authenticates **headless against a live Clerk-protected
    app** and saves a reusable session.
- No breaking changes to test-case generation, execution, or reporting.

## 1.3.0 and earlier
- 5-phase UAT workflow (discovery → environment setup → test-case generation →
  execution → reporting) driven via the Playwright MCP browser tools, with
  screenshot evidence and a priority-weighted PASS/FAIL/PARTIAL verdict.
