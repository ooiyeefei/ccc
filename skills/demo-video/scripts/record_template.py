#!/usr/bin/env python3
"""Hi-res demo recorder template - Xvfb framebuffer + ffmpeg x11grab + CDP driving.

Why this shape: Playwright's recordVideo captures at CSS-viewport size with a
~0.6 Mbps webm encoder, which macroblocks above 1080p. Here we record the REAL
framebuffer (Xvfb at 2560x1600) while Chrome renders a 1280x800 CSS viewport at
device-scale-factor 2 - retina-crisp - and encode with CRF (controlled quality).
See ../references/recording.md for the full rationale before changing flags.

EDIT the CONFIG and BEATS sections. The plumbing below them is done.

Usage:  python3 record_template.py [out_name]
Needs:  Xvfb, ffmpeg, google-chrome (or chromium), pip install websockets
"""
import asyncio, json, os, pathlib, signal, socket, subprocess, sys, time, urllib.request

import websockets

# ── CONFIG ─────────────────────────────────────────────── EDIT ME ──
URL = "http://127.0.0.1:3000"        # what to film (stage + log in OFF camera first)
OUT_DIR = pathlib.Path("recordings"); OUT_DIR.mkdir(exist_ok=True)
OUT_NAME = sys.argv[1] if len(sys.argv) > 1 else "demo"
W, H = 2560, 1600                     # physical framebuffer (Xvfb)
CSS_W, CSS_H = 1280, 800              # CSS viewport; DSF 2 -> fills W,H
FPS = 25                              # 25 for app footage, 30 for slide decks
CRF = 17                              # 16-18; lower = better
DISPLAY = ":99"
CDP_PORT = 9343                       # fresh per run beats fighting stale ones
CHROME = "google-chrome"

# BEATS: the recording IS this list. Each beat: a label (milestone name),
# an optional JS action run at beat start, an optional readiness condition
# (JS expression polled until truthy - use for variable-latency backends),
# and the hold in seconds (>= the narration segment it must carry).
BEATS = [
    {"label": "OPEN",       "js": None,                                        "hold": 6},
    {"label": "RUN_TRIAGE", "js": "document.querySelector('#run-btn').click()", "hold": 8},
    {"label": "CASE_OPEN",  "js": "document.querySelector('.case-row').click()",
     "ready": "!!document.querySelector('.worklog-done')", "ready_timeout": 20, "hold": 10},
    {"label": "CLOSE",      "js": None,                                        "hold": 4},
]
# ── END CONFIG ───────────────────────────────────────────────────────


def wait_port(port, timeout=12):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.15)
    return False


async def run():
    targets = json.loads(urllib.request.urlopen(
        f"http://127.0.0.1:{CDP_PORT}/json").read())
    page = next(t for t in targets if t.get("type") == "page")
    _id = 0
    milestones = []

    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=None) as ws:
        async def send(method, params=None):
            nonlocal _id
            _id += 1
            await ws.send(json.dumps({"id": _id, "method": method,
                                      "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == _id:
                    return msg

        async def evaluate(expr):
            r = await send("Runtime.evaluate",
                           {"expression": expr, "returnByValue": True})
            return r.get("result", {}).get("result", {}).get("value")

        await send("Page.enable"); await send("Runtime.enable")

        # Settle load (fonts, layout) BEFORE ffmpeg starts.
        await send("Page.navigate", {"url": URL})
        await asyncio.sleep(3.0)

        ff = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-video_size", f"{W}x{H}", "-framerate", str(FPS),
             "-f", "x11grab", "-draw_mouse", "0", "-i", f"{DISPLAY}.0",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF),
             "-pix_fmt", "yuv420p", "-movflags", "+faststart",
             str(OUT_DIR / f"{OUT_NAME}.mp4")],
            env={**os.environ, "DISPLAY": DISPLAY})
        time.sleep(1.2)  # ffmpeg spin-up

        # Re-navigate ON camera so the entry animation is in the take.
        t_ff = time.time()
        await send("Page.navigate", {"url": URL})
        t0 = time.time()

        def mark(label):
            milestones.append({"t_seconds": round(time.time() - t0, 1),
                               "milestone": label})
            print(f"  {milestones[-1]['t_seconds']:6.1f}s  {label}", flush=True)

        for beat in BEATS:
            if beat.get("js"):
                await send("Runtime.evaluate", {"expression": beat["js"]})
            mark(beat["label"])
            if beat.get("ready"):  # condition-poll for variable latency
                deadline = time.time() + beat.get("ready_timeout", 30)
                while time.time() < deadline:
                    if await evaluate(beat["ready"]):
                        break
                    await asyncio.sleep(0.5)
            await asyncio.sleep(beat["hold"])
        mark("END")

        ff.send_signal(signal.SIGINT)  # SIGINT, not kill: finalizes the mp4
        try:
            ff.wait(timeout=15)
        except subprocess.TimeoutExpired:
            ff.kill()

    (OUT_DIR / f"{OUT_NAME}.json").write_text(json.dumps(
        {"trim_seconds": round(t0 - t_ff, 2), "res": f"{W}x{H}", "fps": FPS,
         "milestones": milestones}, indent=2))
    print(f"DONE -> {OUT_DIR}/{OUT_NAME}.mp4 (+ .json milestones)")


def main():
    profile = pathlib.Path(f"/tmp/rec-profile-{OUT_NAME}")
    # Pre-write prefs so the "Save password?" bubble never covers the frame.
    (profile / "Default").mkdir(parents=True, exist_ok=True)
    (profile / "Default" / "Preferences").write_text(json.dumps(
        {"credentials_enable_service": False,
         "profile": {"password_manager_enabled": False}}))

    xvfb = subprocess.Popen(
        ["Xvfb", DISPLAY, "-screen", "0", f"{W}x{H}x24", "-nolisten", "tcp"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Readiness = the X socket, NOT pgrep (self-match trap).
    sock = pathlib.Path(f"/tmp/.X11-unix/X{DISPLAY.lstrip(':')}")
    for _ in range(40):
        if sock.exists():
            break
        time.sleep(0.25)

    chrome = subprocess.Popen(
        [CHROME, "--no-first-run", "--no-default-browser-check",
         "--disable-infobars", "--disable-features=Translate",
         "--force-device-scale-factor=2", "--force-color-profile=srgb",
         "--hide-scrollbars", "--kiosk", "--window-position=0,0",
         f"--window-size={CSS_W},{CSS_H}",
         f"--remote-debugging-port={CDP_PORT}", "--remote-allow-origins=*",
         f"--user-data-dir={profile}", f"--app={URL}"],
        env={**os.environ, "DISPLAY": DISPLAY},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not wait_port(CDP_PORT):
        raise SystemExit("Chrome CDP port did not come up")
    time.sleep(1.5)
    try:
        asyncio.run(run())
    finally:
        for p in (chrome, xvfb):
            try:
                p.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()
