# Case Studies

Four worked examples through the memory-and-feedback lens. Each case starts by checking the over-engineering filter, then walks the architecture ladder, then designs (or refuses to design) a closed loop. The headline lesson — **state cache, not learning** — is the spine of the first case and a cross-cutting check on the others.

---

## 0. The Brandling Mutation Engine — "state cache, not learning"

This is the canonical lesson the skill exists to teach.

**What Brandling looked like.** A multi-stage agentic pipeline (Foreman → Marketing Head → Content Creator → Brand Critic → Engagement Critic → Review Council) that produces marketing clips. The "Mutation Engine" lives in `src/lib/agents/mutation-engine.ts:413` — it iterates over BrandDNA fields, mutating each with feedback from critics, and emits an evolved DNA + clip for the run.

**The instinctive (wrong) framing.** "We have a Mutation Engine. It evolves the DNA. That's learning." Multiple internal docs called it "self-improvement". The team had `mem0`/`Letta` on the roadmap because the framing implied memory + learning was the natural next step.

**The actual diagnosis.** Run the rubric:

1. Cross-session continuity — yes (same brand returns across many runs).
2. Mutable state — yes (BrandDNA evolves).
3. **Ground-truth feedback exists** — *no.* Critics inside the run are *judges*, not external signals. There's no engagement signal flowing back, no A/B win-rate, no held-out brand-fidelity human review. The Mutation Engine's "feedback" is the Engagement Critic's score, which is the agent grading its own work in a different costume.
4. Cost > infra cost — moot if (3) is no.
5. Volume justifies — yes.
6. Audit & redact — yes (BrandDNA is structured).

Score: 4/6 yes, but **(3) is the single load-bearing question** for whether memory becomes learning. (3) was no. The Mutation Engine was a **state cache** — it remembered what worked in *previous stages of the same run*, not what worked in *previous runs against engagement reality*.

**The right call.** Ship the Mutation Engine as a state cache (which it is). **Do not** wire `mem0` or `Letta`. **Do** instrument the missing signal: publish clips, measure 24h engagement, build a brand-fidelity LLM judge (cross-family, decomposed rubric, calibrated against human marketers), accumulate `(clip_id, BrandDNA_snapshot, engagement_24h, fidelity_score)` tuples in an experience store. **In a quarter**, when there's a real signal, revisit this skill and design the closed loop on top of the state cache. Not before.

**Anti-patterns this case names explicitly:**
- Cache labeled "memory" — happens when the team has read the literature but skipped Stage 1.
- Memory as the first move — adding `mem0`/`Letta` before the stateless agent has shipped against a real signal.
- Reward hacking via vanity metrics — engagement-only signal trains the agent toward clickbait.
- Self-play with no external verifier — agent grading agent is not a signal; it's distribution collapse waiting to happen.

The lesson is general. Any team that says "we have a feedback loop" should be tested with: name the external signal, name its latency, name the source. If those three blanks aren't fillable, it's a state cache.

---

## 1. Marketing / content (closed-loop possible, signal design is the lever)

A marketing agency agentic pipeline — multi-persona council producing campaigns or content clips, similar to Brandling but with the *missing piece* (the engagement signal) instrumented from day one.

**Memory verdict.** Hybrid: tier 5 KV (per-brand BrandDNA, per-audience preferences, per-vertical playbooks that worked) + tier 4 vector RAG over the corpus of published clips and their engagement records + tier 1 scratchpad inside each run. **No tier 6 graph** — the data looks graph-shaped (brand → audience → competitors → vertical → channel) but stays in KV+vector until you have >3 entities × >50 relationships in a real eval requirement; graph schema drift is too expensive to maintain for what's essentially a structured KV problem.

**Signal.** Composite reward: `engagement (CTR/dwell/save composite at 24h) × brand_fidelity_judge × safety_check`. Brand-fidelity judge is cross-family from the generator, decomposed rubric (tone, terminology, taboo-avoidance, audience-fit), calibrated against human marketers via 5–10% weekly audit, Cohen's κ tracked. Sample-audit detects judge drift. Held-out human-judged set every 6 months detects long-horizon distribution collapse.

