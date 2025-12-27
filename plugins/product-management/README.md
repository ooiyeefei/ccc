# Product Management Plugin

AI-native product management for startups. Transform Claude into an expert PM that processes signals, not just feature lists.

## Features

- **Competitive Research**: Deep autonomous competitor analysis with multi-source research
- **Gap Analysis**: Systematic identification with WINNING filter prioritization
- **PRD Generation**: Generate PRDs and automatically create GitHub Issues
- **Deduplication**: Sync with GitHub Issues to avoid duplicate feature requests
- **Staleness Alerts**: SessionStart hook warns when PM data is outdated

## Core Philosophy

```
WINNING = Pain × Timing × Execution Capability
```

Score: 40-60 FILE | 25-39 WAIT | 0-24 SKIP

## Installation

```bash
# Add to Claude Code
claude plugin add /path/to/product-management

# Or copy to project
cp -r product-management/ /your/project/.claude-plugin/
```

## Commands

| Command | Description |
|---------|-------------|
| `/pm:analyze` | Scan codebase + interview for product inventory |
| `/pm:landscape [name]` | Research competitor landscape or deep-dive |
| `/pm:gaps` | Run gap analysis with WINNING filter |
| `/pm:file [id\|all]` | Batch create GitHub Issues for approved gaps |
| `/pm:prd <feature>` | Generate PRD and create GitHub Issue |
| `/pm:sync` | Sync local cache with GitHub Issues |

## Agents

| Agent | Triggers On | Purpose |
|-------|-------------|---------|
| `research-agent` | "research [competitor]", "scout [name]" | Deep web research |
| `gap-analyst` | "find gaps", "what should we build" | WINNING scoring |
| `prd-generator` | "create PRD for [feature]" | PRD + GitHub Issue |

## Workflow

```
1. /pm:analyze          → Understand current product
2. /pm:landscape        → Research competitors
3. /pm:gaps             → Identify & score gaps (WINNING filter)
4. /pm:file             → Create GitHub Issues
5. /pm:prd <feature>    → Generate PRD → GitHub Issue

→ Hand off to spec-kit for implementation
```

## Data Storage

```
.pm/
├── config.md                 # Positioning, scoring weights
├── product/                  # Product inventory, architecture
├── competitors/              # Competitor profiles
├── gaps/                     # Gap analyses with scores
├── requests/                 # Synced GitHub Issues (dedup)
├── prds/                     # Generated PRDs
└── cache/last-updated.json   # Staleness tracking
```

## Deduplication

Before creating issues, the plugin:
1. Syncs existing GitHub Issues (`/pm:sync`)
2. Fuzzy matches new gaps against existing (>80% = duplicate)
3. Warns about similar issues (50-80% match)
4. Only creates truly new issues

## GitHub Integration

**Labels** (auto-created):
```
pm:feature-request    pm:gap-identified    pm:competitor-intel
priority:now          priority:next        priority:later
winning:high (40+)    winning:medium (25-39)    winning:low (<25)
```

**Prerequisites**:
- GitHub CLI (`gh`) installed and authenticated
- Run `gh auth login` if needed

## Integration with spec-kit

PM plugin handles **WHAT** (discovery), spec-kit handles **HOW** (implementation):

```
/pm:prd → Creates GitHub Issue → /speckit.specify #issue
```

The GitHub Issue IS the handoff—no extra command needed.

## Plugin Components

| Type | Count | Files |
|------|-------|-------|
| Skills | 1 | SKILL.md + 4 references + 2 examples |
| Agents | 3 | research-agent, gap-analyst, prd-generator |
| Commands | 6 | analyze, landscape, gaps, file, prd, sync |
| Hooks | 1 | SessionStart staleness check |

## License

MIT
