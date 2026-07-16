---
name: pitch-craft
description: Write or fix any spoken script that has to hit a clock - demo-video voiceovers, deck walkthrough narration, and live pitch speeches. Use whenever the user asks for narration, a voiceover, a timestamp script, a pitch script, a speech that fits N minutes, wants it to "sell like Steve Jobs", or needs an existing script re-synced after a re-record or re-timed to a new slot. This is also the engine the demo-video, pitch-deck, and pitch-package skills call for their scripts. Not for - written submission forms or essays (no clock), building deck HTML (pitch-deck), or recording video (demo-video).
---

# Pitch Craft - Timed Spoken Scripts

A timed script is engineering plus theater. The clock is a hard constraint; the storytelling is why anyone remembers you. Every failure mode of a bad script traces to violating one of those two, so this skill enforces both: **beats before words**, and **the craft rules** in `references/storytelling.md`.

## Steps

### 1. Beats before words

Get three things before drafting a single sentence:

- **The beats**: what is on screen (or on stage) at each moment, in order. For a demo voiceover these are the recording's milestones; for a deck they are the slides; for a live pitch they are slides plus stage moments (team intro, demo break).
- **The clock**: either fixed windows from an existing recording (`0:16 -> 0:43`), or a total slot to budget (a 5-minute pitch).
- **What each beat proves**: a beat with no claim behind it gets cut, not narrated.

If the beats don't exist yet, build the beat sheet first and get the user's sign-off. Prose written before beats always runs long and anchors the story to sentences instead of evidence.

### 2. Budget the words

Read `references/timing.md` and compute a word ceiling per segment (words = seconds x words-per-second; voiceover ~2.4-2.6 wps, live stage ~2.0-2.2 wps). Write the budget line at the top of the script (e.g. `5:00 slot = ~2:30 spoken + 2:36 demo`). If the numbers don't fit before writing, they won't fit after.

### 3. Draft with the craft rules

Read `references/storytelling.md` and apply it: **hook before names**, **analogy per abstraction**, **throughline three times**, plain words, numbers that land twice. Recorded voiceover and live speech are different registers - never reuse one as the other (see the register section in storytelling.md).

### 4. Timing check

Count words per segment against its ceiling. Fix overruns by cutting, never by asking the speaker to rush. Every script ships with 1-2 **named trim points** ("fold #6 into #7, cut #12 to one sentence, saves ~15s") so the speaker can hit the clock live without improvising.

### 5. Honesty pass

**Claim only what's wired.** Every factual sentence must be verifiable on screen or against the codebase. Where on-screen labels differ from reality, use generic phrasing ("a fast model, our strongest model") instead of names that contradict the pixels. Prefer precision rewrites over impressive vagueness ("tracing relationships between accounts, not claiming it's the same banknote"). Judges and buyers probe; one caught overclaim poisons every true claim.

### 6. Output in the standard formats

Recorded (chunked to milestones):

```
1. 0:00 -> 0:16
An analyst opens a queue of twelve hundred alerts. The rule engine closes
eleven hundred sixty-five under policy, each with a sealed reason.
```

Live (slide-anchored, with stage cues):

```
[2:35 - Slide 7 - Proof, then roll the demo]
Most demos ask you to just believe them. We'd rather show you.
(cue: click through slides 8-10 as you say it, then roll the video)
>>> PLAY DEMO VIDEO (~2:10) - this covers slides 8, 9, 10 <<<
```

The demo-break marker always states what the video covers, so a numbering jump never reads as a gap.

## Re-syncing an existing script

When a recording is redone, milestones shift (live backends have latency variance). Map each segment's cue point to the new milestone timestamps and cut prose to the new window - never stretch prose to fill. 1-2 seconds of drift per segment is acceptable. Details in `references/timing.md`.

## References

- `references/storytelling.md` - the craft: hook, team intro placement, analogies, throughline, registers, delivery cues, honesty guardrails. Read before drafting.
- `references/timing.md` - words-per-second tables, formats, estimation loop, trim points, re-sync procedure. Read before budgeting.
