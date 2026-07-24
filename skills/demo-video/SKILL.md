---
name: demo-video
description: Record a crisp, high-resolution product demo video by driving the real app with a browser agent - the full pipeline from storyboard approval to staged app, smoke take, Xvfb framebuffer recording, MP4-derived timestamps, and a narration script synced to the frames. Use whenever the user wants a demo video, a product walkthrough recording, a screen capture of an app for a hackathon / launch / submission, or complains that a recording came out pixelated, blurry, blocky or soft, showed title cards instead of the product, jumped straight to the final feature, had narration landing on the wrong frame, or looks static / like a slideshow when the capture is genuine. Also the home of the recording harness that pitch-deck reuses for slide walkthroughs. Not for - live pitching or deck building (pitch-deck, pitch-package), one-off screenshots, or editing footage that already exists.
---

# Demo Video - film the real product, crisply

A demo is an argument: every beat on camera proves a claim, and the narration is written **to the frame** - describing what is actually on screen at that second.

> **Boundary - this recording has no substitute.** The `video-shotcraft` motion library captures STILL screenshots and glides a fake camera over them; it CANNOT record interaction. Never let it stand in for a tutorial, walkthrough, or any real-product film. It decorates RENDERED scenes in `motion-video`; the live recording, the DOM motion, and the timestamp-synced script stay here, always. (Standing owner rule, 2026-07-23; see `motion-video/references/shotcraft-bridge.md`.)

## The recording contract

This fires **automatically** on every demo film, whether or not the user asks for it. These are the rules an agent under time pressure skips first, which is exactly why they are not optional. Rules 1-4: `references/storyboard.md`. Rules 5-6: `references/recording.md`.

1. **Film the product, not a poster - annotate, never substitute.** Every frame is real browser state from the running app, changing because the driver acted on it.

   Annotation drawn *over* live state is **standard practice**: callouts, the drawn cursor, spotlight, the terminal panel. A film that explains itself on mute is doing its job. The test is whether the overlay is load-bearing: **remove it, and does the frame still show the product doing the thing?** If yes it is annotation, use it freely. If no it is a poster - a title card, slide interstitial, mocked screen, static hero image - and it stays banned.

   If a beat can't be staged, cut the beat or fix the app. Never substitute a picture of the claim for the claim. (Slides are legitimate in `pitch-deck`'s deck take, stitched *around* the demo film, never inside it.) Motion and annotation: `references/motion.md`.

2. **Show the whole journey, not just the money shot.** The film covers entry -> setup -> the core loop -> the payoff. A viewer who has never seen the product must be able to follow how a real user gets from opening it to the result. Opening on the final feature reads as a mockup and answers none of "what is this, who uses it, how do you get there".

3. **Every claim gets a frame.** The storyboard runs both directions: each beat names what it proves, *and* each claim the narration will make names the beat that shows it. This binds hardest on agent actions - "the agent searched", "it updated memory", "it chose the cheaper route" all need visible on-screen evidence (the tool log, the memory panel, the route badge). A claim with no frame is cut from the narration or earns a beat that shows it. Invisible work is not proof.

4. **Storyboard approved before capture** - Gate 1 below. Blocking.

5. **Smoke take inspected before the full capture** - Gate 2 below. Blocking: any failed check means fix the staging and re-smoke, never start the full capture on a known-bad frame.

6. **Timestamps derived from the delivered MP4** - Gate 3 below. Never from planned waits, never from the storyboard's estimated holds.

## Steps

### 0. Preflight

Check the machine can do this before promising it: `ffmpeg` and `Xvfb` installed (`apt-get install -y xvfb` on Linux; this recipe is Linux-first - on macOS capture the retina display with `ffmpeg -f avfoundation` or the built-in screen recorder, same principles: physical pixels, controlled bitrate). Confirm the app runs with demo data and demo credentials, and that credentials stay OUT of the repo (scratchpad only).

### 1. Storyboard - **GATE 1: approval before any capture**

Write the visual storyboard before recording anything. One row per beat:

`phase | screen | action | proof | narration | duration`

Read `references/storyboard.md` for the format, the journey-coverage checklist, and the claim-to-frame audit. Then **show it to the user and stop.** Do not stage, do not smoke-test, do not record until they approve or amend it.

A blanket "just make it, I trust you" issued *before* the storyboard existed is not approval of it - the user has not seen the plan yet. Show the table and wait.

The harness enforces this too: a full take requires `--storyboard <path>`, and stamps its hash into the sidecar.

This gate is not politeness - it is the cheapest point to change the film. After capture, every edit re-shoots footage *and* re-syncs narration against new timestamps.

### 2. Stage the app

Deterministic demo data, seeded to make the beats true. Log in OFF camera. Kill anything that can interrupt the frame: notifications, password-manager bubbles (pre-write Chrome preferences - see recording.md), first-run dialogs. Never trigger JS alerts mid-take; they freeze the driver.

