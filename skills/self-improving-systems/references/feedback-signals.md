# Feedback Signal Design

The signal determines whether memory becomes **learning** or stays a **state cache**. There is no third option.

## The rule (loud, repeat once per session)

> **No signal = state cache, not learning.**

If the user cannot name a ground-truth signal that arrives within hours-to-weeks of an agent action, do not design a closed loop. Recommend they ship the state cache first, instrument the signal in production, and revisit this skill in a quarter.

The signal does not have to be perfect. It has to be **measurable, attributable to specific runs, and external to the model itself.** Self-judging is not a signal — it's the source of distribution collapse ([V-STaR](https://arxiv.org/abs/2402.06457), [Quiet-STaR](https://arxiv.org/abs/2403.09629)).

---

## Per-domain signal table

| Domain | Signal | Latency | Risk | Mitigation |
|---|---|---|---|---|
| Marketing / content (Brandling-class) | Engagement deltas (CTR, dwell, conversion, save/share) + variant A/B win-rate + brand-safety review | hours-days | Vanity metrics → reward hacking; clickbait drift | Composite reward = engagement × brand-fidelity LLM-judge × sample human audit. Never reward on engagement alone. |
| Finance / compliance | Audit findings, reconciliation breaks, regulator outcomes | weeks | Sparse signal → late discovery; rubber-stamping if proxied | Hybrid RLAIF: intermediate proxies (lint-style rule violations on chart-of-accounts, materiality thresholds, segregation-of-duties violations) + sparse human signoff |
| HAZOP / safety | Incident-DB recall (held-out incident set), expert reviewer agreement | continuous | Agent learns to game the recall metric; incident DB pollution | Build regression set of historical incidents; recall@k as eval. **Never let agent's own write-back update incident DB.** |
| Tutorials / education | Completion rate, comprehension quiz scores, time-to-first-success | minutes-days | Cleanest closed loop in this list — verifier is cheap and online | Standard A/B with held-out segments; no special mitigation needed |
| Code-emitting agents | Unit tests, type-check, runtime, linter, benchmark deltas | minutes | The gold standard — verifier is free and deterministic | Pin the verifier suite; require monotonic improvement on regression set before promoting any change |
| General LLM-as-judge | Held-out judge with calibrated rubric | continuous | Judge drifts; self-preference if judge shares family with generator | Cross-family judge; sample-audit 5–10% against humans; recompute Cohen's κ weekly; stop trusting below threshold |

---

## 1. Marketing / content

**Signal source.** Production engagement metrics from the publishing platform (CTR, dwell time, save/share, conversion if downstream funnel is instrumented), plus variant A/B win-rate from controlled experiments.

**Latency.** Hours to days. CTR is fast; conversion is slow. Build the loop around the fastest reliable signal — typically dwell × save composite at the 24h mark.

**Risk.** Vanity metrics are reward-hackable. Engagement-only signal trains the agent toward clickbait, drama, low-trust hooks. Brand voice degrades silently because nothing in the loop measures it.

**Mitigation (composite reward).** `reward = w1 · engagement + w2 · brand_fidelity_judge_score - w3 · safety_violation_count`. Brand-fidelity judge is a cross-family LLM with a calibrated rubric (decomposed: tone, terminology, taboo-phrase avoidance, audience-fit). Sample-audit 5–10% of agent outputs with a human against the same rubric weekly to detect judge drift. Never let the agent see the engagement-only score as its sole training signal.

