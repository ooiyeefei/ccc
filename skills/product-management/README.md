# Product Management Skill

AI-native product management for startups. Process signals, not features.

## Quick Start

```bash
# Install the skills collection
/plugin marketplace add ooiyeefei/ccc
/plugin install ccc-skills@ccc

# Then ask Claude Code:
"Analyze my product"
"Research competitors in my space"
"Find feature gaps we should build"
```

## Philosophy

```
WINNING = Pain × Timing × Execution Capability
```

Expert PMs don't track features—they **process signals**. This skill filters 50 gaps down to 3-5 high-conviction priorities using objective scoring.

## Commands

| Command | Purpose |
|---------|---------|
| `/pm analyze` | Deep product understanding (code scan + user interview) |
| `/pm audit` | Quick health check |
| `/pm landscape` | Market overview, identify competitors |
| `/pm scout [name]` | Deep competitor profile |
| `/pm gaps` | **THE key command** - batch gap analysis with WINNING scores |
| `/pm review` | Interactive decision: FILE / WAIT / SKIP for each gap |
| `/pm file` | Batch create GitHub Issues for filed gaps |
| `/pm backlog` | View filed issues sorted by priority |
| `/pm prd [feature]` | Generate PRD from feature request |
| `/pm roadmap` | Organize into Now / Next / Later |
| `/pm standup` | Quick status summary |

## Workflow

```
/pm analyze  →  /pm landscape  →  /pm gaps  →  /pm review  →  /pm file  →  /pm roadmap
    │               │                │              │            │            │
    ▼               ▼                ▼              ▼            ▼            ▼
 Product        Competitor       15 gaps       FILE 3       GitHub       Now/Next/
 inventory      profiles         scored        WAIT 7       Issues       Later
                                               SKIP 5
```

## WINNING Filter

Hybrid scoring: Claude suggests Pain/Timing (researchable), you score Exec/Fit/Revenue/Moat (domain knowledge).

| Criterion | Scorer | Score Range |
|-----------|--------|-------------|
| Pain Intensity | Claude | 1-10 |
| Market Timing | Claude | 1-10 |
| Execution Capability | You | 1-10 |
| Strategic Fit | You | 1-10 |
| Revenue Potential | You | 1-10 |
| Competitive Moat | You | 1-10 |

**Thresholds:**
- **40-60**: FILE (high conviction)
- **25-39**: WAIT (monitor)
- **0-24**: SKIP (not worth it)

## GitHub Integration

Issues are created with:
- Problem statement + user stories
- Competitor evidence
- WINNING score breakdown
- Acceptance criteria

Labels auto-applied:
- `pm:feature-request`, `priority:now/next/later`, `winning:high/medium/low`

## spec-kit Integration

This skill handles **WHAT to build and WHY** (product discovery).
For **HOW to build it**, use [spec-kit](https://github.com/github/spec-kit):

```
PM Skill                    spec-kit
────────                    ────────
/pm file → GitHub Issue  →  /speckit.specify
                            /speckit.plan
                            /speckit.tasks
                            /speckit.implement
```

The GitHub Issue IS the handoff—no extra step needed.

## Data Storage

All data in `.pm/` folder (add to git for team sharing):

```
.pm/
├── config.md              # Preferences, positioning
├── product/               # Feature inventory, architecture
├── competitors/           # Profiles + landscape overview
├── gaps/                  # Date-stamped analyses
└── requests/              # Local copies of filed issues
```

## Example Usage

```bash
# Full PM sprint
/pm analyze                    # Understand your product
/pm landscape                  # Find top 5 competitors
/pm scout notion              # Deep dive on Notion
/pm scout linear              # Deep dive on Linear
/pm gaps                      # Identify and score all gaps
/pm review                    # Decide: FILE/WAIT/SKIP
/pm file                      # Create 3 GitHub Issues
/pm roadmap                   # Organize into Now/Next/Later

# Then pick an issue and use spec-kit to build it
```

## See Also

- [SKILL.md](./SKILL.md) - Full skill documentation
- [references/winning-filter.md](./references/winning-filter.md) - Detailed scoring guide
- [examples/gap-analysis.md](./examples/gap-analysis.md) - Sample output
