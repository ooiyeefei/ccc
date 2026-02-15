# UAT Test Case Template

Use this template when generating `uat-test-cases.md`. Adapt sections based on what the feature requires.

## Document Header

```markdown
# UAT Test Cases: [Feature Name]

**Feature**: [feature-id or branch name]
**Branch**: `[branch-name]`
**Date**: [YYYY-MM-DD]
**Tester**: [human name or "Claude Code (automated via Playwright MCP)"]
**Environment**: [e.g. "Local (`npm run dev` + `npx convex dev`)"]

## Prerequisites

1. **Start local dev server**: [command]
2. **Start backend services** (if needed): [commands]
3. **Ensure environment variables**: `.env.local` has all required keys
4. **Authenticate**: Log in via [auth provider] using test account
5. **Seed test data** (if needed): [describe what data must exist]

## Test Timeout

[Note any expected delays, e.g. cold starts, streaming timeouts]
```

## Test Case Format

Each test case should follow this structure:

```markdown
## TC-NNN: [Test Case Title]

**User Story**: [reference to spec user story]
**Priority**: Critical | High | Medium | Low

### TC-NNN.1: [Sub-test description]

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | [What the tester does] | [What should happen] |
| 2 | [Next action] | [Expected outcome] |

**Pass criteria**: [One-line summary of what constitutes a pass]
```

## Prioritization Guidelines

Group test cases by priority. Execute Critical/High first:

- **Critical (P1)**: Core happy-path functionality. If these fail, the feature is broken.
- **High (P2)**: Important secondary flows, error handling for common cases.
- **Medium (P3)**: Edge cases, visual polish, cross-browser behavior.
- **Low (P4)**: Nice-to-have checks, future-proofing validation.

## Test Categories to Cover

For any feature, consider these categories (include only what applies):

1. **Happy path** — Primary user flow works end-to-end
2. **Data rendering** — Correct data displayed with proper formatting
3. **User interactions** — Buttons, forms, navigation respond correctly
4. **Error handling** — Graceful behavior on failures, timeouts, missing data
5. **Historical/persistence** — Data survives page reload, re-renders correctly
6. **Auth/permissions** — Role-based access enforced
7. **Responsive/mobile** — Layout adapts to smaller viewports
8. **Cross-cutting** — Design consistency, no regressions to existing features
9. **Performance** — Acceptable load times, no memory leaks
10. **Accessibility** — Keyboard navigation, screen reader labels
