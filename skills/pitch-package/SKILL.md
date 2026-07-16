---
name: pitch-package
description: The step-back skill for pitching as a person - given an audience (hackathon judges, VCs, investors, customers) and a time slot, it budgets the slot, decides what to build or reuse (deck, demo video, live speech), and orchestrates the pitch-deck, demo-video, and pitch-craft skills into one rehearsed package with a stitch plan, Q&A prep, and a day-of checklist. Use whenever the user says they need to pitch, present, or demo at a hackathon or demo day, to investors or a customer, mentions an N-minute slot, or asks to "prepare the whole pitch" end to end. Not for - a single artifact in isolation (call pitch-deck, demo-video, or pitch-craft directly) or written-only submission forms.
---

# Pitch Package - the whole performance

A pitch is one argument delivered through three instruments: the deck (setup), the demo (proof), and the speaker (trust). **The demo is the proof; the deck is the setup.** This skill's job is sequencing and budget, so the instruments never fight each other. Two rules govern everything: **interview before you build**, and **budget the slot first**.

## Phase 1 - Interview before you build

STOP: produce no artifacts in this phase. Ask (adapting to what's already known):

1. **Audience**: hackathon judges, VCs, or a customer? What do they explicitly judge or care about (rubric, thesis, their own pain)?
2. **Slot**: total minutes? Is Q&A inside or after it?
3. **Inventory**: what already exists - working product? demo video? deck? scripts? Reuse beats rebuild.
4. **Demo mode**: live product on stage (higher wow, higher risk) or recorded film (deterministic)? Default to recorded unless the live path has been rehearsed with a fallback.
5. **Speakers**: who talks, and are there real credentials to weave into the intro?
6. **Constraints**: venue machine? offline? projector resolution? phone-as-teleprompter?

Reflect the answers back as a one-paragraph brief and get a nod before Phase 2. Skipping this interview is how pitches end up with a beautiful deck for the wrong audience.

## Phase 2 - Budget the slot first

Before writing or building anything, write the budget line:

```
5:00 slot = ~2:30 spoken deck + 2:36 demo video + ~0:10 transitions
(runs ~5:15 as written -> trim points named in the script)
```

The budget decides scope: how many slides get narrated, whether the demo needs a shorter cut, what gets trimmed live. Every downstream artifact inherits this budget. If the pieces don't sum inside the slot on paper, they won't on stage.

## Phase 3 - Compose (gap-fill via the other skills)

Pick the audience lens from `references/audiences.md` - same assets, different lead, emphasis, and close. Then fill only the gaps the inventory revealed:

- Missing demo film -> **demo-video** skill (beat sheet keyed to the proof this audience needs).
- Missing or stale deck -> **pitch-deck** skill (demo-slot slide included; appendix slides for this audience's hard questions).
- The live speech -> **pitch-craft** skill, LIVE register: hook first, team intro after the hook, the demo-break marker stating what the video covers, delivery cues, named trim points.

One throughline threads all three artifacts - if the deck's tagline, the video's close, and the speech's refrain differ, unify them before rehearsal.

## Phase 4 - Rehearse and ship

- **Stitch plan** per `references/stitching.md` (which variant: fully recorded film, live-with-recorded-demo, fully live) plus the fallback ladder.
- **Rehearse against the clock**: read the script aloud with a stopwatch once; apply the named trims if over. Adjust the script, never the speaking pace.
- **Q&A prep**: appendix slides + a one-page honest-defense brief (the questions you fear, answered with what's true - overclaims die here, before a judge finds them).
- **Day-of checklist**: local copies of deck AND video on the presenting machine (no network dependency), test in an incognito window at venue resolution, backup speaker for each section, the teleprompter (phone-friendly script page) charged and loaded.

## References

- `references/audiences.md` - the three lenses (judges / VC / customer): what each judges, what leads, what closes.
- `references/stitching.md` - assembly variants, ffmpeg stitch recipe, fallback ladder, phone-teleprompter pattern.
