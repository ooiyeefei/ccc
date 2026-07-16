# Recording - the framebuffer recipe

## Why not the obvious tools

These are verified failure modes, not opinions:

- **Playwright `recordVideo` / Chromium screencast records at the CSS viewport size.** Setting `deviceScaleFactor: 2` adds ZERO video pixels - it only supersamples anti-aliasing inside the same 1280x800 frame. Setting `recordVideo.size` larger just black-pads.
- **Playwright's built-in webm encoder caps around 0.6 Mbps**, which starves anything above ~1080p into visible macroblocking ("pixelation").
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

## Process gotchas (cost hours; read once)

- `pkill -f <pattern>` matches the running script's OWN cmdline and kills it (exit 144). Use `pkill -x chrome`, exact PIDs, or run cleanup in a separate call.
- In zsh, an unquoted `$VAR` holding multiple CLI flags does NOT word-split - flags arrive as one bogus argument. Inline flags or use `${=VAR}`.
- Stuck ports from a previous run: prefer fresh ports per attempt over fighting the old process.

## Quality bar

- 2560x1600 at DSF 2 over 1280x800 CSS is the proven sweet spot: retina-crisp, ~1.3 Mbps at CRF 18, files small enough to upload anywhere.
- Poster frames: prefer a curated still (a clean screenshot of the money shot) over a frame extracted from video - extracted frames often carry cursor specks or mid-animation states.
- Upscaling + sharpening an existing low-bitrate recording (lanczos, CAS) does NOT rescue it - sharpening amplifies the blocking. Re-record instead.
