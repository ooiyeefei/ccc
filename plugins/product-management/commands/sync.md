---
description: Sync local cache with GitHub Issues
allowed-tools: Read, Write, Bash
---

# GitHub Sync

Sync local `.pm/requests/` cache with GitHub Issues for deduplication.

## Prerequisites

Check GitHub CLI:
```bash
gh auth status
```
If not authenticated: "Run `gh auth login` first."

## Process

1. **Fetch All PM Issues**
   ```bash
   gh issue list --label "pm:feature-request" --state all --json number,title,body,labels,state,createdAt,updatedAt --limit 200
   ```

2. **Create/Update Local Cache**
   - Create `.pm/requests/` directory if not exists
   - For each issue, create/update `.pm/requests/[issue-number].md`:

   ```markdown
   ---
   github_issue: [number]
   title: "[title]"
   state: [open/closed]
   labels: [list]
   created: [date]
   updated: [date]
   synced: [now]
   ---

   [Issue body content]
   ```

3. **Clean Up Stale Entries**
   - Remove local files for issues that no longer exist
   - Update state for closed issues

4. **Update Timestamp**
   - Update `.pm/cache/last-updated.json`:
   ```json
   {
     "github_sync": "[ISO timestamp]",
     "issues_count": [N]
   }
   ```

5. **Report Summary**
   ```
   GitHub Sync Complete
   - Issues synced: [N]
   - New: [N]
   - Updated: [N]
   - Removed: [N]
   - Last sync: [timestamp]
   ```

## When to Run

- Automatically suggested on session start if >24 hours since last sync
- Before running `/pm:gaps` for accurate deduplication
- After creating issues outside of PM plugin
