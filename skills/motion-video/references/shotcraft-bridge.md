# Leveraging video-shotcraft (the motion + sound vocabulary)

`video-shotcraft` (https://github.com/Vincentwei1021/video-shotcraft, Apache-2.0) is an
external motion-design library: 106 tuned shot-recipe cards, a 2.5D page camera (PageCam),
a SFX + BGM set with a beat-sync method, and a browsable preview gallery. It is the
**palette**. This skill (`motion-video`) is the **director**: film structure, brand-match,
truth guardrails, the three ratios, and the one real-proof beat stay here. shotcraft
composes UNDER those layers; it never wraps them.

Install if absent on the machine:

```
git clone https://github.com/Vincentwei1021/video-shotcraft.git ~/.claude/skills/video-shotcraft
# or: npx skills add Vincentwei1021/video-shotcraft
```

## The one boundary: RENDERED vs RECORDED

Draw the line here, not by video type. Every film is a blend of two scene kinds:

- **RENDERED** (motion graphics, mocked UI, animated charts, titles, brand/abstract beats,
  a camera glide over a screenshot): shop shotcraft freely.
- **RECORDED** (the real app being operated): `demo-video` ONLY. shotcraft captures STILL
  screenshots (`page.screenshot` + element cutouts) and glides a fake camera over them
  (PageCam renders `<Img staticFile>`); zero of its 152 demos touch live video. It CANNOT
  record interaction.

Never point shotcraft at a tutorial, walkthrough, how-to, or any film whose job is showing
the real product being used. That is `demo-video`'s live recording + timestamp-synced
narration, and it is not replaced or degraded. (Standing owner rule, 2026-07-23.)

## ABSORB - DONE, the kit is carried in this skill

The pieces every film reuses are no longer a shopping list: they live in
**`../assets/motion/`**, already brand-parameterised and format-aware, with the upstream
Apache-2.0 licence beside them. Copy them from there into the film's `src/motion/`, not from
the upstream repo, or you re-import two defects (see below). Read
`../assets/motion/README.md` for when each earns its place.

Carried: **PageCam**, **DigitRoll**, **FlashCut**, **Caption**, **VerticalTicker**, and
`helpers/{motion,rand,shake}`. All pure Remotion, no new deps.

Two upstream defaults are deliberately changed in the carried copies, because a naive copy
violates this skill's own rules:

- `PageCam` hardcodes a 1920x1080 viewport (960/540 centres, 1920 page width) and so
  mis-frames every vertical cut. Ours derives the centre from `useVideoConfig()` and takes
  `pageW` as a prop. (Rule 1.5, reframe never crop.)
- `DigitRoll`, `Caption`, `FlashCut`, and `PageCam`'s backdrop bake in the Ink Press amber
  `oklch(52% 0.115 65)` / cream `#faf7f2`. Ours default to `currentColor` and transparent.
  (Rule 3, brand-match verbatim.)

Re-apply both if you ever re-absorb from upstream.

Still NOT carried, pull deliberately if a shot needs it: `FlatPanel` and `helpers/camera`
(optional WebGL orbit) need `three` + `@react-three/fiber` + `@remotion/three`.

A **BGM track and SFX bed** stay per-film: they are a rights decision, not a component (see
Sound below). Standardise the film's signature easing + recurring camera grammar in its own
project; that is where cross-video consistency for a given brand comes from.

## REFER - shop the long tail per film (do not fork)

The remaining ~100 cards + the gallery stay a reference; the kit above is the part that
repeats. Per beat:

1. Pick a move from the gallery:
   `cd ~/.claude/skills/video-shotcraft/gallery && python3 -m http.server 4178`.
2. Read the card in full AND its `demos/<card>/` implementation before using it. The card
   gives semantics; the demo holds the tuned params (easing, timing ratios, known-pitfall
   workarounds). Writing from the card name alone throws away all the tuning.
3. Adapt freely, but never downgrade a param the card marks "known pitfall". Quality only rises.

Starter card-to-beat map (Groot films):

| Beat | Cards to reach for |
|------|--------------------|
| Cold open / the enemy | glitch-text-intro, crash-zoom-punch, speed-ramp-freeze |
| Duplicate / fraud catch (hero) | crash-zoom-punch (hard-stop landing), impact-feedback |
| Agent / Autopilot reveal | slam-entrance-moves, type-assembly-moves, command-palette-summon |
| Data / documents flowing | montage-rhythm-moves, beat-cut-moves, card-flock-tumble |
| A number landing | odometer-digit-roll / DigitRoll |
| Persona / lane cards | panel-grid-moves, segmented-thumb-hero |
| Close / brand lockup | ui-to-brand-morph, brand-frame-snap |

## RESTRUCTURE - the wrap that never changes

shotcraft has NO truth guardrail and ships a single 1920x1080 template. Our layers ride on
top, always:

- **Guardrail overlay**: figures reconcile; no prices, success rates, or
  how-a-sensitive-capability-works on screen; no real customer data (the demo tenant holds
  real PII); wrapper-not-proof (a rendered scene is never passed off as live);
  annotate-never-substitute.
- **Three ratios**: keep our format layer (`fmtOf` / `safeBand` / `panelSize`, see
  `references/platform-formats.md`). Port a shot's motion INTO our multi-ratio scene; do not
  adopt the single-ratio Ink Press template wholesale.
- The **real-proof beat** still comes from `demo-video`, not a dressed-up screenshot.

## Sound

- SFX + BGM under `assets/audio/` are Mixkit free-commercial (no attribution) per
  `assets/audio/ATTRIBUTION.md`. Three files are flagged "source unknown, verify before
  commercial use": `pop.mp3`, `typewriter.mp3`, `bgm-tech-house.mp3`. Verify those before
  shipping (owner rule: no music without clear rights).
- Beat-sync: if a BGM has a strong pulse, analyse it first and write the timeline in beats
  (`references/music-beat-sync.md` inside the shotcraft repo), then re-check cut error from
  the rendered audio.

## Post-production camera on RECORDED footage

You may apply shotcraft's easing/timing feel (dolly, zoom-to-callout, slide, speed-ramp) to a
recorded MP4 in Remotion. Two hard rules, both already ours:

- Pixels stay the real product. Zoom / pan / annotate is fine; compositing fake UI is banned.
- Any time-warp shifts every narration cue: re-derive timestamps and re-sync the script after
  (`demo-video` Gate 3).

Do NOT push this on tutorials; the in-capture DOM motion (`demo-video` `cinema.js`) is already
the right approach there.
