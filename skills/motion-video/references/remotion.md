# Remotion - the setup that works

Read before writing a scene. Every item here was a real defect on a shipped film.

## Isolated project

Remotion lives in its OWN folder with its OWN `package.json`, never merged into the product's dep
tree. It pulls in React + a compositor and would fight the app's versions.

```
video/
  package.json        # remotion, @remotion/cli, react, react-dom, @remotion/google-fonts
  remotion.config.ts  # Config.setVideoImageFormat('jpeg'); Config.setOverwriteOutput(true)
  tsconfig.json       # jsx: react-jsx, moduleResolution: bundler, noEmit
  src/
    index.ts          # registerRoot(RemotionRoot)
    Root.tsx          # <Composition> per scene
    theme.ts          # the REAL brand tokens (see brand-match.md)
    scenes/*.tsx
```

Render: `remotion render <CompId> out/<name>.mp4 --crf 16`. Scenes are vector-crisp, so CRF 16 is
cheap and sharp.

## Frame-clock, not wall-clock - the rule that surprises everyone

Remotion renders each frame by seeking a synthetic clock. **Anything driven by real time renders
frozen or wrong:** `framer-motion`, CSS `transition`/`animation`, `requestAnimationFrame`,
`setTimeout`, `Date.now()`, `new Date()`. There is no framer-motion integration and there will not
be one.

Everything animates off `useCurrentFrame()`:

```tsx
const frame = useCurrentFrame();
const { fps } = useVideoConfig();
const s = spring({ frame: frame - startAt, fps, config: { damping: 200 }, durationInFrames: 16 });
// opacity: s, transform: `translateY(${interpolate(s, [0, 1], [16, 0])}px)`
```

Stagger by subtracting a per-item offset from `frame`. Count a number up with
`interpolate(spring, [0,1], [0, value])`. A "typing" or "building" feel is just later `startAt`
values, never a timer.

If you catch yourself importing `framer-motion` or writing a CSS `transition` for motion, stop -
it will look frozen in the render even though it animates in the browser preview.

## Brand fonts

Use `@remotion/google-fonts/<Family>` when the brand font is on Google Fonts (Geist, Inter, etc.).
Constrain weights and subset or a single render fires 90+ font requests:

```ts
import { loadFont } from '@remotion/google-fonts/Geist';
const geist = loadFont('normal', { weights: ['400','500','600','700'], subsets: ['latin'] });
// theme.sans = geist.fontFamily
```

For a non-Google brand font, embed the woff2 as a data-URI `@font-face` and gate the composition on
`document.fonts.ready` via `delayRender`/`continueRender`. Never link a CDN font URL - the render
runner may not fetch it, and it fails silently to a system fallback.

## Colour and motion discipline

- One accent that means one thing (e.g. green = a positive outcome only). If everything is the
  accent, the accent stops meaning anything.
- Mocked figures reconcile: a chart's bars sum to its headline; a ledger balances. Verify with a
  one-line node script before rendering, not by eye.
- Keep motion legible: rise + fade a bubble, grow a bar, count a number. Skip motion that does not
  carry meaning; too much reads as "AI made this".

## Rendering the localized/variant cuts

Two cuts that share most footage (e.g. MY and SG) are why code-defined video pays off: render the
same composition twice with different `inputProps`, scenes read copy from a passed map, and the
shared portion is guaranteed identical. In an NLE those are two timelines that drift the first time
someone fixes a typo in one.
