---
description: Run gap analysis with WINNING filter
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# Gap Analysis

Identify product gaps and score with WINNING filter.

## Prerequisites Check

1. Verify `.pm/product/inventory.md` exists
   - If missing: "Run `/pm:analyze` first to create product inventory."

2. Verify `.pm/competitors/*.md` files exist
   - If missing: "Run `/pm:landscape` first to research competitors."

3. Check staleness in `.pm/cache/last-updated.json`
   - If competitor data >30 days old: Prompt to refresh first

## Process

Use the **gap-analyst agent** for systematic analysis:

1. **Sync with GitHub Issues** for deduplication:
   ```bash
   gh issue list --label "pm:feature-request" --json number,title,body,labels --limit 100
   ```
   Update `.pm/requests/` with current issues.

2. **Load Context**
   - Read `.pm/product/inventory.md`
   - Read all `.pm/competitors/*.md`
   - Read `.pm/requests/*.md` (existing issues)

3. **Identify ALL Gaps**
   - Features competitors have that we don't
   - Features multiple competitors are building (trends)
   - Features from user reviews/requests

4. **Deduplication Check**
   For each gap, fuzzy match against existing issues:
   - >80% match → Mark EXISTING (show linked issue)
   - 50-80% → Mark SIMILAR (warn user)
   - <50% → Mark NEW (proceed with scoring)

5. **WINNING Filter Scoring** (hybrid):
   - Claude suggests: Pain Intensity, Market Timing
   - Ask user to score: Execution, Fit, Revenue, Moat

6. **Recommendations**
   - 40-60: FILE (high conviction)
   - 25-39: WAIT (monitor)
   - 0-24: SKIP

7. **Save Analysis**
   - Save to `.pm/gaps/[YYYY-MM-DD]-analysis.md`
   - Update `.pm/cache/last-updated.json`

Reference `references/winning-filter.md` in the product-management skill for scoring criteria.