**Closed loop.** After each clip is published, signal collector pulls 24h engagement → joins with brand-fidelity judge score on the same clip → emits composite reward → writes `(clip_id, BrandDNA_snapshot, persona_bindings, composite_reward, audit_flag)` into the experience store. Reflection LLM periodically synthesizes "what worked for Brand X in vertical Y" patterns; these become tier 3 (Voyager-style) skill-library entries gated by human review before promotion to shared library. Single-brand preference KV updates can be autonomous; **shared playbook library is human-gated** because one bad playbook poisons many brands.

**Risk register specifics.**
- Reward hacking: vanity metrics drive clickbait. Composite reward (geometric mean of engagement × fidelity) makes any single-axis collapse fail the whole sample.
- Memory poisoning: a malicious user's brand could try to plant a "successful pattern" that's actually a brand-attack. Source-tag every memory; quarantine before promotion to shared library.
- Drift: brand voice evolves; fidelity rubric needs review quarterly with the brand owner.

---

## 2. Finance / compliance (sparse signal, hybrid RLAIF)

CFO + Auditor + Compliance Officer council reviewing journal entries, classifications, materiality calls, and IFRS treatments.

**Memory verdict.** Tier 5 KV (per-vendor "is related party", per-account "materiality threshold by class", per-period "what was decided last quarter") + tier 1 scratchpad inside each review session. **No tier 6 graph** even though the chart-of-accounts is a graph — schema drift on chart-of-accounts is an existential threat in regulated jurisdictions; stay in KV. **No tier 7 Letta** — agent-mutable core memory in finance is a regulatory non-starter; controls must be human-mutable.

