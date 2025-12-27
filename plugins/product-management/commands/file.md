---
description: Batch create GitHub Issues for approved gaps
argument-hint: [gap-id] (optional, or "all" for all FILE gaps)
allowed-tools: Read, Write, Bash
---

# Feature Filing

Create GitHub Issues for gaps marked "FILE" in gap analysis.

## Prerequisites

1. Check GitHub CLI availability:
   ```bash
   gh auth status
   ```
   If not authenticated: "Run `gh auth login` first."

2. Check gap analysis exists:
   - Read latest `.pm/gaps/*.md` file
   - If missing: "Run `/pm:gaps` first."

## Process

### Without Arguments - Review Mode

Walk through each gap from latest analysis:

1. Show gap with score and evidence
2. Ask: "FILE / WAIT / SKIP?"
3. Allow score adjustments
4. Save decisions to gap analysis file

### With Argument - File Specific or All

If `$ARGUMENTS` is "all":
- File all gaps marked "FILE"

If `$ARGUMENTS` is specific gap ID:
- File only that gap

## GitHub Issue Creation

For each gap to file:

1. **Deduplication Check**
   ```bash
   gh issue list --search "[gap title]" --label "pm:feature-request" --json number,title
   ```
   If >70% match exists: Show existing issue, ask to continue

2. **Create Issue** using template from `references/issue-template.md`:
   ```bash
   gh issue create \
     --title "Feature: [Gap Name]" \
     --body "[Issue template filled]" \
     --label "pm:feature-request" \
     --label "[winning-label]" \
     --label "[priority-label]"
   ```

3. **Apply Labels**:
   - WINNING 40+: `winning:high`, `priority:now`
   - WINNING 25-39: `winning:medium`, `priority:next`
   - WINNING <25: `winning:low`, `priority:later`

4. **Save Local Copy**
   - Save to `.pm/requests/[issue-number].md`
   - Include GitHub issue number for reference

5. **Return Issue URLs** to user

## If gh CLI Unavailable

Output markdown formatted for manual GitHub issue creation.
