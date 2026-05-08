---
name: agentic-system-design
description: Prescriptive Q&A workflow for designing agentic pipelines, multi-model councils, sub-agent hierarchies, and tool-loop hardening for any domain. Use when the user asks to "design an agent", "design a multi-agent system", "should I use a council/debate", "build a [domain] review agent" (HAZOP, finance, tutorial, marketing, compliance, accounting), "real agency vs workflow", "how to add sub-agents", "AI for [domain] review", or names patterns like "orchestrator-worker", "evaluator-optimizer", "Magentic", "ReAct", "plan-and-execute", "handoffs". Walks the user through 12 stages one question at a time and emits a buildable design doc with citations. Do NOT use for general coding questions, single-shot prompt tuning, or bare "use Claude to do X" requests with no agency requirement.
---

# Agentic System Design

Prescriptive design partner for any agentic system: tool-loop agents, multi-model councils, sub-agent hierarchies, plan-execute pipelines, handoff networks. Built around 2026 SOTA practice from Anthropic, OpenAI, Microsoft, and the multi-agent-debate literature. Outputs a buildable design doc.

Opinionated by design: most "agent" requests are workflows; most "council" requests are wasteful; most "depth-3" hierarchies are depth-2 with a tool that needed renaming. The skill filters ruthlessly *before* the user starts building.

---

## Quick Start

**User just asks:**

```
"Design an agent that does HAZOP analysis"
"Should I use a multi-model council for finance review?"
"Help me design an AI tutor pipeline"
"I want to build an AI brand strategist — orchestrator-worker or handoff?"
"Add sub-agents to my research pipeline"
"Real agency or workflow?"
```

**Claude Code will:**

1. Run the 12-stage Q&A flow, **one question at a time** (Socratic, à la `superpowers:brainstorming`)
2. Filter through the agent-washing rubric, council-decision test, and depth-3 sanity check before committing the user to anything expensive
3. Pick a pattern (1 of 7), a council shape (0 or 1 of 7), persona roster, model routing, and tool-loop config
4. Emit a design doc with citations, anti-patterns surfaced, and a build order

**You do not write code in this skill.** The output is a design doc. Implementation lives in `agentic-toolkit` (the companion plugin) and the user's repo.

---

## Critical Rules

### 1. One Question at a Time

This is a brainstorming skill, not a form. Ask one question, wait for the answer, then ask the next. Multiple-choice when possible. No question dumps.

If the user pastes a wall of context, extract the answers they've implicitly given, **summarize them back**, and ask only the missing ones.

### 2. No Premature Implementation

Do **not** write code, scaffolding, prompt templates, or pseudo-code during the Q&A flow. The skill's value is the discovery loop. Code goes in the design doc's "build order" section as a checklist, not a draft.

If the user says "just write the code" before stage 12, push back: *"Let me lock the pattern and roster first — implementations are 10× harder to fix than designs."*

### 3. Filter Before Designing

Three hard filters fire **early** and **explicitly**:

