# LLM-as-Judge: 7 Rules

When a council uses a judge — for evaluator-optimizer loops, tournament rounds, jury aggregation, or eval harnesses — these are the 7 non-negotiable rules. Skip any one and the judge becomes noise.

---

## 1. Decompose the rubric (analytic, not holistic)

**Why it matters.** Holistic scoring ("rate this 1–5") collapses under halo effects: the judge picks one salient property and lets it dominate the score. Analytic scoring forces the judge to evaluate criterion-by-criterion, which raises agreement with humans and reduces variance.

**How to implement.** Break the rubric into 3–6 named criteria (e.g., for marketing copy: *brand voice fit*, *hook strength*, *CTA clarity*, *factual accuracy*). Have the judge score each independently. Aggregate with a documented weighting — equal weights are fine if you can't justify otherwise.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791).

---

## 2. Bounded discrete scales (1–5 or 1–7)

**Why it matters.** Free continuous floats (e.g., "score from 0.0 to 1.0") look precise but produce noisy, unreliable scores — the judge can't actually distinguish 0.73 from 0.78. Binary yes/no is too coarse — it loses the partial-credit signal where most disagreements live. Bounded discrete scales (1–5 or 1–7) sit at the precision sweet spot the model can actually hit consistently.

**How to implement.** Use a 1–5 or 1–7 Likert scale per criterion. Define **anchors** for each integer ("3 = meets baseline; 4 = exceeds in one named way; 5 = best-in-class"). Reject the model's tendency to produce 3.5 or 4.2 — force discrete output via prompt or post-processing.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791).

---

## 3. Show reasoning before score

**Why it matters.** Score-first prompting lets the model anchor on a number and rationalize backward. Reasoning-first (CoT-before-score) forces evaluation to drive the score, not the reverse. Empirical work shows this raises agreement with human raters meaningfully.

**How to implement.** Prompt structure: *"For each criterion, write 2–4 sentences explaining your assessment, then output the score on a separate line."* Parse the score from the structured output. Reject responses that produce score-then-reasoning — re-prompt or post-process.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791).

---

## 4. Randomize candidate order; average across positions

**Why it matters.** Position bias is asymmetric and large — judges preferentially score candidates in position A or position B regardless of content, often by 10%+. In pairwise tournaments this is the dominant noise source. Single-position evaluation produces order-dependent rankings that don't survive a re-run.

**How to implement.** For pairwise: run each pairing twice with positions swapped (A vs B, then B vs A); average the scores or require both passes to agree on the winner. For N-way: randomize order on every judging call. Track per-position score deltas as a calibration metric — if A-position systematically beats B-position across thousands of runs, position bias is leaking through your mitigation.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791). See also [failure-modes.md](failure-modes.md) §4.

---

## 5. Anonymize model identities

**Why it matters.** Models recognize their own outputs through stylistic fingerprints (sentence length distribution, common phrases, formatting habits) and rate them ~10% higher even when explicit identity is stripped ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819)). Naming the source ("Output A from Claude, Output B from GPT-4") makes it dramatically worse.

**How to implement.** Strip all identity cues: no model names, no "I generated this", no provider-specific formatting tells. Normalize whitespace and markdown formatting if possible. Treat anonymization as defense-in-depth — it reduces but doesn't eliminate self-preference, so always pair with rule #6.

**Citation.** [Self-Preference Bias (arXiv 2410.21819)](https://arxiv.org/abs/2410.21819).

---

## 6. Rotate the judge across models

**Why it matters.** Same-family judging is the largest reproducible bias in LLM-as-judge. Claude judging Claude has measurable self-preference; same for GPT and Gemini. The fix isn't a better prompt — it's a different model family.

**How to implement.** **Cross-family judge mandatory.** If candidates come from Claude, the judge runs on GPT or Gemini. Rotate the judge across runs (Claude→GPT→Gemini cycling) to prevent any single model's biases from anchoring the system over time. For high-stakes decisions, run two judges from different families and require agreement; flag disagreements for human review.

**Citation.** [Self-Preference Bias (arXiv 2410.21819)](https://arxiv.org/abs/2410.21819). See also [failure-modes.md](failure-modes.md) §5.

---

## 7. Validate against a golden set

**Why it matters.** A judge that doesn't agree with humans is producing noise dressed up as scores. Without calibration, you're optimizing toward whatever the judge happens to like — discriminator collapse ([failure-modes.md](failure-modes.md) §7) — which may diverge arbitrarily far from truth.

**How to implement.** Build a **golden set** of 50–500 hand-judged examples covering the rubric's range and edge cases. Run the judge against the golden set; compute agreement (Cohen's κ for categorical, Spearman ρ for ordinal). Require **75–90% agreement** with human labels — below 75% the judge is unusable; above 90% is suspicious (either the rubric is too easy or the golden set is too narrow). Recompute weekly; stop trusting the judge if agreement drops below threshold.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791).

---

## Rule summary

| # | Rule | Why |
|---|---|---|
| 1 | Decompose the rubric | Halo effects collapse holistic scores |
| 2 | Bounded discrete scales | Precision sweet spot the model can hit |
| 3 | Reasoning before score | Stops backward rationalization |
| 4 | Randomize order; average positions | Kills position bias |
| 5 | Anonymize identities | Reduces self-preference (defense-in-depth) |
| 6 | Rotate judge across families | Primary fix for self-preference |
| 7 | Validate against golden set | The judge itself needs calibration |

---

## When to violate these rules

Almost never, but two narrow cases:

- **Holistic scoring (rule 1)** is acceptable when the entire decision is "ship or don't" with no partial credit and no further use of the score. Even then, capture the reasoning for audit.
- **Free continuous scales (rule 2)** are acceptable when the score is feeding a downstream regressor, not a human decision — e.g., learned reward models. The model still can't produce reliable continuous scores; you're just comfortable with that noise floor because the regressor smooths it out.

If you find yourself violating rule 6 (cross-family judge) or rule 7 (golden set) you don't have a judge — you have a vibe check. Re-architect.

---

## Cross-references

- For failure modes the judge inherits or causes → [failure-modes.md](failure-modes.md).
- For council shapes that use judges (Iterative Refinement, Judge + Jury, Tournament) → [council-shapes.md](council-shapes.md).
