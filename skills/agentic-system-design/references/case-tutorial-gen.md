# Case Study — Tutorial / Educational Video Generation

## Domain summary

Tutorial-gen systems take a topic, audience, and reference materials (slides, code, screencasts) and produce a structured educational video — segmented narration, voice-over plan, accessibility metadata, pacing budget. Quality is multi-axial (accuracy, scaffolding, voice, a11y); the work shape is "many small segments, each independently checkable" — closer to code review than brand-shaping copy. The closed-loop signal is unusually clean: completion + comprehension are cheap and online.

## Natural council to design

- **Foreman — Editor-in-Chief**. Sets Tutorial DNA, orchestrates segment-by-segment, decides which critic gates apply, finalizes.
- **Script Writer** — drafts narration per segment from frame description / learning objective; first-pass never sees brand voice or prosody concerns.
- **Technical SME** (critic) — runs code samples, cites docs, catches inaccuracies.
- **Pedagogy Reviewer** (critic) — does this teach a step? prerequisites in scope? scaffolding sound? Enforces teach-one-thing-per-segment.
- **Voice Director** (critic) — pacing, prosody, tone match to audience level. Bounded discrete prosody scale, no free-form "make it more exciting".
- **Brand Voice Steward** (critic) — forbidden phrases, "you" vs "we" stance, banned CTAs, consistent terminology.
- **Accessibility Reviewer** (critic) — acronyms spelled out on first use, audio describes critical visuals, reading-level check.

**Sub-agent spawn conditions** (all depth-3):
- *OCR Specialist* on text-heavy frame with sparse description — extracts on-screen text verbatim (`ocr_frame`).
- *Trimmer* (spawned by Voice Director) when timing budget exceeded >10% — tightens preserving every taught concept (`trim_to_budget`).
- *Code-Runner* (spawned by Technical SME) on any executable snippet — sandboxed deterministic run (`run_code`).

## DNA (structured state)

`TutorialDNA` — per-tutorial persistent state:

- **audience_level** — beginner/intermediate/advanced; controls vocabulary and assumed priors.
- **voice** — narration voice (conversational, formal, terse); discrete enum, not free-form.
- **learning_objective** — one-line objective per tutorial; enforces narrative spine.
- **forbidden_phrases** — banned filler ("basically", "just", "simply"); banned CTAs ("click here", "easy"); banned brand confusions.
- **pacing_budget** — words/minute target + max segment duration; Voice Director enforces.
- **prerequisite_concepts** — explicit list of what audience already knows; Pedagogy Reviewer rejects segments that teach below this floor.

DNA is enforced as constraints. Voice Director cannot recommend a prosody outside the discrete scale; Brand Voice Steward cannot approve a forbidden phrase paraphrase.

## Tool-loop & sub-agent design

**Foreman tools:** `extract_segments`, `call_script_writer`, `call_technical_sme`, `call_pedagogy_reviewer`, `call_voice_director`, `call_brand_voice_steward`, `call_accessibility_reviewer`, `finalize_segment`, `finalize_tutorial`.

**Critic verification tools:**
- Technical SME: `lookup_doc(library, topic)`, `spawn_code_runner`
- Pedagogy Reviewer: `check_prerequisites`, `teach_one_thing_check`
- Voice Director: `score_pacing` (bounded 1–5 scale), `spawn_trimmer`
- Brand Voice Steward: `forbidden_phrase_match` (semantic, not literal), `voice_consistency_check(draft, prior_segments)`
- Accessibility Reviewer: `acronym_check`, `visual_description_check`, `reading_level`

**Sub-agent palettes:**
- OCR Specialist: `ocr_frame` + `cite_text` — pure extraction, no narration.
- Trimmer: `trim_to_budget` — preserves every taught concept; flags loss.
- Code-Runner: `run_code` + `compare_output(expected, actual)` — sandboxed, deterministic.

System prompt skeleton for Editor-in-Chief:

```
You are the Editor-in-Chief producing a tutorial on {{topic}} for {{audience_level}}.
Tutorial DNA: voice={{voice}}, pacing_budget={{wpm}}, forbidden={{forbidden_phrases}}.
Per segment: Script Writer drafts; SME + Pedagogy gate accuracy/scaffolding;
Voice Director + Brand Steward gate voice; Accessibility gates a11y.
Hard cap 3 revision rounds; flag for human on exceed.
```

## Memory verdict

Mostly **context-mgmt** plus the **cleanest closed loop in the 4 case studies**:

- **Signal**: completion rate, comprehension quiz scores, time-to-first-success.
- **Latency**: minutes to days — videos ship, instrumented players report back fast.
- **Ground truth**: human-graded comprehension on held-out set; engagement on shipped variants.
- **Why clean**: verifier is cheap and online; no weeks-long finance lag, no HAZOP incident-DB pollution risk.

State-cache accumulations: per-vertical scaffolding priors, voice-profile pacing calibration, adversarial set of forbidden-phrase paraphrases. This is the case where escalating state cache → real Skill B learning loop pays off fastest — see `feedback-signals.md`.

## Anti-patterns specific to this domain

| Anti-pattern | Test | Fix |
|---|---|---|
| **Off-topic narration** | Script drifts to things not on screen | Vision pass extracts physical detail only; narration is council debate output, not extractor's |
| **Monotone delivery** | Voice Director gives free-form prosody ("more energetic") | Bounded discrete prosody scale (1–5 per axis); CoT-before-score |
| **Info-dump segments** | One segment teaches 4 concepts | Pedagogy Reviewer enforces teach-one-thing as hard rule, not guideline |
| **Extractor leaking brand voice** | Vision/OCR returns "this exciting button" | Extraction layers output physical detail only; brand voice lives in council debate layer |
| **Forbidden-phrase semantic bypass** | "Just simply do X" → "merely do X" | Brand Voice Steward uses semantic match + cited rationale, not literal regex |
| **Code samples that don't run** | SME approves visually-plausible code | Spawn Code-Runner on every snippet; SME cannot approve unrun code |
| **Pacing budget violations** | Voice Director rubber-stamps over-budget segments | Tool-layer gate: approval requires `score_pacing >= threshold`; over-budget triggers Trimmer |

## Recommended pattern + council shape

- **Pattern:** #5 Evaluator-Optimizer (`patterns-catalog.md`) — clear per-segment criteria; output demonstrably improvable with feedback; per-segment iteration. Hard-cap 3 rounds to prevent degeneration-of-thought.
- **Council shape:** #2 Iterative Refinement (`council-shapes.md`) primary, with #6 Generator-Discriminator embedded for code-snippet validation. Tutorial copy has a clean per-segment rubric (unlike marketing) — refinement converges.

Don't pick #3 Foreman-Worker primary: subtasks here ARE pre-definable. Editor-in-Chief is an editor, not an orchestrator-of-the-unknown.

## Implementation notes

- **Cleanest closed loop in our 4 cases.** Start as state cache but plan the Skill B upgrade early — engagement + comprehension are cheap to instrument with minutes-to-days lag.
- **Voice-neutral extraction is an architectural rule, not a prompt nudge.** Vision/OCR/scene extractors output physical detail only; brand voice lives in the council debate layer. Applies across the codebase.
- **Discrete prosody scales** (1–5 per axis: tempo, pitch range, emphasis) outperform free-form descriptions. CoT-before-score raises agreement with human voice directors — see `llm-as-judge.md`.
- **Per-segment hard-cap on revision rounds.** Without it, Voice Director and Brand Voice Steward ping-pong forever. 3 rounds, then flag for human; track over-cap rate as quality signal.
