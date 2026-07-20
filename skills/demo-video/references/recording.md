# Recording - the framebuffer recipe

## Why not the obvious tools

These are verified failure modes, not opinions:

- **Screencast-based capture records at the CSS viewport size.** Setting a device scale factor adds ZERO video pixels - it only supersamples anti-aliasing inside the same 1280x800 frame. Asking for a larger recording size just black-pads.
- **Built-in webm encoders in these stacks cap around 0.6 Mbps**, which starves anything above ~1080p into visible macroblocking ("pixelation").
- **CSS zoom tricks** (`html{zoom:1.25}` at native 1080p) blur any `<canvas>` content - fatal when the demo's centerpiece is a canvas graph.

The fix is to capture a REAL framebuffer at the resolution you want, with a bitrate you control.

## The recipe

1. **Virtual display at physical resolution**:
   `Xvfb :99 -screen 0 2560x1600x24 -nolisten tcp`
   Readiness check = wait for the socket `/tmp/.X11-unix/X99` to exist. Do NOT use `pgrep -f 'Xvfb :99'` - it matches the checking script's own cmdline (false "up").

2. **Chrome, launched manually on that display**, chromeless and retina:
   ```
   DISPLAY=:99 chrome --app=<url> --window-size=1280,800 \
     --force-device-scale-factor=2 --force-color-profile=srgb \
     --hide-scrollbars --no-first-run --user-data-dir=<fresh dir> \
     --remote-debugging-port=0 --remote-allow-origins=*
   ```
   This yields a 1280x800 CSS viewport (same framing as design) rendered at 2560x1600 physical pixels; canvas elements render at DPR 2 = crisp. Use `--kiosk` instead of `--app` if the app-mode top rounding shows.
   - `--remote-debugging-port=0` + read the real port from `<profile>/DevToolsActivePort`. Never hardcode 9222: a stale Chrome holding the port produces confusing half-connections. (Fixed fresh ports per run also work if you must.)
   - **Pre-write `<profile>/Default/Preferences`** before launch: `{"credentials_enable_service":false,"profile":{"password_manager_enabled":false}}` - otherwise Chrome's "Save password?" bubble covers the frame on the first login.

3. **Capture with ffmpeg x11grab**:
   ```
   ffmpeg -y -video_size 2560x1600 -framerate 25 -f x11grab -draw_mouse 0 \
     -i :99.0 -c:v libx264 -preset ultrafast -crf 16 raw.mkv
   ```
   then re-encode `-crf 18 -preset slow -movflags +faststart` for delivery. For static content (slide decks) a direct `-crf 18 -preset veryfast` single pass is fine at 30fps.
   - `-draw_mouse 0` is mandatory: x11grab otherwise burns the X cursor into every frame as a stray black arrow.
   - CRF-controlled encoding is the whole point - it holds quality at any resolution instead of starving.

4. **Sequence matters**: load the page and let fonts/layout settle -> start ffmpeg -> **re-navigate to the start URL** so the entry animation plays ON camera -> drive the beats -> stop ffmpeg with SIGINT (not SIGKILL) and wait, so the moov atom is written.

5. **Login happens before ffmpeg starts.** Credentials never appear on camera and never live in the repo.

## The smoke take (before every full capture)

Record a short test capture and **look at it** before spending a full take:

```
python3 record_template.py <name> --smoke
```

It records through the first beat that actually drives something (rendering beat 1 alone cannot catch a dead selector), extracts a frame per milestone, and prints a contact sheet. Read what it printed - no manual extraction needed - and check:

- [ ] **Right app, right screen** - the entry state the storyboard names, not a login or error page
- [ ] **Framing** - full 2560x1600, no black padding bars, no letterboxing
- [ ] **Crisp at 1:1** - body text sharp, no macroblocking (if soft, DSF/framebuffer mismatch - re-check the flags above)
- [ ] **Clean frame** - no password bubble, no first-run dialog, no notification toast
- [ ] **No stray OS pointer** - `-draw_mouse 0` should mean the only cursor in frame is the one `cinema.js` draws. A second, unstyled arrow means the flag is not taking effect
- [ ] **Chrome hidden** - no tab strip, no address bar, no infobar
- [ ] **Seeded data present** - the actual demo rows/records, not an empty state
- [ ] **Colors right** - `--force-color-profile=srgb` is doing its job; no washed-out or oversaturated render

**Any unchecked box means the take is not ready.** Fix the staging and re-smoke; never start the full capture on a known-bad frame.

Every one of these has shipped as a ruined full take. The smoke take costs ~30 seconds; a bad full take costs the recording *plus* the narration written against it.

## Timestamp truth - the MP4, not the clock

The harness marks milestones from wall clock during the drive. Treat those as a **hypothesis**, never as delivery timestamps. They drift because:

- **Capture start is assumed, not measured.** The `sleep` after `Popen` is a guess at when x11grab begins. Guess wrong and every timestamp shifts the same way - a bias no single frame check reveals.
- **x11grab drops frames under load.** 2560x1600 at 25fps is heavy; a busy machine loses frames.
- **The trim offset moves t0.** The on-camera re-navigation is where "first useful frame" begins, not where the file begins.

Estimated holds from the storyboard are worse still - they ignore variable backend latency entirely. Never derive a delivery timestamp from a planned wait.