**Signal.** Sparse and slow on the ground truth; intermediate proxies for the dense signal. Hybrid RLAIF ([Constitutional AI](https://arxiv.org/abs/2212.08073)-style):
- (a) Dense proxy: lint-style rule violations on chart-of-accounts mapping, materiality thresholds, segregation-of-duties, related-party flags.
- (b) Medium-density signal: weekly controller signoff on a random 5% sample.
- (c) Ground truth: monthly audit reconciliation, quarterly audit findings, annual regulator outcomes.

The composite weighs (a) for fast iteration, (b) for catching drift in (a), (c) for ground-truth correction at quarterly cadence.

**Closed loop.** Per journal entry: agent emits classification + rationale + cited rules → lint-violation count attached → controller agreement (weekly) attached → audit finding (quarterly) attached. Experience store is append-only, signed (immutable for audit trail). Reflection layer synthesizes "vendor X has been classified Y N times by controller without override" → promotes to KV tier 5 as confirmed fact, **human-gated** if it would change a regulator-relevant treatment.

**Risk register specifics.**
- Reward hacking via "% reviewed cleanly" → rubber-stamping. Composite includes materiality threshold check + reviewer agreement; never let "% lint-clean" be the sole reward.
- Hallucinated GL entries — never invent account codes; cite chart-of-accounts. Memory is read-only against the chart for the agent.
- Letting LLM judge final IFRS treatment without human signoff in regulated jurisdictions — hard architectural constraint.
- Drift on jurisdiction tax codes — TTL on rules; periodic refresh from authoritative source; never trust agent's own write-back to the rules KV.

---

## 3. HAZOP / safety analysis (held-out incident DB, never write-back)

6-persona HAZOP team council (Facilitator, Process, Safety, Operator, Instrumentation, Maintenance) deliberating per-deviation cause/consequence/IPL findings.

**Memory verdict.** Tier 5 KV scoped per site (entity = node; facts = "this site has had X failures", "this equipment class has Y inspection history") + tier 4 vector RAG over the corpus of past HAZOP studies (search for "similar systems") + tier 1 scratchpad inside each per-deviation deliberation. **No tier 7 Letta** — same constraint as finance, controls must be human-mutable.

**Signal.** Held-out historical incident DB. Real incidents the agent never sees during operation. **Recall@k against the held-out set is the primary eval.** Plus expert reviewer agreement on `BORDERLINE` foreseeability and `HYPOTHESIS` novelty cases.

**Closed loop.** Eval-driven, not agent-driven. The eval harness runs recall@5 against the held-out incident DB on every model/prompt change. Agent improvements come from prompt/rubric updates that improve recall@5 *on the fixed held-out set*, never from the agent writing back into the incident DB. The "learning" lives in the eval set + the human-curated rubrics; the agent is a static reasoning engine over a structured KV that grows only via human curation.

**Risk register specifics.**
- **The hardest constraint in this list: the incident DB is read-only for the agent.** All learning happens through eval changes (golden set updates, rubric updates), never through agent write-back. Agent self-edit of the incident DB is an architectural disqualifier.
- Recall-only optimization → precision collapse. Bound recall optimization with a precision floor (e.g., disqualify any change that drops P below 0.6 even if recall improves).
- Generic guide-word output — persona-distinct prompts + operational context packs routed per persona. Memory layer surfaces site-specific facts to the right persona only.
- LOPA done by LLMs — pure-Python deterministic math; council stops at scenario assembly; LOPA computation is read-only from the agent's perspective.

---

## 4. Tutorial-gen / scripting (cleanest closed loop)

Editor-in-Chief council generating tutorial scripts segment-by-segment (Script Writer + Technical SME + Pedagogy Reviewer + Voice Director + Brand Voice Steward + Accessibility Reviewer).

**Memory verdict.** Tier 4 vector RAG over published tutorials ("similar tutorials taught X this way") + tier 5 KV per learner ("audience level, prior tutorials completed, comprehension trajectory") + tier 1 scratchpad inside each segment debate. **No tier 6/7** — overhead doesn't pay; tier 4 + tier 5 covers the use cases.

**Signal.** Per-segment quiz score + per-tutorial completion rate + per-tutorial time-to-first-success. Cheap, online, deterministic. **The cleanest closed-loop case in this list** — verifier is fast and unambiguous. Distinct from the marketing case because completion/comprehension are objective; clickbait can't game them long-term (a clickbait segment may get watched but won't improve quiz scores).

**Closed loop.** After each tutorial is published, signal collector aggregates per-segment quiz scores + completion rate over a fixed window → joins with voice-fidelity judge on the same segment → emits composite reward `quiz × completion × voice_fidelity_judge`. Experience store keyed by `(segment_id, tutorial_dna_snapshot, persona_bindings, composite_reward)`. Reflection LLM synthesizes "this audience level + this concept type teaches best with this approach" patterns; promoted to a teaching-pattern library (tier 3 Voyager-style) with human gate before shared promotion.

**Risk register specifics.**
- Distribution collapse from agent self-play — held-out tutorials with human-written scripts run on every release; canary for narrowing.
- Off-topic narration — vision pass extracts physical detail; narration is council debate output (per the [voice-neutrality rule](../../../memory/feedback_extraction_layer_neutral.md): extraction layers stay voice-neutral, brand voice belongs to the council debate layer).
- Voice Director reward hacking → monotone delivery — bounded discrete prosody scale, not continuous.
- Pedagogy reviewer reward hacking → info-dump segments — teach-one-thing-per-segment rule enforced at segment generation time, not after.

The tutorial case is the **counter-example to Brandling's lesson**: when the signal exists and is cheap and online, the closed loop is the easiest tier-4-or-5 build in the four cases. Most domains are not this lucky. Marketing has slow vanity-metric signals. Finance has sparse weeks-late signals. HAZOP has no agent-writable signal at all. Tutorial-gen has minutes-to-days of clean signal — and that's why it's the best place to demonstrate a closed loop end-to-end.

---

## Cross-cutting patterns

Across all four cases, the same five rules apply:

1. **Diagnose first, design second.** Run the 6-question rubric. Score (3) [signal exists] is load-bearing. If (3) is no, you have a state cache, not learning. The Brandling case shows how easy it is to skip (3) and ship a "learning" build that's actually a sophisticated cache.
2. **Tier 4 (mem0 KV) + tier 1 (Reflexion) is the default.** Three of the four cases land here for the persistent layer. Tier 5 (Letta) and tier 6 (graph) are not justified by any of the four.
3. **External verifier is non-negotiable.** Tutorial-gen has the easiest. Code-agents have the freest. Marketing earns it via engagement instrumentation. Finance and HAZOP need hybrid RLAIF or external eval-set gates because the dense signal isn't there.
4. **Some memory is read-only by architectural constraint.** Incident DB in HAZOP. Chart-of-accounts in finance. Identity / voice / safety blocks in any agent. The skill makes these constraints explicit upfront, not as afterthoughts.
5. **Most teams ship tier 4 + a state cache for a quarter, then revisit.** The "ship the lower tier and instrument the signal, decide next quarter" pattern is the right default for almost every team that walks into this skill.
