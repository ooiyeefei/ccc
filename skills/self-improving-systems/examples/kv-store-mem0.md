# KV Fact Store — Production Personalization with mem0

Once Reflexion isn't enough — once a user comes back next week and the agent should *remember* that they're allergic to peanuts, that they ship to São Paulo, that their favorite color is teal — you need a real persistent fact store. This is mem0's territory ([Chhikara et al., 2025, arXiv 2504.19413](https://arxiv.org/abs/2504.19413), ECAI 2025): on the LoCoMo personalization benchmark mem0 hit 91.6 with ~90% token savings vs full-context replay.

The architecture is deliberately boring: extract entity-fact pairs from each turn, validate them at write time, store them keyed by entity, retrieve them at read time. No graph, no agent self-editing memory, no fine-tune loop. **Boring is the feature** — every fancy bit you add is another surface for poisoning, drift, and silent breakage.

## Why KV beats vector RAG for personalization

The classic failure mode: user asks "what's my favorite color?" Vector RAG embeds the query, retrieves nearest neighbors from a chunked transcript, finds three messages about color preferences from different sessions, and the LLM synthesizes "you mentioned you like blue, green, and teal" — which is wrong, because the most recent answer (teal) was the user *correcting* the older ones.

Vector RAG is reactive and order-blind. KV is keyed and temporal. `get(user_id, "favorite_color")` returns one value, the current one, with a write timestamp. When the user says "actually, I prefer teal now," you do `set(user_id, "favorite_color", "teal", supersedes=prev_id)` and the old fact is archived, not blended.

This is the [State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) #1 production lesson: temporal queries break vector RAG, and personalization is mostly temporal queries.

## The single-pass ADD pipeline (mem0 pattern)

```
turn arrives
  -> extractor LLM(turn, recent_context) -> candidate facts: [(entity, key, value, evidence)]
  -> write-time validator(candidate, existing_store) -> accept | reject | supersede
  -> KV store(entity, key, value, ts, source_turn_id, evidence)

[next turn]
  retrieval(query, user_id) -> hybrid: vector(top-k) U BM25(top-k) U entity_link(exact)
  -> inject as a structured "what we know about this user" block in the system prompt
```

mem0's contribution is single-pass: extract + decide (ADD vs UPDATE vs DELETE vs NOOP) in one LLM call rather than the older two-pass extract-then-resolve. Lower latency, fewer drift opportunities.

## Reference excerpt

```typescript
// kv-store-mem0.ts -- extract -> validate -> write -> retrieve, ~30 lines
type Fact = { entity: string; key: string; value: string; evidence: string };
type Decision = { op: "ADD" | "UPDATE" | "NOOP" | "REJECT"; fact: Fact; reason: string };

async function ingestTurn(turn: string, userId: string, store: KVStore, llm: LLM) {
  // 1. Extract candidates in one pass (mem0's ADD pattern)
  const existing = await store.list(userId);
  const candidates: Fact[] = await llm.extract({
    system: "Extract durable facts about the user. Skip ephemeral state, opinions about third parties, and anything time-bounded under 1 day.",
    turn,
    existing, // for UPDATE/NOOP detection
    schema: { entity: "string", key: "string", value: "string", evidence: "string (verbatim quote)" },
  });

  // 2. Write-time validator -- never trust the extractor blind
  for (const fact of candidates) {
    const decision: Decision = await validate(fact, existing, turn);
    if (decision.op === "REJECT" || decision.op === "NOOP") continue;
    if (decision.op === "UPDATE") {
      const prev = existing.find(f => f.key === fact.key);
      await store.set(userId, fact.key, fact.value, { supersedes: prev?.id, ts: Date.now(), source: turn, evidence: fact.evidence });
    } else if (decision.op === "ADD") {
      await store.add(userId, fact, { ts: Date.now(), source: turn });
    }
  }
}

async function retrieve(query: string, userId: string, store: KVStore): Promise<Fact[]> {
  // Hybrid: entity_link exact match dominates, vector + BM25 as tiebreakers
  const exact = await store.entityLink(userId, query); // e.g., "favorite color" -> key match
  if (exact.length) return exact;
  const [vec, bm25] = await Promise.all([store.vectorSearch(userId, query, 5), store.bm25(userId, query, 5)]);
  return rerank([...vec, ...bm25]).slice(0, 3);
}
```

## The validator pattern — never trust the extractor

This is the bit teams skip and regret. The extractor LLM is *generous* — it will tell you the user's "favorite color is teal" because they said "teal looks nice on this widget." Without a validator, your store fills with hallucinated preferences within a week.

A validator does four things:

1. **Evidence check.** The candidate fact must include a verbatim quote from the source turn. If the quote doesn't actually appear in the turn, reject. (Catches LLM hallucination cheaply.)
2. **Contradiction check.** If the candidate contradicts an existing fact, decide UPDATE vs REJECT vs HUMAN_REVIEW. "I moved to Berlin" supersedes "lives in Lisbon"? Probably yes — but if the prior fact is two days old and the new one is at low confidence, hold.
3. **Schema/scope check.** Reject facts about third parties, ephemeral state ("user is currently in a meeting"), and anything outside your declared schema. The schema is the firewall against scope creep.
4. **Source provenance.** Every accepted fact carries `source_turn_id`, `evidence`, `ts`, and ideally `extractor_model_version`. When (not if) you find a poisoned fact, you can grep all writes from that turn and roll them back.

The validator is itself an LLM call in most setups, but a cheap one — a small model with a strict rubric runs in ~50ms and catches 80% of garbage. The remaining 20% is what the [evaluation harness](./eval-harness.md) and the 5-10% human audit is for.

A blunt rule from the [MINJA memory-poisoning paper](https://arxiv.org/abs/2503.03704): if your write path doesn't have a validator that *can refuse the extractor*, you're one prompt-injection away from corrupted production memory. The poisoning success rate in the lab was >=95%.

## When KV is enough — and when to escalate

Stay in KV when:

- Facts are **flat key-value** (preferences, settings, single-hop relations like "user works at company X").
- Queries are **direct lookups** ("what's my X?", "where do I live?").
- Entities count in the dozens per user, not thousands.

Escalate to **graph memory** ([mem0g](https://arxiv.org/abs/2504.19413), [AriGraph](https://arxiv.org/abs/2407.04363)) only when:

- You need **multi-hop reasoning**: "Who at company X did I meet last quarter who later moved to company Y?"
- The relationship graph exceeds **roughly >3 entity types x >50 active relationships per user** — below that, graph overhead loses to a flat KV with a couple of join keys.
- Schema-extension churn is low — graph memory rots fast when an LLM is allowed to invent new edge types ad-hoc; you end up with a glorified vector store and worse latency.

Escalate to **Letta-style hierarchical self-editing memory** ([MemGPT, arXiv 2310.08560](https://arxiv.org/abs/2310.08560)) only when you genuinely need agent-driven memory management *and* you've solved the trust problem (no untrusted input ever reaches core memory; quarantined-LLM pattern; full audit trail). For most personalization work, KV + write-time validator + human-gated promotion to "core memory" blocks is dramatically safer and gets you 90% of the wins.

The rule of thumb the skill enforces: **stay in KV until you can name the multi-hop query you can't answer.** "We might want graph queries someday" is not a reason. "Show me everyone in user X's network who works in fintech and also subscribed to product Y" is a reason.

Pair this with a real evaluation harness from day one — see [`eval-harness.md`](./eval-harness.md) for the golden-set + drift-alarm pattern that catches a poisoned KV before your users do.
