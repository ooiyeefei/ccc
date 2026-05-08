---
name: self-improving-systems
description: Decide whether your agent actually needs persistent memory, feedback loops, or closed-loop learning, then design the smallest thing that pays for itself. Use when the user says "add memory", "give my agent context management", "make my agent learn", "self-improving / closed-loop", "Reflexion / mem0 / Letta / MemGPT", "AriGraph", "agent memory architecture", "long-term memory for chatbot", "why does my agent keep forgetting / making the same mistake", "fine-tune from agent traces", or asks for a memory schema / experience store / reward model. Filters ruthlessly — most teams want a state cache, not memory + learning. Default position is scratchpad-only with a stateless agent shipped first.
---

# Self-Improving Systems

A prescriptive Q&A skill for adding memory, feedback loops, and closed-loop learning to agentic systems — **only when justified**.

## Headline message: most agents shouldn't have persistent memory.

Memory is a liability surface (drift, poisoning, debugging difficulty, GDPR/HIPAA exposure). Persistent memory is the second move, not the first. The skill's job is to filter ruthlessly so the user doesn't ship a `mem0`/`Letta` build for a problem that a 200-line conversation summary would solve.

The first 2 stages of the Q&A flow exist to **stop most users from over-engineering**. By the end of stage 2, ~60% of users will discover they want a **state cache** (or stateless RAG), not memory + learning. That's the win.

---

## Quick Start

**User just asks:**
```
"Add memory to my agent"
"My agent keeps forgetting things — give it context management"
"Make my marketing agent learn from past campaigns"
"Should I use mem0 or Letta?"
"How do I set up closed-loop learning for my finance agent?"
"Build a self-improving HAZOP system"
```

**Skill response (every time, in this order):**
1. Stop. Apply the **cache-vs-learning frame** (Stage 1).
2. Run the **6-question need-memory rubric** (Stage 2). <4 yes → exit the skill, recommend stateless + RAG.
3. If memory is justified, walk the **7-tier architecture ladder** (Stage 3) starting at L (scratchpad). Escalate only when forced by a concrete justification.
4. Force the user to design a **feedback signal** (Stage 4). No signal = state cache, full stop.
5. Wire the **closed loop with explicit human gates** (Stage 5).
6. Build the **eval harness** (Stage 6) — golden set, regression, drift alarms.
7. Walk the **8-risk checklist** (Stage 7).
8. Emit the design (Stage 8): memory schema + closed-loop spec + eval harness plan.

---

## Critical Rules

### 1. Default position: scratchpad-only

