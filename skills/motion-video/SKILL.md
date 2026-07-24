---
name: motion-video
description: Build a marketing or explainer video that is mostly RENDERED scenes - motion graphics, mocked or rebuilt product UI, data-driven animated charts, brand-matched title design - authored in Remotion and stitched around one real product-capture beat. Use whenever the user wants a marketing video, a brand film, a launch or website hero video, an animated explainer, motion graphics, a video with mocked/idealised UI or animated charts, or says "build the video in Remotion", or needs one film cut to the aspect ratios and UI safe zones each platform wants (Instagram Reels, TikTok, YouTube Shorts, 4:5 feed) for paid ads or organic posts. This is the marketing branch's build engine, the counterpart to demo-video (which films the REAL product to prove it). Not for - a screen recording or product walkthrough of the real app (demo-video), a pitch deck (pitch-deck), a live pitch or its script (pitch-package, pitch-craft), or editing footage that already exists.
---

# Motion video - render the story, prove it once

A demo-video films the real product to **prove** it. A motion video **renders** the story to
**sell or explain** it. The mix is the opposite: a marketing film is mostly rendered scenes with
**one** real capture stitched in as proof. Get that inversion wrong and you have either a
screen-recording that bores or a cartoon that convinces no one.

## The contract

Four rules. They are the ones an agent under time pressure abandons first, which is why they are
not optional. Repeat the bolded phrase in your reasoning as you work; it is the behaviour.

1. **Wrapper, not proof.** Rendered and mocked scenes are the WRAPPER; the ONE real capture (from
   `demo-video`) is the PROOF. Never pass a rendered UI off as a live screen recording. When a
   figure is illustrative, say so on screen. This is `demo-video`'s "annotate never substitute"
   ethic moved up one level: mocks are legitimate in the wrapper, banned inside the proof beat.

2. **Frame-clock, not wall-clock.** Every animation is driven by Remotion's `useCurrentFrame()`.
   `framer-motion`, CSS transitions, `requestAnimationFrame`, `setTimeout`, `Date.now()` all render
   FROZEN, because Remotion seeks a synthetic clock frame by frame. This is the single biggest
   surprise; internalise it before you write a scene. (`references/remotion.md`.)

3. **Brand-match verbatim.** Pull the real font, logo mark, wordmark, and palette from the
   product's OWN repo and use them exactly. An approximated brand reads as fake and undoes the
   film. (`references/brand-match.md`.)

4. **Figures reconcile.** A mocked ledger still balances; a mocked chart's bars still sum to its
   headline. No fabricated numbers, no prices the brand keeps private, no success rates or
   compliance claims, and nothing that reveals HOW a sensitive capability works if the brand does
   not want it shown. Marketing gets a warmer voice, never a pass on truth.

## Steps

### 0. Preflight
Node + `ffmpeg` present. Locate the product's repo (you need its real brand assets) and confirm it
runs with demo data (you need one real beat). Remotion is free for teams of 3 or fewer; 4+ needs a
paid licence - flag it before promising a Remotion build.

### 1. Storyboard - GATE, same as demo-video
One row per scene: `scene | shows | real or rendered | motion | narration | dur`. Mark every scene
real or rendered, and name the ONE real proof beat. **Show it and stop** until the user approves.
This is the cheapest point to change the film; after scenes are rendered every edit re-renders and
re-times. (Storyboard format: `demo-video/references/storyboard.md`, adapted - the "proof" column
becomes "real or rendered".)

### 1.5 Target formats - GATE with the storyboard
A film rarely ships as one file: the same story goes to 16:9 YouTube, 9:16 TikTok/Reels/Shorts, and
4:5 feed. Ask which platforms and placements it ships to (a multi-select), collapse them to the
minimal master-ratio set - almost always a subset of {9:16, 16:9, 4:5, 1:1} - and note each one's UI
safe zone. Two rules the agent under pressure breaks: **reframe, never crop the extremes** (16:9 to
9:16 discards ~56% of the frame and must be re-authored, not cropped), and **compose inside the safe
box** (keep every title and logo clear of the caption bar, action rail, and CTA button the platform
paints over the video). Decide this BEFORE building scenes - it sets how each scene lays out in
vertical vs landscape. Remotion makes the cut cheap: one component set renders at any width/height via
`useVideoConfig()`. (`references/platform-formats.md`.)

