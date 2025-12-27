---
description: Generate PRD and create GitHub Issue
argument-hint: <feature-name>
allowed-tools: Read, Write, Bash, WebFetch
---

# PRD Generation

Generate Product Requirements Document for $ARGUMENTS and create GitHub Issue.

## Prerequisites

1. Check GitHub CLI:
   ```bash
   gh auth status
   ```

2. Check for existing context in:
   - `.pm/gaps/*.md` (for WINNING score)
   - `.pm/competitors/*.md` (for competitive evidence)

## Process

Use the **prd-generator agent** for comprehensive PRD:

1. **Gather Context**
   - Load gap analysis data for $ARGUMENTS if exists
   - Load competitor implementations
   - Ask user for additional requirements if needed

2. **Deduplication Check**
   ```bash
   gh issue list --search "$ARGUMENTS" --label "pm:feature-request" --json number,title
   ```
   If similar issue exists (>70% match):
   - Show existing issue
   - Ask: "Update existing or create new?"

3. **Generate PRD** with sections:
   - Problem Statement
   - User Stories
   - Competitive Analysis
   - Requirements (Functional, Non-Functional)
   - Acceptance Criteria (P0/P1/P2)
   - Edge Cases
   - Out of Scope
   - Technical Considerations
   - Success Metrics

4. **Save PRD**
   - Create `.pm/prds/` directory if not exists
   - Save to `.pm/prds/[feature-slug].md`

5. **Create GitHub Issue**
   ```bash
   gh issue create \
     --title "Feature: $ARGUMENTS" \
     --body "$(cat .pm/prds/[feature-slug].md)" \
     --label "pm:feature-request" \
     --label "[winning-label]" \
     --label "[priority-label]"
   ```

6. **Update Tracking**
   - Save issue reference to `.pm/requests/[issue-number].md`
   - Update `.pm/cache/last-updated.json`

7. **Return Results**
   - PRD file location
   - GitHub Issue URL
   - Next steps: `/speckit.specify #[issue-number]`

## If gh CLI Unavailable

Output PRD formatted for manual GitHub issue creation.
