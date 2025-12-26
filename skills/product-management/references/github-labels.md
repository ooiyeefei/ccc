# GitHub Labels for Product Management

Standard label set for PM workflow. Create these labels on first use of `/pm file`.

## Label Categories

### Type Labels (Purple - `#7057ff`)

| Label | Description | Usage |
|-------|-------------|-------|
| `pm:feature-request` | Feature request from PM analysis | All features filed via `/pm file` |
| `pm:gap-identified` | Gap identified from competitor analysis | From `/pm gaps` output |
| `pm:competitor-intel` | Competitor intelligence gathering | Research tasks |
| `pm:tech-debt` | Technical debt identified | From `/pm analyze` |

### Priority Labels (Red/Orange/Yellow)

| Label | Color | Description | Criteria |
|-------|-------|-------------|----------|
| `priority:now` | `#d73a4a` (red) | Current sprint priority | Top 2-3 by WINNING score |
| `priority:next` | `#fbca04` (yellow) | Upcoming priority | Next 3-5 after "now" |
| `priority:later` | `#c5def5` (light blue) | Future backlog | Remaining filed items |

### WINNING Score Labels (Green shades)

| Label | Color | Description | Score Range |
|-------|-------|-------------|-------------|
| `winning:high` | `#0e8a16` (green) | High conviction | 40-60 points |
| `winning:medium` | `#84b6eb` (blue) | Monitor/wait | 25-39 points |
| `winning:low` | `#e4e669` (yellow-green) | Low priority | 0-24 points |

### Status Labels (Gray shades)

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `pm:stale` | `#d4c5f9` (lavender) | No activity >60 days | Auto-flagged by `/pm backlog` |
| `pm:hot` | `#ff6b6b` (coral) | High recent activity | Auto-flagged by `/pm backlog` |
| `pm:blocked` | `#b60205` (dark red) | Blocked by dependency | Manual or detected |

---

## Auto-Creation Script

Create all labels with `gh` CLI:

```bash
#!/bin/bash
# Run this once per repository

# Type labels
gh label create "pm:feature-request" --color "7057ff" --description "Feature request from PM analysis"
gh label create "pm:gap-identified" --color "7057ff" --description "Gap identified from competitor analysis"
gh label create "pm:competitor-intel" --color "7057ff" --description "Competitor intelligence gathering"
gh label create "pm:tech-debt" --color "7057ff" --description "Technical debt identified"

# Priority labels
gh label create "priority:now" --color "d73a4a" --description "Current sprint priority"
gh label create "priority:next" --color "fbca04" --description "Upcoming priority"
gh label create "priority:later" --color "c5def5" --description "Future backlog"

# WINNING score labels
gh label create "winning:high" --color "0e8a16" --description "WINNING score 40-60"
gh label create "winning:medium" --color "84b6eb" --description "WINNING score 25-39"
gh label create "winning:low" --color "e4e669" --description "WINNING score 0-24"

# Status labels
gh label create "pm:stale" --color "d4c5f9" --description "No activity >60 days"
gh label create "pm:hot" --color "ff6b6b" --description "High recent activity"
gh label create "pm:blocked" --color "b60205" --description "Blocked by dependency"
```

---

## Label Assignment Logic

### On Issue Creation (`/pm file`)

```
IF winning_score >= 40:
    labels += ["winning:high"]
ELIF winning_score >= 25:
    labels += ["winning:medium"]
ELSE:
    labels += ["winning:low"]

labels += ["pm:feature-request"]
```

### On Roadmap Planning (`/pm roadmap`)

```
sorted_issues = sort_by_winning_score(open_issues)

FOR i, issue IN sorted_issues:
    IF i < 3:
        add_label(issue, "priority:now")
        remove_labels(issue, ["priority:next", "priority:later"])
    ELIF i < 8:
        add_label(issue, "priority:next")
        remove_labels(issue, ["priority:now", "priority:later"])
    ELSE:
        add_label(issue, "priority:later")
        remove_labels(issue, ["priority:now", "priority:next"])
```

### On Backlog Check (`/pm backlog`)

```
FOR issue IN open_issues:
    last_activity = get_last_activity_date(issue)
    comment_count_7d = get_comments_since(issue, 7_days_ago)

    IF days_since(last_activity) > 60:
        add_label(issue, "pm:stale")
    ELSE:
        remove_label(issue, "pm:stale")

    IF comment_count_7d > 5:
        add_label(issue, "pm:hot")
    ELSE:
        remove_label(issue, "pm:hot")
```

---

## Filtering Examples

### Find All High-Priority Items
```bash
gh issue list --label "priority:now"
```

### Find High-Conviction Features
```bash
gh issue list --label "winning:high" --label "pm:feature-request"
```

### Find Stale Items Needing Attention
```bash
gh issue list --label "pm:stale"
```

### Find Hot Items (Active Discussion)
```bash
gh issue list --label "pm:hot"
```

### Complex Query: Now + High Conviction
```bash
gh issue list --label "priority:now" --label "winning:high"
```

---

## Label Maintenance

### Weekly (during `/pm standup`)
- Check for stale issues (>60 days no activity)
- Check for hot issues (sudden activity spike)

### After Gap Analysis (`/pm gaps`)
- New gaps get `pm:gap-identified` temporarily
- Converted to `pm:feature-request` when filed

### After Roadmap Update (`/pm roadmap`)
- Reassign priority labels based on current scores
- Only one priority label per issue

---

## Integration with GitHub Projects (Optional)

If using GitHub Projects, map labels to columns:

| Column | Filter |
|--------|--------|
| Now | `label:priority:now` |
| Next | `label:priority:next` |
| Later | `label:priority:later` |
| Stale | `label:pm:stale` |

This creates an auto-organized Kanban board from PM labels.
