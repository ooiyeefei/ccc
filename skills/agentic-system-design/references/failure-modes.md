# Council Failure Modes

The 9 ways multi-agent systems silently fail. Each has a 1-line mitigation; deeper mitigation guidance lives in the cross-referenced docs.

---

## 1. Echo chamber

Agents in the council share priors (same family, similar training data) and converge on the same answer regardless of correctness. The council looks confident; it's just three copies of one mind.

**Mitigation.** Enforce cross-family model composition (Anthropic + OpenAI + Google); weight minority dissent in the aggregator instead of majority-voting it away.

**Citation.** [Can LLM Agents Really Debate? (arXiv 2511.07784)](https://arxiv.org/abs/2511.07784) — composition (model diversity) dominates structural debate tweaks.

---

## 2. Sycophancy / agreement bias

When one agent shifts position, others follow even without new evidence. The council collapses to the loudest voice. Compounds with foreman bias when the foreman speaks first.

**Mitigation.** Bake into worker prompts: *"stick to your reasoning unless given new evidence; cite specifically what changed your mind."* Reward dissent in the aggregator; flag flips that lack a cited new fact.

**Citation.** [Talk Isn't Always Cheap (arXiv 2509.05396)](https://arxiv.org/pdf/2509.05396); [Peacemaker or Troublemaker (arXiv 2509.23055)](https://arxiv.org/html/2509.23055v1).

---

## 3. Foreman / orchestrator bias

The foreman briefs workers with its own framing. Workers argue the foreman's hypothesis instead of reasoning from raw input. The council looks like deliberation; it's actually one voice replicated by three.

**Mitigation.** Pass *raw input* to workers, not the foreman's summary. Mandate independent reasoning in worker prompts. Rotate the foreman role across runs to break per-run anchoring. See [council-shapes.md](council-shapes.md) §3 (Foreman-Worker).

**Citation.** [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents).

---

## 4. Anchor / position bias

Judges rate candidates differently based on order of presentation, often by 10%+. First-presented or last-presented gets systematically higher scores depending on the model. Pairwise tournaments inherit this directly.

**Mitigation.** Randomize candidate order on every judging round. Run each pairing twice with positions swapped; average the scores. Track per-position score gaps as a calibration metric — if A-position consistently wins, the bias is unmitigated. See [llm-as-judge.md](llm-as-judge.md) rule #4.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791).

---

## 5. Self-preference

A judge from the same family as a candidate-generator inflates that candidate's score by **~10%** ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819)). The bias survives even when model identities are stripped — stylistic fingerprints leak through.

**Mitigation.** Cross-family judge **mandatory** when any council uses a judge. Anonymize candidates as best as possible (strip "I generated" cues, normalize formatting), but treat anonymization as defense-in-depth, not the primary fix — the family swap is the primary fix. See [llm-as-judge.md](llm-as-judge.md) rules #5 and #6.

**Citation.** [Self-Preference Bias (arXiv 2410.21819)](https://arxiv.org/abs/2410.21819).

---

## 6. Infinite refinement loops

Evaluator-optimizer systems oscillate between two attractor states or chase diminishing returns past round 4. Quality stops improving; tokens keep burning. The system *looks* productive (rounds advance, scores fluctuate) but produces no net gain.

**Mitigation.** Hard-cap rounds (3 or 4 max). Require **monotonic** improvement: if round N+1 doesn't strictly beat round N on the rubric, abort and ship round N. Track score deltas; flag near-zero deltas as the convergence signal, not just turn count.

**Citation.** [Literature Review of MAD (arXiv 2506.00066)](https://arxiv.org/html/2506.00066v1) — degeneration-of-thought past round 4.

---

## 7. Discriminator collapse

In generator-discriminator setups (e.g., 50 candidates → score → pick top), if the discriminator is uncalibrated, the system optimizes toward whatever the discriminator likes — which may not correlate with ground truth. The pipeline runs cleanly; the output drifts from the actual goal.

**Mitigation.** Validate the discriminator on a held-out gold set **before** using it as a selector. Require ≥90% accuracy on the gold set; below that, the discriminator is noise. Sample-audit 5–10% of selections against human judgment continuously; recompute calibration weekly.

**Citation.** [Self-Rewarding LMs (arXiv 2402.10890)](https://arxiv.org/abs/2402.10890).

---

## 8. Context explosion

Sub-agents inherit parent transcripts. Foreman accumulates worker outputs. Iterative rounds append to history. The context window blows up well before the nominal limit — Anthropic notes accuracy degrades long before 200K nominal capacity, often around ~130K ([Anthropic — Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

**Mitigation.** Pass *summaries* + *task* to sub-agents, not full transcripts. Cap rounds at 3–4. Add a "secretary agent" that compacts the running ledger between rounds. For sub-agents specifically, isolate context — the grandchild does not need the parent's history.

**Citation.** [Anthropic — Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

---

## 9. Degeneration-of-thought

Distinct from infinite refinement: even in finite rounds, output quality peaks at round 2–3 and decays after. The council finds a local good answer, then "improves" it into something worse — over-elaborating, adding unnecessary caveats, polishing away the original insight.

**Mitigation.** Track quality scores per round; if round N has the highest score and round N+1 drops, return round N. Don't trust the final-round output by default; pick the highest-scoring round across the loop. Pair with the round cap from §6.

**Citation.** [Literature Review of MAD (arXiv 2506.00066)](https://arxiv.org/html/2506.00066v1).

---

## Failure mode → mitigation map

| # | Failure mode | Primary mitigation |
|---|---|---|
| 1 | Echo chamber | Cross-family models; weight minority dissent |
| 2 | Sycophancy | "Stick to reasoning unless new evidence" prior; reward dissent |
| 3 | Foreman bias | Raw input to workers; rotate orchestrator |
| 4 | Position bias | Randomize order; average passes with positions swapped |
| 5 | Self-preference | Cross-family judge mandatory |
| 6 | Infinite loops | Hard-cap rounds; require monotonic improvement |
| 7 | Discriminator collapse | Validate ≥90% on gold set before iteration |
| 8 | Context explosion | 3–4 agents, 2–4 rounds, secretary agent |
| 9 | Degeneration-of-thought | Track per-round score; return best round, not last |

---

## Cross-references

- For position bias and self-preference mitigation in detail → [llm-as-judge.md](llm-as-judge.md).
- For council shapes and which failure modes each inherits → [council-shapes.md](council-shapes.md).
- For pattern selection that avoids these traps in the first place → [patterns-catalog.md](patterns-catalog.md).
