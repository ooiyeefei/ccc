# UAT Results Report Template

Use this template when generating `uat-results.md` after test execution.

## Document Structure

```markdown
# UAT Results: [Feature Name]

**Date**: [YYYY-MM-DD]
**Tester**: [name or "Claude Code (automated via Playwright MCP)"]
**Branch**: `[branch-name]`
**Environment**: [e.g. "Local (`npm run dev` on port 3001 + `npx convex dev`)"]
**Build**: `npm run build` [passed/failed] with [N] errors

---

## Summary

| Result | Count |
|--------|-------|
| PASS   | N     |
| FAIL   | N     |
| BLOCKED| N     |
| NOT TESTED | N |

**Overall Result**: [PASS/FAIL] ([brief explanation])

---

## Test Data Seeded

- [Describe seeded data: counts, types, date ranges]
- [Test account used]
- [Business/org context if applicable]

---

## Results

| Test Case | Status | Details |
|-----------|--------|---------|
| **TC-001.1** [description] | PASS/FAIL | [What happened, what was observed] |
| **TC-001.2** [description] | NOT TESTED | [Why skipped if relevant] |

---

## Fixes Applied During Testing

### Fix N: [Short Title] (SEVERITY)

**Root cause**: [What was broken and why]
**Investigation**: [How the issue was diagnosed]
**Fix**: [What code/config was changed]
**Verification**: [How the fix was confirmed]

---

## Component Status

| Component | Build | Visual Test | Notes |
|-----------|-------|-------------|-------|
| [file.tsx] | PASS/FAIL | PASS/FAIL/NOT TESTED | [Details] |

---

## Screenshots

| Screenshot | Description |
|------------|-------------|
| ![description](path) | What it shows |

---

## Remaining Issues

- [ ] [Issue description] — [severity: low/medium/high]

## Next Steps

- [What should be done next]
```

## Reporting Guidelines

1. **Be specific in Details column**: Include actual values, tool names called, data observed.
2. **Document all fixes**: Any code change made during testing gets a "Fix" section with root cause analysis.
3. **Screenshot key states**: Capture evidence for PASS results (especially visual components) and all FAIL results.
4. **Distinguish NOT TESTED from BLOCKED**: NOT TESTED = skipped by choice. BLOCKED = cannot test due to dependency.
5. **Include build verification**: Always note whether `npm run build` (or equivalent) passes before and after fixes.
