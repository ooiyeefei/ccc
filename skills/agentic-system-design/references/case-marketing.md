# Case Study — Marketing / Content (Brandling)

> Status: this is the canonical shipped reference. The Brandling system already implements this council; the design below is the template you adapt for any brand-content domain (social posts, video scripts, ad copy, newsletters).

## Domain summary

Marketing-content generation produces brand-shaping outputs (posts, scripts, ad creative) from a brief plus brand context. Inputs are a goal, an audience hint, and reference assets; outputs are short-form copy, storyboards, or end-to-end video plans. Blast radius per output is high and quality is multi-axial — accuracy, brand voice, hook strength, taboo compliance, and engagement all matter at once.

## Natural council to design

- **Foreman role — Marketing Head** (orchestration). Sets the brief into a debate plan, decides which personas speak in which round, finalizes the winning candidate. Brandling routes this to Opus.
- **Content Creator** (3 parallel drafts) — produces independent first drafts so downstream critics see a real spread, not anchored variants.
- **Brand Critic** — positioning, voice fidelity, taboo enforcement, audience match. Brandling routes to GPT-5.5 specifically because cross-family judging mitigates self-preference bias.
- **Engagement Critic** — hook strength, scroll-stopping power, CTA clarity. Brandling routes to Gemini 3 Flash for cheap, fast scoring.
- **Review Council** — winner selection across the surviving candidates with mandated dissent capture.

**Sub-agent spawn conditions:**
- *Brand Critic spawns Verification Specialist* (depth-3) with `web_search` when a factual claim or competitor reference appears in a draft and cannot be verified from BrandDNA alone.
- *Engagement Critic spawns Engagement Analyst* (depth-3) with `apify_top_posts` when a hook claim depends on platform-specific virality patterns the critic doesn't have priors for.

This is the canonical "critic-spawns-specialist" depth-3 pattern from `patterns-catalog.md`.

## DNA (structured state)

`BrandDNA` — the persistent shared state every persona reads:

- **audience** — primary audience descriptor (ICP, vertical, seniority).
- **tone** — voice descriptors (e.g. "wry, terse, anti-corp"), forbidden registers.
- **visualWorld** — palette, recurring imagery, continuity anchors for video.
- **taboo** — phrases, claims, comparators that must never appear.
- **goals** — campaign objectives (awareness vs conversion vs activation).
- **provenance** — `_source` stamps per field (operator-set vs mutation-evolved vs default).

DNA is the spec each critic verifies against. Without it, critiques degenerate into taste battles.

## Tool-loop & sub-agent design

**Foreman tools:** `call_marketing_head`, `call_content_creator(brief, n_drafts=3)`, `call_brand_critic`, `call_engagement_critic`, `call_review_council`, `finalize(winner, dissent)`.

**Critic verification tools:**
- Brand Critic: `read_brand_dna`, `check_taboo_match`, optional `spawn_verification_specialist`
- Engagement Critic: `score_hook(rubric)`, optional `spawn_engagement_analyst`

**Sub-agent palettes** (depth-3, cap 2 spawns/critic, 60s timeout):
- Verification Specialist: `web_search` + `cite_source`
- Engagement Analyst: `apify_top_posts(platform, topic)` + `summarize_pattern`

System prompt skeleton for the foreman:

```
You are the Marketing Head running a debate over {{brief}}.
Tools: call_*, finalize.
Mandatory start: call_content_creator with n_drafts=3.
Mandatory end: finalize() — never return without it.
Hard cap: 4 rounds. Reward dissent; do not collapse minority views.
```

## Memory verdict

Currently a **state cache** (Brandling's Mutation Engine), not a learning loop. The Mutation Engine evolves BrandDNA fields across runs but has no external feedback signal — DNA mutates from operator edits and per-run reflections, not from observed outcomes.

To become a real learning loop:
- **Signal**: composite of engagement deltas (CTR, dwell, save/share) + brand-fidelity LLM-judge + sample-audited human review.
- **Latency**: hours to days (post performance) for engagement; minutes for judge-based brand-fidelity.
- **Ground truth**: held-out human-labeled brand-voice set + production engagement on shipped variants.
- **Risk**: vanity-metric reward hacking (engagement-only rewards push toward clickbait drift). Must combine signals.

See `case-studies.md` in `self-improving-systems` for the upgrade path.

## Anti-patterns specific to this domain

| Anti-pattern | Test | Fix |
|---|---|---|
| **Vanity-metric reward hacking** | Engagement-only signal → drafts drift toward clickbait, brand voice degrades | Composite reward = engagement + brand-fidelity judge + sample human audit |
| **Same-family judge** | Claude generates and Claude judges → self-preference ~10% lift | Cross-family critic mandatory (Brandling: Claude generates, GPT-5.5 + Gemini judge) |
| **Anchored drafts** | Three drafts all argue Marketing Head's hypothesis | Content Creator gets raw brief, NOT the strategy framing; force independent reasoning |
| **Taboo bypass via paraphrase** | Critic only literal-matches forbidden phrases | Taboo check uses semantic match + explicit rationale citation back to BrandDNA |
| **Council debating closed-form facts** | Council debates whether a stat is true | Spawn Verification Specialist with `web_search`; council does not vote on facts |
| **Visual continuity drift** | Multi-clip video forgets palette/anchor between clips | Continuity anchor as DNA field, not regex-on-visualWorld; Foreman threads it explicitly |

## Recommended pattern + council shape

- **Pattern:** #2 Orchestrator-Workers (`patterns-catalog.md`) — Marketing Head decomposes the brief, parallel Content Creators draft independently, critics evaluate. Subtasks aren't pre-definable (which axis matters most varies per brief).
- **Council shape:** #3 Foreman-Worker (`council-shapes.md`) with #6 Generator-Discriminator embedded (Content Creator × N → Engagement Critic ranks). Brandling's actual choice — open-ended where subtasks aren't pre-definable, plus discriminator over many candidates.

Why not #2 Iterative Refinement: marketing copy doesn't have a single rubric clean enough to converge; the council needs spread + selection, not iterative polish.

## Implementation notes

- **Cross-family is the strongest single lever.** Brandling routes Brand Critic to GPT-5.5 and Engagement Critic to Gemini 3 Flash — diversity dominates structural tweaks (arXiv 2511.07784). Don't ship same-family councils.
- **Critic-spawns-specialist justifies depth-3.** Verification Specialist needs its own context (search, citations) that would pollute the critic's judgement loop — see `patterns-catalog.md`.
- **Provenance on every DNA field** is non-optional. Without `_source`, you cannot debug why a mutation cycle drifted brand voice or revert surgically.
- **`finalize` is the only legal terminator.** Never return on max_turns without an explicit error path — that's how silent regressions ship to brand-shaping channels.
