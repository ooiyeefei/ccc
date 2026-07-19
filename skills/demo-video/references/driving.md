# Driving - controlling the app on camera

The recorder connects to Chrome over CDP (raw websocket; no Playwright dependency needed) and drives the app between milestone marks. Patterns that hold up:

## Connect

- List targets from `http://127.0.0.1:<port>/json`, take the `page` target's `webSocketDebuggerUrl`, connect with any websocket client.
- Enable `Page` and `Runtime` domains once; then everything is `Runtime.evaluate`.

## Act

- **Click via JS, not OS events**: `Runtime.evaluate("document.querySelector('#next').click()")` is focus-proof - it works even if the window never had OS focus (it never does under Xvfb). Synthetic keyboard/mouse events need focus and silently no-op.
- Fill inputs by setting `.value` + dispatching `input`/`change` events, or use the app's own test hooks if it has them.
- **Never trigger `alert()`/`confirm()`** - a native dialog blocks the CDP channel and the take is dead. If a flow has a confirm step, prefer a build/flag that skips it, or click the in-page (non-native) modal.

## Wait

Two kinds of waits, chosen per beat:

- **Fixed hold** for static content: `sleep(hold_seconds)` where the hold comes from the narration budget (each beat's hold >= its narration segment's length).
- **Condition-poll for variable latency**: when a beat depends on a live backend (a graph traversal, an LLM call), poll the DOM until the ready condition is true, with a hard timeout:
  ```python
  while time.time() < deadline:
      done = evaluate("!!document.querySelector('.result-badge')")
      if done: break
      await asyncio.sleep(0.5)
  ```
  Live latency varies by seconds between takes - fixed sleeps on variable beats are the #1 cause of milestone drift and dead air.

## Mark

Emit a milestone at the START of every beat: `{"t_wall": <since t0>, "milestone": "CASE_OPEN"}` appended to a list, written as a JSON sidecar next to the video.

Then, once the beat's ready condition resolves and its animation has landed, record a second mark on the same milestone (`t_settled`). The beat start is the narration **cue**; the settled mark is where the beat's **proof** is actually on screen. On an async beat these are seconds apart, and verifying at the cue fails a correct take - see the cue-vs-proof section in `recording.md`.

`t_wall` is the raw drive clock - a **hypothesis**, not a delivery timestamp. After the take, the harness reconciles it against the delivered MP4's real duration and writes `t_video` alongside it (see the timestamp-truth section in `recording.md`). Record the anchors that reconciliation needs: wall time from ffmpeg `Popen` to `SIGINT`, and the offset from `Popen` to the on-camera re-navigation.

**`t_video` is what pitch-craft syncs narration against**, and what a re-record re-aligns from. Never hand `t_wall` downstream.

## Cursor visibility

Default is invisible (`-draw_mouse 0` in the capture). If the viewer needs to see "where to look", inject a fake cursor: a small red dot `<div>` positioned via JS before each click, moved with a CSS transition. This reads better on video than a real cursor and can't wander mid-frame.

## Pacing

- Hold each beat at least as long as its narration needs, plus ~0.5s of breathing room.
- Slow visual reveals (staggered animations) read better on video than instant state changes; if the app supports a demo pacing flag, use it.
- End the take with a deliberate final hold (3-4s) on the closing state - stitching and fade-outs need the runway.
