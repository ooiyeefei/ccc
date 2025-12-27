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

## Commands Reference

### `/pm:analyze` - Product Discovery

**Purpose:** Build a comprehensive understanding of your current product

**When to use:** First command when starting PM workflow on a new project

**What it does:**
- Scans codebase structure (domains, APIs, features)
- Interviews you about positioning, target users, differentiators
- Creates `.pm/product/inventory.md` with feature inventory
- Identifies technical moats and constraints

**Output:** `.pm/product/` directory with product documentation

---

### `/pm:landscape [name]` - Competitor Research

**Purpose:** Research the competitive landscape or deep-dive on specific competitors

**When to use:** After `/pm:analyze`, before gap analysis

**Usage:**
```bash
/pm:landscape              # Market overview, identify top 5 competitors
/pm:landscape Expensify    # Deep-dive on specific competitor
/pm:landscape Dext         # Deep-dive on another competitor
```

**What it does:**
- Without argument: Creates market landscape overview
- With argument: Deep research on named competitor (pricing, features, positioning)

**Output:** `.pm/competitors/_landscape.md` or `.pm/competitors/[name].md`

---

### `/pm:gaps` - Gap Analysis with WINNING Filter

**Purpose:** Identify feature gaps and score them objectively

**When to use:** After competitor research, to prioritize what to build

**What it does:**
1. Loads product inventory + competitor data
2. Identifies gaps (features competitors have that you don't)
3. Scores each gap with WINNING filter (Pain + Timing + Execution + Fit + Revenue + Moat)
4. Outputs decision: FILE (40-60), WAIT (25-39), SKIP (0-24)

**Output:** `.pm/gaps/[date]-analysis.md` with scored gaps and recommendations

---

### `/pm:file [id|all]` - Batch File Gaps as Issues

**Purpose:** Convert gaps from analysis into GitHub Issues (lightweight)

**When to use:** After `/pm:gaps` when you want to quickly file multiple gaps

**Usage:**
```bash
/pm:file              # Interactive: review each gap, decide FILE/WAIT/SKIP
/pm:file GAP-003      # File specific gap by ID
/pm:file all          # Batch file all gaps scored 40+ (FILE threshold)
```

**What it does:**
- Creates GitHub Issues from gap analysis results
- Applies labels: `pm:feature-request`, `winning:high/medium/low`, `priority:now/next/later`
- Checks for duplicates against synced issues

**Output:** GitHub Issues with gap summary, WINNING score breakdown

**Issue detail level:** Brief (title, score, short description)

---

### `/pm:prd <feature>` - Generate Full PRD + Issue

**Purpose:** Create comprehensive Product Requirements Document for a specific feature

**When to use:** When you need detailed specs before implementation

**Usage:**
```bash
/pm:prd Plaid bank transaction matching
/pm:prd Bulk invoice processing
/pm:prd Real-time collaboration
```

**What it does:**
1. Gathers context from gap analysis and competitor data (if available)
2. Generates comprehensive PRD with 10+ sections
3. Saves PRD to `.pm/prds/[feature-slug].md`
4. Creates GitHub Issue with full PRD as body

**PRD sections:**
- Problem Statement
- User Stories
- Competitive Analysis
- Requirements (Functional, Non-Functional)
- Acceptance Criteria (P0/P1/P2)
- Edge Cases
- Out of Scope
- Technical Considerations
- Success Metrics

**Output:** Full PRD file + detailed GitHub Issue

**Issue detail level:** Comprehensive (full PRD, ready for spec-kit handoff)

---

### `/pm:sync` - GitHub Sync for Deduplication

**Purpose:** Sync local cache with existing GitHub Issues

**When to use:**
- At session start (hook will remind you if >24 hours since last sync)
- Before running `/pm:gaps` to ensure accurate deduplication
- After creating issues outside of PM plugin

**What it does:**
1. Fetches all GitHub Issues with `pm:feature-request` label
2. Saves to `.pm/requests/[issue-number].md`
3. Updates `.pm/cache/last-updated.json` timestamp

**Output:** Synced local cache, prevents duplicate issue creation

---

## `/pm:file` vs `/pm:prd` - When to Use Which

| Aspect | `/pm:file` | `/pm:prd` |
|--------|-----------|----------|
| **Input** | Gap IDs from `/pm:gaps` | Any feature name |
| **Output** | Lightweight GitHub Issue | Full PRD + GitHub Issue |
| **Detail** | Brief (score + description) | Comprehensive (10+ sections) |
| **Use for** | Batch filing many gaps | Deep spec for priority feature |
| **Speed** | Fast (multiple at once) | Slower (thorough analysis) |

**Typical workflow:**
```bash
/pm:gaps                    # Identify 15 gaps
/pm:file all                # Quick: batch file all high-score gaps
/pm:prd <top priority>      # Deep: full PRD for #1 priority feature
```

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
