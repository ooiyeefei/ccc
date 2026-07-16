# pitch-deck

Build a pitch deck as **one self-contained HTML file** (opens from disk, no CDN, no network), write its timed walkthrough narration, and optionally record the walkthrough as video parts that stitch around a demo film.

The deck's philosophy: **the deck is the backdrop, the speech carries the pitch**. One idea per slide, minimal text, numbers **cited or cut** (every stat hyperlinks a real, verified source), vector icons never emojis, a persistent brand mark on every slide, and appendix slides that hold the hard Q&A answers so the main arc stays clean.

Recording support: hash deep-links (`#11`) let the recorder fresh-load any slide so its entry animation plays on camera; the `#next` button is driven via CDP click (focus-proof under a virtual display). Per-slide HOLD durations derive from the narration windows; recorded as Part A (pauses on the demo slide) + Part B (fresh-loads after it), stitched around the demo film. The harness lives in `demo-video` - single source of truth.

Narration is written by the `pitch-craft` skill; audience strategy by `pitch-package`.

## Use this, not that

- **Use pitch-deck when the deliverable is the DECK** (and optionally its recorded walkthrough).
- The product demo film itself -> `demo-video`. The narration and live speech -> `pitch-craft`. Audience strategy and slot budgeting -> `pitch-package`.
- Part of the pitch suite: decision guide in [skills/README.md](../README.md#the-pitch-suite---when-to-use-what).

## Structure

- `SKILL.md` - the five-step workflow
- `references/deck-patterns.md` - the single-file skeleton: nav, animations, brand mark, citations, demo-slot, appendix
- `references/deck-recording.md` - HOLDS from narration, the two-part split, stitch order
