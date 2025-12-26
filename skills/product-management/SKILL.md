---
name: product-management
description: This skill should be used when the user asks to "analyze my product", "research competitors", "find feature gaps", "create feature request", "prioritize backlog", "generate PRD", "plan roadmap", "what should we build next", "competitive analysis", "gap analysis", or mentions product management workflows. Provides AI-native PM capabilities for startups with signal-based feature tracking and the WINNING prioritization filter.
version: 0.1.0
---

# Product Management Skill

AI-native product management for startups. Transform Claude into an expert PM that processes signals, not just feature lists.

## Core Philosophy

```
WINNING = Pain × Timing × Execution Capability
```

Filter aggressively from 50 gaps to 3-5 high-conviction priorities. Expert PMs don't track features—they track **signals** with confidence scores, timestamps, and velocity.

## Quick Start

**Trigger phrases → Flows:**

| User Says | Flow |
|-----------|------|
| "analyze my product" / "what features do we have" | Flow 1: Product Analysis |
| "research competitors" / "competitive landscape" | Flow 2: Competitive Intelligence |
| "find gaps" / "what are we missing" / "gap analysis" | Flow 3: Gap Analysis |
| "file feature request" / "log this as a request" | Flow 4: Feature Filing |
| "show backlog" / "prioritize features" | Flow 5: Backlog Management |
| "create PRD" / "write spec for [feature]" | Flow 6: PRD Generation |
| "plan roadmap" / "what's next" | Flow 7: Roadmap Planning |
| "standup" / "quick status" | Flow 8: Status Summary |

## Data Storage

All data stored in `.pm/` folder at project root:

```
.pm/
├── config.md                    # Positioning, scoring weights
├── product/
│   ├── inventory.md             # Features from code + user context
│   └── architecture.md          # Tech constraints, moats
├── competitors/
│   ├── _landscape.md            # Market overview
│   └── [competitor].md          # Per-competitor profiles
├── gaps/
│   └── [date]-analysis.md       # Batch gap analyses
├── requests/
│   └── [request-id].md          # Local feature request copies
└── cache/
    └── last-updated.json        # Staleness tracking
```

See `references/data-structure.md` for complete file templates.

---

## Flow 1: Product Analysis (`/pm analyze`)

Deep understanding of current product state.

### Process

1. **Scan codebase** for structure:
   - Routes/pages → user-facing features
   - Components → UI capabilities
   - API endpoints → backend functionality
   - Database models → data entities

2. **Interview user** for business context:
   - "What's your core value proposition?"
   - "Who are your target users?"
   - "What's your pricing model?"
   - "What do users love most? Complain about most?"

3. **Generate inventory**:
   - List all features with metadata
   - Identify technical moats (hard to replicate)
   - Flag technical debt areas
   - Note architectural constraints

4. **Save to** `.pm/product/inventory.md` and `.pm/product/architecture.md`

### Output Format

```markdown
# Product Inventory - [Date]

## Core Value Proposition
[User-provided]

## Features

| Feature | Type | Technical Moat | Debt Level |
|---------|------|----------------|------------|
| [Name] | Core/Differentiator/Nice-to-have | High/Med/Low | High/Med/Low |

## Architecture Constraints
- [Constraint 1]
- [Constraint 2]
```

---

## Flow 2: Competitive Intelligence (`/pm landscape`, `/pm scout [name]`)

Multi-source competitor research with hybrid approach (AI research + user input).

### `/pm landscape` Process

1. **Identify competitors**:
   - Ask user: "Who are your top 3-5 competitors?"
   - Supplement with web research if user unsure

2. **For each competitor**, gather via WebFetch/WebSearch:
   - Website → features, pricing, positioning
   - Product Hunt → launch history, user reception
   - G2/Capterra → user reviews, ratings
   - Job postings → future direction signals

3. **Create market overview** in `.pm/competitors/_landscape.md`

### `/pm scout [name]` Process

Deep dive on single competitor:

1. **Research multiple sources**:
   - Pricing page → feature tiers
   - Changelog/blog → velocity and direction
   - Reviews → user sentiment
   - Job postings → hiring signals

2. **Categorize features**:
   - **Tablestakes** - Everyone has these
   - **Differentiators** - Their unique selling points
   - **Emerging** - New bets they're making
   - **Deprecated** - What they gave up on

3. **Save profile** to `.pm/competitors/[name].md`

See `examples/competitor-profile.md` for format.

---

## Flow 3: Gap Analysis (`/pm gaps`)

THE key command. Identifies batch gaps and scores with WINNING filter.

### Process

1. **Load context**:
   - Read `.pm/product/inventory.md`
   - Read all `.pm/competitors/*.md`

2. **Check staleness**:
   - If data >30 days old, prompt: "Competitor data is [X] days old. Refresh first?"
   - See `references/data-structure.md` for staleness rules

3. **Identify ALL gaps**:
   - Features competitors have that we don't
   - Features multiple competitors are building (trends)
   - Features from user reviews/requests