**The reconciliation.** The delivered file's duration tells you exactly how much wall clock ffmpeg missed at the front:

```
D   = ffprobe duration of the delivered mp4
W   = wall seconds from ffmpeg Popen to SIGINT
eps = W - D                      # what capture missed during spin-up
t_video(beat) = (t0 - t_popen - eps) + t_wall(beat)
```

`ffprobe -v error -show_entries format=duration -of csv=p=0 out.mp4` gives `D`. Sanity-check `eps`: **measured on a healthy machine it is near zero** (0.01-0.05s - x11grab starts capturing almost immediately after `Popen`). The head padding you see in the file is the deliberate post-`Popen` sleep, and `base` already subtracts it. A large positive `eps` means capture actually stalled. The harness accepts `[-0.25, 3.0]` (small negatives are container-duration rounding); outside that band the model broke (a stalled grab, a mid-take freeze) - do not trust the arithmetic, locate the beats visually instead.

## Cue vs proof - two timestamps per beat

A milestone is marked at the START of its beat. That is the **cue point** (`t_video`) - correct for narration, because the voiceover segment begins when the beat begins.

It is the wrong frame to verify against. On any beat with an async result - a backend call, a staggered animation - the screen at the cue point still shows the PREVIOUS state. Verifying there produces a false failure on every live-backend beat: the frame shows no proof, and a correct timestamp gets "fixed" into a wrong one.

So the harness records a second mark, `t_proof`: after the ready condition resolves, plus a settle margin (`settle`, default 0.6s) for the entry animation to land.

```
beat start ──cue (t_video)──> [backend work] ──> [animation] ──proof (t_proof)──> hold ──>
             narration here                                     verify here
```

Real numbers from a take with a ~2s async render: `RUN_AUDIT` cue at 5.19s (work log mid-render, one line drawn), proof at 7.80s (all rows in, log complete). Same beat, same take, 2.6s apart - and only the second frame proves the claim.

Bump `settle` per beat when animations are slow; the beat's total on-screen time is unchanged (`ready_wait + hold`).

**Then verify with your eyes, per milestone.** Arithmetic narrows it; frames confirm it:

```
ffmpeg -ss <t_proof> -i out.mp4 -frames:v 1 /tmp/m-<label>.png
```

Extract at every reconciled milestone, Read each PNG, and confirm it shows the screen that beat claims. `record_template.py <name> --verify` does the whole loop, rewrites the sidecar with `t_video` and `t_proof` alongside `t_wall`, and tiles every milestone into one contact sheet so inspection is a single read.

A milestone frame showing the wrong screen means the timestamp is wrong - fix it now, not after the voiceover is recorded against it.

**No sidecar?** Footage you did not record with this harness has no `t_wall`/`wall_popen_to_sigint`/`t0_since_popen`, so the arithmetic is unavailable - the reconcile needs the drive-clock anchors, not just the file. Scrub visually instead: `ffmpeg -i out.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null -` lists state changes with their timestamps; extract the candidates and Read them.

**Trimming after the fact.** The reconciliation attributes all missing duration to the front, so cutting the TAIL shifts every mark early with no arithmetic warning. The harness pins `recorded_duration` at the first reconcile and flags `timestamps_suspect` if the file's duration later changes - but the fix is to re-cut from the original take, not to re-verify a trimmed one. A head trim reconciles correctly.

**High-stakes fallback:** if the drift model keeps failing, burn a visual sync marker instead - flash a full-screen color for ~200ms at t0, then find that frame with `ffmpeg -vf "select='gt(scene,0.4)'" -vsync vfr`. Heavier to set up, exact by construction.

## Process gotchas (cost hours; read once)

- `pkill -f <pattern>` matches the running script's OWN cmdline and kills it (exit 144). Use `pkill -x chrome`, exact PIDs, or run cleanup in a separate call.
- In zsh, an unquoted `$VAR` holding multiple CLI flags does NOT word-split - flags arrive as one bogus argument. Inline flags or use `${=VAR}`.
- Stuck ports from a previous run: prefer fresh ports per attempt over fighting the old process.
- **Delete `<profile>/DevToolsActivePort` before launching Chrome.** A reused profile still holds the previous run's port; read it back and you connect to a dead port, or to a live Chrome from another run and drive the wrong browser while filming a display it isn't on.
- **Check the X socket is a socket** (`stat.S_ISSOCK`), not merely that the path exists - a crashed run can leave a plain file there, and adopting a foreign display films the wrong size or nothing at all.
- **Check `ffmpeg.poll()` after the spin-up sleep.** If the framebuffer isn't the size you asked for, ffmpeg exits immediately; without this check the whole storyboard drives against a dead recorder and you find out minutes later at ffprobe.

## Quality bar

- 2560x1600 at DSF 2 over 1280x800 CSS is the proven sweet spot: retina-crisp, ~1.3 Mbps at CRF 18, files small enough to upload anywhere.
- Poster frames: prefer a curated still (a clean screenshot of the money shot) over a frame extracted from video - extracted frames often carry cursor specks or mid-animation states.
- Upscaling + sharpening an existing low-bitrate recording (lanczos, CAS) does NOT rescue it - sharpening amplifies the blocking. Re-record instead.
