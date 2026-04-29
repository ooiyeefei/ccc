---
name: rethink-surveys
description: Design, critique, or scaffold surveys grounded in Caroline Jarrett, Dillman, and Tourangeau methods. Use when designing a new survey, critiquing an existing one, or turning questions into an app. Triggers on "survey", "questionnaire", "user research", "customer discovery", "intent capture", "interview script", or "how to ask better questions". Captures real past behavior over hypotheticals, supports text/voice/AI-interviewer modalities, and includes templates for event organizers, startup founders, and gig-economy workers.
---

# Rethink Surveys

A survey is a conversation with a busy person. Design it like one.

This skill packages a framework for designing, critiquing, and operationalizing surveys that capture real intent — not satisficed checkbox approval. Built from the experience of designing the Proxymate muShanghai survey (which surfaced bugs in ~6 hours of testing that a category-checkbox flow would have hidden for weeks).

## Three operating modes (commands)

1. `/design-survey` — interactive design session: research goal → audience → hypotheses → questions → modality → output schema. Walks the user through 5–8 decisions, each with explicit trade-offs. Reuses templates where appropriate.
2. `/critique-survey` — paste-in review: identify leading questions, double-barreled items, satisficing bait, missing behavioral anchors, demographic-for-demographic noise. Returns a Jarrett-style critique with concrete rewrites.
3. `/turn-into-app` — implementation handoff: takes a finalized question set and produces app scaffold (TanStack Start / Next.js / pure HTML, plus Supabase or simple JSON storage). User picks the stack; this command emits the code.

If the user's intent is unclear, ask: *"Are you (a) starting fresh, (b) reviewing something you already wrote, or (c) ready to ship — meaning: turn an existing question set into an app?"*

## The seven design principles (the spine)

Every survey-design decision routes back to one of these. Memorize.

1. **Ask about real past behavior, not hypotheticals.** "Last time X happened, what did you do?" beats "What would you do if X happened?" by an order of magnitude in signal quality. Hypotheticals invite imagined-self answers.
2. **Don't pre-signal the right answer.** "Most people find X useful — would you?" is broken. Replace with neutral framing.
3. **Start broad and open-ended before narrowing.** Open-ended question first → respondent's authentic frame; structured questions after → that frame doesn't get lost in a checkbox.
4. **Separate screening / diagnosis / segmentation.** Screening = "are you the right respondent?" Diagnosis = "what's actually happening?" Segmentation = "what cohort do you fit into?" Mixing them leads to confusing branching and worse data.
5. **No double-barreled questions.** "Was the food fast and cheap?" should be two questions. If you can't decompose without losing the meaning, reword.
6. **Behavioral anchors over Likert scales** when anchors exist. "I'd lose ~30 minutes" is universal; "Somewhat annoying" is whatever the respondent thinks today.
7. **Honest length claim on the landing page.** If you say 60 seconds, deliver 60 seconds. Lying about length is the single fastest way to nuke completion rate. Jarrett's rule: never lie about length.