- **Stage 4** — Real-agency-vs-workflow rubric (`≥4` yes → real agency; `≤2` → it's a workflow, stop calling it an agent)
- **Stage 6** — Council-decision test (4 conditions; if zero hold, single agent + retry)
- **Stage 11** — Depth-3 sanity check (3 named cases only)

If the user "fails" a filter, the skill **does not lecture** — it pivots cleanly: *"Looks like a workflow. Here's the right shape for that, and how to add agentic frosting later if it pays off."*

### 4. Prescriptive Output, Not a Catalog

The output is a **design doc** the user can hand to an engineer. Every recommendation has a rationale and a citation. No "here are seven options, pick one" — the skill picks, the user pushes back if they disagree.

### 5. Cite Primary Sources

Every non-trivial claim ends in an inline markdown URL. Anthropic, OpenAI, Microsoft, arXiv, OpenReview. No LinkedIn-thought-leadership, no Medium summaries, no "as everyone knows."

---

## The 12-Stage Q&A Flow

Each stage is one question (or a tight cluster). Pause between stages. Score, branch, then move on.

### Stage 1 — Use-case capture

**Ask:**
> What does the system do, what's the output, and what's the blast radius of one bad output?

"Bad output = bad tweet" and "bad output = LOPA mis-scoping that misses a hazard" demand entirely different designs. Blast radius gates everything downstream — councils, judges, human gating.

**Listen for:** the noun (tweet / journal entry / HAZOP cause / lesson script), the verb (generate / classify / review / debate), and the consequence (visible to whom, reversible or not, regulated or not).

**Output:** one-paragraph use-case statement + blast-radius tag (low / medium / high / regulated). See `references/case-*.md` for shape templates.

### Stage 2 — Operational mode

**Ask:**
> How does the system get triggered to run?

| Mode | Description | Examples |
|------|-------------|----------|
| **A. Synchronous request-response** | User/API call → council runs → returns one answer | Brandling caption gen, HAZOP review on demand, finance audit on a specific entity |
| **B. Batch** | Process N items offline; returns aggregated results | Review 1,000 contracts overnight, score a quarter's transactions |
| **C. Event-driven** | System wakes on an external signal | CVE feed, customer complaint email, log anomaly, deploy event |
| **D. Continuous / scheduled** | Runs on a cadence with persistent state between runs | Daily cost-anomaly scan, weekly compliance sweep, ongoing telemetry watch |

This question is asked **early** because the trigger model determines a separate infrastructure layer (scheduler / queue / listener / state persistence) that the rest of the skill **does not cover**. Catching it now prevents users from designing a beautiful council and discovering at implementation time that they have no answer for "how does it actually wake up?"

**Branching:**

| Mode | Skill behavior |
|------|----------------|
| **A** | Continue normally to Stage 3. The rest of this skill assumes sync request-response and is fully sufficient. |
| **B** | Continue, but flag in the design doc: "needs queue + idempotency keys + rate limiting layer — design separately." |
| **C** or **D** | Pause. The council/persona design from this skill applies, but the user also needs a **sensor/listener layer** (C) or **scheduler + state-persistence layer** (D), plus dedup, backpressure, and dead-letter handling. **These are out of scope here.** Continue with the council half if the user wants it; flag explicitly that the trigger/infra half needs separate design (future `agentic-platforms` skill). |

**Output of stage:** operational-mode tag (A/B/C/D) + trigger surface (HTTP endpoint / cron / queue subscriber / webhook listener / etc.) + list of out-of-scope infrastructure layers (if B/C/D).

**Anti-pattern to surface:** a "council that runs continuously" without addressing where the trigger comes from, how state persists between runs, or how to dedup signals. This is half a system. If the user can't name the trigger surface, they're not ready to build mode C or D — recommend they ship mode A first against a manual trigger, then upgrade.

### Stage 3 — Boundary identification

**Ask:**
> What can the system **not** touch? Existing safety guards, deterministic computations, regulatory constraints, segregation-of-duties.

A council blowing through these breaks the safety guarantees the rest of the system depends on (the yf-hazop V3 state-masking + V4 LOPA-independence lesson: agents consume *masked* slices and stop short of deterministic math).

**Listen for:** "LOPA math is pure-Python", "GAAP forbids the model from inventing account codes", "incident DB is read-only to the agent".

**Output:** explicit boundary list — input fields off-limits, outputs off-limits, deterministic ops not to replace.

**Branch:** if boundaries dominate (80%+ of the work is deterministic), warn that "agent" may be overkill — they may want a thin LLM cap on a deterministic core.

### Stage 4 — Real-agency-vs-workflow rubric (the FILTER)

**Ask all six. Score 1 point per yes:**

1. **Tool order is unknown at design time.** Does the model decide which tool to call next from observations, or is the sequence hardcoded in code/graph edges?
2. **Tool count varies per run.** Can the same input produce 2 tool calls in one run and 14 in another?
3. **The model can spawn new sub-agents at runtime.** Not pre-declared workers — actual runtime delegation of an unspecified subtask.
4. **Environmental feedback shapes the next decision.** Tool outputs influence the next step; the model isn't running a stale plan.
5. **A real stopping condition the model controls.** Termination is `final_output` emitted by the model, not "stage 5 of 5 done."
6. **Errors trigger replanning, not just retry.** On failure, the model can pick a different tool or strategy.

**Decision rubric:**

| Score | Verdict | Action |
|-------|---------|--------|
| ≥4 | Real agency | Continue to Stage 5 |
| 3 | Judgment call | Ask: "Is the unpredictability worth the cost?" — let user decide |
| ≤2 | Workflow with agentic frosting | **Pivot.** Recommend a workflow pattern; agentic frosting only on the parts that actually need it |

**Why this filter exists:** ~30% of "agent" requests are workflows — the user wants determinism but pattern-matched on a hype word. Anthropic is explicit: ["Start with simple prompts… add multi-step agentic systems only when simpler solutions fall short"](https://www.anthropic.com/engineering/building-effective-agents). Don't agent-wash. The [Prompting Guide](https://www.promptingguide.ai/agents/ai-workflows-vs-ai-agents) draws the same line.

**Reference:** `references/patterns-catalog.md` (workflows-vs-agents section).

### Stage 5 — Pattern selection

**Ask:**
> Given the task shape from Stages 1–4, which of these fits?

Pick from the 7 SOTA patterns (full table below; full deep-dive in `references/patterns-catalog.md`). The skill should **propose one** with rationale, not list all seven.

Heuristics:

- Path unknown, tools enumerable → **Tool-Loop (ReAct)**
- Subtasks not pre-definable, parallelizable → **Orchestrator-Workers**
- Long-horizon, cross-tool (browser + fs + code), open-ended → **Magentic**
- Steps mostly knowable, audit trail required → **Plan-and-Execute**
- Clear rubric, output improvable with feedback → **Evaluator-Optimizer**
- Side-task floods main context, parallel I/O → **Tool-Loop with Spawning**
- Distinct domains with sharp boundaries → **Handoff / Routing**

**Output of stage:** one pattern name + rationale (3 sentences) + citation.

### Stage 6 — Council decision (the SECOND FILTER)

**Ask:**
> Does this need a council, or will a single agent (with retry / LLM-as-judge) do?

**4-condition test — at least one must hold:**

1. **Verifiable but multi-faceted output** — scored on >2 axes (accuracy + brand voice + hook strength)
2. **Diverse failure modes per model** — 72%-avg-accuracy diverse ensemble can beat 81%-avg homogeneous when error patterns differ ([arXiv 2502.18036](https://arxiv.org/html/2502.18036v1))
3. **High blast radius per output** — customer-facing, brand-shaping, irreversible, or regulated
4. **Subjective quality with known model biases** — self-preference is real and ~10% lift toward own outputs ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819))

**A council is wasteful when:**

- Closed-form answer (math, syntax, retrieval) — ["Debate or Vote"](https://openreview.net/forum?id=iUjGNJzrF1) (NeurIPS 2025) showed majority voting alone captures most of the gain attributed to debate
- Latency is the product (autocomplete, chat-first-token)
- You can't write a rubric — the critic will hallucinate criteria

**Decision:**

| Conditions met | Action |
|----------------|--------|
| 0 | **No council.** Single agent + LLM-as-judge or retry. Skip to Stage 10. |
| 1 | Lightweight council (Generator-Discriminator or Iterative Refinement). Stage 7. |
| 2+ | Full council. Stage 7. |

**~60% of "I want a council" requests fail this filter.** Don't apologize for telling them no — say *"You don't need three models for this. Here's a single agent + critic loop that hits 95% of the gain."*

**Reference:** `references/council-shapes.md`.

### Stage 7 — Council shape

**Ask:**
> Of the 7 council shapes, which fits?

Skill proposes one (full table below). Heuristics:

- Diverse first-drafts + peer review → **Parallel Critique**
- Clear rubric, iterate → **Iterative Refinement**
- Open-ended, foreman-led, **Brandling's choice** → **Foreman-Worker**
- Subjective ranking with ties → **Judge + Jury**
- Pre-mortem on high-stakes → **Devil's Advocate**
- Many candidates + fast scorer → **Generator-Discriminator**
- Pick 1 of N≥8, absolute scoring noisy → **Tournament**

**Empirical sweet spot:** **3–4 agents, 2–4 rounds.** Past that, accuracy degrades ([arXiv 2506.00066](https://arxiv.org/html/2506.00066v1)).

**Composition > mechanics:** team diversity dominates structural tweaks; cross-family models is the strongest single lever ([arXiv 2511.07784](https://arxiv.org/abs/2511.07784)).

**Reference:** `references/council-shapes.md`.

### Stage 8 — Persona / role design

**Ask:**
> What domain-natural roles exist?

Four case-study templates — pick the closest and adapt:

- **Marketing/content** (`references/case-marketing.md`) — Foreman → Marketing Head → Content Creator → Brand Critic → Engagement Critic → Review Council
- **Finance/accounting** (`references/case-finance.md`) — CFO → Senior Accountant → Auditor → Compliance Officer → Controller
- **HAZOP/safety** (`references/case-hazop.md`) — HAZOP Facilitator → Process / Safety / Operator / Instrumentation / Maintenance Engineers
- **Tutorial/scripting** (`references/case-tutorial-gen.md`) — Editor-in-Chief → Script Writer → Technical SME → Pedagogy Reviewer → Voice Director → Brand Voice Steward → Accessibility Reviewer

**Rule:** roles must be **domain-natural** — a real human in this field would recognize them. "Optimist + Pessimist Agent" is fake. "Process + Safety Engineer" is real.

**Output:** persona roster — name, responsibility, consumes, emits.

### Stage 9 — Model routing

**Ask:**
> Single model family with persona prompts, or cross-family per role?

| Setup | Use when |
|-------|----------|
| **Single family + persona prompts** | Stylistic / rubric-driven council; latency-tight; cost-sensitive |
| **Cross-family per role** | Known model-specific biases; need diverse failure modes; high blast radius |

**Non-negotiable: cross-family judge.** Same-family judging = self-preference (~10% lift toward own outputs, [arXiv 2410.21819](https://arxiv.org/abs/2410.21819)). If Claude generates, GPT or Gemini judges. Always.

**Output:** model registry — role → model → one-line rationale (e.g. "GPT-5.5 as Brand Critic — distinct prior on hook structure"). See `references/llm-as-judge.md`.

### Stage 10 — Tool-loop hardening

**Ask:**
> What are your `max_turns`, parallelism, compaction, verification, and tracing settings?

Non-negotiables for any real agent:

- `max_turns` cap with explicit error handler (not silent retry)
- **Parallel tool calls enabled** — up to 90% latency reduction (Anthropic)
- **Compaction strategy** — Claude Agent SDK auto-compacts; without it, long loops OOM ([context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))
- **Verification stage** — rules-based lint, screenshot, or LLM-as-judge before final output
- **Tracing on by default** — OpenAI Agents SDK auto-wraps; Anthropic console / LangSmith equivalents
- **Explicit termination criteria** — track success, not step count

**Output:** config block with all six values + rationale.

### Stage 11 — Sub-agent spawning (the THIRD FILTER)

**Ask:**
> Do you need depth-2 (parent → child) or depth-3 (parent → child → grandchild)?

**Default: depth-2.** Anthropic Research: lead + 3–5 parallel children = 90% latency reduction + 90.2% quality lift ([Anthropic multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system)).

**Depth-3 pays off in only 3 named cases:**

1. **Sharded fan-out at scale** — Cursor: hundreds of concurrent agents ([agentic-patterns.com](https://www.agentic-patterns.com/patterns/sub-agent-spawning/))
2. **Critic-spawns-specialist** — a critic at level 2 spawning a verification specialist at level 3 (Brandling's pattern: Brand Critic → Verification Specialist; Engagement Critic → Engagement Analyst)
3. **Context-isolation requirement** — grandchild reads logs/files parent must never see

**Depth-3 does NOT pay off when:**

- The grandchild's job could be a single tool on the child
- Coordination overhead exceeds parallelism
- Token cost can't be justified by task value

**Hard caps:**

- 2–4 sub-agents per parent for in-process spawning
- \>10 needs git-worktree isolation
- \>100 needs cloud workers

**Output of stage:** depth + spawn rules + caps. If user asks for depth-3 without hitting one of the 3 cases, push back: *"That's a tool, not a sub-agent."*

### Stage 12 — Output the design doc

**Emit the doc.** Format below. Stop talking, hand it over.

---

## Pattern Catalog Summary (7 patterns)

Full deep-dive: `references/patterns-catalog.md`.

| # | Pattern | One-line use case |
|---|---------|-------------------|
| 1 | **Tool-Loop (ReAct)** | Path unknown upfront; tools enumerable; model decides next call from observations |
| 2 | **Orchestrator-Workers** | Subtasks not pre-definable; parallelizable; lead model decomposes at runtime |
| 3 | **Magentic Orchestrator** | Long-horizon open-ended tasks crossing browser + fs + code; plan→ledger→re-plan |
| 4 | **Plan-and-Execute** | Steps mostly knowable; cost of wrong calls non-trivial; auditable plan |
| 5 | **Evaluator-Optimizer (Critic Loop)** | Clear rubric; output demonstrably improvable with feedback |
| 6 | **Tool-Loop with Spawning** | Side-task floods main context; parallel I/O fan-out |
| 7 | **Handoff / Routing Network** | Distinct domains with sharp boundaries (refunds vs order-status vs FAQ) |

**Citations:** [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (1, 2, 5, 6); [Microsoft Magentic-One](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html) (3); [LangChain Planning Agents](https://www.langchain.com/blog/planning-agents) (4); [OpenAI Agents SDK Handoffs](https://openai.github.io/openai-agents-python/handoffs/) (7).

**Empirical anchors:**

- Anthropic's research system: **+90.2% over single-agent quality, ~15× tokens** ([source](https://www.anthropic.com/engineering/multi-agent-research-system))
- Cursor in production: Planner → Sub-Planners → Workers, hundreds of concurrent agents

---

## Council Shape Catalog Summary (7 shapes)

Full deep-dive: `references/council-shapes.md`.

| # | Shape | One-line use case |
|---|-------|-------------------|
| 1 | **Parallel Critique** (Karpathy `llm-council`) | Diverse first-drafts + peer review across models |
| 2 | **Iterative Refinement (Evaluator-Optimizer)** | Translation, code, copy with clear rubric |
| 3 | **Foreman-Worker (Orchestrator-Worker)** | Open-ended; subtasks emerge at runtime; **Brandling's choice** |
| 4 | **Judge + Jury** | Subjective rankings where ties happen |
| 5 | **Devil's Advocate** | Pre-mortem on high-stakes decisions |
| 6 | **Generator-Discriminator** | Many candidates + fast scorer (Engagement Critic + Apify pattern) |
| 7 | **Tournament / Bracket** | Pick 1 from N≥8 where absolute scoring is unreliable |

**Empirical sweet spot:** 3–4 agents, 2–4 rounds. Past that, accuracy degrades ([arXiv 2506.00066](https://arxiv.org/html/2506.00066v1)).

**Composition > mechanics:** diversity dominates structural tweaks; cross-family models is the strongest single lever ([arXiv 2511.07784](https://arxiv.org/abs/2511.07784)).

---

## Anti-Patterns (load-bearing — surface during Q&A, not after)

Call these out **before** the user picks the wrong path. Each one has a one-line test and a one-line fix.

| Anti-pattern | Test | Fix |
|--------------|------|-----|
| **Agent-washing a workflow** | 6-question rubric scores ≤2 yes | Either commit to real agency or call it a workflow |
| **Council-for-everything** | Closed-form answer, or single agent + retry hits 95% | Single agent + LLM-as-judge, or just retry |
| **Same-family judge** | Claude generates, Claude judges | Cross-family judge mandatory |
| **Depth-3 by default** | Grandchild has its own tool palette? Or just a prompt rewrite? | If just a prompt change, it's a tool, not a sub-agent |
| **Infinite refinement** | Loop runs past round 4 chasing diminishing returns | Hard-cap rounds; require monotonic improvement |
| **Foreman bias** | Workers all argue the foreman's hypothesis | Workers get raw input + mandated independent reasoning |
| **Tool descriptions as comments** | Vague `description` fields in tool schemas | Tool descriptions ARE the model's primary signal — write like product copy |
| **No max_turns** | One bad input drains the token budget | `max_turns` cap + explicit error path |

**Failure modes to mitigate** (full table in `references/failure-modes.md`):

- Echo chamber → cross-family models; weight minority dissent ([arXiv 2511.07784](https://arxiv.org/abs/2511.07784))
- Sycophancy → "stick to reasoning unless given new evidence" prior; reward dissent ([arXiv 2509.05396](https://arxiv.org/pdf/2509.05396))
- Position bias → randomize order; average two passes with positions swapped ([arXiv 2406.07791](https://arxiv.org/abs/2406.07791))
- Self-preference → cross-family judge ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819))
- Discriminator collapse → validate ≥90% accuracy on gold set before iteration ([arXiv 2402.10890](https://arxiv.org/abs/2402.10890))
- Context explosion → 3–4 agents, 2–4 rounds, secretary agent for summary

---

## LLM-as-Judge Rules (when council uses a judge)

Full deep-dive: `references/llm-as-judge.md`.

1. **Decompose the rubric** — analytic, criterion-by-criterion, not holistic. Halo effects collapse otherwise.
2. **Bounded discrete scales (1–5 or 1–7)** — not free continuous floats, not binary yes/no.
3. **Show reasoning before score** — CoT-before-score raises agreement with humans.
4. **Randomize candidate order; average across positions** — position bias is asymmetric and large.
5. **Anonymize model identities** — strip "I generated this" cues.
6. **Rotate the judge across models** — same family judging itself = self-preference.
7. **Validate against a golden set** — 75–90% agreement with human labels; below = noise.

---

## Output Format (the design doc the skill produces)

After Stage 12, emit a markdown doc with these sections:

```markdown
# Agentic System Design — [name]

## 1. Use-case statement
- One paragraph. Noun, verb, consequence.
- Blast radius: low / medium / high / regulated.

## 2. Operational mode
- Mode: A (sync request-response) / B (batch) / C (event-driven) / D (continuous).
- Trigger surface: HTTP endpoint / cron / queue subscriber / webhook listener / etc.
- Out-of-scope infrastructure layers (B/C/D only): queue / scheduler / sensor-listener / state-persistence / dedup / backpressure.

## 3. Boundaries (what the system must NOT touch)
- Bulleted: input fields off-limits, outputs off-limits, deterministic ops not to replace.

## 4. Agency score (Stage-4 rubric)
- Score: X/6
- Verdict: real agency / judgment call / workflow with frosting
- Rationale: 2 sentences

## 5. Pattern selected
- One of 7 SOTA patterns
- Rationale (3 sentences)
- Citation

## 6. Council shape (or "no council")
- 0 or 1 of 7 shapes
- 4-condition test result
- Rationale

## 7. Persona roster
- Table: role | responsibility | consumes | emits

## 8. Model routing
- Table: role | model | rationale
- Cross-family judge: yes/no (must be yes if council)

## 9. Tool-loop config
- max_turns: N
- parallel calls: yes/no
- compaction: strategy
- verification: type
- tracing: provider
- termination: criterion

## 10. Sub-agent spawning rules
- Depth: 1 / 2 / 3
- Spawn cap per parent: N
- 3-case justification (if depth-3)
- Isolation: in-process / worktree / cloud

## 11. Build order
- [ ] Single-agent skeleton with tool-loop config (Stage 10)
- [ ] Verification stage
- [ ] Persona prompts
- [ ] Council orchestrator
- [ ] Sub-agent spawning
- [ ] Eval harness against golden set

## 12. Acceptance criteria
- Bulleted, falsifiable.

## 13. Citations
- Inline markdown URLs from primary sources only.
```

The doc is **buildable**. An engineer with no prior context should be able to start coding from it on Monday.

---

## References + Examples Index

### `references/`

| File | Contains |
|------|----------|
| `references/patterns-catalog.md` | 7 SOTA patterns deep-dive: when to use, when not, pitfalls, citations |
| `references/council-shapes.md` | 7 council shapes deep-dive: sweet spots, failure modes, empirical anchors |
| `references/failure-modes.md` | Echo chamber, sycophancy, position bias, self-preference, discriminator collapse, context explosion |
| `references/llm-as-judge.md` | 7 rules + calibration recipe + golden-set protocol |
| `references/case-marketing.md` | Brandling Foreman → Marketing Head → Brand Critic → Engagement Critic case study |
| `references/case-finance.md` | CFO + Senior Accountant + Auditor + Compliance + Controller council |
| `references/case-hazop.md` | 6-seat HAZOP team council + Incident-DB Researcher sub-agent |
| `references/case-tutorial-gen.md` | Editor-in-Chief + Script Writer + Pedagogy + Voice + Brand + Accessibility council |

### `examples/`

| File | Contains |
|------|----------|
| `examples/tool-loop.md` | Canonical Tool-Loop excerpt (from Brandling Synthesizer) |
| `examples/foreman.md` | Canonical Foreman with 7-tool palette and mandatory-start/end constraints |
| `examples/sub-agent-runner.md` | Canonical `runSubAgent` with depth + timeout + spawn-cap |
| `examples/multi-model-router.md` | Canonical TokenRouter / OpenAI-compatible gateway pattern |

### Companion plugin: `agentic-toolkit`

The skill produces a design doc; `agentic-toolkit` ships the reusable infra to build it (multi-model gateway, `runSubAgent` runner, `AgentSseEvent` schema, provenance tags, council debate state machine). Point users at it instead of letting them re-implement.

### Companion skill: `self-improving-systems`

If the user wants memory, feedback loops, or closed-loop learning *after* shipping the agentic design, hand off to `self-improving-systems`. A is decomposition + orchestration; B is feedback signals + persistence + retrieval. Don't conflate.

---

## Primary Sources

Cite these (and only these) in design docs. Inline markdown URLs, primary sources only.

**Agentic patterns:** [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents), [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system), [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/handoffs/), [Microsoft Magentic-One](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html), [LangChain Planning Agents](https://www.langchain.com/blog/planning-agents), [agentic-patterns.com Sub-Agent Spawning](https://www.agentic-patterns.com/patterns/sub-agent-spawning/), [Prompting Guide Workflows-vs-Agents](https://www.promptingguide.ai/agents/ai-workflows-vs-ai-agents).

**Council / debate / LLM-as-judge:** [Du et al. multi-agent debate (arXiv 2305.14325)](https://arxiv.org/abs/2305.14325), [Karpathy llm-council](https://github.com/karpathy/llm-council), [Constitutional AI (arXiv 2212.08073)](https://arxiv.org/abs/2212.08073), [Talk Isn't Always Cheap (arXiv 2509.05396)](https://arxiv.org/pdf/2509.05396), [Can LLM Agents Really Debate? (arXiv 2511.07784)](https://arxiv.org/abs/2511.07784), [Debate or Vote (NeurIPS 2025)](https://openreview.net/forum?id=iUjGNJzrF1), [MAD Literature Review (arXiv 2506.00066)](https://arxiv.org/html/2506.00066v1), [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791), [Self-Preference Bias (arXiv 2410.21819)](https://arxiv.org/abs/2410.21819).

---

## Design Philosophy

> Most "agent" requests are workflows. Most "council" requests are wasteful. Most "depth-3 hierarchies" are depth-2 with a tool that needed renaming.

The value is not the seven patterns or seven shapes — those are catalogs anyone can find. The value is **filtering discipline**: catching agent-washing in Stage 4, council-for-everything in Stage 6, depth-3-by-default in Stage 11, *before* the user sinks two weeks into the wrong build. Opinionated. Cited. Buildable.
