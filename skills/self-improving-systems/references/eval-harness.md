# Eval Harness

Six patterns for evaluating memory-bearing agents. Ship at least the first three before going live with any persistent memory tier ≥ 3. The eval harness is not optional infrastructure — without it, you cannot tell when your memory store has been poisoned, your agent has started to drift, or your judge has lost calibration.

The fundamental problem: **stateless agents fail in ways you can reproduce by re-running the input.** Memoryful agents fail in ways you can't. The eval harness is how you compensate.

---

## 1. Golden set

**What.** 50–500 hand-curated `(input, expected behavior, expected memory side-effect)` tuples. Mix happy-path, edge cases, and adversarial / poisoning attempts. Tag each tuple with which memory tier it stresses.

**How to implement.**
- Write the tuples in a flat YAML/JSON file under version control.
- Each tuple specifies: the input prompt(s), pre-run memory state, expected agent output (or a regex/judge rubric), expected post-run memory delta.
- Include at least 5–10% adversarial tuples — prompt injection in user input, MINJA-class injection in retrieved content, contradictory facts that should trigger arbitration.
- CI: every PR that touches the agent or memory layer runs the golden set; threshold-fail blocks merge.

**What failure looks like.**
- Agent passes happy-path but fails edge cases → coverage gap.
- Memory side-effect doesn't match → extractor is lossy or arbitration is wrong.
- Adversarial tuple succeeds (injection lands) → quarantine pattern broken.

**Citation.** [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (eval discipline); [Letta — RAG vs Agent Memory](https://www.letta.com/blog/rag-vs-agent-memory).

---

## 2. Regression on memory side-effects

**What.** Assert exact post-run memory state for specific high-value tuples. Beyond "did the output look right" — did the right facts land, in the right shape, with the right source-tagging?

**How to implement.**
- For each high-value tuple, declare expected memory state: `assert get(user, "allergies") == ["peanut"]` after run X.
- Include source-tag assertions: `assert get(user, "allergies").source == "user-stated-2026-04-15"`.
- Negative assertions matter as much as positive: `assert "credit_card_number" not in get(user, *)`.
- Run after every model upgrade, prompt change, retrieval-config change. Memory side-effects are the silent kill.

**What failure looks like.**
- Fact extracted but wrong shape (`["peanut allergy"]` vs `["peanut"]`) → downstream queries miss.
- Fact extracted but wrong source-tag → redaction can't find it on a delete request.
- Fact extracted that shouldn't have been (PII leak into store) → privacy breach.
- Fact silently overwritten without arbitration → you didn't know the agent contradicted itself.

**Citation.** [State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) flags drift as #1 production pain.

---

## 3. Drift alarms via OpenTelemetry GenAI semconv

**What.** Real-time observability on memory-store health using the [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/blog/2025/ai-agent-observability/). Trace every retrieval, embedding, write. Aggregate into rolling metrics; alarm on anomalies.

**How to implement.**
- Instrument retrieval calls: hit rate, top-k score distribution, candidate count.
- Instrument writes: extraction confidence, arbitration rate (% of writes that triggered conflict), memory-store size growth rate.
- Instrument runs: judge-score rolling mean (7-day window), % of runs that mutate core memory, % of runs that hit context-rot threshold.
- Alarm rules:
  - Judge-score rolling mean drops >2σ from baseline → drift.
  - Memory-store size growth rate exceeds 1.5× last-month baseline → bloat or poisoning.
  - Retrieval hit-rate distribution shifts (KS-test against baseline) → corpus drift or query drift.
  - % of runs mutating core memory rises sharply → likely a new prompt-injection vector landing.

**What failure looks like.**
- Silent drift you don't catch until users complain.
- Runaway memory growth from one bad extractor → storage bill spike, retrieval quality collapse.
- Judge-score steady on average but distribution skew (mode collapse) hidden by the mean.

**Citation.** [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/blog/2025/ai-agent-observability/).

---

## 4. A/B between agent versions

**What.** Slice production traffic between agent v(n) and v(n+1). Compare composite reward over a fixed window with statistical power computed up front.

**How to implement.**
- Define the composite reward in advance — engagement × brand-fidelity × safety, or whatever the domain calls for. **Do not pick the metric after looking at the data.**
- Compute required sample size for the effect you care about (typical: detect 5% lift at 80% power).
- Slice randomly (per-user, not per-session — session-level slicing leaks treatment).
- Run for the full sample-size window; do not peek and stop early.
- Stratify the analysis by user cohort to detect Simpson's-paradox patterns.

**What failure looks like.**
- v(n+1) wins on the composite but only because of one cohort that happens to dominate the slice → roll out, regress everywhere else.
- Memory side-effect from v(n+1) pollutes shared store, confounds future comparisons → A/B contaminated.
- Significance reached early but only on the noisy half-window → publication-bias-style false positive.

**Citation.** Standard online-experimentation practice; see [State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) for memory-specific failure modes in A/B.

---

## 5. LLM-as-judge with human calibration

**What.** Use a cross-family LLM with a decomposed rubric to score outputs. Audit 5–10% of judge outputs against human labels. Recompute judge–human Cohen's κ weekly; stop trusting the judge below threshold.

**How to implement.**
- **Cross-family judge mandatory.** If the generator is Claude, the judge is GPT-class or Gemini-class, never Claude. Self-preference is real and worth ~10% lift toward own outputs ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819)).
- Decomposed rubric. Score each criterion (tone, accuracy, audience-fit, …) on a bounded discrete scale (1–5 or 1–7). Composite is geometric mean, not sum, so any single-axis collapse fails the whole sample.
- CoT before score. The judge writes reasoning before emitting numbers. Raises agreement with humans.
- Randomize candidate order; average two passes with positions swapped.
- Anonymize model identities. Strip "I generated this" cues.
- Weekly audit: 5–10% sample reviewed by a human against the same rubric. Cohen's κ tracked; alarm if κ < 0.6 — retrain rubric or swap judge model.

