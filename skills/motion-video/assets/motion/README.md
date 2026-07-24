# The motion kit — carried, brand-matched, format-aware

These are the shotcraft pieces this skill **carries** rather than describes. Copy the ones a
film needs into its Remotion project (`src/motion/`) and use them directly. They are
Apache-2.0 from [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft);
`LICENSE.upstream` travels with them.

Copy the component in and modify it — that is upstream's own rule and ours. Do not add the
library as a dependency.

## What is here

| Component | Use it when | Deps |
|---|---|---|
| `PageCam` | Any shot over a real product screenshot. A slow push turns a flat capture into a scene. The single biggest visual upgrade available. | none |
| `DigitRoll` | A NUMBER is the point of the shot: a total, a count, a balance, a percentage. | none |
| `FlashCut` | A HARD tonal break needs impact (the enemy giving way to the product). Not between two calm beats. | none |
| `Caption` | The film needs to talk in its own voice, distinct from a lower-third that labels the screen. | none |
| `VerticalTicker` | A wall of many items scrolling (a catalog, a document flood, logos). Sells VOLUME. | none |
| `helpers/motion` | Derive velocity from a trajectory, drive stretch/blur/shake from speed, build lag/follow-through, closed-form settle. | none |
| `helpers/rand` | Deterministic PRNG. Any randomness in a film MUST be seeded or frames disagree. | none |
| `helpers/shake` | Deterministic handheld camera noise. | none |

Everything here is pure Remotion. Nothing needs `three`. If a shot genuinely needs a WebGL
orbit, that is `FlatPanel` + `helpers/camera` upstream, and it pulls in three
`@react-three` packages — decide that deliberately.

## What we changed, and why it must stay changed

Two of this skill's rules are violated by a naive copy, so the carried versions differ:

1. **Format-aware** (rule 1.5, reframe never crop). Upstream `PageCam` hardcodes a 1920x1080
   viewport: `960`/`540` centres and a `1920` page width. It silently mis-frames in 9:16 and
   4:5. Ours derives the centre from `useVideoConfig()` and takes `pageW` as a prop, so one
   component set renders every ratio. `fitWidthZoom(vpW, pageW)` is exported for the common
   vertical reframe: the landscape page becomes a band across the middle, and the freed space
   above and below carries the title and CTA.

2. **Brand-neutral** (rule 3, brand-match verbatim). Upstream bakes the Ink Press template's
   amber `oklch(52% 0.115 65)` into `DigitRoll` and `Caption`, its warm white into `FlashCut`,
   and its cream `#faf7f2` into `PageCam`'s backdrop. Shipping any of those paints a foreign
   brand into another product's film. All are props now, defaulting to `currentColor` or
   transparent so they inherit the product's real palette.

If you re-absorb from upstream later, re-apply both. They are not preferences.

## Using it

```tsx
// One beat: a real screenshot, a slow push, the figure rolling up.
<AbsoluteFill style={{ backgroundColor: T.paper }}>
  <PageCam
    src="textures/live/invoices.png"
    pageH={1080}
    keys={[
      { frame: 0,   cx: 960, cy: 470, zoom: 1.0 },
      { frame: 165, cx: 980, cy: 520, zoom: 1.18 },
    ]}
  />
  <DigitRoll value="RM6,821.00" delay={24} fontSize={64} color={T.ink} fontFamily={T.mono} />
</AbsoluteFill>
```

Two things that bite:

- **`keys` are absolute comp frames.** Inside a `<Sequence>` or `TransitionSeries`,
  `useCurrentFrame()` is rebased to 0, so the keys re-align to the scene. That is usually what
  you want. When it is not, pass the restored absolute frame via the `frame` prop.
- **`children` ride in PAGE space** (they track the camera, good for pinning a callout to a
  row); anything that must stay crisp and still belongs in SCREEN space, as a sibling AFTER
  `PageCam`. Deep zooms soften a 1x capture, so put the sharp focal detail in a screen-space
  overlay and let the screenshot be the proof behind it.

## The long tail stays referred

These are the pieces that repeat across films. The other ~100 shot cards, the preview gallery,
and the SFX/BGM set are shopped per beat from the installed shotcraft skill and are NOT copied
here. See `../../references/shotcraft-bridge.md`.