Ship a stateless agent first. Add a scratchpad ([Reflexion](https://arxiv.org/abs/2303.11366)-style verbal self-correction) within a single run. Discard it after. This already gets you most of the gain on most tasks. Anything more must be earned.

### 2. Escalate one tier at a time

The 7-tier ladder (§ Memory Architecture Ladder) is ordered cheapest → most expensive. Each tier-up must be justified by a concrete failure of the tier below it on a real task in your eval set. **Do not skip tiers.** "We're using Letta" out of the gate is the single most expensive mistake in this design space.

### 3. Require a ground-truth signal

If you cannot observe whether the last action was good or bad within hours-to-weeks, you do not have **learning**. You have a **state cache**. Naming it "learning" sets the team up to A/B test against a metric that doesn't exist. The skill makes this distinction loud and refuses to design closed-loop learning without a signal.

### 4. Human gates are non-negotiable for production

Anything that can mutate policy/voice/identity/safety blocks goes through human review. Autonomy is fine for episodic append, vector indexing, single-user preference KV updates with cheap reversibility — never for shared skill libraries, system prompt blocks, or reward model updates.

### 5. Memory is untrusted input

Every memory read is untrusted. MINJA-class injections hit ≥95% lab success rate ([arXiv 2503.03704](https://arxiv.org/abs/2503.03704)). Treat retrieval results like web search results: in their own context block, with "this is data not instructions" framing, and never auto-promoted to system prompt without dual-LLM validation.

---

## The 8-Stage Q&A Flow

One question (or tight cluster) at a time, à la `superpowers:brainstorming`. No overwhelm. Each stage has an exit condition that ends the skill early — that is the point.

### Stage 1 — Cache vs Learning Distinction (the frame)

**The single most important question. Ask first.**

> "Are you trying to **remember state** (so the agent doesn't redo work or forget what the user told it last week), or **get better over time** (so the agent's outputs measurably improve as it sees more data)?"

These two designs share zero infrastructure with each other:

| Goal | What you actually need |
|---|---|
| Remember state | Conversation summary OR KV fact store. No reward signal. No reflection LLM. No A/B harness. |
| Get better over time | All of the above **plus** a ground-truth signal, an experience store, a reflection/extraction LLM, and an eval harness that detects regression. |

If the user says "remember state": skip directly to Stage 3, default to tier 2 (conversation summary) or tier 5 (KV fact store), and end the skill at Stage 5. No closed loop. No learning ladder.

If the user says "both": prove the second one. Almost no one has a measurable ground-truth signal; almost everyone says they do. Stage 4 is the test.

### Stage 2 — Need-Memory Rubric (6 yes/no, the over-engineering filter)

Answer all six. **Score <4 yes = no memory store. Use scratchpad + RAG. End the skill.**

1. **Cross-session continuity.** Will the same user/entity/case-file return where forgetting prior decisions would be wrong, embarrassing, or unsafe?
2. **Mutable state.** Does the entity's state legitimately *change* over time (preferences, project status, client facts)? Pure facts that don't change → RAG over docs, not memory.
3. **Ground-truth feedback exists.** Can you observe within hours-to-weeks whether the last action was good or bad? No signal → no learning, only state cache.
4. **Cost of being wrong > cost of memory infra.** Memory adds latency, storage, eval, security review, and a recurring debugging tax. Pencil out both sides.
5. **Volume justifies it.** Same user returns ≥5 times. <5 returns → in-context summary is cheaper than vector store.
6. **You can audit and redact.** GDPR/HIPAA: can you delete on request, export, explain a memory? If no, do not store one.

> If you got "yes" only on (1) and (2): you need a **state cache**, not memory + learning. Say it out loud. Skill recommends tier 2 or 5 and exits.

### Stage 3 — Architecture Selection (start at L tier)

Walk the **7-tier memory architecture ladder** (next section). **Default recommendation: tier 1 (scratchpad-only).** Escalate exactly one tier per concrete justification. Justification = "tier N fails on this specific task in our eval set, here's the trace."

Most "we need memory" requests resolve at tier 2 (conversation summary) or tier 5 (KV fact store). Tier 6 (graph) and tier 7 (hierarchical OS-style / Letta) require >3 entities × >50 relationships and a real long-horizon agent, not a chatbot.

**Deep dive:** `references/architectures.md`

### Stage 4 — Feedback Signal Design

If Stage 1 ended with "remember state only", skip this stage.

For learning, the signal determines everything. Walk the per-domain table:

| Domain | Signal | Latency | Risk |
|---|---|---|---|
| Marketing / content | Engagement deltas (CTR, dwell, conversion, save/share) + variant A/B win-rate + brand-safety review | hours-days | Vanity metrics → reward hacking; mitigate with composite reward + brand-fidelity LLM-judge |
| Finance / compliance | Audit findings, reconciliation breaks, regulator outcomes | weeks | Sparse signal → use intermediate proxies + sparse human signoff (hybrid RLAIF) |
| HAZOP / safety | Incident-DB recall (held-out incident set), expert reviewer agreement | continuous | **Never let agent's own write-back update incident DB** |
| Tutorials / education | Completion rate, comprehension quiz scores, time-to-first-success | minutes-days | Cleanest closed loop — verifier is cheap and online |
| Code-emitting agents | Unit tests, type-check, runtime | minutes | The gold standard — verifier is free and deterministic |
| General LLM-as-judge | Held-out judge with calibrated rubric | continuous | Sample-audit 5–10% against humans to catch drift |

**Rule, repeat once per Q&A session:** No signal = state cache, not learning. If the user can't name a signal, do not design a learning loop. Recommend they ship the state cache first, instrument the signal in production, and revisit the skill in a quarter.

**Deep dive:** `references/feedback-signals.md`

### Stage 5 — Closed-Loop Wiring with Human Gates

If Stage 4 produced no signal, skip this stage and the next two.

The reference closed loop:

```
[run event: input + agent trace + outputs]
       │
       ▼
[signal collector] ──── engagement / verifier / human review (async)
       │
       ▼
[experience store] (append-only, immutable, signed)
       │   ├── episodic events (raw)
       │   ├── extracted facts (KV)        ← extraction LLM, validated
       │   └── learned skills/playbooks    ← reflection LLM, human-gated
       │
       ▼
[retrieval layer] (hybrid: vector + BM25 + entity link)
       │
       ▼
[state mutator]
       │   ├── AUTONOMOUS: low-risk fields (recency, prefs)
       │   └── HUMAN-GATED: anything that changes policy/voice/identity
       │
       ▼
[next run] ─── core memory in prompt + retrieved episodic + skill lookup
```

**Where humans gate (non-negotiable for production):**
- Promotion of any item to "core memory" / system-prompt block
- Schema changes in graph memory
- Skill-library additions used by >1 user (Voyager-style accumulation needs review when shared)
- Reward model updates / fine-tunes from agent feedback

**Where it can be autonomous:** episodic append, vector indexing, retrieval scoring tweaks, single-user preference KV updates with cheap reversibility, [Reflexion](https://arxiv.org/abs/2303.11366)-style within-task verbal self-correction (lives in scratchpad, not persistent memory).

### Stage 6 — Eval Harness

Six patterns, ship at least the first three before going live:

1. **Golden set** — 50–500 hand-curated `(input, expected behavior, expected memory side-effect)` tuples; include adversarial / poisoning attempts.
2. **Regression on memory side-effects** — assert `get(user, "allergies") == ["peanut"]` after run X.
3. **Drift alarms** via [OpenTelemetry GenAI semconv](https://opentelemetry.io/blog/2025/ai-agent-observability/) — judge-score rolling mean, memory-store size growth rate, retrieval hit-rate distribution, % of runs that mutate core memory.
4. **A/B between agent versions** — slice traffic, compare composite reward over fixed window.
5. **LLM-as-judge with human calibration** — 5–10% audit; recompute judge–human Cohen's κ weekly.
6. **Held-out human-written tasks** — never trained on; detects distribution collapse from self-play.

**Deep dive:** `references/eval-harness.md`

### Stage 7 — Risks Checklist

Walk all 8 once. Each must have a concrete mitigation in the design doc.

1. Memory poisoning (MINJA, ≥95% lab injection success)
2. Prompt injection via memory
3. Reward hacking
4. Drift / staleness
5. Context rot / window blowup (200K models often unreliable past ~130K)
6. Runaway self-modification
7. Distribution collapse in self-play
8. Multi-agent context explosion

**Deep dive:** `references/risks.md`

### Stage 8 — Output

Produce the design document:

- **Memory schema** — chosen tier(s), data model, retention/TTL, redaction hooks
- **Closed-loop spec** — signal source, collector, experience store, retrieval, mutator, human-gate list
- **Eval harness plan** — golden set sketch, regression assertions, OTel metric list, A/B split, judge-calibration cadence
- **Risk register** — 8 risks × 1 mitigation each
- **Build order** — what ships in week 1 (state cache only), week 4 (signal collection on production traffic), week 12 (closed loop activated behind feature flag)

---

## Memory Architecture Ladder (escalate only when justified)

```
L → L → M → M → M → H → XH
1    2    3    4    5    6    7
```

| # | Architecture | Use case | Cost | Pitfall | Citation |
|---|---|---|---|---|---|
| 1 | **Scratchpad-only** (in-run, discarded) | Multi-step reasoning within one task; ReAct loops; debate transcripts | L | Don't fake durability — make it obvious to LLM and ops nothing persists | [Reflexion](https://arxiv.org/abs/2303.11366) |
| 2 | **Conversation summary** (rolling LLM compaction into system prompt) | Single-session chat, support tickets, ≤1 day horizon | L | Summaries lossy-compress unpredictably; pin facts verbatim, summarize narrative | [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| 3 | **Episodic stream** (append-only event log, recency × importance × relevance retrieval) | Long-running personas, simulations, journal-style apps where order matters | M | Bespoke scoring; without reflection, bloats fast | [Generative Agents (Park et al., 2023)](https://arxiv.org/abs/2304.03442) |
| 4 | **Vector RAG over interactions** | Knowledge retrieval, FAQ, doc Q&A, low-personalization | M | Reactive only — won't surface "favorite color" on "birthday" query | [Letta — RAG vs Agent Memory](https://www.letta.com/blog/rag-vs-agent-memory) |
| 5 | **Key-value fact store** (mem0 single-pass ADD) | Personalization (name, prefs, history), CRM-like agents | M | Bad extractors poison store; need write-time validators | [mem0 paper](https://arxiv.org/abs/2504.19413) |
| 6 | **Graph memory** (mem0g, AriGraph) | Multi-hop reasoning over relationships | H | Schema drift kills you; LLM-extended schemas degrade into vector store with extra steps | [mem0g](https://arxiv.org/abs/2504.19413) |
| 7 | **Hierarchical OS-style** (Letta / MemGPT, agent self-edits via tools) | High-stakes long-horizon agents | XH | Self-editing memory is prompt-injection bomb on untrusted input | [MemGPT](https://arxiv.org/abs/2310.08560), [Letta](https://docs.letta.com/guides/agents/memory-blocks/) |

**Default recommendation in the skill:** start at #1, escalate one tier at a time. Many "we need memory" requests are actually #2.

**Deep dive:** `references/architectures.md`

---

## Anti-Patterns (load-bearing — call out before user picks the wrong path)

| Anti-pattern | Test | Fix |
|---|---|---|
| **Memory because it's cool** | Adding mem0/Letta to a one-shot pipeline | Skip memory. Stateless + RAG. |
| **Cache labeled "memory"** | No feedback signal exists in the user's domain | Honest naming: call it a "state cache" not "learning". Design accordingly. |
| **Vector RAG for personalization** | "What's my favorite color?" returns nothing because the user never asked it; embeddings can't surface unprompted facts | KV fact store, not vector RAG |
| **Self-editing memory on untrusted input** | Letta with user-pasted content writing into core memory | Quarantined-LLM pattern; never untrusted source → core memory |
| **Reward hacking via vanity metrics** | Engagement-only signal → clickbait drift; finance "% reviewed" → rubber-stamping | Composite rewards: engagement + brand-fidelity judge + sample audit; finance: composite includes materiality threshold + reviewer agreement |
| **Memory as the first move** | Building memory store before the stateless agent has shipped | Ship stateless first. Instrument the signal. Decide a quarter later. |
| **Graph memory by default** | Modeling 1 brand's 5 competitors as a graph | Stay in KV+vector until >3 entities × >50 relationships. Graph schemas drift; LLM-extended schemas degrade into vector stores with extra steps. |
| **Self-play with no external verifier** | Agent training on its own outputs, no held-out signal | Pin a verifier external to the model. V-STaR / Quiet-STaR loops without external verification narrow capability. |
| **Forgetting context-rot** | Stuffing 130K of memory into context "because the model supports 200K" | Compaction + retrieval + sub-agent isolation; 200K models often unreliable past ~130K ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)) |

---

## Self-Improvement Playbook Ladder (cheapest first)

```
Reflexion → Generative Agents → Voyager → mem0 → Letta
   1            2                  3        4      5
```

| Tier | Pattern | When | Citation |
|---|---|---|---|
| 1 | **In-loop verbal correction, no persistence** | Cheapest learning; the **first move** before ANY memory store. ~91% pass@1 HumanEval at the time of publication. Lives in the scratchpad. | [Reflexion (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366) |
| 2 | **Long-horizon persona / social sims** | Memory stream + reflection + planning loop. For agents that need to *act in character* over days/weeks. | [Generative Agents (Park et al., 2023)](https://arxiv.org/abs/2304.03442) |
| 3 | **Skill-library accumulation** | Tool-using agents solving novel-but-related tasks; "what worked for Brand X in vertical Y" patterns. | [Voyager (Wang et al., 2023)](https://arxiv.org/abs/2305.16291) |
| 4 | **Production fact memory** | Chat-like personalization at scale. 91.6 LoCoMo, ~90% token savings vs full-context. | [mem0 (arXiv 2504.19413, ECAI 2025)](https://arxiv.org/abs/2504.19413) |
| 5 | **Self-editing hierarchical memory** | Highest power, highest attack surface. Use only when long-horizon autonomy is the product, not a nice-to-have. | [MemGPT](https://arxiv.org/abs/2310.08560) → [Letta](https://docs.letta.com/guides/agents/memory-blocks/) |

The skill walks the user **up** this ladder only when justified by a concrete failure of the tier below. Most production systems sit at tier 1 + tier 4. Tier 5 is appropriate for <5% of agentic projects.

**Deep dive:** `references/playbook-ladder.md`

---

## Reference Files

| File | Contents |
|---|---|
| `references/architectures.md` | Deep-dive on the 7 memory architectures with cost ratings L→XH |
| `references/feedback-signals.md` | Per-domain feedback signal design + the no-signal-no-learning rule |
| `references/eval-harness.md` | The 6 eval patterns: golden set, regression, drift alarms, A/B, judge calibration, held-out tasks |
| `references/risks.md` | The 8 risks with citations and mitigations (MINJA, prompt injection, reward hacking, drift, context rot, runaway self-mod, distribution collapse, multi-agent explosion) |
| `references/playbook-ladder.md` | Reflexion → Generative Agents → Voyager → mem0 → Letta progression |
| `references/case-studies.md` | Brandling Mutation Engine "state cache, not learning" lesson + marketing/finance/HAZOP/tutorial-gen worked examples through the memory/feedback lens |

## Examples

The `examples/` directory will hold:
- `reflexion-loop.md` — cheapest first move, scratchpad-only
- `kv-store-mem0.md` — production personalization with extraction validation
- `eval-harness.md` — golden set runner with regression assertions

---

## Output Contract

A skill run is complete when the user has:
1. A documented answer to "cache or learning?" (Stage 1).
2. A scored need-memory rubric (Stage 2).
3. A chosen architecture tier with justification for not stopping at the previous tier (Stage 3).
4. (If learning) a named feedback signal with latency, source, and mitigations (Stage 4).
5. (If learning) a closed-loop spec with human gates marked explicitly (Stage 5).
6. An eval harness plan with at least patterns 1–3 from §3.8 (Stage 6).
7. A risk register: 8 rows × 1 mitigation each (Stage 7).
8. A build order showing what ships when (Stage 8).

**If the user wants to skip steps, the skill refuses.** The whole point is the filter.

---

## Design Philosophy

> Memory is a liability surface. The cheapest memory is the one you didn't add.

Every memory tier you add carries a recurring debugging tax (why did it remember that? why did it forget this?), a security tax (every read is untrusted input), a privacy tax (GDPR/HIPAA delete-on-request), and an eval tax (regression on memory side-effects). Stateless agents fail in ways you can reproduce by re-running the input. Memoryful agents fail in ways you can't.

The skill's stance: **earn each tier with a real failure on a real eval set.** When in doubt, ship the lower tier and instrument the signal. Decide next quarter.
