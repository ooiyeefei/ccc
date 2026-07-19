---
name: pitch-deck
description: Build a pitch deck as one self-contained HTML file (keyboard and click navigation, staggered slide-entry animations, a persistent brand mark, cited numbers with real links), write its timed walkthrough narration, and optionally record the walkthrough as video parts that stitch around a demo film. Use whenever the user asks for a pitch deck, demo-day / hackathon / investor slides, a slide walkthrough video, deck narration, or wants an existing HTML deck polished, re-branded, or recorded. Not for - PowerPoint / PPTX output (use a pptx skill), the product demo film itself (demo-video), or deciding overall pitch strategy and audience framing (pitch-package).
---

# Pitch Deck - one HTML file, narrated, recordable

The deck is the backdrop; the speech carries the pitch. So the deck's job is: one idea per slide, minimal text, numbers that are **cited or cut**, and navigation reliable enough to drive by hand on stage or by script on camera. One file, no CDN - it must open from disk, on a venue machine, with no network.

## Steps

### 1. Outline: one slide, one idea

Derive the slide list from the pitch story (the pitch-craft skill's storytelling rules apply to structure too). A proven arc to adapt, not worship:

Hook -> what-it-is 101 -> the cost of the status quo -> Reveal (name + throughline) -> test bed / credibility -> the concrete example -> how it works (one flow, end to end) -> "watch it work" (the demo slot) -> the differentiator ("it learns") -> one-more-thing -> roadmap -> architecture -> Close (numbers land again + name).

Appendix slides (anticipated hard questions: safety, "is this really agentic", adoption, commercials) go AFTER the close, are never narrated, and are opened only when a judge asks.

### 2. Build the single file

Follow `references/deck-patterns.md`: section-per-slide skeleton, hash-based deep links (`#11` starts at slide 11 - the recorder depends on this), `data-anim` staggered entries, a fixed brand mark in the top-right of every slide, progress bar + counter. Rules that earn their keep: **cited or cut** (every industry number hyperlinks a real source, verified to load), vector icons never emojis, synthetic-data disclaimers as one corner legend rather than per-slide clutter.

### 3. Narrate via pitch-craft

Hand the slide list to the **pitch-craft** skill for the walkthrough script (per-slide timestamp windows, recorded register). If the deck will also be presented live, have pitch-craft write the LIVE variant separately (team intro after the hook, stage cues, trim points) - the two registers do not interchange.

### 4. Record the walkthrough (optional)

Follow `references/deck-recording.md`: per-slide HOLD durations derived from the narration windows, recorded in two parts around the demo slot (Part A ends paused on the demo slide, Part B fresh-loads after it). The recording harness lives in the **demo-video** skill (`demo-video/scripts/record_template.py`) - single source of truth; this skill only contributes the deck-specific driver (click `#next`, hold per window).

### 5. Publish and verify

Serve locally, or publish (htmldrop / static host) if a link is needed. Then actually click through every slide checking: entry animations fire, no broken assets, citations open, the brand mark sits on every slide, and the demo embed (if any) loads. A deck you haven't paged through end-to-end is not done.

## References

- `references/deck-patterns.md` - the single-file skeleton: nav, animations, brand mark, citations, demo-slot slide, appendix pattern.
- `references/deck-recording.md` - HOLDS from narration windows, the two-part split around the demo, stitching order.
