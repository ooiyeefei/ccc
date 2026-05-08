# Self-Improvement Playbook Ladder

Five tiers for self-improvement, ordered cheapest-to-most-expensive. The skill walks the user **up** this ladder only when justified by a concrete failure of the tier below on a real task in their eval set.

```
Reflexion → Generative Agents → Voyager → mem0 → Letta
   1            2                  3        4      5
```

**Default for most production systems: tier 1 (Reflexion-style scratchpad correction) plus tier 4 (mem0 KV fact memory).** Tier 2 and tier 3 are domain-specific. Tier 5 is appropriate for <5% of agentic projects.

---

## Tier 1 — Reflexion (in-loop verbal correction, no persistence)

**When to use.** The first move before *any* memory store. Cheapest learning available. Lives entirely in the scratchpad — the agent reflects on its own trajectory within a single run, generates a verbal correction, retries with the correction in context. Nothing persists past the run.

**What it gets you.** Reported ~91% pass@1 on HumanEval at the time of publication. Most of the gain on most tasks. You can ship this without any memory infrastructure, eval harness changes, or ops overhead — it's a prompt-and-loop pattern.

**Implementation sketch.**
- Run the agent on the task.
- If the result fails verification (tests, judge, rubric), the agent generates a "what went wrong and what I'll try next" reflection.
- Re-run with the reflection in context.
- Cap iterations (3–5). Discard the reflection at end of run.

**Why tier 1.** No store, no schema, no eval-side changes, no privacy footprint, no MINJA surface. Adding this is reversible in one PR.

