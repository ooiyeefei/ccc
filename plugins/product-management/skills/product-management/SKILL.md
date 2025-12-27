---
name: product-management
description: This skill should be used when the user asks to "analyze my product", "research competitors", "find feature gaps", "create feature request", "prioritize backlog", "generate PRD", "plan roadmap", "what should we build next", "competitive analysis", "gap analysis", "sync issues", or mentions product management workflows. Provides AI-native PM capabilities for startups with signal-based feature tracking, the WINNING prioritization filter, and GitHub Issues integration with deduplication.
version: 0.2.0
---

# Product Management Skill

AI-native product management for startups. Transform Claude into an expert PM that processes signals, not just feature lists.

## Core Philosophy

```
WINNING = Pain × Timing × Execution Capability
```

Filter aggressively from 50 gaps to 3-5 high-conviction priorities. Expert PMs track **signals** with confidence scores, timestamps, and velocity.

## Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `/pm:analyze` | Scan codebase + interview for product inventory |
| `/pm:landscape` | Research competitor landscape |
| `/pm:gaps` | Run gap analysis with WINNING filter |
| `/pm:file` | Batch create GitHub Issues for approved gaps |
| `/pm:prd` | Generate PRD and create GitHub Issue |
| `/pm:sync` | Sync local cache with GitHub Issues |

## Agents

This plugin provides specialized agents for autonomous tasks:

| Agent | Triggers On | Purpose |
|-------|-------------|---------|
| `research-agent` | "research [competitor]", "scout [name]" | Deep autonomous web research |
| `gap-analyst` | "find gaps", "what should we build" | Systematic gap identification with scoring |
| `prd-generator` | "create PRD for [feature]" | Generate PRD + create GitHub Issue |

## Data Storage

All data stored in `.pm/` folder at project root:

```
.pm/
├── config.md                 # Positioning, scoring weights
├── product/                  # Product inventory, architecture
├── competitors/              # Competitor profiles
├── gaps/                     # Gap analyses with scores
├── requests/                 # Synced GitHub Issues (for dedup)
├── prds/                     # Generated PRDs
└── cache/last-updated.json   # Staleness tracking
```

See `references/data-structure.md` for complete file templates.

## WINNING Filter Scoring

Hybrid scoring approach - Claude suggests researchable criteria, user scores domain-specific:

| Criterion | Scorer | Source |
|-----------|--------|--------|
| Pain Intensity (1-10) | Claude | Review sentiment, support data |
| Market Timing (1-10) | Claude | Search trends, competitor velocity |
| Execution Capability (1-10) | User | Architecture fit, team skills |
| Strategic Fit (1-10) | User | Positioning alignment |
| Revenue Potential (1-10) | User | Conversion/retention impact |
| Competitive Moat (1-10) | User | Defensibility once built |

**Total: X/60** → Recommendation:
- **40+** → FILE (high conviction)
- **25-39** → WAIT (monitor)
- **<25** → SKIP (not worth it)

See `references/winning-filter.md` for detailed scoring criteria.

## Deduplication & Sync

Prevent duplicate feature requests by syncing with GitHub Issues:

### On Session Start
1. Check `.pm/cache/last-updated.json` for staleness
2. If >24 hours since last sync, prompt for `/pm:sync`

### `/pm:sync` Process
1. Fetch all GitHub Issues with `pm:*` labels via `gh issue list --json`
2. Update `.pm/requests/[issue-number].md` for each issue
3. Update `last-updated.json` timestamp

### Deduplication During Gap Analysis
1. Load existing issues from `.pm/requests/`
2. For each new gap, fuzzy match against existing:
   - Title similarity (Levenshtein): 40% weight
   - Keyword overlap: 30% weight
   - Label match: 20% weight
   - Description similarity: 10% weight
3. Mark gaps as:
   - **EXISTING** (>80% match) → Show linked issue
   - **SIMILAR** (50-80%) → Warn, ask user
   - **NEW** (<50%) → Proceed normally

### Output Format
```markdown
| Gap | WINNING | Status | Match |
|-----|---------|--------|-------|
| OAuth support | 47/60 | EXISTING | #42 (95%) |
| Dark mode | 38/60 | NEW | - |
```

## Flow Summaries

### Product Analysis (`/pm:analyze`)
1. Scan codebase for features (routes, components, APIs, models)
2. Interview user for business context
3. Generate inventory with technical moats and debt flags
4. Save to `.pm/product/`

### Competitive Intelligence (`/pm:landscape`, `/pm:scout [name]`)
1. Research competitors via WebFetch/WebSearch
2. Categorize features: Tablestakes, Differentiators, Emerging, Deprecated
3. Save profiles to `.pm/competitors/`

### Gap Analysis (`/pm:gaps`)
1. Load product inventory + competitor profiles
2. Check staleness (>30 days → prompt refresh)
3. Sync with GitHub Issues for deduplication
4. Identify all gaps, score with WINNING filter
5. Mark as NEW/EXISTING/SIMILAR
6. Save to `.pm/gaps/[date]-analysis.md`

### Feature Filing (`/pm:review`, `/pm:file`)
1. `/pm:review` - Walk through gaps, decide FILE/WAIT/SKIP
2. `/pm:file` - Create GitHub Issues for approved gaps (skips duplicates)
3. Apply labels: `pm:feature-request`, `winning:*`, `priority:*`

### PRD Generation (`/pm:prd [feature]`)
1. Load feature context from gap analysis or GitHub Issue
2. Generate PRD: Problem, User Stories, Acceptance Criteria, etc.
3. Save to `.pm/prds/[slug].md`
4. **Create GitHub Issue** with PRD content as feature request

### Backlog & Roadmap (`/pm:backlog`, `/pm:roadmap`)
1. Fetch open issues with `pm:` labels
2. Sort by WINNING score or RICE
3. Organize into Now/Next/Later priorities

## GitHub Integration

### Labels (Auto-Created)
```
pm:feature-request    pm:gap-identified    pm:competitor-intel
priority:now          priority:next        priority:later
winning:high (40+)    winning:medium (25-39)    winning:low (<25)
```

### Prerequisites
- GitHub CLI (`gh`) installed and authenticated
- Run `gh auth status` to verify

See `references/github-labels.md` for label definitions.
See `references/issue-template.md` for issue format.

## Integration with spec-kit

This plugin handles **WHAT to build and WHY** (product discovery).
For **HOW to build it**, use spec-kit:

```
PM Plugin → GitHub Issue → spec-kit
/pm:file     Creates issue   /speckit.specify
/pm:prd      Creates issue   /speckit.plan → /speckit.implement
```

The GitHub Issue IS the handoff—no separate command needed.

## Staleness Handling

PM data ages. Handle proactively:

- **Competitor data >30 days**: Prompt refresh before gap analysis
- **Gap analysis >14 days**: Warn when viewing backlog
- **GitHub sync >24 hours**: Suggest `/pm:sync` on session start

```
⚠️ Competitor data is 45 days old. Run `/pm:landscape` to refresh.
```

## Additional Resources

### Reference Files
- **`references/winning-filter.md`** - Detailed WINNING scoring criteria
- **`references/github-labels.md`** - Label definitions and colors
- **`references/issue-template.md`** - GitHub Issue template
- **`references/data-structure.md`** - Complete `.pm/` folder structure

### Example Files
- **`examples/gap-analysis.md`** - Sample gap analysis output
- **`examples/competitor-profile.md`** - Sample competitor profile