### 3. Smoke take - **GATE 2: inspect before the full capture**

Run `record_template.py <name> --smoke`. It records through the first beat that actually *drives* something - rendering beat 1 alone cannot catch a dead selector, which is half of what this gate is for - then extracts frames and prints a contact sheet. **Read it as an image.**

Checking: right app, right screen, right framing, text crisp at full scale, no cursor, no dialog or bubble in frame, chrome hidden, seeded data actually present. Full checklist in `references/recording.md`.

**Any unchecked box means the take is not ready:** fix the staging and re-smoke. Never start the full capture on a known-bad frame - that is the whole point of the gate.

A smoke take costs ~30 seconds and catches the failures that otherwise surface *after* a full take plus a written narration: wrong scale factor, unstaged data, a dead selector, a login bubble covering the money shot.

The harness enforces this: a full take refuses to run until a smoke take exists for that name. `--no-smoke` overrides it and is stamped into the sidecar - use it only when this app was already captured at this config.

### 4. Full take - real frames, not upscaled

Xvfb at physical 2560x1600, Chrome in app mode with `--force-device-scale-factor=2` over a 1280x800 CSS viewport, ffmpeg x11grab with `-draw_mouse 0` at CRF 16-18, driven over CDP.

Read `references/recording.md` before changing ANY parameter - every flag in that recipe exists because the obvious capture paths produce macroblocked or soft footage at high resolution.

**Camera move, not a cut.** Genuine footage still reads as a slideshow when the driver teleports: `scrollIntoView()` jumps and setting `.value` inserts a whole string in one frame. Beats therefore carry a `motion` field (an awaited camera move or annotation) and use `click` / `type`, which drive a drawn cursor to the target and then dispatch real CDP input events, so the app receives genuine events while the frame shows the movement. Motion costs real seconds, so budget it in the storyboard's `dur` column. Primitives, their costs, the annotate-never-substitute test, and proof-frame timing: `references/motion.md`.

### 5. Verify the film and derive timestamps - **GATE 3: the MP4 is the arbiter, not the clock**

The harness records wall-clock marks during the drive. Those are a *hypothesis*; the delivered file is the fact. (Why they drift, and the reconciliation arithmetic, are in `references/recording.md`.)

A full take already reconciles and extracts on the way out - read the contact sheet it printed. Use `record_template.py <name> --verify` to re-check, or after a re-encode. (After a *trim*, prefer re-cutting from the original: the reconcile assumes missing time is at the front, so a tail cut shifts every mark early - the harness flags it, but flagged is not fixed.) (Manual `ffprobe`/`ffmpeg -ss` procedure in `references/recording.md`, including what to do for footage with no sidecar.)

Extract a frame per milestone and **look at every one**. Each frame must show the screen its beat claims.

Each beat gets **two** timestamps, and using the wrong one breaks the gate: `t_video` is the narration cue (beat start), `t_proof` is where the claim is actually visible (after the async result renders). Verify against `t_proof`; sync narration to `t_video`. On a live-backend beat these are seconds apart, and checking at the cue fails a correct take.

Ship nothing whose frames you have not seen. If a proof frame shows the wrong screen, the timestamp is wrong - fix it before narration, not after voicing.

### 6. Narrate to the frame

Hand the **verified** milestone JSON and the storyboard to the **pitch-craft** skill. The narration describes what IS on screen at each timestamp, in the recorded register, chunked to the milestone windows. Every claim traces to a beat per contract rule 3.

### 7. Re-records

A new take shifts every milestone (live backends vary by seconds). Re-verify against the new MP4, then re-align the narration per pitch-craft's `timing.md` re-sync procedure. Treat take + script as one versioned pair.

**If the beat list changed, Gate 1 reopens.** Dropping beats that wouldn't stage, merging two, or reordering the journey all change the film the user approved - re-show the storyboard and get sign-off before re-shooting. Silently shipping four of six approved beats is the most likely way this pipeline fails in practice, because unstageable beats only reveal themselves once you try.

## References

- `references/motion.md` - the motion and annotation layer: primitives, the substitution test, beat wiring, what motion costs. Read before writing beats that move.
- `references/storyboard.md` - the storyboard format, journey coverage, the claim-to-frame audit, and how to run the approval gate. Read before writing the storyboard.
- `references/recording.md` - the framebuffer recipe and why each flag exists; the smoke-take and timestamp-verification checklists; process gotchas. Read before recording or debugging quality.
- `references/driving.md` - CDP driving patterns: clicks, variable-latency waits, milestone marking, staying dialog-safe.
- `scripts/record_template.py` - the harness. Edit the CONFIG and BEATS sections; the plumbing is done. Supports `--smoke` and `--verify`.
- `scripts/cinema.js` - the in-page motion layer, injected automatically. Read it before changing a primitive's defaults; they were arrived at by fixing real defects.
