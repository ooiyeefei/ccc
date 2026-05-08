# Council Shapes

Deep-dive on the 7 council shapes. Pick after you've decided a council is justified — most "we need a council" requests don't pass the 4-condition test below.

---

## The case for a council vs. a single agent

A council pays for itself when **at least one** of these holds:

1. **Verifiable but multi-faceted output.** The output is scored on more than two axes — e.g., accuracy + brand voice + hook strength for marketing copy; correctness + safety + auditability for finance entries. A single critic can't hold all axes without halo-effect collapse.
2. **Diverse failure modes per model.** Empirical ensemble work shows a 72%-avg-accuracy diverse ensemble can beat an 81%-avg homogeneous ensemble when error patterns differ ([arXiv 2502.18036](https://arxiv.org/html/2502.18036v1)). Cross-family models in a council exploit this.
3. **High blast radius per output.** Customer-facing, brand-shaping, irreversible. One bad output = lost trust, not just a retry.
4. **Subjective quality where one model has known biases.** Self-preference is real and adds **~10% lift** toward a model's own outputs ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819)). A council with a cross-family judge mitigates.

## When a council is wasteful

Skip the council if any of these are true:

- **Closed-form answer.** Math, syntax, retrieval — ["Debate or Vote" (NeurIPS 2025)](https://openreview.net/forum?id=iUjGNJzrF1) showed majority voting alone captures most of the gain attributed to debate. Don't pay debate prices for vote-class tasks.
- **Latency is the product.** Autocomplete, chat-first-token, real-time UI. A council adds rounds; rounds add seconds.
- **You can't write a rubric.** If the criteria can't be articulated, the critic will hallucinate them and you'll ship vibes.

## Empirical sweet spot

**3–4 agents, 2–4 rounds** ([arXiv 2506.00066](https://arxiv.org/html/2506.00066v1)). Beyond that, accuracy degrades. More agents ≠ better; more rounds ≠ better. Composition (model diversity) dominates structural tweaks ([arXiv 2511.07784](https://arxiv.org/abs/2511.07784)) — cross-family models are the strongest single lever, far stronger than fancier debate protocols.

---

## 1. Parallel Critique

N agents independently produce drafts and then peer-review each other's outputs. Karpathy's `llm-council` pattern. After the round, an aggregator synthesizes consensus and dissent.

**Use case.** Diverse first-drafts where you want both range (each agent generates without seeing others) and review (each agent sees the others' work and critiques). Good for creative briefs, hypothesis generation, brainstorm-then-rank.

**Failure mode.** Echo chamber when models share priors — three OpenAI models will mostly agree with each other. Mitigation: enforce cross-family composition; weight minority dissent in the aggregator. See [failure-modes.md](failure-modes.md) on echo chamber.

**Citation.** [Karpathy — llm-council](https://github.com/karpathy/llm-council).

---

## 2. Iterative Refinement (Evaluator-Optimizer)

A generator produces a candidate; an evaluator scores it against a rubric; the generator revises. Loop until the rubric passes or rounds are capped.

**Use case.** Translation, code, copy — anywhere the rubric is writable and improvement is monotonic. The cleanest pattern when you have a verifier.

**Failure mode.** Degeneration-of-thought after round 4 — output stops improving and starts drifting toward a local attractor ([arXiv 2506.00066](https://arxiv.org/html/2506.00066v1)). Mitigation: hard-cap rounds; require monotonic rubric improvement; abort if score doesn't strictly increase.

**Citation.** [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents).

---

## 3. Foreman-Worker (Orchestrator-Worker)

A foreman LLM owns the plan and delegates to specialist workers (each with its own persona, prompt, and possibly model). Workers return drafts/critiques; foreman finalizes. Brandling's choice.

**Use case.** Open-ended where subtasks aren't pre-definable and workers need distinct viewpoints. Marketing copy councils, finance review boards, HAZOP teams. The foreman's job is orchestration + final synthesis, not generation.

**Failure mode.** Foreman bias anchors workers — if the foreman briefs workers with its own hypothesis, workers argue that hypothesis instead of reasoning independently. Mitigation: pass *raw input* to workers, not the foreman's interpretation; mandate independent reasoning in worker prompts; rotate the foreman role across runs.

**Citation.** [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (orchestrator-worker pattern).

---

## 4. Judge + Jury

Multiple jurors score independently; a separate judge synthesizes. Distinct from Parallel Critique — jurors don't see each other's reviews; the judge holds aggregation logic explicitly.

**Use case.** Subjective rankings where ties happen often and you need a tiebreak rule. Editorial selection from N candidates, ranking ad variants, choosing one of many model outputs.

**Failure mode.** Self-preference if the judge is also a juror or shares family with jurors ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819)). Mitigation: cross-family judge mandatory; judge never generates the candidates being judged; rotate the judge across runs.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791); [Self-Preference Bias (arXiv 2410.21819)](https://arxiv.org/abs/2410.21819).

---

## 5. Devil's Advocate

A dedicated critic argues *against* the leading proposal — pre-mortem mode. Surfaces failure modes the consensus would miss.

**Use case.** High-stakes decisions where confirmation bias is the dominant risk. Architecture choices, go/no-go reviews, "should we ship this?" calls. Used as a checkpoint, not a continuous loop.

**Failure mode.** Performative dissent — the critic invents flaws to justify its role. Mitigation: require the critic to cite specific evidence (transcript line, data point) for each objection; reject objections without citations.

**Citation.** [DEBATE — Devil's Advocate (ACL 2024)](https://aclanthology.org/2024.findings-acl.112/).

---

## 6. Generator-Discriminator

A generator produces many candidates fast; a discriminator scores them and selects/ranks. The discriminator is typically cheaper than the generator and runs at higher fanout. Brandling's Engagement Critic + Apify pattern.

**Use case.** Many candidates + fast scorer. Hook-line generation (50 candidates, scored), variant selection in A/B prep, code-completion ranking.

**Failure mode.** Discriminator collapse — if the scorer is shaky, the system optimizes toward whatever the discriminator likes, which may not correlate with truth ([arXiv 2402.10890](https://arxiv.org/abs/2402.10890)). Mitigation: validate the discriminator against a gold set (≥90% accuracy) **before** deploying it as a selector; sample-audit selections against humans.

**Citation.** [Self-Rewarding LMs (arXiv 2402.10890)](https://arxiv.org/abs/2402.10890).

---

## 7. Tournament / Bracket

Pairwise comparisons between candidates; winners advance, losers drop out. Single-elimination or round-robin. Useful when absolute scoring is unreliable but pairwise judgment is stable.

**Use case.** Selecting 1 from N≥8 where you've found absolute scoring (1–5) noisy but pairwise (A vs B) reliable. Image generation selection, long-form copy comparison.

**Failure mode.** Position bias in pairwise judging — judges prefer candidates in position A or B asymmetrically and significantly ([arXiv 2406.07791](https://arxiv.org/abs/2406.07791)). Mitigation: randomize candidate order; run each pairing twice with positions swapped; average. See [llm-as-judge.md](llm-as-judge.md) rule #4.

**Citation.** [Judging the Judges (arXiv 2406.07791)](https://arxiv.org/abs/2406.07791).

---

## Shape selection cheat sheet

| Decision shape | Council |
|---|---|
| Need diverse drafts + peer review | Parallel Critique |
| Have a writable rubric | Iterative Refinement |
| Open-ended, persona-driven, foreman-led | Foreman-Worker |
| Need explicit aggregation logic | Judge + Jury |
| High-stakes go/no-go | Devil's Advocate |
| Many candidates + fast scorer | Generator-Discriminator |
| Absolute scoring unreliable | Tournament |

---

## Composition rules that apply to all shapes

- **Cross-family models** for diversity ([arXiv 2511.07784](https://arxiv.org/abs/2511.07784)). Same-family councils underperform single-agent on hard tasks because of shared priors.
- **3–4 agents, 2–4 rounds** sweet spot ([arXiv 2506.00066](https://arxiv.org/html/2506.00066v1)).
- **Cross-family judge mandatory** when any council uses a judge — same-family judge has measurable self-preference.
- **Rotate orchestrator/foreman/judge** across runs to prevent persona-anchoring drift.
- **Pass raw input to workers**, not the foreman's interpretation, to break foreman bias.

For the failure modes each shape inherits → [failure-modes.md](failure-modes.md). For judge hardening across all shapes → [llm-as-judge.md](llm-as-judge.md).
