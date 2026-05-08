# Memory Architectures

Deep-dive reference for the 7 memory architectures. The ladder runs L → L → M → M → M → H → XH. **Default starting position is tier 1 (scratchpad-only).** Escalate exactly one tier per concrete justification — a real failure on a real eval set. Skipping tiers is the most expensive mistake in this design space.

---

## Empirical anchors

Three numbers worth pinning to the wall before picking a tier:

- **Most agentic projects sit at tier 1 + tier 4 (vector RAG) or tier 5 (KV).** Graph and hierarchical OS-style are appropriate for <5% of projects. If you find yourself at tier 6 or 7 in week 1, you skipped the filter.
- **mem0 reported 91.6 LoCoMo accuracy and ~90% token savings vs full-context** ([arXiv 2504.19413](https://arxiv.org/abs/2504.19413)) — most "we need persistent memory" requests resolve here, not at Letta.
- **200K-context models often degrade well before ~130K** ([Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). "Just stuff it all in context" is not an architecture; it's a delayed bug.

---

## 1. Scratchpad-only (cost: L)

The agent writes intermediate reasoning, tool-call rationales, and self-corrections to an in-run buffer. The buffer is discarded at the end of the run. Nothing persists across sessions.

**Use case.** Multi-step reasoning within one task. ReAct loops, debate transcripts, [Reflexion](https://arxiv.org/abs/2303.11366)-style verbal self-correction within a single trajectory. This is the **default move** before any persistent memory is even considered.

**When to escalate.** Same user/entity returns, and forgetting their last interaction is wrong, embarrassing, or unsafe. If the user does not return — or returns <5 times — stay here. Your task is one-shot.

**When NOT to escalate.** "We might want it later." That is not justification. Add memory when a real session fails, not when you imagine one might.

**Pitfall.** Don't fake durability. Be explicit in the system prompt and ops dashboards that nothing persists. Otherwise downstream code starts to *assume* retention and you end up with a half-built tier 2 that nobody owns.

**Citation.** [Reflexion (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366); [Anthropic — Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

---

## 2. Conversation summary (cost: L)

A rolling LLM-driven compaction step. As the conversation grows, the system periodically summarizes older turns and prepends the summary to the system prompt. The Claude Agent SDK's auto-compaction is the canonical example.

**Use case.** Single-session chat, support tickets, ≤1 day horizon, anything where the same user returns inside one logical session and you want to avoid blowing the context window.

**When to escalate.** The summary keeps losing facts the agent later needs ("you told me your address last week, why did you ask again?"). That's tier 5 (KV fact store) territory.

**When NOT to escalate.** Summary feels "lossy but acceptable" — that's the design working as intended. Stay here.

**Pitfall.** Summaries lossy-compress unpredictably. Hard rule: **pin facts verbatim, summarize narrative.** Maintain a separate "facts about this user" KV section in the system prompt that the summarizer never touches; let the narrative summary cover the conversation arc only.

**Citation.** [Anthropic — Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); [Claude Agent SDK auto-compaction docs](https://claude.com/blog/building-agents-with-the-claude-agent-sdk).

---

## 3. Episodic stream (cost: M)

Append-only event log. Each interaction is stored as a timestamped event. Retrieval scores events by **recency × importance × relevance**, classic [Generative Agents](https://arxiv.org/abs/2304.03442) recipe. A reflection LLM periodically summarizes streaks of episodes into higher-level "reflections" that re-enter the same store.

**Use case.** Long-running personas, simulations, journal-style apps where **order matters** and the agent needs to reason about "what happened on Tuesday vs Wednesday." NPCs in games, social-sim research, longitudinal habit-tracking agents.

**When to escalate.** You need multi-hop relational queries ("who is friends with whom") that recency × relevance can't answer. That's tier 6 (graph) territory.

**When NOT to escalate.** You're tempted to "just add a graph" because it sounds powerful. Most journal-style apps don't need a graph. Stay here.

**Pitfall.** Bespoke scoring is hard to tune. Without periodic reflection compaction, the store bloats fast and retrieval quality collapses. Budget for the reflection LLM call; it's not optional.

**Citation.** [Generative Agents (Park et al., 2023)](https://arxiv.org/abs/2304.03442).

---

## 4. Vector RAG over interactions (cost: M)

Every turn (or chunk of a turn) is embedded and stored in a vector index. Retrieval happens at query time via similarity search, often hybrid with BM25.

**Use case.** Knowledge retrieval, FAQ surfaces, doc Q&A, low-personalization assistants. Anything where the agent's job is to **find the most semantically similar past content** and cite it.

**When to escalate.** Personalization queries fail. Vector RAG can't surface "favorite color" when the query is "what should I get them for their birthday" — embeddings are reactive, not proactive. Tier 5 (KV fact store) fixes this.

**When NOT to escalate.** Pure doc-retrieval works. Stay here. Don't bolt on a KV store you don't need.

**Pitfall.** Reactive-only retrieval. The agent surfaces what looks like the question, not what's *relevant to the answer*. Pair vector RAG with a small KV fact store for "things the agent should always know about this user" if you cross over into personalization.

**Citation.** [Letta — RAG vs Agent Memory](https://www.letta.com/blog/rag-vs-agent-memory).

---

## 5. Key-value fact store (cost: M)

A structured store of `(entity, attribute, value, timestamp, source)` tuples. Writes go through an extraction LLM that pulls candidate facts from the conversation and an arbitration step that merges with existing facts (mem0's single-pass ADD pattern).

**Use case.** Personalization at scale. Name, preferences, history, project status, CRM-like agents. The "core memory" of any chat product that crosses 5+ sessions per user.

**When to escalate.** Multi-hop relational queries — "who is X's manager and what project are they on" — fail because relations aren't first-class. Tier 6 (graph) territory, but only if you have **>3 entities × >50 relationships** as a real eval requirement.

**When NOT to escalate.** Most chat products live here forever. mem0's reported 91.6 LoCoMo accuracy and 90% token savings ([arXiv 2504.19413](https://arxiv.org/abs/2504.19413)) make tier 5 the default destination for production personalization.

**Pitfall.** Bad extractors poison the store. A single hallucinated `(user, allergies, [shellfish, penicillin])` causes hard-to-debug downstream failures. **Write-time validators are mandatory** — schema check, source attribution, dual-LLM disagreement triggers human review.

**Citation.** [mem0 paper (arXiv 2504.19413, ECAI 2025)](https://arxiv.org/abs/2504.19413); [mem0 repo](https://github.com/mem0ai/mem0); [State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026).

---

## 6. Graph memory (cost: H)

Entities and relationships as a typed graph. Either fixed schema (rare in practice, expensive to maintain) or LLM-extended (schemas extend at write-time as new relationships emerge). [mem0g](https://arxiv.org/abs/2504.19413) and [AriGraph](https://arxiv.org/abs/2407.04363) are the reference implementations.

**Use case.** Multi-hop reasoning over relationships. Real graph queries, not graph-shaped data you could have stored in tier 5 with a join. Examples: corporate-knowledge agent that needs to traverse "team → projects → upstream dependencies → vendor incidents", investigative agents tracing entity relationships, agents whose primary value is *the graph traversal*, not the facts at the nodes.

**When to escalate.** Graph queries are the product, you have schema governance, and tier 5 has empirically failed on >3 multi-hop tasks in your eval set.

**When NOT to escalate.** "It sounds powerful" or "the LLM extends the schema for us." Schema drift is an existential threat to graph memory. LLM-extended schemas degrade into vector stores with extra steps unless you have a human reviewer signing off on schema mutations weekly.

**Pitfall.** Schema drift. Without governance, the LLM mints a new edge type every other week and your queries silently lose recall. Treat schema changes the same as code migrations — reviewed, versioned, reversible.

**Citation.** [mem0g (in arXiv 2504.19413)](https://arxiv.org/abs/2504.19413); [AriGraph (Anokhin et al., 2024)](https://arxiv.org/abs/2407.04363).

---

## 7. Hierarchical OS-style (cost: XH)

The agent treats memory as paged virtual memory: a small "core memory" block in-context, an "archival memory" tier on disk, and tools (`memory_insert`, `memory_replace`, `archival_search`, `core_memory_replace`) that the agent invokes to manage its own state. [MemGPT](https://arxiv.org/abs/2310.08560) introduced the pattern; [Letta](https://docs.letta.com/guides/agents/memory-blocks/) is the production heir.

**Use case.** High-stakes long-horizon agents where autonomy is the product. Multi-week digital workers, agents that need to evolve their own persona over time, research assistants that build up domain expertise across many sessions. **Not for chatbots.**

**When to escalate.** You have a real long-horizon agent (weeks of operation per user), the agent's value comes from *self-directed memory management*, you have the security/governance posture to handle agent-mutable system prompts, and tier 5 has demonstrably failed.

**When NOT to escalate.** Anything else. This tier is appropriate for <5% of agentic projects. The marketing copy makes it sound universal; the production reality is that self-editing memory is a prompt-injection bomb on untrusted input.

**Pitfall.** Self-editing memory is the largest attack surface in this list. MINJA-class injections ([arXiv 2503.03704](https://arxiv.org/abs/2503.03704)) hit ≥95% lab success on systems exactly like this. **Never let untrusted source content land in core memory without dual-LLM quarantine.** Treat the agent's own write tools the same way you'd treat shell access — least-privilege, audit log, human-reviewed for schema-level changes.

**Citation.** [MemGPT (Packer et al., 2023, arXiv 2310.08560)](https://arxiv.org/abs/2310.08560); [Letta — memory blocks](https://docs.letta.com/guides/agents/memory-blocks/); [Letta — RAG vs Agent Memory](https://www.letta.com/blog/rag-vs-agent-memory).

---

## Tier-skipping cost table

| From | Skip to | Likely outcome |
|---|---|---|
| 1 → 5 | mem0 directly | You'll discover at month 2 that summary would have been enough; rip out KV and refactor. |
| 1 → 7 | Letta directly | Two weeks of plumbing, then you find out you don't have a feedback signal. State cache misnamed as learning. |
| 4 → 7 | RAG directly to Letta | You skipped KV; personalization queries fail; the agent self-edits its way around the gap and now its core memory is unaudited. |
| 5 → 7 | KV directly to Letta | You introduced agent-mutable core memory before instrumenting the audit log. First MINJA report from a researcher in week 6. |

The pattern: skipping tiers means you discover the missing infrastructure under load, in production. Walk the ladder.

---

## Cross-cutting concerns (apply to every tier ≥ 3)

- **Source-tag every memory.** `(content, source, timestamp, signature)`. Web content, user-pasted content, agent-generated content — different sources get different downstream privileges. Untrusted source must never auto-promote to core memory.
- **TTL on volatile facts.** "Currently working at X" expires. "Born in Y" doesn't. Apply TTLs at write-time; let retrieval filter expired facts.
- **Contradiction detection on writes.** Before adding `(user, allergies, [peanut])` when `(user, allergies, [shellfish])` exists, flag for arbitration. Don't silently overwrite.
- **Audit + redact.** GDPR/HIPAA: every memory must be deletable, exportable, and explainable. If you can't answer "why does the agent know this", you can't ship it.
- **Retrieval is hybrid.** Vector + BM25 + entity link. Pure vector misses keyword matches; pure BM25 misses paraphrase. Hybrid with reranking is the production default.
