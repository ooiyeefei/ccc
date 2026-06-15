# Agent Configuration for UAT Testing

## Do You Need a Dedicated Agent?

In most cases, **no**. This skill turns the main Claude session into a UAT specialist. The Playwright MCP tools (browser_navigate, browser_snapshot, browser_click, browser_fill_form, browser_take_screenshot, etc.) are already available as deferred tools.

A dedicated agent is useful when:
- You want to run UAT **in the background** while doing other work
- You want **parallel test execution** across multiple test suites
- You need a **repeatable, automated pipeline** (e.g. CI integration)

## Agent Setup (Optional)

If you decide to create a dedicated agent, configure it as a Task agent with these capabilities:

```
subagent_type: general-purpose
description: "Execute UAT test cases"
prompt: |
  You are a UAT test executor. You have access to Playwright MCP tools for browser automation.

  Your task:
  1. Read the test cases from [path-to-uat-test-cases.md]
  2. Start the dev server if not running
  3. Execute each test case using Playwright browser tools
  4. Take screenshots for evidence
  5. Write results to [path-to-uat-results.md]

  Rules:
  - Wait for networkidle after each navigation
  - Take a screenshot before and after each test case
  - If a test fails, document the exact error and DOM state
  - Do not modify source code — only report failures
```

## Playwright MCP Tool Reference

Key tools available via deferred loading (use ToolSearch to load):

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to URL |
| `browser_snapshot` | Get accessibility tree (faster than screenshot for DOM inspection) |
| `browser_take_screenshot` | Visual evidence capture |
| `browser_click` | Click elements by ref or selector |
| `browser_fill_form` | Fill input fields |
| `browser_type` | Type text into focused element |
| `browser_press_key` | Keyboard actions (Enter, Tab, etc.) |
| `browser_wait_for` | Wait for selector/text to appear |
| `browser_console_messages` | Check for JS errors |
| `browser_evaluate` | Run arbitrary JS in page context |

## Test Execution Pattern

For each test case:

```
1. browser_navigate → target page
2. browser_wait_for → page fully loaded (networkidle)
3. browser_snapshot → verify initial state matches expectations
4. browser_click/fill_form/type → perform test actions
5. browser_wait_for → wait for result
6. browser_snapshot → verify outcome
7. browser_take_screenshot → capture evidence
8. browser_console_messages → check for errors
```

## Auth Handling

Most apps require authentication. The agent cannot create new accounts (email verification, 2FA, etc.).

> **Never type a password (or any credential) into a login field interactively** —
> not via `browser_fill_form`, `browser_type`, `computer`, or any other live tool.
> Interactive credential entry is a security risk (the agent reads page/file
> content that can carry injected instructions and could be steered onto a
> lookalike/phishing page, and the secret would pass through the agent's context)
> and it is a hard-blocked action for AI agents. Authenticate with the **env-var
> code-script** pattern below instead.

**Pattern: code-driven auth → saved session → reuse.** A small script reads
credentials from `process.env` (loaded from a gitignored env file), signs in, and
saves the authenticated browser session (`storageState`) to a gitignored file.
The credential flows env-file → script → auth field deterministically, and never
through the agent's interactive tool calls or output. The UAT then reuses the
saved session — so the rest of the run drives a browser that is *already* logged
in, and the agent never handles the password.

### 1. Credentials in a gitignored env file (never committed, never echoed)
```
# .env.uat   (add to .gitignore)
UAT_BASE_URL=https://app.example.com
UAT_USER_EMAIL=test@example.com
UAT_USER_PASSWORD=...        # the agent must never read, print, log, or screenshot this value
```

### 2. Auth setup script (reads env → saves storageState)
Copy `references/uat-auth-setup.mjs` into the project, adapt the selectors in
`signIn()` to the app's auth provider, then run it:
```bash
node --env-file=.env.uat uat-auth-setup.mjs   # saves .uat-auth/state.json
```
It fails closed if a required env var is missing (errors with the var NAME, never
the value) and never falls back to interactive entry.

### 3. Reuse the saved session for the UAT (no re-auth)
- **Fully code-driven (recommended, reproducible):** write the test cases as a
  Playwright script that loads `storageState: '.uat-auth/state.json'` and runs the
  assertions + screenshots. The session token never passes through interactive tools.
- **Interactive MCP tools:** read the storageState file and apply its cookies via
  `browser_evaluate` (`document.cookie = ...`) before navigating, then drive the
  UAT with the `browser_*` tools against the already-authenticated session.

### Security best practices (MANDATORY for AI agents)
- Secrets live ONLY in the gitignored env file — never hardcode them in the
  script, never commit them, never paste them into chat or a tool argument.
- Reference `process.env.X` only; never `console.log`/print/echo a credential value.
- **Fail closed:** if a required env var is missing, stop with the var NAME (not
  value). Do NOT fall back to typing the password interactively.
- Treat the saved `storageState` file as a live secret (it holds a session token):
  gitignore it, don't commit it, don't print it.
- Redact secrets from screenshots and the results report — never screenshot a
  populated password field.
- Prefer dedicated, low-privilege test accounts; rotate them.

### Security posture: this is the BASELINE tier, not the strongest

This env-file + `process.env` pattern is the standard E2E/CI auth approach and the
right **default for local/dev/test** UAT — but be honest that it is **not** the top
of the secrets hierarchy. OWASP rates environment-variable secrets *below* secrets
managers ("not recommended unless the other methods are not possible"), for real
reasons:
- `process.env` is **process-global**: every child process inherits it and **any
  transitive dependency can read it** — and Playwright pulls in many deps, so it's
  a genuine supply-chain surface.
- The env file is **plaintext at rest** — it can leak via logs, crash dumps,
  backups, or a verbose runner.
- A static long-lived password, and the saved `storageState` (a bearer token at
  rest), are standing liabilities.

**Escalate to the hardened tier when the target is shared/staging/prod or the
account is privileged:**
- Source secrets from a **secrets manager** (Vault, AWS/GCP Secrets Manager,
  1Password CLI, Doppler) or the **OS keychain**, injected at runtime — not written
  to a plaintext file.
- Prefer **token/API auth** (or seed `storageState` via an API login) over UI
  password entry where the app supports it.
- Use a **dedicated, least-privilege, rotated/ephemeral test account on staging** —
  never prod credentials. **Never put MFA codes in env** (enter them via UI/prompt).
- Keep the auth script **minimal-dependency**; treat `storageState` as **short-TTL**
  and delete it after the run.

Default to the env-file flow for local/dev/test; escalate as above otherwise.

### Bot detection
Some providers challenge headless/automated browsers (CAPTCHA, device checks). If
the setup script can't pass the challenge: retry headed (`UAT_HEADFUL=1` in the
template) and/or with a persistent profile, or — last resort — have the **user**
sign in once in a real browser and export the session (cookies / storageState) for
the script to load. The agent still never types the password. (Tested working
headless against a live Clerk app, but provider behavior varies.)

### Token/cookie auth (alternative)
If the app uses token-based sessions, set the auth cookie via the storageState
file or `browser_evaluate` (`document.cookie = "session=<token>; path=/"`),
sourcing the token from `process.env` the same way — never inline it.
