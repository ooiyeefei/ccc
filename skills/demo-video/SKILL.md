---
name: demo-video
description: Record a crisp, high-resolution product demo video by driving the real app with a browser agent - the full pipeline from beat sheet to staged app, Xvfb framebuffer recording, milestone timestamps, and a narration script synced to the frames. Use whenever the user wants a demo video, a product walkthrough recording, a screen capture of an app for a hackathon / launch / submission, or complains that a recording came out pixelated, blurry, or blocky. Also the home of the recording harness that pitch-deck reuses for slide walkthroughs. Not for - live pitching or deck building (pitch-deck, pitch-package), one-off screenshots, or editing footage that already exists.
---

# Demo Video - film the real product, crisply

A demo is an argument: every beat on camera proves a claim, and the narration is written **to the frame** - describing what is actually on screen at that second. The three leading rules: **milestones first**, **real frames not upscaled**, **verify with your eyes**.

## Steps

### 0. Preflight

Check the machine can do this before promising it: `ffmpeg` and `Xvfb` installed (`apt-get install -y xvfb` on Linux; this recipe is Linux-first - on macOS capture the retina display with `ffmpeg -f avfoundation` or QuickTime, same principles: physical pixels, controlled bitrate). Confirm the app runs with demo data and demo credentials, and that credentials stay OUT of the repo (scratchpad only).

### 1. Milestones first - the beat sheet

Before any recording, write the beat sheet: for each beat, `label / what's on screen / what it PROVES / estimated hold seconds`. A beat that proves nothing gets cut. Order the beats so the strongest proof lands last (the moment the product does the thing competitors can't - e.g. a learning loop closing live on camera). Target total duration comes from the pitch budget, not from how much footage exists.

Show the beat sheet to the user and get sign-off before recording. Re-records are cheap in tooling but expensive in narration re-sync.

### 2. Stage the app

Deterministic demo data, seeded to make the beats true. Log in OFF camera. Kill anything that can interrupt the frame: notifications, password-manager bubbles (pre-write Chrome preferences - see recording.md), first-run dialogs. Never trigger JS alerts mid-take; they freeze the driver.

### 3. Record - real frames, not upscaled

Use `scripts/record_template.py` as the starting point: Xvfb at physical 2560x1600, Chrome in app mode with `--force-device-scale-factor=2` over a 1280x800 CSS viewport, ffmpeg x11grab with `-draw_mouse 0` at CRF 16-18, driven over CDP, milestones written to a JSON sidecar.

Read `references/recording.md` before changing ANY parameter - every flag in that recipe exists because the obvious path (Playwright's recordVideo) produces macroblocked or soft footage at high resolution.

### 4. Verify with your eyes

Extract 3-4 frames (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 frame.png`) and actually look at them (Read them as images): text crisp (no macroblocking), no stray cursor, correct screens, entry animations captured. Never ship a video whose frames you have not looked at - encoder settings that "should" work regularly don't.

### 5. Narrate to the frame

Hand the milestone JSON and beat sheet to the **pitch-craft** skill. The narration describes what IS on screen at each timestamp, in the recorded register, chunked to the milestone windows.

### 6. Re-records

A new take shifts every milestone (live backends vary by seconds). Re-align the narration per pitch-craft's `timing.md` re-sync procedure. Treat take + script as one versioned pair.

## References

- `references/recording.md` - the framebuffer recipe and why each flag exists; the failure modes of the obvious tools; process gotchas. Read before recording or debugging quality.
- `references/driving.md` - CDP driving patterns: clicks, variable-latency waits, milestone marking, staying dialog-safe.
- `scripts/record_template.py` - the harness. Edit the CONFIG and BEATS sections; the plumbing is done.
