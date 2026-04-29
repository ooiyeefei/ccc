# Design Principles — The Why Behind the Rules

Loaded when the user wants to know **why** a recommendation was made, or wants to argue for an exception.

## Table of contents

- [Caroline Jarrett — Surveys That Work](#caroline-jarrett--surveys-that-work)
- [Don Dillman — Tailored Design Method](#don-dillman--tailored-design-method)
- [Roger Tourangeau — The cognitive response model](#roger-tourangeau--the-cognitive-response-model)
- [Krosnick — Satisficing theory](#krosnick--satisficing-theory)
- [Caroline Fink — How to Ask Survey Questions](#caroline-fink--how-to-ask-survey-questions)
- [The Mom Test — Customer discovery for founders](#the-mom-test--customer-discovery-for-founders)
- [How these traditions disagree](#how-these-traditions-disagree)

## Caroline Jarrett — Surveys That Work

**Core thesis:** A survey is a conversation with a busy person. If you forget that, you'll get bad data.

**Five rules every survey design routes back to:**

1. **The respondent's first instinct is to leave.** Default state is "skip this." Every screen, every question must justify its existence. Apply the *cut test*: if I removed this question, would the analysis still work? If yes, cut it.
2. **Never lie about length.** A landing page that says "60 seconds" but takes 90 burns trust. The completion-rate cliff at the broken-promise moment is steeper than the cliff at "this is too long." Better: say 90s, deliver 75s.
3. **One question per screen on mobile.** Cognitive load is the bottleneck, not page count.
4. **Test with real users in the actual completion context.** A survey designed for desktop reading and tested in a desktop browser will fail on a phone in a noisy venue. Always test in the venue you'll deploy in.
5. **Name and shame double-barreled questions.** "Was the food fast and cheap?" is two questions. The respondent picks the dimension they care about; you don't know which.

**Practical pattern: the Caroline Jarrett Review.** When designing, ask a colleague to read each question aloud and tell you what they think it's asking. If they reframe it differently than you intended → the question is broken. Rewrite, retry.

## Don Dillman — Tailored Design Method

**Core thesis:** Survey design is a multi-channel respondent-engagement strategy, not just question-writing. Includes invitation copy, follow-up cadence, incentives, and visual design.

**Most operationally useful pieces for software-builders:**

- **Question order matters more than people think.** Warm-up questions first (easy, non-threatening) → diagnostic questions in the middle (highest engagement) → demographics last (low cognitive cost, respondents already invested).
- **Visual hierarchy carries semantic weight.** A bold question feels more important. A small "(optional)" tag invites skipping. Design accordingly.
- **Pre-test with respondents from the actual target population.** Not your team, not your friends. The wording that's "obvious" to a startup founder is alienating to a gig-economy worker.

**The Dillman incentive trap:** offering a draw/raffle increases completion rates but biases your sample toward people who like raffles. Acceptable for marketing-funnel surveys; dangerous for research instruments.

## Roger Tourangeau — The cognitive response model

**Core thesis:** Every answer to a survey question goes through 4 stages in the respondent's mind. Bad questions break stages.

| Stage | What happens | What can break it |
|---|---|---|
| **1. Comprehension** | Respondent decodes the question | Jargon, double-barrels, ambiguous referents |
| **2. Retrieval** | Respondent searches memory for relevant info | Asking about events too long ago / too vague to anchor |
| **3. Judgment** | Respondent decides on an answer | Lack of clear criteria; satisficing kicks in |
| **4. Response** | Respondent maps their answer onto your options | Mismatched scale, missing options, leading framing |

**Diagnostic value:** when a respondent answers something weird, it's almost always one of these four stages that broke. Fixing the question = fixing the right stage.

**Implication for AI-interviewer mode:** the LLM can probe each stage. "I want to make sure I'm reading this right — when you say X, do you mean Y or Z?" is a Stage 1 repair. "Can you tell me about the most recent time this happened?" is a Stage 2 anchor.

## Krosnick — Satisficing theory

**Core thesis:** Respondents have a budget of cognitive effort. When the question requires more effort than they want to spend, they "satisfice" — give the first acceptable answer instead of the optimal one.

**Satisficing red flags in surveys:**

- Long matrices (rows × columns of Likert questions) — respondents pick a column and stay there ("straight-lining")
- Mid-scale answers ("3", "neutral") clustering above expected base rate — sign of "I don't know but want to keep moving"
- Don't know / no opinion options chosen at high rates on questions that don't merit it
- Identical responses across many questions ("acquiescence bias")

**Mitigation:** keep surveys short, vary question formats, force-choice (no neutral middle option) for items where you actually want a directional answer, behavioral anchors instead of fuzzy Likert.

## Caroline Fink — How to Ask Survey Questions

**Core thesis:** Specific > open unless open is the point. Most surveys err on the side of vague open-ended questions and shallow forced-choice; the right balance has *one or two genuinely open questions* and the rest forced-choice with well-curated options.

**Operational rules:**

- **Open-ended for novelty, forced-choice for comparison.** If you want to discover what you don't know → open. If you want to compare across respondents → forced-choice.
- **Forced-choice options should be MECE** (mutually exclusive, collectively exhaustive). If a respondent reasonably maps to two options, you've failed MECE.
- **Always include "Other" with optional text input** for genuinely-novel answers — but treat the rate of "Other" as a quality metric. If >15% pick Other, your options are wrong.

## The Mom Test — Customer discovery for founders

**Core thesis (Rob Fitzpatrick):** When you ask people about your idea, they lie to be nice. The way to get truth is to *not ask about your idea* — instead, ask about their life and past behavior, and let your idea's value (or lack thereof) emerge from the data.

**Rules:**

1. **Talk about their life, not your idea.** "What do you struggle with?" beats "Would you use my product?"
2. **Ask about specifics in the past, not generalities or opinions about the future.**
3. **Talk less, listen more.** Five-second silence after a question gets you the real answer; jumping in to clarify gets you the polite answer.

**Implication for survey design:** the discovery (Part 1) question should follow Mom Test rules — "What's the last time X happened?" rather than "Would you find Y useful?"

## How these traditions disagree

These five thinkers don't fully agree. When in doubt, here's the call:

- **Jarrett vs. Dillman** on length: Jarrett says shorter is always better. Dillman says length matters less than perceived relevance. **Pick Jarrett for mobile / event QR / cold audience; Dillman for warm email lists.**
- **Krosnick vs. Fink** on Likert: Krosnick says Likert produces noise; Fink says force-choice can be too rigid. **Pick Krosnick when behavioral anchors exist; pick Fink when the construct is genuinely continuous (e.g., "how confident are you").**
- **Mom Test vs. Tourangeau** on probing: Mom Test says shut up and listen; Tourangeau says probe the cognitive stages. **Pick Mom Test for early discovery; pick Tourangeau for AI-interviewer mode where you have permission to probe.**

## Quick lookup — when violating which rule is OK

The rules are guidelines, not laws. Document when you're breaking one and why.

- **Hypothetical question is OK when** there's no past behavior to ask about (e.g., "Would you pay for X" when X doesn't exist yet) — but pair it with a forced-choice over concrete amounts, never an open "how much would you pay"
- **Demographic question is OK when** it actually changes downstream routing (e.g., asking country to pick currency on willingness-to-pay)
- **Likert is OK when** the construct is genuinely continuous and behavioral anchors don't exist (e.g., "how confident are you" — confidence has no obvious behavioral anchor)
- **Optional question is OK when** the question is high-cost-low-yield (e.g., free-text "anything else?") and you'd rather not ask than force a satisficed answer
