# Agentic System Design - Prescriptive Design Partner

Design any agentic system — tool-loop agents, multi-model councils, sub-agent hierarchies, plan-execute pipelines, handoff networks — through a 12-stage Q&A flow that emits a buildable design doc with citations.

---

## What It Does

This skill turns Claude Code into an opinionated design partner that filters ruthlessly *before* you build anything expensive:

1. **Captures the use case** — what the system does, and the blast radius of one bad output
2. **Filters agent-washing** — a 6-point real-agency-vs-workflow rubric (~30% of "agent" requests are workflows)
3. **Filters wasteful councils** — a 4-condition council-decision test (~60% of "I want a council" requests fail it)
4. **Picks a pattern** — one of 7 SOTA patterns (Tool-Loop/ReAct, Orchestrator-Workers, Magentic, Plan-and-Execute, Evaluator-Optimizer, Tool-Loop with Spawning, Handoff/Routing), with rationale
5. **Designs the roster** — council shape, personas, model routing, tool-loop config
6. **Sanity-checks depth** — depth-3 hierarchies are allowed in 3 named cases only
7. **Emits a design doc** — every recommendation cited (Anthropic, OpenAI, Microsoft, arXiv), anti-patterns surfaced, build order included

**No code is written.** The output is a design doc you can hand to an engineer. Implementation lives in the companion [agentic-toolkit](../../plugins/agentic-toolkit) reference package and your repo.

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Usage

Trigger the skill naturally:

```
"Design an agent that does HAZOP analysis"
"Should I use a multi-model council for finance review?"
"I want to build an AI brand strategist — orchestrator-worker or handoff?"
"Real agency or workflow?"
"Add sub-agents to my research pipeline"
```

The skill asks **one question at a time** (Socratic style, no question dumps). If you paste a wall of context, it extracts the answers you've implicitly given and asks only the missing ones.

## How It Works

### The 12-Stage Flow

| Stages | What gets decided |
|--------|-------------------|
| 1–3 | Use case + blast radius, operational mode (sync/batch/event/scheduled), hard boundaries the system must not touch |
| 4 | **Filter #1:** real-agency-vs-workflow rubric — score ≤2 and it pivots you to a workflow pattern instead |
| 5 | Pattern selection — the skill proposes one of 7, not a menu |
| 6 | **Filter #2:** council-decision test — 0 conditions met means single agent + judge/retry, skip the council |
| 7–10 | Council shape, persona roster, model routing, tool-loop hardening |
| 11 | **Filter #3:** depth-3 sanity check — most depth-3 hierarchies are depth-2 with a tool that needed renaming |
| 12 | Design doc emitted: pattern + roster + routing + build order, with inline citations |

### Why the Filters Exist

Most "agent" requests want determinism but pattern-matched on a hype word; most "council" requests buy latency and cost for gains that majority voting or a single critic loop already captures. When you fail a filter the skill doesn't lecture — it pivots: *"Looks like a workflow. Here's the right shape for that, and how to add agentic frosting later if it pays off."*

## Skill Structure

```
agentic-system-design/
├── SKILL.md                       # The 12-stage Q&A flow + decision rubrics
├── README.md                      # This file
├── references/
│   ├── patterns-catalog.md        # 7 patterns deep-dive, workflows-vs-agents
│   ├── council-shapes.md          # 7 council shapes + when each pays off
│   ├── llm-as-judge.md            # Judge design, self-preference bias
│   ├── failure-modes.md           # Known multi-agent failure modes
│   └── case-*.md                  # Worked cases: HAZOP, finance, marketing, tutorial-gen
└── examples/
    ├── tool-loop.md               # Minimal tool-loop agent
    ├── foreman.md                 # Council foreman state machine
    ├── multi-model-router.md      # Per-role model routing
    └── sub-agent-runner.md        # Depth-capped sub-agent spawning
```

See [SKILL.md](./SKILL.md) for the full 12-stage flow and decision rubrics.