For the *why* behind each principle (Tourangeau's 4-stage cognitive model, satisficing theory, etc.) read `references/design-principles.md`.

## The 4-part hybrid structure

This is the structural skeleton every well-designed survey shares. Use it as a checklist:

| Part | Purpose | Example questions | Failure mode |
|------|---------|-------------------|--------------|
| **1. Discovery (open-ended)** | Capture authentic frame before constraining it | "What's the one thing you're worried about?" / "Last time X, what did you do?" | Skipping → checkbox-only data with zero novelty |
| **2. Diagnostic (targeted, structured)** | Make responses analyzable across users | Severity 1–5 with anchors / Frequency / Workaround text | Skipping → can't cluster or rank |
| **3. Intent & prioritization** | Surface willingness, urgency, willingness-to-pay | Top-3 priorities / WTP buckets / "When would help most?" | Skipping → no demand signal, can't prioritize |
| **4. Segmentation & follow-up** | Cohort the respondent + qualify for follow-up | Who-are-you / Group composition / Contact + split consent | Skipping → can't compare cohorts, no interview pipeline |

For each question, **tag it** with which part it serves. Questions that don't clearly belong to one part are usually candidates for cutting.

For battle-tested question patterns by part (with EN+ZH parallel text and trade-off notes), read `references/question-library.md`.

## Modality decision tree

Match modality to context:

- **Pure form (tap-to-select)** — physical QR scan, on-venue, low-attention. Target ≤60s.
- **Form with optional voice on key questions** — moderate attention; the diagnostic question benefits from authentic phrasing. Target ≤90s.
- **AI-conversational interviewer** — pre-event email warm-list, deep research mode, willing respondents. AI probes with follow-ups based on prior answers. Target 3–5 minutes, ~10 substantive answers.
- **Voice-note only** — accessibility-first / language-flexible / low-literacy contexts. Single open prompt, transcribed server-side, post-processed for cluster signals.

Default rule: **start with form + optional voice on the discovery question.** Add AI-interviewer only if the research goal requires probing depth that a flat form can't deliver.

For the full UX/UI guide (with React/HTML scaffolds and storage schema recommendations), read `references/multimodal-ux.md`.

## What to ask AI conversationally vs. show as form fields

| Show as form field | Ask via AI |
|---|---|
| Multiple-choice with finite known options | Open-ended diagnosis with potential follow-up |
| Numeric or scale (with behavioral anchors) | Causal explanation: "Why did that happen?" |
| Demographic/segmentation | Workaround: "What did you try first?" |
| Consent checkboxes | Edge cases the form options don't cover |

AI is for the parts where **you don't know what answers to expect**. Form is for the parts where you do.

## Scoring & tagging framework

After collection, every response should map to:

- **`pain_unit`** — the specific worry/problem captured in the discovery question, ideally with a cluster ID assigned by post-hoc LLM enrichment
- **`severity`** (1–5 with behavioral anchors)
- **`willingness_to_pay`** (bucket or numeric range, currency-localized for bilingual audiences)
- **`workaround_strength`** — derived from whether the respondent has an existing fallback (text length + sentiment)
- **`segment`** — derived from screening/segmentation answers
- **`interview_score`** — composite for ranking interview-call candidates: `severity × specificity × wtp_weight × consent_research_call × novelty_bonus`

For the full intent-scoring math (composite formula, tag taxonomy, cluster assignment heuristics), read `references/scoring-framework.md`.

## Use-case templates

Three full templates with research goal, target respondent, hypotheses, full question set, branching, and output schema:

- **Event organizers** — pre-event attendee surveys, post-event NPS-with-teeth, vendor-feedback
- **Startup founders** — customer-discovery (Mom-Test-style), product-validation, churn diagnosis
- **Gig-economy workers** — supply-side onboarding, fairness/pay diagnosis, retention drivers

When the user names a use case that matches one of the three (or wants to fork from one), read `references/use-cases.md`.

## Anti-patterns to flag aggressively

- **"Rate your excitement 1–10"** — pure satisficing bait. Always cut.
- **Demographics for demographics' sake** (age, gender, nationality without a routing reason) — increases drop-off, adds zero signal. Cut unless one of those answers actually changes downstream behavior.
- **Single combined consent checkbox** ("OK to contact me about anything") — forces respondents to opt in to too much. Split into specific consents per channel of follow-up.
- **"Optional" research questions at the bottom** — respondents infer "this is the throwaway part." Move research-grade questions to the middle, where engagement is highest.
- **Self-routing landing pages** ("Got 60s or 2min?") — pushes a design decision onto the respondent. Pick the right instrument for the channel and serve it directly.

## Workflow patterns (high level)

### When user says "I want to design a survey for X"

1. Scope: what's the **research goal** (single sentence)? Don't proceed without this.
2. Audience: who's the **respondent**? How will they encounter the survey?
3. Length budget: 60s / 90s / 3min / longer? Be honest with yourself before being honest with them.
4. Hypotheses: what 2–4 things are you trying to prove or disprove? Each becomes a section.
5. Match to template if available (use case in `references/use-cases.md`).
6. Walk through the 4-part hybrid structure, picking 1–3 questions per part.
7. Modality: form / voice-mixed / AI-interviewer.
8. Output schema: what columns/JSONB shape lands in the DB?

### When user says "Critique this survey"

1. Read the survey question by question.
2. Check each against the seven principles. Note violations.
3. Check the 4-part structure: which parts are missing or duplicated?
4. Check the length claim against actual estimated time.
5. Return: a punch-list of issues + concrete rewrites for the worst 3–5 + a verdict on the overall instrument.

### When user says "Turn this into an app"

1. Confirm the question set is final. If not → bounce back to `/design-survey`.
2. Pick the stack: TanStack Start (we have a reference impl), Next.js, or static HTML. Default: TanStack Start if user has no preference and wants voice support.
3. Pick the storage: Supabase (default), or simple JSON-on-disk for local prototypes.
4. Emit the scaffold per `references/multimodal-ux.md`.

## Reference files (load on demand)

- **`references/design-principles.md`** — Jarrett, Dillman, Tourangeau primer + satisficing theory. Read when designing from scratch and the user wants the *why*.
- **`references/question-library.md`** — battle-tested question patterns by part, with EN+ZH parallel text. Read when proposing specific questions.
- **`references/use-cases.md`** — three full templates: event organizers, startup founders, gig-economy workers. Read when the user names a matching use case.
- **`references/multimodal-ux.md`** — UX/UI patterns + React scaffolds. Read when running `/turn-into-app`.
- **`references/scoring-framework.md`** — full intent-scoring math + cluster taxonomy. Read when ranking or clustering responses.

## What this skill is NOT for

- **Statistical analysis of response data** — that's a downstream job, use a different tool.
- **Survey-platform recommendations** (Typeform vs. Tally vs. SurveyMonkey) — this skill is opinionated about the survey *itself*, not the SaaS that hosts it. We assume custom code.
- **General market research strategy** — survey design is one tool, not the strategy.
