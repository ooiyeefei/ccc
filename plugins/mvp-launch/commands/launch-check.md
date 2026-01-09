---
description: Run MVP launch readiness gap analysis
allowed-tools: Read, Glob, Grep, AskUserQuestion, Write
---

# MVP Launch Check

Analyze your codebase against the 10-point MVP launch checklist and identify gaps.

## Usage

```
/launch-check
```

## Process

Use the **mvp-gap-analyst agent** for systematic 4-phase analysis:

1. **DISCOVER** - Search codebase for implementations
2. **UNDERSTAND** - Read files, trace flows, assess completeness
3. **CONFIRM** - Present findings to user for validation
4. **REPORT** - Generate gap analysis with P0/P1/P2 priorities

## Output

Analysis saved to `.pm/gaps/[YYYY-MM-DD]-mvp-launch-analysis.md` with:
- Summary score (0-100)
- Per-item assessment (10 areas)
- Prioritized action items (P0 blockers, P1 should-fix, P2 nice-to-have)
- Evidence with file paths

## Philosophy

"Don't overbuild. Just make it stable, usable, and something people can trust."
