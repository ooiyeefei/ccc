# Deck recording - walkthrough video in two parts

The walkthrough is recorded with the **demo-video** skill's harness (`demo-video/scripts/record_template.py`) - that skill owns the Xvfb/ffmpeg/CDP recipe and its gotchas. This file adds only the deck-specific deltas.

**Scope note on demo-video's "film the product, not a poster" rule:** it governs the *demo film*, not this take. Slides are the legitimate subject here - that is what a deck walkthrough is. The boundary is the stitch: slide content lives in Part A and Part B, and never inside the demo film they wrap. A deck that narrates the product instead of showing it running is still failing the rule; that's what the demo slot is for.

**Which gates apply.** Gate 1 is already satisfied for a deck take: the approved slide list plus its narration windows *is* the storyboard (pass the script or slide list to `--storyboard`). Gates 2 and 3 apply unchanged - smoke take before the full capture, MP4-derived `t_video` for every milestone. Slide walkthroughs drift less than live-backend demos, but capture offset is identical, and a half-second shift puts the voiceover on the wrong slide.

## HOLDS come from the narration

The narration (written first, via pitch-craft) fixes each slide's window. The recorder's hold per slide = that window's length:

```
narration:  1. 0:00 -> 0:11  (Hook)        -> hold 11
            2. 0:11 -> 0:26  (AML 101)     -> hold 15
            3. 0:26 -> 0:34  (The cost)    -> hold 8
```

If a hold and its narration segment disagree, the voiceover lands on the wrong slide - keep them as one versioned pair, and re-derive HOLDS whenever the script changes.

This is the one place planned holds legitimately drive the recording: for a deck the causality runs narration -> holds -> capture, so the window IS the design. It does not exempt the take from Gate 3. **After recording, compare each slide's reconciled `t_video` against the window it was built from.** Drift under ~0.5s: ignore. Over: re-cut that segment to the real window per pitch-craft's `timing.md`. Never voice against the planned holds just because they were the input - the file is still the arbiter.

## Two parts around the demo

Record the deck as two takes, stitched around the demo film:

- **Part A**: slides 1 -> demo slot. The last beat PAUSES on the demo-slot slide (~4s) and never plays the embed.
- **Part B**: fresh-load the deck at `#<demo_slot+1>` (hash deep link) so the first post-demo slide plays its entry animation on camera, then run to the Close.

Fresh-loading matters: continuing a single take across the demo boundary either shows the embed or shows a stale slide with spent animations.

## The deck driver

In the harness template, the BEATS list becomes: first beat `{"js": None, "hold": HOLDS[0]}` (the fresh-loaded first slide), then one beat per remaining slide:

```python
# settle 1.4 (not the 0.6 default): deck entries animate .8s with a
# calc(var(--i)*110ms) stagger, so the last element lands past 1.0s - proof
# frames at the default would catch half-faded text on every slide.
BEATS = [{"label": "SLIDE_1", "js": None, "hold": HOLDS[0], "settle": 1.4}] + [
    {"label": f"SLIDE_{i+2}",
     "js": "document.getElementById('next').click()",
     "hold": h, "settle": 1.4}
    for i, h in enumerate(HOLDS[1:])
]
```

Set the harness URL to `http://127.0.0.1:<port>/deck.html#1` for Part A and `#<demo_slot+1>` for Part B (serve the deck dir with `python3 -m http.server`; deterministic, no network). 30fps and single-pass CRF 18 are fine for slides (static content).

## Stitch order

`Part A + demo film + Part B`, in that order. Normalize first if sources differ (same resolution and fps), then concat:

```
ffmpeg -f concat -safe 0 -i list.txt -c copy stitched.mp4   # if uniform
# else re-encode: -c:v libx264 -crf 18 -preset slow
```

Voice is recorded separately over the stitched cut, following the combined script's timestamps (deck Part A windows, then the demo narration, then Part B windows). The milestone JSON sidecars from each part give the exact per-slide times if anything needs re-alignment.