**What failure looks like.**
- Judge agrees with itself (κ between two judge runs is high) but disagrees with humans (κ vs human is low) → judge has a different rubric than the team thinks it does.
- Judge κ stable on average but drops sharply on edge cases → you're shipping the easy 80%, missing the hard 20%.
- Judge drifts after a model update on the judge side → you didn't pin the judge model version.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791); [Self-Preference Bias (arXiv 2410.21819)](https://arxiv.org/abs/2410.21819).

---

## 6. Held-out human-written tasks

**What.** A small set (20–100) of human-written tasks the agent is **never** trained or in-loop-improved on. Run them on every release. Detects distribution collapse from self-play.

**How to implement.**
- Lock the held-out set behind access control. Engineers building the agent should not see the contents.
- Run on every release; report scores in the release notes.
- Refresh the held-out set every 6–12 months as the domain evolves; keep the old held-out set as a regression baseline.
- For self-improving systems specifically: this is your only protection against the agent narrowing capability by training on its own outputs.

**What failure looks like.**
- Golden-set scores improve, held-out scores plateau or regress → agent is overfitting to the in-loop distribution.
- Held-out scores drop sharply on edge-case clusters → distribution collapse, the agent has stopped exploring.
- Held-out scores are stable but composition has shifted (new task types added) → pre-update baselines no longer comparable.

**Citation.** [V-STaR (arXiv 2402.06457)](https://arxiv.org/abs/2402.06457); [Quiet-STaR (arXiv 2403.09629)](https://arxiv.org/abs/2403.09629) — both highlight distribution collapse risks in self-improvement loops without external verifiers.

---

## Minimum viable eval harness

If you can only ship three patterns before going live:

1. **Golden set** (#1) — without it, every release is a regression risk.
2. **Memory side-effect regression** (#2) — without it, memory poisoning is invisible.
3. **Drift alarms** (#3) — without it, you find out about problems from users.

Add A/B (#4), judge calibration (#5), and held-out tasks (#6) before scaling beyond an initial cohort.

**Hard rule:** if you're at memory tier ≥ 5 (KV fact store or above) without #1 + #2 + #3 in production, you're flying blind. Either ship the harness or downgrade to tier 2 (conversation summary).
