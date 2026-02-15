---
name: uat-testing
description: End-to-end User Acceptance Testing for web applications. Analyzes branch changes and specs to generate exhaustive test cases, sets up the local environment, executes tests via Playwright browser automation, and produces a pass/fail results report with screenshots and fix documentation. Use when the user says "run UAT", "test this feature", "UAT testing", "acceptance test", "test my branch", "generate test cases", or wants to verify a feature branch against its spec before merge.
---

# UAT Testing

End-to-end UAT workflow: analyze → generate test cases → set up environment → execute → report.

## Workflow Overview

```
Phase 1: Discovery
  ├─ Read spec/requirements (if provided)
  ├─ Analyze git branch diff against base
  └─ Identify what was built/changed

Phase 2: Environment Setup
  ├─ Check for .env.local (or equivalent)
  ├─ If missing → ask user for env file or credentials
  ├─ Ask user for test account credentials
  └─ Verify dev server starts successfully

Phase 3: Test Case Generation
  ├─ Write uat-test-cases.md (see references/test-case-template.md)
  ├─ Cover: happy path, errors, persistence, auth, responsive
  └─ Present to user for review before execution

Phase 4: Test Execution
  ├─ Start dev server (framework-appropriate command)
  ├─ Authenticate with test account via browser
  ├─ Execute test cases with Playwright MCP tools
  ├─ Take screenshots as evidence
  └─ If a test fails → document the failure, continue testing

Phase 5: Reporting
  ├─ Write uat-results.md (see references/results-template.md)
  ├─ Include: summary table, detailed results, screenshots, fixes
  └─ Present overall PASS/FAIL verdict
```

## Phase 1: Discovery

### Finding the Spec

Look for feature context in this priority order:

1. **User-provided spec**: If user gives a path to a spec, requirements doc, or thread — read it first
2. **Spec directory**: Check `specs/[branch-name]/spec.md` or `specs/[feature-id]/spec.md`
3. **Tasks/todo**: Check `tasks/todo.md` or similar for what was planned
4. **PR description**: If a PR exists, read it via `gh pr view`

### Analyzing Branch Changes

```bash
# What branch are we on?
git branch --show-current

# What changed vs base branch?
git log main..HEAD --oneline
git diff main..HEAD --stat

# What files were modified?
git diff main..HEAD --name-only
```

Read the changed files to understand what was built. Focus on:
- New components or pages (user-facing features)
- Modified API routes or backend logic (behavior changes)
- Schema changes (data model additions)
- Config changes (new env vars needed)

### Output

Summarize findings to the user:
- "This branch adds [feature] based on [spec]"
- "Key changes: [list of modified areas]"
- "I'll generate test cases covering [scope]"

## Phase 2: Environment Setup

### Check Environment Variables

```bash
# Check if env file exists
ls -la .env.local .env 2>/dev/null
```

**If `.env.local` does not exist**, ask the user:

> I don't see a `.env.local` file. Do you have an environment file or credentials I should use? Common needs:
> - Database connection (e.g., Convex URL/deploy key)
> - Auth provider keys (e.g., Clerk publishable/secret key)
> - API keys (e.g., AI model keys, external service keys)
>
> Please provide the file path or paste the required variables.

### Request Test Account

Always ask before attempting to authenticate:

> For UAT testing I need a test account to log in. Most auth systems require email verification, so I can't create a new account.
>
> Please provide:
> 1. **Login URL** (if not the default `/sign-in`)
> 2. **Email/username** for the test account
> 3. **Password**
> 4. **Any 2FA/MFA steps** I should be aware of
> 5. **Which business/org/team** to select after login (if applicable)

### Verify Dev Server

Detect the framework and start the dev server:

| Signal | Framework | Start Command |
|--------|-----------|---------------|
| `next.config.*` | Next.js | `npm run dev` |
| `vite.config.*` | Vite | `npm run dev` |
| `angular.json` | Angular | `ng serve` |
| `nuxt.config.*` | Nuxt | `npm run dev` |
| `package.json` scripts | Generic | Read `dev` script |