**Worked example: Brandling-class system.** Currently a state cache (Mutation Engine doesn't learn — it generates per-run). To become learning: instrument engagement signal on published clips, attach BrandDNA-fidelity LLM judge as second axis, store `(clip_id, BrandDNA_snapshot, engagement_24h, fidelity_score, audit_flag)` tuples in experience store. Use the composite to bias mutation-engine field selection in subsequent runs. Human gate: any change to BrandDNA core fields (taboo, audience, tone).

---

## 2. Finance / compliance

**Signal source.** Audit findings (post-close audit reports), reconciliation breaks (when bank/GL don't match), regulator outcomes (LHDN/IRAS/IRS notices, IFRS opinions).

**Latency.** Weeks to quarters. The signal is too sparse and too slow to drive a tight closed loop. This is a hybrid RLAIF case ([Constitutional AI](https://arxiv.org/abs/2212.08073)-style): use intermediate proxies for the dense signal, sparse human signoff for the ground truth.

**Risk.** Two failure modes. Sparse-signal-only: nothing arrives for 6 weeks, the agent drifts undetected, audit catches it at quarter-end and you've polluted 6 weeks of memory. Proxy-only: the agent learns to optimize the proxy (e.g., "% of journal entries with no flagged lint violations") and silently rubber-stamps real errors.

**Mitigation.** Composite signal. (a) Dense proxy: lint-style rule violations on chart-of-accounts mapping, materiality thresholds, segregation-of-duties, related-party flags. (b) Sparse signal: weekly human controller signoff on a random 5% sample, monthly audit reconciliation. (c) Hard constraint: never let LLM judgment finalize IFRS treatment without human signoff in regulated jurisdictions.

**Worked example.** CFO + Auditor council emits journal entries. Signal: lint-violation count per entry (dense, immediate) + weekly controller agreement (sparse, supervised) + quarterly audit findings (sparse, ground truth). The agent's reward composite weighs lint-clean × controller-agreement × no-audit-findings. Memory verdict: tier 5 KV (entity = vendor or account; facts = "is related party", "materiality threshold by class"), tier 1 scratchpad inside each review session. **No tier 6 graph** even though the data is graph-shaped — schema drift on chart-of-accounts is too dangerous; stay in KV.

---

## 3. HAZOP / safety

**Signal source.** Held-out incident database (real historical incidents the agent never sees during operation). Expert reviewer agreement on per-deviation findings. Recall@k against the held-out set is the primary eval.

**Latency.** Continuous on the held-out set. The eval runs on every model/prompt change.

**Risk.** Two failure modes. (a) Agent learns to game the recall metric — surfaces every plausible incident type for every node, recall goes up, precision collapses, real reviewers stop trusting it. (b) Agent's own outputs leak into the incident DB via downstream writes — the held-out set is no longer held-out, the eval is silently corrupted.

**Mitigation.** **Never let the agent's own write-back update the incident DB.** Make this a hard architectural constraint, not a guideline. Recall@k as the eval, but bound by precision floor (recall optimization disqualified below P=0.6). Expert reviewers sign off on borderline cases (`BORDERLINE` foreseeability, `HYPOTHESIS` novelty tier).

**Worked example.** 6-persona HAZOP team council emits per-deviation cause/consequence/IPL findings. Signal: recall@5 on held-out historical incident DB + reviewer agreement on `BORDERLINE` and `HYPOTHESIS` cases. Memory verdict: tier 5 KV scoped per site (entity = node; facts = "this site has had X failures", "this equipment class has Y inspection history"). **Critical constraint: incident DB is read-only for the agent.** All learning happens through eval changes (golden set updates, rubric updates), never through agent write-back.

---

## 4. Tutorials / education

**Signal source.** Completion rate, comprehension quiz scores, time-to-first-success. All cheap, all online, all deterministic.

**Latency.** Minutes to days. Quiz scores are immediate; completion rate is hours; time-to-first-success is days. The loop is fast.

**Risk.** Minimal. This is the **cleanest closed-loop case** in the table — verifier is cheap, online, and deterministic. Standard A/B harness with held-out segments handles it.

**Mitigation.** Standard. Held-out user segments to detect distribution collapse from agent self-play. Brand-voice judge as second axis to keep the agent from optimizing comprehension by dropping the show's persona ("just say the answer").

**Worked example.** Editor-in-Chief council generates tutorial scripts. Signal: per-segment quiz score + per-tutorial completion rate + per-tutorial time-to-first-success. Composite reward = quiz × completion × voice-fidelity-judge. Memory verdict: tier 4 vector RAG over published tutorials ("similar tutorials taught X this way"), tier 5 KV per learner ("audience level, prior tutorials completed"), tier 1 scratchpad inside each segment debate.

---

## 5. Code-emitting agents

**Signal source.** Unit tests, type-checker, runtime, linter, benchmark deltas. The verifier is free, deterministic, and runs in seconds.

**Latency.** Minutes. Sometimes seconds (for syntax/type checks).

**Risk.** Distribution collapse if the agent trains on its own outputs without an external verifier. V-STaR / Quiet-STaR loops without external verification narrow capability.

**Mitigation.** Pin the verifier suite. Include hard external benchmarks (HumanEval, SWE-bench, custom regression set). Require monotonic improvement on the regression set before promoting any change to memory or to the agent's skill library.

**Worked example.** Voyager-style skill library accumulating "verified working solutions to subtask X". Signal: tests pass + lints clean + runtime within budget. Memory verdict: tier 1 scratchpad inside each task, tier 5 KV (skill name → verified code + test record), tier 4 vector RAG over the skill library for retrieval at query time. Human gate: skill-library additions used by >1 user pass through review.

---

## 6. General LLM-as-judge

**Signal source.** A held-out judge LLM with a calibrated rubric. Decomposed (criterion-by-criterion, not holistic), bounded discrete scale (1–5 or 1–7), CoT-before-score, randomized candidate order, anonymized identities, cross-family from the generator.

**Latency.** Continuous.

**Risk.** Three failure modes. (a) Self-preference if judge shares family with generator (~10% lift toward own outputs, [arXiv 2410.21819](https://arxiv.org/abs/2410.21819)). (b) Judge drift over time as the underlying model is updated. (c) Halo effects when the rubric is holistic instead of decomposed.

**Mitigation.** Cross-family judge mandatory. Sample-audit 5–10% of judge outputs against human labels weekly. Compute judge–human Cohen's κ, alarm below threshold (< 0.6 = stop trusting), retrain rubric or swap judge model. Validate against a 50-sample golden set before any prompt or rubric change ships.

**Worked example.** Marketing brand-fidelity judge. Generator: Claude. Judge: GPT-class or Gemini-class, never Claude. Rubric: tone (1–5), terminology (1–5), taboo-avoidance (1–5), audience-fit (1–5) — composite is geometric mean, not sum (so any single-axis collapse fails the whole sample). Weekly audit: 5% sample reviewed by a human marketer against the same rubric; Cohen's κ tracked; threshold-alarm hooked to the team chat.

---

## How to detect "no signal" early

If the user's domain doesn't appear in the table above, ask:

1. **Can you name a measurable outcome attributable to a specific run within hours-to-weeks?** If the answer is "user satisfaction" with no instrumentation, the answer is no.
2. **Is the signal external to the model?** Self-judging is not a signal.
3. **Can you replay a run and recompute the signal?** If not, regression testing is impossible.
4. **Will the signal stay valid if the agent learns to optimize it?** Or is it Goodhart-vulnerable in obvious ways?

If two of these are "no", recommend the state-cache path. Tier 2 or tier 5 memory, no closed loop, no learning ladder. Ship it. Revisit when the signal exists.
