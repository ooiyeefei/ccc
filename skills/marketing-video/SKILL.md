---
name: marketing-video
description: Plan and script a product or solution marketing video for strangers - the pain, the value, one real proof moment and one ask, high level and non-technical. Use whenever someone wants a marketing video, promo, launch film, website or homepage video, YouTube explainer, a short film per workflow or feature, a 15 to 90 second cut, or a long "a month in the life of a [industry] business" film, or says a video is too technical or reads like a feature tour. Not for a pitch in a booked slot (pitch-package) or a how-to for a user finishing a task (help-center-tutorial).
---

# Marketing video - a stranger, one pain, one proof moment

The viewer has never heard of us and asks two questions: is this my problem, and is this for me? The film answers both in plain words and asks for one thing. Three leading words, used the same way throughout:

- **stranger** - someone who knows neither our name, our category word nor our menu labels. A stranger may know their own trade well: its words (the head, the abattoir, the till) are theirs and stay. Ours do not. The **stranger test**: would a person from that trade follow this line the first time they hear it?
- **pain** - a moment in the stranger's own week, in their words, with a time and an object ("it is the 28th and you are still keying in receipts"). Our category's name for it is not a pain.
- **proof moment** - the one real on-screen moment behind a value, seen in seconds (a receipt filling its own form). A value with no proof moment is a slogan.

## Steps

### 0. Confirm the family

If the viewer must finish a task, this is a tutorial. If they decide in a booked slot, it is a pitch (`film-line`, section 1). If the pain or the props are specific to one trade (a farm, a shop, a clinic), the film belongs to an industry: fill the industry brief first (`film-line/references/industry-brief.md`) and read `references/industry-flagship.md`.

### 1. The brief

One line each: **stranger** (who, where they watch, what they know) | **pain** (one, in their words, and where you heard it) | **promise** (what changes for them, one sentence) | **values** (two or three outcomes they feel, each with its proof moment) | **limit** (the one thing it does not do, said once) | **ask** (one, in its exact words; spoken, with the address shown rather than read) | **length** (from the ladder in `references/story.md`) | **avoid** (our category words the stranger would not say) | **guardrails** (purpose, third-party logos, rights line, where it plays: `demo-video/references/distribution.md`; for a public marketing film the company's own wording in `film-line/references/house-rules-groot.md` replaces that file's "demonstration" cards and "not for redistribution" line).

With no support threads, calls or reviews to cite, write the pain as a hypothesis, mark it unsourced, and ask for one sentence a real stranger said.

### 2. Storyboard - blocking, one nod for brief and storyboard together

`# | beat | pain or value | proof moment (the real frame) | seen | draft line | dur`, where `seen` says whether the proof moment was seen on the real product or is unconfirmed. The spine is **pain, turn, values, limit, ask**. The pain is the first thing heard, and no logo card comes before it (a band under the picture is not a logo card). The pain beat may carry no product (a prop shot, a plain card, a rendered frame): record that as an approved exception in the storyboard. A product state that shows the pain (a full inbox, an overdue list) is better. Every other beat is real. The turn is the product starting to move: its frame shows only the start, so a promise larger than that frame is proved by the value beats that follow and is marked so in the audit. Each value beat names its proof moment. The limit names where the edge sits, over the screen where it sits. The ask is last. Draft lines only size the beats. Settle the structure questions of `demo-video/references/structure.md` in the storyboard header with defaults; the one nod covers them. Spine patterns and timing: `references/story.md`.

**Route**, proposed in the storyboard header and covered by the same nod. The test: could this beat have come from a PNG? If the promise needs to be seen working, the film is **filmed**: stage and record per `film-line`, cut from the take bank, real product, annotate never substitute (`demo-video`). If the film is mostly idea (an ad, a hero loop, a 15 second social cut) with one to four real proof beats, it is **rendered**: `motion-video` builds the wrapper and `demo-video` records the proof. Both keep the proof real.

Audit both ways. Forward: every value has a proof moment. Backward: every sentence the voice will say names the frame that shows it (the limit is the one sentence that names an absence). Check the draft lines now, so no rewrite waits for QA: against the **avoid** list with `film-line/scripts/narration_scan.py --avoid <words>`, and against the company's honest-claim lines in `film-line/references/house-rules-groot.md`. Drafts need not hit the pace band. A read-only look at the real product before the nod is allowed and wise: it confirms each proof moment exists, and writes nothing. Write the audit out, name what the film does not show, show the table and stop. Nothing is staged, recorded or rendered before the nod. A changed beat list reopens this gate.

### 3. Build, then narrate after the cut

Build per the route. Write the voice after the cut, to the verified frames, in the plain register of `film-line/references/narration.md`: second person, present tense, concrete, 2.2 to 2.6 words per second (`pitch-craft` for the clock and the honesty pass). Marketing films play muted in a feed, so the proof moment must read without sound; captions are burned in for a feed and a subtitle file ships for YouTube.

### 4. QA and hand back

Run `film-line` post gates. Then the marketing checks, each one checkable:

- Every line passes the stranger test. Scan the voice for the brief's **avoid** list: `film-line/scripts/narration_scan.py --avoid <words>` reports each hit.
- No more than five distinct screens are named in any 90 seconds. A screen shown again counts once; navigation chrome does not count. A long film applies it per chapter.
- One ask, last. One limit, said once. No claim without a frame.

## What stays out

Feature tours, settings screens, pricing and plan names unless the brief says so, architecture, click-by-click steps (that is a tutorial), customer logos without consent, traction claims.

## References

- `references/story.md` - the length ladder, spine patterns, finding the pain, value to proof moment, endings and cut-downs.
- `references/industry-flagship.md` - the month-in-the-life shape; cutting shorter films and tutorials from the same takes.
