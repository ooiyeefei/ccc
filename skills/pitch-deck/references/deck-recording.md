# Deck recording - walkthrough video in two parts

The walkthrough is recorded with the **demo-video** skill's harness (`demo-video/scripts/record_template.py`) - that skill owns the Xvfb/ffmpeg/CDP recipe and its gotchas. This file adds only the deck-specific deltas.

## HOLDS come from the narration

The narration (written first, via pitch-craft) fixes each slide's window. The recorder's hold per slide = that window's length:

```
narration:  1. 0:00 -> 0:11  (Hook)        -> hold 11
            2. 0:11 -> 0:26  (AML 101)     -> hold 15
            3. 0:26 -> 0:34  (The cost)    -> hold 8
```

If a hold and its narration segment disagree, the voiceover lands on the wrong slide - keep them as one versioned pair, and re-derive HOLDS whenever the script changes.

## Two parts around the demo

Record the deck as two takes, stitched around the demo film:

- **Part A**: slides 1 -> demo slot. The last beat PAUSES on the demo-slot slide (~4s) and never plays the embed.
- **Part B**: fresh-load the deck at `#<demo_slot+1>` (hash deep link) so the first post-demo slide plays its entry animation on camera, then run to the Close.

Fresh-loading matters: continuing a single take across the demo boundary either shows the embed or shows a stale slide with spent animations.

## The deck driver

In the harness template, the BEATS list becomes: first beat `{"js": None, "hold": HOLDS[0]}` (the fresh-loaded first slide), then one beat per remaining slide:

```python
BEATS = [{"label": "SLIDE_1", "js": None, "hold": HOLDS[0]}] + [
    {"label": f"SLIDE_{i+2}",
     "js": "document.getElementById('next').click()",
     "hold": h}
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