4. **Score each gap** with WINNING filter (hybrid scoring):

   | Criterion | Scorer | Source |
   |-----------|--------|--------|
   | Pain Intensity (1-10) | Claude suggests | Review sentiment, support data |
   | Market Timing (1-10) | Claude suggests | Search trends, competitor velocity |
   | Execution Capability (1-10) | User scores | Architecture fit, team skills |
   | Strategic Fit (1-10) | User scores | Positioning alignment |
   | Revenue Potential (1-10) | User scores | Conversion/retention impact |
   | Competitive Moat (1-10) | User scores | Defensibility once built |

   **Total: X/60** → Recommendation:
   - 40+ → FILE (high conviction)
   - 25-39 → WAIT (monitor)
   - <25 → SKIP (not worth it)

5. **Save analysis** to `.pm/gaps/[date]-analysis.md`

See `references/winning-filter.md` for detailed scoring criteria.
See `examples/gap-analysis.md` for output format.

---

## Flow 4: Feature Filing (`/pm review`, `/pm file`)

Batch decision-making and GitHub Issue creation.

### `/pm review` Process

Walk through each gap from latest analysis:
1. Show gap with score and evidence
2. Ask: "FILE / WAIT / SKIP?"
3. Allow score adjustments
4. Save decisions to gap analysis file

### `/pm file` Process

Batch create GitHub Issues for all gaps marked "FILE":

1. **Check `gh` CLI availability**:
   ```bash
   gh auth status
   ```

2. **If `gh` available**, auto-create issues with template from `references/issue-template.md`

3. **If `gh` unavailable**, output markdown for manual creation

4. **Apply labels** (see `references/github-labels.md`):
   - `pm:feature-request`
   - `winning:high` / `winning:medium` / `winning:low`
   - `priority:now` / `priority:next` / `priority:later`

5. **Save local copies** to `.pm/requests/[id].md`

---

## Flow 5: Backlog Management (`/pm backlog`)

View and sort filed feature requests.

### Process

1. **Fetch open issues** with `pm:` labels via `gh issue list`
2. **Sort by** multiple frameworks:
   - WINNING score (default)
   - RICE (Reach × Impact × Confidence / Effort)
   - Recency (newest first)
3. **Flag issues**:
   - "Hot" → velocity spike (many recent comments)
   - "Stale" → no activity >60 days
4. **Display** as formatted table

---

## Flow 6: PRD Generation (`/pm prd [feature]`)

Generate PRD from feature request context.

### Process

1. **Load feature context** from GitHub Issue or `.pm/requests/`
2. **Generate PRD sections**:
   - Problem Statement (from issue)
   - User Stories (from patterns)
   - Acceptance Criteria (from competitor implementations)
   - Edge Cases (from review complaints)
   - Technical Requirements (from architecture analysis)
   - Out of Scope (explicit boundaries)
3. **Save to** `.pm/prds/[feature-slug].md`
4. **Note**: PRD is spec-kit ready—user runs `/speckit.specify` next

---

## Flow 7: Roadmap Planning (`/pm roadmap`)

Organize backlog into Now/Next/Later.

### Process

1. **Load all filed issues** from GitHub
2. **Apply labels** based on WINNING scores:
   - `priority:now` → Top 2-3 highest scores
   - `priority:next` → Next 3-5
   - `priority:later` → Rest
3. **Check dependencies** between features
4. **Output roadmap** view:

```markdown
## Now (Current Sprint)
1. [Feature A] - WINNING: 47/60
2. [Feature B] - WINNING: 44/60

## Next (Upcoming)
3. [Feature C] - WINNING: 41/60 (blocked by #1)

## Later (Backlog)
4-N. [Remaining features...]
```

---

## Flow 8: Status Summary (`/pm standup`)

Quick status for standups or updates.

### Process

1. **Summarize**:
   - Issues in progress
   - Recently closed
   - Blocked items
   - Top priority next
2. **Check staleness** of PM data
3. **Output** concise summary

---

## Staleness Handling

PM data ages. Handle proactively:

- **Passive**: Show warning when viewing stale data (>30 days)
- **Active**: Prompt refresh before gap analysis

```markdown
⚠️ Competitor data is 45 days old. Run `/pm scout [name]` to refresh.
```

---

## GitHub Integration

### Labels (Auto-Created on First Use)

```
pm:feature-request    pm:gap-identified    pm:competitor-intel
priority:now          priority:next        priority:later
winning:high          winning:medium       winning:low
```

See `references/github-labels.md` for complete definitions.

### Issue Template

Issues created by `/pm file` include:
- Problem statement
- User stories
- Competitor evidence
- WINNING score breakdown
- Constraints
- Acceptance criteria

See `references/issue-template.md` for full template.

---

## Integration with spec-kit

This skill handles **WHAT to build and WHY** (product discovery).
For **HOW to build it**, use spec-kit:

```
PM Skill → GitHub Issue → spec-kit
/pm file    Creates issue   /speckit.specify (consumes issue)
                            /speckit.plan
                            /speckit.tasks
                            /speckit.implement
```

The GitHub Issue IS the handoff—no separate command needed.

---

## Additional Resources

### Reference Files

For detailed information, consult:
- **`references/winning-filter.md`** - Complete WINNING scoring criteria and examples
- **`references/github-labels.md`** - Standard label definitions and colors
- **`references/issue-template.md`** - GitHub Issue template for feature requests
- **`references/data-structure.md`** - Complete `.pm/` folder structure and file templates

### Example Files

Working examples in `examples/`:
- **`examples/gap-analysis.md`** - Sample gap analysis output
- **`examples/competitor-profile.md`** - Sample competitor research profile
