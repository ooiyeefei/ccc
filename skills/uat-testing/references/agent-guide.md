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

Strategy:
1. Ask user for test account credentials before starting
2. Navigate to login page
3. Use browser_fill_form to enter credentials
4. Use browser_click to submit
5. Verify auth by checking for logged-in state (user avatar, dashboard content)
6. Store the authenticated page context — all subsequent tests reuse it

If using cookie/token-based auth, an alternative is to set auth cookies directly via `browser_evaluate`:
```js
document.cookie = "session=<token>; path=/"
```