If the project needs multiple services (e.g., Next.js + Convex), start all of them.

Verify the server is reachable before proceeding:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

## Phase 3: Test Case Generation

Read `references/test-case-template.md` for the full template format.

### Generation Rules

1. **Map spec to test cases**: Each user story or requirement gets at least one test case
2. **Prioritize**: Critical (P1) = core happy path; High (P2) = error handling; Medium (P3) = edge cases
3. **Be specific**: Each step should be a concrete action ("Type 'hello' in the input field"), not vague ("Test the input")
4. **Include expected data**: Use actual values from the seeded test data or spec examples
5. **Cover persistence**: Always include a "reload page and verify" test case for stateful features
6. **Cover auth boundaries**: If the feature has role-based access, test with different roles

### Writing the File

Write `uat-test-cases.md` to the spec directory (e.g., `specs/[feature-id]/uat-test-cases.md`) or to the project root if no spec directory exists.

**Present the test cases to the user for review before executing.** Ask:

> I've generated [N] test cases in [file path]. Review them and let me know:
> - Any test cases to add or remove?
> - Any priority adjustments?
> - Ready to proceed with execution?

## Phase 4: Test Execution

### Playwright MCP Setup

Load the Playwright tools via ToolSearch before starting:
```
ToolSearch: "playwright browser"
```

Key tools: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_fill_form`, `browser_type`, `browser_press_key`, `browser_take_screenshot`, `browser_wait_for`, `browser_console_messages`, `browser_evaluate`.

See `references/agent-guide.md` for the full tool reference and auth handling patterns.

### Execution Pattern

For each test case:
1. Navigate to the target page
2. Wait for page load (`browser_wait_for` or snapshot check)
3. Perform the test actions (click, type, submit)
4. Wait for the expected result
5. Verify via `browser_snapshot` (check accessibility tree for expected text/elements)
6. Take `browser_take_screenshot` for evidence
7. Check `browser_console_messages` for JS errors
8. Record PASS or FAIL with details

### Failure Handling

When a test fails:
- **Document exactly what happened** (expected vs actual)
- **Take a screenshot** of the failure state
- **Check console for errors** (`browser_console_messages`)
- **Continue testing** other cases — do not stop on first failure
- **If the fix is obvious and small** (< 5 lines), ask user if you should fix it. If yes, fix, re-verify, and document the fix in the results report

### Screenshot Naming Convention

Save screenshots to the project root with descriptive names:
```
uat-tc001-invoice-card.png
uat-tc002-cashflow-dashboard.png
uat-tc003-fail-missing-button.png
```

## Phase 5: Reporting

Read `references/results-template.md` for the full report format.

### Writing the Report

Write `uat-results.md` alongside the test cases file.

Include:
1. **Summary table**: PASS/FAIL/BLOCKED/NOT TESTED counts
2. **Per-test results**: What happened for each test case with specific details
3. **Fixes applied**: Any code changes made during testing, with root cause analysis
4. **Component status**: Build pass/fail for each modified component
5. **Screenshots**: Reference all captured screenshots
6. **Remaining issues**: Known problems that weren't fixed
7. **Overall verdict**: PASS (all critical tests pass) or FAIL (any critical test fails)

### Verdict Rules

- **PASS**: All Critical (P1) and High (P2) test cases pass. Medium/Low failures are documented but don't block.
- **FAIL**: Any Critical (P1) test case fails, OR more than 50% of High (P2) cases fail.
- **PARTIAL**: Critical tests pass but significant High (P2) failures exist. Merging is a judgment call.

## References

- **Test case format**: See [references/test-case-template.md](references/test-case-template.md)
- **Results report format**: See [references/results-template.md](references/results-template.md)
- **Agent setup and Playwright tools**: See [references/agent-guide.md](references/agent-guide.md)
