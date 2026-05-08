# Agentic Patterns Catalog

Deep-dive reference for the 7 SOTA agentic patterns. Pick one based on task shape, not aesthetics.

---

## Empirical anchors

Two numbers worth pinning to the wall before any design decision:

- **Anthropic's multi-agent research system** delivers **+90.2% quality over single-agent** baseline at **~15× the token cost** ([Anthropic — Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)). Multi-agent isn't free; budget for the multiplier or skip it.
- **Cursor** runs Planner → Sub-Planners → Workers in production with **hundreds of concurrent agents** at depth-3, but only because their domain (code edits) has cheap deterministic verification ([agentic-patterns.com — Sub-Agent Spawning](https://www.agentic-patterns.com/patterns/sub-agent-spawning/)).

If your task can't justify 15× tokens or doesn't have a verifier, you probably want a single agent with retry, not a council.

---

## 1. Tool-Loop (ReAct)

A single model alternates `reason → call tool → observe → reason` until it emits a final answer. The classic ReAct loop ([Yao et al., 2023](https://arxiv.org/abs/2210.03629)). All other patterns are extensions or compositions of this one.

**When to use.** The path to the solution is unknown upfront; the model can't enumerate which tools to call without seeing intermediate results. Examples: research synthesis, codebase exploration, debugging from a stack trace.

**When NOT to use.** Steps are predictable and enumerable (use a workflow). High-stakes actions with no rollback (use plan-and-execute with human approval). Autocomplete-class latency budgets (one model call max).

**Pitfalls.**
- No `max_turns` cap → one bad input drains your token budget.
- Vague tool descriptions → the model picks the wrong tool. Tool descriptions are the model's primary signal; write them like product copy ([Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).
- Silent retry on error masks the real failure. Pair `max_turns` with an explicit error path.

**Citation.** [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents); [Yao et al. — ReAct](https://arxiv.org/abs/2210.03629).

---

## 2. Orchestrator-Workers

A central LLM dynamically decomposes a task and delegates subtasks to worker agents that run in parallel. The orchestrator synthesizes results.

**When to use.** Subtasks aren't pre-definable at design time; they emerge from the input. Examples: "summarize these 50 docs by theme" (themes unknown), code refactor where the orchestrator reads the codebase before deciding what to change.

**When NOT to use.** Subtasks are knowable in advance — use a workflow with parallel branches instead. Tight token budget — orchestrator-workers is the **~15×** pattern.

**Pitfalls.**
- Insufficient worker specialization → workers do redundant work.
- Orchestrator decomposes poorly → workers receive vague subtasks and over-explore.
- Orchestrator inherits the full input *and* full worker outputs → context bloat. Pass summaries up, not full transcripts.

**Citation.** [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents); [Anthropic — Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system).

---

## 3. Magentic Orchestrator (Plan → Ledger → Re-plan)

Microsoft's pattern for long-horizon open-ended tasks. The orchestrator maintains an explicit ledger (facts, gaps, plan, progress), watches for stalls, and re-plans when progress halts. Workers cross tools (browser, filesystem, code).

**When to use.** Long-horizon tasks crossing multiple tool families: web research that involves browsing, downloading files, running code, and writing a report. State-of-the-art on GAIA benchmark.

**When NOT to use.** Short single-domain tasks — the ledger overhead exceeds the task. The pattern shines on horizon ≥ 10 steps with heterogeneous tools.

**Pitfalls.**
- Stall thresholds too lenient → silent infinite loop on a stuck subtask.
- Stall thresholds too aggressive → premature replans that throw away good progress.
- Ledger becomes context bloat unless compacted. Treat the ledger like a database, not a transcript.

**Citation.** [Microsoft Magentic-One](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html); [MS Learn — Magentic Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/magentic).

---

## 4. Plan-and-Execute

A planner LLM produces a full step list before any execution; an executor (often a different model or a code path) runs the steps. Re-planning happens at checkpoints, not every turn.

**When to use.** Steps are largely knowable upfront. Cost of wrong tool calls is non-trivial. You need an auditable plan a human can review before execution starts. Examples: financial reconciliation, surgical code refactors, regulated workflows.

**When NOT to use.** Real-time conversational adaptation needed (use ReAct). The plan must change every turn (use Magentic).

**Pitfalls.**
- No re-plan trigger → the executor blindly continues a wrong plan. Always define replanning conditions.
- Planner hallucinates steps that depend on data it hasn't seen — pair with a "check assumptions" step.
- Planner and executor disagree about tool semantics — pin tool definitions in both prompts.

**Citation.** [LangChain — Planning Agents](https://www.langchain.com/blog/planning-agents).

---

## 5. Evaluator-Optimizer (Critic Loop)

A generator produces a candidate, an evaluator scores it against a rubric, the generator revises. Loop until the rubric passes or rounds are exhausted. The classical critic-loop pattern.

**When to use.** Clear, decomposable evaluation criteria (rubric is writable). Output demonstrably improves with feedback. Examples: translation (BLEU + fluency), code (tests + lint), copy (rubric scoring).

**When NOT to use.** Quality is subjective with no measurable rubric — the critic will hallucinate criteria. One pass already meets bar — adding a critic just burns tokens.

**Pitfalls.**
- No convergence criterion → infinite oscillation between two attractor states.
- Evaluator shares generator's biases (same model family) → echo chamber. Use a cross-family judge ([self-preference bias arXiv 2410.21819](https://arxiv.org/abs/2410.21819)).
- Degeneration-of-thought past round 4 — quality stops improving and starts drifting ([arXiv 2506.00066](https://arxiv.org/html/2506.00066v1)). Hard-cap rounds.

See [llm-as-judge.md](llm-as-judge.md) for evaluator hardening.

**Citation.** [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents).

---

## 6. Tool-Loop with Spawning (Hierarchical Sub-Agents)

A parent agent delegates to ephemeral sub-agents that run their own tool loops, then return summaries. Sub-agents have isolated contexts. The pattern behind Anthropic's research system and Cursor's planner architecture.

**When to use.** A side-task would flood the parent's context (e.g., reading 200 search results to answer one sub-question). Parallel I/O fan-out where each branch is independent (Anthropic measured **up to 90% latency reduction** with parallel tool calls). Critic-spawns-specialist pattern: a level-2 critic spawning a level-3 verification specialist.

**When NOT to use.** A single tool call would do — spawning a sub-agent to do "lookup-and-format" is overkill. The grandchild's job could be a single tool on the child — then it's a tool, not a sub-agent.

**Pitfalls.**
- Sub-agent given a vague subject → it explores the wrong space. Pass *task* + *constraints* + *expected output shape*.
- Summaries lose information the parent later needs. Either return raw artifacts or run a second extraction pass.
- Depth-3 by default. Depth-2 is the default win; depth-3 only pays off in 3 named cases (sharded fan-out at scale, critic-spawns-specialist, context-isolation requirements). Hard-cap 2–4 spawns per parent for in-process.

**Citation.** [Anthropic — Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) (90.2% lift, 15× tokens, depth-2 default); [agentic-patterns.com](https://www.agentic-patterns.com/patterns/sub-agent-spawning/) (Cursor depth-3 hundreds of agents); [Anthropic — Custom Subagents docs](https://code.claude.com/docs/en/sub-agents).

---

## 7. Handoff / Routing Network

A classifier routes input to one of N specialist agents; each specialist owns a domain with its own tool palette. Specialists can hand off to peers but typically don't recurse.

**When to use.** Distinct domains with sharp boundaries. Customer support: refunds vs. order-status vs. FAQ vs. account changes. Each domain has different tools and policies.

**When NOT to use.** All "agents" share the same tool palette and only differ in prompt — that's prompt selection, not routing. Use a single agent with system prompt switching.

**Pitfalls.**
- Handoff loops (A→B→A→B). Detect cycles; cap handoffs per session.
- Over-eager classification — the router sends everything to the most general specialist. Pin the classifier with examples per route.
- Specialists that need each other's context lose it on handoff. Use a shared session state, not a fresh context per handoff.

**Citation.** [OpenAI Agents SDK — Handoffs](https://openai.github.io/openai-agents-python/handoffs/).

---

## Pattern selection cheat sheet

| Task shape | Pattern |
|---|---|
| Single trajectory, unknown tool order | Tool-Loop (ReAct) |
| Subtasks emerge from input, parallelizable | Orchestrator-Workers |
| Long-horizon, multi-tool, possible stalls | Magentic |
| Steps knowable upfront, audit needed | Plan-and-Execute |
| Quality has a rubric | Evaluator-Optimizer |
| Sub-task floods context or fans out | Tool-Loop with Spawning |
| Distinct domains with own tool palettes | Handoff/Routing |

If two patterns fit, the cheaper one wins. Compose only when single patterns demonstrably fail.

---

## Cross-references

- For the council shapes that wrap Patterns 2, 5, 6 → [council-shapes.md](council-shapes.md).
- For evaluator hardening (Pattern 5) → [llm-as-judge.md](llm-as-judge.md).
- For the failure modes that hit each pattern → [failure-modes.md](failure-modes.md).