**Citation.** [Reflexion (Shinn et al., 2023, arXiv 2303.11366)](https://arxiv.org/abs/2303.11366).

---

## Tier 2 — Generative Agents (long-horizon persona / social sims)

**When to use.** The agent needs to *act in character* over days or weeks. Memory stream + reflection + planning loop. Use cases: NPC agents in games, social-sim research, longitudinal personas (a tutor that remembers a student's arc), journal-style apps where the agent has a stable identity that evolves with experience.

**What it gets you.** Coherent long-horizon behavior. The agent's actions reference its own past experiences in a way that feels continuous to the user. Reflection compaction keeps the memory stream manageable.

**Implementation sketch.**
- Tier 3 episodic stream (append-only event log, recency × importance × relevance retrieval).
- Periodic reflection: an LLM call summarizes streaks of episodes into higher-level reflections that re-enter the same store.
- Planning step: before action, the agent retrieves relevant past episodes + reflections, plans, then acts.

**Why tier 2.** Higher cost than tier 1 (you now have a persistent store and a reflection LLM in the loop), but the persona-stability you get isn't achievable any other way. **Skip this tier** if your agent's value isn't tied to persona continuity.

**Citation.** [Generative Agents (Park et al., 2023, arXiv 2304.03442)](https://arxiv.org/abs/2304.03442).

---

## Tier 3 — Voyager (skill-library accumulation)

**When to use.** Tool-using agents solving novel-but-related tasks where you want to **accumulate verified working solutions** as a reusable library. "What worked for Brand X in vertical Y" patterns. Code-emitting agents are the canonical case (verifier is free), but it generalizes to any domain with a cheap verifier — design templates, configuration recipes, marketing playbooks with engagement signal.

**What it gets you.** Compositionality. The agent solves novel tasks by retrieving and combining skills it (or other agents) have solved before. Reduces re-derivation cost over time.

**Implementation sketch.**
- After a successful run, extract a reusable skill (code, template, recipe) and store it in a skill library, keyed by `(skill_name, embedding, verification_record)`.
- On new tasks, retrieve top-k relevant skills; the agent decides which to invoke or compose.
- **Critical: verification before storage.** A skill enters the library only if it passed external verification (tests, judge, signal). Unverified attempts go into scratchpad/episodic, never into the library.

**Why tier 3.** Powerful when you have a verifier; sterile without one. The cheap-verifier requirement is what makes code-emitting agents the canonical fit. **Skip this tier** if your domain doesn't have a verifier — without it, the skill library accumulates noise.

**Citation.** [Voyager (Wang et al., 2023, arXiv 2305.16291)](https://arxiv.org/abs/2305.16291).

---

## Tier 4 — mem0 (production fact memory)

**When to use.** Chat-like personalization at scale. Tier 5 on the architecture ladder (KV fact store) operationalized. The default destination for most production assistants that cross 5+ sessions per user.

**What it gets you.** Reported **91.6 LoCoMo accuracy and ~90% token savings** vs full-context baselines ([arXiv 2504.19413](https://arxiv.org/abs/2504.19413)). Single-pass ADD pattern: extraction LLM pulls candidate facts from a turn, arbitration step merges with existing facts, store retrieves at next session.

**Implementation sketch.**
- Use [mem0](https://github.com/mem0ai/mem0) directly or implement the pattern: extraction → arbitration → store.
- Source-tag every fact. Validators on write. Contradiction detection.
- Hybrid retrieval (vector + BM25 + entity link).
- Pair with tier 1 (Reflexion) inside each session — they compose cleanly.

**Why tier 4.** This is where most production personalization belongs. Cheap enough to operate, accurate enough to be the default, well-understood failure modes. **Most "we need memory" requests resolve here, not at tier 5.**

**Citation.** [mem0 paper (arXiv 2504.19413, ECAI 2025)](https://arxiv.org/abs/2504.19413); [mem0 repo](https://github.com/mem0ai/mem0); [State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026).

---

## Tier 5 — Letta / MemGPT (self-editing hierarchical memory)

**When to use.** Highest power, highest attack surface. Use only when long-horizon autonomy is the product, not a nice-to-have. Multi-week digital workers, agents that need to evolve their own persona and skill set across many sessions, research assistants building up domain expertise.

**What it gets you.** True self-managed memory. The agent invokes tools (`memory_insert`, `memory_replace`, `archival_search`, `core_memory_replace`) to manage its own state. Treats memory as paged virtual memory: a small core block in-context, archival on disk, agent-controlled paging.

**Implementation sketch.**
- Use [Letta](https://github.com/letta-ai/letta) directly. Memory blocks pattern documented at [docs.letta.com](https://docs.letta.com/guides/agents/memory-blocks/).
- Identity / voice / safety blocks read-only to the agent. Only operators mutate.
- Audit log on every self-edit. Drift detection vs baseline. Periodic re-anchor.
- Dual-LLM quarantine for any untrusted input that could land in core memory.

**Why tier 5.** The marketing positions this as universal; the production reality is that self-editing memory is a prompt-injection bomb on untrusted input (MINJA, ≥95% lab success rate, [arXiv 2503.03704](https://arxiv.org/abs/2503.03704)). **Appropriate for <5% of agentic projects.** Most teams that ship this could have shipped tier 4 instead.

**Citation.** [MemGPT (Packer et al., 2023, arXiv 2310.08560)](https://arxiv.org/abs/2310.08560); [Letta — memory blocks](https://docs.letta.com/guides/agents/memory-blocks/); [Letta — RAG vs Agent Memory](https://www.letta.com/blog/rag-vs-agent-memory).

---

## How the skill walks this ladder

In Stage 3 of the Q&A flow, the skill recommends starting at the lowest tier that maps to the user's domain. For most users that's tier 1 (Reflexion) for in-loop correction *and* tier 4 (mem0) for cross-session facts — they compose, not compete.

To escalate from tier 4 to tier 5, the user must demonstrate:
1. A real long-horizon agent (weeks of operation per user, not a chatbot).
2. The agent's value comes from self-directed memory management (not personalization, which tier 4 covers).
3. Security/governance posture in place to handle agent-mutable system prompts.
4. Tier 4 has empirically failed on >3 specific tasks in the eval set.

Three of these are weak; all four together are rare. The skill leans toward "ship tier 4, instrument the failure modes, revisit next quarter."

To skip directly to tier 3 (Voyager) without tier 1 + tier 4 in place: only if the domain has a free deterministic verifier (code agents, math), in which case tier 3 is the *first* memory move and tiers 1/4 layer on later if needed.

The headline frame, repeated: most teams are not at tier 5. Most teams are not even at tier 4 yet. **Earn each tier with a real failure on a real eval set.**