### 2. Brand-match
Find the real font (next/font or tailwind config), logo (SVG/component), wordmark, and palette in
the product repo. Wire them into the Remotion project. Do this FIRST - it changes every scene.
(`references/brand-match.md`.)

### 3. Build the rendered scenes
An isolated Remotion project, one component per scene, everything on `useCurrentFrame()`. If the film
targets more than one aspect ratio, branch each scene's layout on orientation (`useVideoConfig()`) and
keep content inside the safe box - do not author for 16:9 and crop to 9:16 later. Setup, the
frame-clock discipline, fonts, and rendering are in `references/remotion.md`; the format matrix and
safe zones are in `references/platform-formats.md`.

**Start from the carried motion kit, not from scratch.** `assets/motion/` holds the shotcraft
pieces every film reuses, already brand-parameterised and format-aware: `PageCam` (2.5D camera over
a real screenshot), `DigitRoll` (a number landing), `FlashCut` (a hard tonal break), `Caption`,
`VerticalTicker` (volume), and deterministic `helpers/`. Copy what the storyboard needs into the
project's `src/motion/` and pass the brand tokens in. Read `assets/motion/README.md` first - it says
when each one earns its place, and which two upstream defaults (hardcoded 1920x1080 framing, and the
Ink Press amber) are deliberately parameterised because a naive re-copy breaks rules 1.5 and 3.

Reach past the kit for anything it does not cover: the remaining ~100 shot cards, the preview
gallery, and the SFX/BGM set stay REFERRED, shopped per beat from the installed `video-shotcraft`
skill per `references/shotcraft-bridge.md`. Our guardrails and three ratios wrap all of it.
Rendered scenes only - the real-proof beat stays `demo-video`, which shotcraft cannot record.

A beat that shows a figure should usually ROLL it (`DigitRoll`), not fade it in: a rolling number
reads as the system computing, a fading number reads as a caption. This is the most common miss.

### 4. Capture the ONE real beat
The proof: the real product doing the real thing, captured crisply with the **demo-video** skill's
harness. Do not rebuild the product's own screen in Remotion when the real one can be filmed - that
is the wrapper-not-proof line.

### 5. Stitch
Rendered scenes + the real beat, crossfaded with ffmpeg. `scripts/stitch.mjs` is the reusable
`xfade` chain; edit its clip list. Derive final timestamps from the DELIVERED mp4, never from
planned scene lengths (same Gate-3 rule as demo-video). Assembly variants and the ffmpeg recipe:
`pitch-package/references/stitching.md`.

### 6. Narrate - optional
A marketing film often ships silent (motion + on-screen text, autoplay-muted). If it needs a
voiceover, write it in the **pitch-craft** marketing register, timed to the encoded mp4.

### 7. Verify
Watch every scene as an image. Figures reconcile. Brand matches the real app. No scene overclaims
or leaks. The real beat is unmistakably the real product. Render each selected format
(`scripts/render-formats.mjs`) and watch it at its TRUE ratio - a layout that reads in 16:9 can
collapse in 9:16, and nothing critical may sit inside a platform safe zone.

## References
- `references/remotion.md` - the Remotion setup that works: isolated project, the frame-clock
  discipline, brand fonts, rendering. Read before writing a scene.
- `references/brand-match.md` - how to find and wire the product's real font, logo, and palette.
- `scripts/stitch.mjs` - the ffmpeg `xfade` stitcher for rendered scenes + the real beat.
- `references/platform-formats.md` - target-platform picker, the minimal master-ratio set, per-placement
  UI safe zones, the export/codec rule, and the Remotion multi-format recipe. Read when the film ships
  to more than one placement (any ad or multi-channel post).
- `assets/motion/` - the CARRIED motion kit: PageCam, DigitRoll, FlashCut, Caption, VerticalTicker,
  and deterministic helpers, brand-parameterised and format-aware, with `LICENSE.upstream`. Copy into
  the film's project. Read its README before building a scene.
- `references/shotcraft-bridge.md` - how to leverage the rest of the external `video-shotcraft`
  motion/sound library (what is carried vs referred, the RENDERED-vs-RECORDED boundary, the
  card-to-beat map, and the guardrail overlay). Read when a scene needs motion the kit does not carry.
- `scripts/render-formats.mjs` - render every chosen ratio from one Remotion project (`Film-<id>` compositions).
- Shared engines this skill leans on, never duplicates: **demo-video** (the real proof beat),
  **pitch-craft** (narration), **pitch-package/references/stitching.md** (assembly).
