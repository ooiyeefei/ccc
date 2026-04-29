---
description: Interactive design session for a new survey — research goal, audience, hypotheses, questions, modality, output schema
allowed-tools: Read, Write, AskUserQuestion
---

# Design Survey

Walk the user through designing a new survey, end to end. Output is a finalized question set + output schema, ready to hand off to `/turn-into-app`.

## Usage

```
/design-survey
```

Optionally with a use-case hint:

```
/design-survey for a startup founder doing customer discovery
/design-survey for an event we're running next month
/design-survey for our gig-worker retention diagnosis
```

## Process

Always invoke the `rethink-surveys` skill first. Then walk the user through these steps **in order**, asking ONE question per turn. Don't dump the whole flow at once.

### Step 1 — Research goal (mandatory)

Ask: *"In one sentence, what's the research goal? Pretend you're explaining to a busy stakeholder why this survey is worth doing."*

If the user gives a vague answer ("to understand users"), push back: *"Specifically — what decision will the survey help you make? If 100 responses came in tomorrow, what would change?"*

Don't proceed without a sharp goal.

### Step 2 — Audience

Ask: *"Who's the respondent, and how will they encounter the survey? (e.g., QR code at venue, email to warm list, push from in-app)"*

The answer determines the modality default:
- QR / cold → form, ≤60s
- Email / warm → form + voice, ≤90s
- In-app / engaged → AI-interviewer mode possible

### Step 3 — Length budget

Ask: *"What's an honest length budget? 60 / 90 / 180 seconds, or longer?"*

Reference Jarrett's rule: never lie about length on the landing page. If they say 60s, they need a 60s instrument.

### Step 4 — Hypotheses

Ask: *"What 2–4 things are you trying to prove or disprove? Each becomes a section of the survey."*

If they don't have hypotheses → suggest reading [`references/use-cases.md`](../skills/rethink-surveys/references/use-cases.md) for templates with pre-formed hypotheses they can fork.

### Step 5 — Match to template (if applicable)

If the use case matches event organizers / startup founders / gig-economy workers → load the template from `references/use-cases.md` and **propose** it as the starting point. Make clear they can fork/adapt.

If no template fits → build from scratch using the 4-part hybrid structure.

### Step 6 — Build the question set, part by part

Walk through Parts 1–4 (discovery / diagnostic / intent / segmentation). For each part:

1. Pull suitable patterns from [`references/question-library.md`](../skills/rethink-surveys/references/question-library.md).
2. Propose 1–3 questions for that part.
3. Show the user the full question text in their target locale(s). For each, briefly note which **principle** it serves and what trade-off they're accepting.
4. Get user confirmation before moving to the next part.

### Step 7 — Modality selection

Reference the modality decision tree in [`references/multimodal-ux.md`](../skills/rethink-surveys/references/multimodal-ux.md). Recommend a default; flag when a non-default is justified by the audience answer in Step 2.

### Step 8 — Output schema

Show the user the resulting Postgres + JSONB schema. Include:
- Top-level columns (respondent_type, segment, contact, consent_*, etc.)
- `response_data` JSONB shape
- Derived columns (cluster_id, scores) reserved for post-hoc enrichment

### Step 9 — Final review checklist

Before declaring "design done", run through:

- [ ] Does each question serve one of the 4 parts? (Tag every Q.)
- [ ] No leading/double-barreled/satisficing-bait questions?
- [ ] Behavioral anchors used where applicable?
- [ ] Length claim matches estimated time?
- [ ] Demographics only included when they actually route?
- [ ] Split consent (not single combined)?
- [ ] Open-ended discovery question first?
- [ ] Auto-skip rules clear (e.g., language step skipped for native speakers)?

### Step 10 — Output

Produce a single Markdown document the user can save (suggest a filename like `survey-design-<date>.md`):

```markdown
# Survey Design: <name>

## Research goal
<sentence>

## Audience & channel
<who, how reached>

## Length: <Xs honest>

## Hypotheses
1. ...
2. ...

## Question set
### Part 1 — Discovery
Q1. ...
   - Principle served: <which>
   - Modality: <text/voice/multi>

### Part 2 — Diagnostic
...

### Part 3 — Intent
...

### Part 4 — Segmentation & follow-up
...

## Branching rules
- ...

## Modality
<form / form+voice / AI-interviewer>

## Output schema
<Postgres DDL + JSONB shape>

## Acceptance checklist (Jarrett review)
- [x] ...
```

Then ask: *"Want me to run `/turn-into-app` and emit a working scaffold?"*

## Anti-patterns to flag if user proposes them

When the user suggests a question, push back if you see any of these:

| User proposes | Flag with |
|---|---|
| "Rate excitement 1-10" | "Pure satisficing bait — pick a behavioral 1-5 with anchors instead." |
| "What demographic info should we collect?" | "Only ask demographics that actually route the response. Otherwise skip." |
| "Combined consent checkbox" | "Split into two: action consent + research-call consent." |
| "Optional Q at the bottom" | "Move it to the middle, or cut it. The bottom signals 'throwaway'." |
| "Self-routing landing page (60s vs 2min)" | "Pick the right instrument for the channel and serve it. Don't push the decision to the respondent." |

## Reference triggers

- User asks "why" about a recommendation → load `references/design-principles.md`
- User wants specific question wording → load `references/question-library.md`
- User names a use case (event/founder/gig) → load `references/use-cases.md`
- User asks about voice/AI/multimodal → load `references/multimodal-ux.md`
- User asks how to rank/cluster results → load `references/scoring-framework.md`
