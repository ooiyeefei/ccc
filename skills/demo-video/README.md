# demo-video

Record a **crisp, high-resolution product demo video** by driving the real app with a browser agent: approved storyboard -> staged app -> smoke take -> Xvfb framebuffer recording -> MP4-derived timestamps -> narration synced to the frames.

Why it exists: the obvious tools produce bad footage at high resolution. Playwright's `recordVideo` captures at CSS-viewport size (device-scale-factor adds zero pixels) with a ~0.6 Mbps encoder that macroblocks anything above 1080p. The proven fix is capturing a real Xvfb framebuffer (2560x1600) while Chrome renders at DSF 2 over a 1280x800 viewport, encoded with CRF via ffmpeg x11grab.

## The recording contract

Three rules about what goes on camera, and three blocking gates that enforce them. They exist because each is what an agent under time pressure drops first - so the harness itself refuses to proceed when 1 or 2 are unmet:

1. **Film the product, not a poster** - real browser state changing because the driver acted. No title cards, mocked screens, or captions unless the user asked for that beat - never propose one.
2. **Whole journey, not just the money shot** - entry -> setup -> core loop -> payoff.
3. **Every claim gets a frame** - especially agent actions, which are invisible unless the app renders the evidence. No frame, no claim.
4. **Gate 1: storyboard approved** before any capture (`phase | screen | action | proof | narration | duration`). The harness requires `--storyboard <path>`.
5. **Gate 2: smoke take inspected** before the full capture. The harness refuses a full take until one exists.
6. **Gate 3: timestamps derived from the delivered MP4** - never from planned waits. Cue (`t_video`) for narration, proof (`t_proof`) for verification.

Plus the quality rules: **real frames not upscaled**, and **narrate to the frame** (via `pitch-craft`).

Also the home of the recording harness that `pitch-deck` reuses for slide walkthroughs.

## Use this, not that

- **Use demo-video when the deliverable is FOOTAGE of the product** - a demo film, or fixing a pixelated recording.
- The words over the footage -> `pitch-craft`. A slide-walkthrough video -> `pitch-deck` (which reuses this skill's harness). The whole pitch -> `pitch-package`.
- Part of the pitch suite: decision guide in [skills/README.md](../README.md#the-pitch-suite---when-to-use-what).

## Structure

- `SKILL.md` - the recording contract and the gated workflow
- `references/storyboard.md` - storyboard format, journey coverage, claim-to-frame audit, approval gate
- `references/recording.md` - the framebuffer recipe and why each flag exists; smoke-take and timestamp-verification checklists
- `references/driving.md` - CDP driving: clicks, variable-latency waits, milestone marking
- `scripts/record_template.py` - the harness (edit CONFIG + BEATS, plumbing is done); `--smoke` and `--verify` modes

## Requirements

Linux with `Xvfb`, `ffmpeg`, Chrome/Chromium, and `pip install websockets`. macOS: capture the retina display with `ffmpeg -f avfoundation` instead; same principles.
