# Motion - camera move, not a cut

A capture can be 100% genuine browser video and still read as a slideshow. `scrollIntoView()` teleports; setting `.value` inserts a whole string in one frame. Both endpoints are true. The motion between them is what a viewer reads as "a person did this", and without it the film looks like stills someone narrated over.

**Camera move, not a cut** is the rule. When the frame needs to go somewhere, move there on camera. Reach for a cut only when the product itself cuts.

The primitives live in `../scripts/cinema.js`, injected into every document by the harness as `window.__cine`. Every function returns a Promise; beats await them.

## The line: annotate, never substitute

Annotation draws **over** live product state. It is standard practice here, not an exception - a film that explains itself on mute is doing its job.

The test, applied to any overlay:

> Remove the overlay. Does the frame still show the product doing the thing?

**Yes** - it is annotation. A callout ring, the drawn cursor, a spotlight, the terminal panel. Use them freely.

**No** - it is a poster, and contract rule 1 still bans it. A title card, a slide interstitial, a mocked screen, a static hero image. The overlay is not adding explanation, it is standing in for state the product never showed.

Two cases that look like annotation and are not:

- A terminal panel typing output the command never printed. `terminal(cmd, lines)` requires `lines` to be output the command actually produced. Plausible-looking output is fabricated evidence.
- A callout asserting something not on screen ("it checked 42 sources") when no frame shows the sources. That is narration wearing a chip. It fails the claim-to-frame audit in `storyboard.md` the same way a narrated overclaim does.

## The primitives

| Call | What it does | Reach for it when |
|---|---|---|
| `glide(sel)` | Eased scroll to an element | Any time the frame must travel. The highest-value primitive here - it is what replaces a jump cut with a camera move. |
| `cursorTo(x,y)` / `cursorToEl(sel)` | Moves a drawn cursor | Showing where attention goes. The capture runs `-draw_mouse 0`, so the OS pointer is deliberately absent. |
| `ripple(x,y)` | Click flourish | Paired with a real click, so the frame shows the press. |
| `callout(sel, text)` | Labelled chip plus a ring on the region | Naming what a viewer is looking at. Flips side automatically so the label never clips off-frame. |
| `spotlight(sel)` | Lifts a clone into a centred card, dims the rest | A diagram or table sized for a document column is unreadable at video scale. |
| `terminal(cmd, lines)` | Floating terminal panel | Products whose command surface is part of the story, without cutting to a separate recording. |
| `selectText(sel)` | Sweeps a selection and fires `mouseup` | Selection-triggered UI that needs the event, not just a Range. |
| `fade(dir)` | Frame to a colour and back | Making a navigation read as a deliberate edit. |

Defaults in `cinema.js` were arrived at by fixing real defects. Two worth knowing before you change them: `spotlight` clones rather than transforms, because transforming the original grows it over its siblings and reads as broken layout; `callout` flips to whichever side has room, because a label clipped at the frame edge is worse than no label.

## Wiring motion into beats

```python
BEATS = [
    {"label": "OPEN",    "motion": "__cine.glide('#queue')",               "hold": 5},
    {"label": "FILTER",  "type": {"selector": "#vendor", "text": "Acme"},  "hold": 4},
    {"label": "RUN",     "click": "#run-btn",
     "ready": "document.body.dataset.done==='1'",                          "hold": 6},
    {"label": "EXPLAIN", "motion": "__cine.callout('#done','Two duplicates, same PO')",
     "hold": 1},
]
```

- **`motion`** runs first and is awaited, so the narration cue lands when movement starts.
- **`click`** and **`type`** drive the drawn cursor to the target, then dispatch **real CDP input events**. The app receives a genuine click and genuine keystrokes; `cinema.js` only supplies the visual half. Never swap these for `.click()` or `.value =` - a product with selection or focus behaviour can tell the difference, and the frame loses the movement.
- **`js`** remains the escape hatch when none of the above fits.

An annotation is usually its own beat: it has a claim, a duration, and a narration segment, which is exactly what a beat is. Set the dwell inside the call (`callout(..., {hold: 2600})`) and keep the beat's `hold` short, since the awaited call already consumed that time.

## Proof frames on annotation beats

`callout`, `spotlight`, and `terminal` fade themselves out before the awaited call returns. Sampling the proof frame after the motion would catch an empty screen, so the harness samples the **midpoint** of the motion for beats whose payload is the motion itself (motion present, no `click` / `type` / `js` / `ready`). Beats that act still sample after the result renders, as before.

You do not configure this. It matters when you read a sidecar and see `t_proof` sitting inside a beat rather than at its end.

## What this costs

Motion consumes real seconds. A `glide` is 1.4s, a `callout` around 3.1s including fade. Budget them in the storyboard's `dur` column or the film runs long, and re-check the total against the pitch budget before the Gate 1 round-trip.

Measured on a shipped demo, adding these primitives to an unchanged journey moved it from 0.4 to 4.6 moving frames per second and cut the longest frozen stretch from 25s to 2.4s. A short take recorded while building this scored 5.1 moving frames per second with 80% of frames static, which is the range to expect: most frames hold, and the eye reads the film as continuous anyway.
