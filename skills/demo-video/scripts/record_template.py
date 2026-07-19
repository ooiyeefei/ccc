#!/usr/bin/env python3
"""Hi-res demo recorder template - Xvfb framebuffer + ffmpeg x11grab + CDP driving.

Why this shape: Playwright's recordVideo captures at CSS-viewport size with a
~0.6 Mbps webm encoder, which macroblocks above 1080p. Here we record the REAL
framebuffer (Xvfb at 2560x1600) while Chrome renders a 1280x800 CSS viewport at
device-scale-factor 2 - retina-crisp - and encode with CRF (controlled quality).
See ../references/recording.md for the full rationale before changing flags.

EDIT the CONFIG and BEATS sections. The plumbing below them is done.

Usage:
  python3 record_template.py NAME --smoke                 test capture (Gate 2)
  python3 record_template.py NAME --storyboard SB.md      full take + reconcile
  python3 record_template.py NAME --verify                re-reconcile a take

A full take REFUSES to run without an approved storyboard (Gate 1) and without a
smoke take on record (Gate 2, override --no-smoke). That is deliberate: these
gates are the ones an agent under deadline skips, so they are enforced here
rather than left to prose.

Needs:  Xvfb, ffmpeg, ffprobe, google-chrome (or chromium), pip install websockets
"""
import asyncio, hashlib, json, math, os, pathlib, signal, socket, stat, subprocess, sys, time, urllib.request

import websockets

# ── CONFIG ─────────────────────────────────────────────── EDIT ME ──
URL = "http://127.0.0.1:3000"        # what to film (stage + log in OFF camera first)
OUT_DIR = pathlib.Path("recordings"); OUT_DIR.mkdir(exist_ok=True)
W, H = 2560, 1600                     # physical framebuffer (Xvfb)
CSS_W, CSS_H = 1280, 800              # CSS viewport; DSF 2 -> fills W,H
FPS = 25                              # 25 for app footage, 30 for slide decks
CRF = 17                              # 16-18; lower = better
DISPLAY = ":99"
CHROME = "google-chrome"

# BEATS: the recording IS this list, and it must match the APPROVED storyboard
# (see ../references/storyboard.md - do not record before that gate passes).
# Each beat: a label (milestone name), an optional JS action run at beat start,
# an optional readiness condition (JS expression polled until truthy - use for
# variable-latency backends), the hold in seconds (>= its narration segment), and
# an optional `settle` (default 0.6s) - how long after the action to sample the
# PROOF frame, so slow entry animations aren't caught half-drawn.
BEATS = [
    {"label": "OPEN",       "js": None,                                        "hold": 6},
    {"label": "RUN_TRIAGE", "js": "document.querySelector('#run-btn').click()", "hold": 8},
    {"label": "CASE_OPEN",  "js": "document.querySelector('.case-row').click()",
     "ready": "!!document.querySelector('.worklog-done')", "ready_timeout": 20, "hold": 10},
    {"label": "CLOSE",      "js": None,                                        "hold": 4},
]
# ── END CONFIG ───────────────────────────────────────────────────────

# Reconciliation tolerance: plausible ffmpeg x11grab spin-up, in seconds.
# Capture starts after Popen and ends at SIGINT, so eps is >= 0 in theory; the
# small negative floor absorbs container-duration rounding. Outside this band
# the front-loaded drift model is not trustworthy - see out_of_tolerance().
EPS_MIN, EPS_MAX = -0.25, 3.0

GATE_META = None                      # set by check_gates(); stamped in the sidecar

SMOKE = "--smoke" in sys.argv
NO_SMOKE = "--no-smoke" in sys.argv       # explicit override, stamped in the sidecar


def _flag_value(name):
    i = sys.argv.index(name)
    if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
        return sys.argv[i + 1]
    raise SystemExit(f"{name} needs a value")


KNOWN_FLAGS = {"--smoke", "--no-smoke", "--verify", "--storyboard"}
_unknown = [a for a in sys.argv[1:] if a.startswith("--") and a not in KNOWN_FLAGS]
if _unknown:                          # never silently swallow a typo that changes mode
    raise SystemExit(f"unknown flag(s): {' '.join(_unknown)}. "
                     f"Known: {' '.join(sorted(KNOWN_FLAGS))}")

STORYBOARD = _flag_value("--storyboard") if "--storyboard" in sys.argv else None
_consumed = {STORYBOARD} if STORYBOARD else set()
_args = [a for a in sys.argv[1:] if not a.startswith("--") and a not in _consumed]
BASE = _args[0] if _args else "demo"
OUT_NAME = BASE + ("-smoke" if SMOKE else "")


def check_gates():
    """Gates 1 and 2, enforced here rather than trusted to prose.

    A full take refuses to run without an approved storyboard, and without a
    smoke take having been recorded for this name. Both are skippable only by
    saying so out loud (--no-smoke), which lands in the sidecar.
    """
    if SMOKE:
        return None
    if not STORYBOARD:
        raise SystemExit(
            "GATE 1: a full take needs --storyboard <path> - the storyboard the "
            "user approved (see references/storyboard.md). Write it, get sign-off, "
            "then pass it here. Use --smoke to shoot a test capture without one.")
    sb = pathlib.Path(STORYBOARD)
    if not sb.exists():
        raise SystemExit(f"GATE 1: no storyboard at {sb}")
    if not (OUT_DIR / f"{BASE}-smoke.json").exists():
        if not NO_SMOKE:
            raise SystemExit(
                f"GATE 2: no smoke take for '{BASE}'. Run "
                f"`python3 {pathlib.Path(sys.argv[0]).name} {BASE} --smoke`, read the "
                f"frames it prints, THEN shoot the full take. Override with --no-smoke "
                f"only when this app was already captured at this config.")
        print("  !! GATE 2 waived (--no-smoke) - rendering setup is unproven", flush=True)
    return {"path": str(sb), "sha256": hashlib.sha256(sb.read_bytes()).hexdigest()[:16],
            "smoke_waived": NO_SMOKE}


def wait_port(port, timeout=12):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.15)
    return False


# ── Timestamp truth: the MP4, not the clock ──────────────────────────
# Wall-clock marks taken during the drive are a HYPOTHESIS. ffmpeg spin-up is
# estimated, x11grab drops frames under load, and the trim offset moves t0.
# The delivered file's duration reveals exactly how much wall clock capture
# missed at the front:  eps = (SIGINT - Popen) - duration.

def ffprobe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True)
    out = r.stdout.strip()
    if r.returncode != 0 or not out or out == "N/A":
        raise SystemExit(
            f"{path} has no readable duration - it is very likely truncated "
            f"(ffmpeg killed without SIGINT writes no moov atom). Re-record.")
    return float(out)


def out_of_tolerance(eps):
    """Policy hook: what to do when the drift model looks broken.

    Default = warn loudly and still emit t_video, because the frame-extraction
    pass that follows is the real check and an agent can see a wrong frame.
    Tighten to `raise SystemExit` if this harness runs unattended, where nobody
    is looking at the PNGs and a silently-wrong timeline reaches the voiceover.
    """
    if EPS_MIN <= eps <= EPS_MAX:
        return False
    print(f"  !! spin-up estimate {eps:+.2f}s outside [{EPS_MIN}, {EPS_MAX}] - "
          f"stalled grab or mid-take freeze. Do NOT trust these timestamps; "
          f"locate beats visually (see recording.md) or re-record.", flush=True)
    return True


def reconcile(side):
    """Map wall-clock marks onto real video time using the delivered duration."""
    video = OUT_DIR / f"{side['name']}.mp4"
    if not video.exists():
        raise SystemExit(f"no such take: {video}")
    missing = [k for k in ("wall_popen_to_sigint", "t0_since_popen") if k not in side]
    if missing:
        raise SystemExit(
            f"{video.with_suffix('.json')} predates MP4 reconciliation "
            f"(no {', '.join(missing)}). Its timestamps came from the raw drive "
            f"clock and cannot be reconciled after the fact - re-record with "
            f"this harness, or locate beats visually per recording.md.")
    duration = ffprobe_duration(video)
    # Pinned at the first reconcile (right after recording) and never updated -
    # comparing against a field we rewrite would launder the warning away on the
    # next --verify.
    side.setdefault("recorded_duration", round(duration, 2))
    was = side["recorded_duration"]
    retimed = abs(was - duration) > 0.15
    if retimed:
        print(f"  !! duration changed since recording ({was}s -> {round(duration,2)}s). "
              f"The reconcile assumes all missing time is at the FRONT, so a tail "
              f"trim silently shifts every mark early. Re-cut from the original, or "
              f"locate beats visually (recording.md).", flush=True)
    eps = side["wall_popen_to_sigint"] - duration       # capture missed at front
    suspect = out_of_tolerance(eps) or retimed
    base = side["t0_since_popen"] - eps                 # video time of t0
    ceiling = max(0.0, duration - 0.2)

    def to_video(t_wall):
        # Clamp inside the file: END is marked at SIGINT, and seeking to exactly
        # the duration yields no frame (silent empty extraction).
        return round(min(max(0.0, base + t_wall), ceiling), 2)

    for m in side["milestones"]:
        m["t_video"] = to_video(m["t_wall"])            # narration cue point
        # t_proof: where the beat's claim is actually visible on screen. Falls
        # back to the cue for END and for sidecars written before settle marks.
        m["t_proof"] = to_video(m["t_settled"]) if "t_settled" in m else m["t_video"]
    stamps = [m["t_video"] for m in side["milestones"]]
    if len(set(stamps)) != len(stamps):
        print(f"  !! {len(stamps) - len(set(stamps))} milestone(s) collapsed onto a "
              f"shared timestamp - the reconcile is wrong even though eps looked "
              f"plausible. Do not narrate against these.", flush=True)
        suspect = True
    side.update({"video_duration": round(duration, 2), "spin_up_seconds": round(eps, 2),
                 "timestamps_suspect": suspect,
                 "note": "sync narration to t_video (cue point); verify proof at "
                         "t_proof (settled frame); t_wall is the raw drive clock"})
    return side


def extract_frames(side):
    """Proof frame per milestone, from the DELIVERED mp4. Look at every one."""
    video = OUT_DIR / f"{side['name']}.mp4"
    if not video.exists():
        raise SystemExit(f"no such take: {video}")
    frames_dir = OUT_DIR / f"{side['name']}-frames"
    if frames_dir.exists():
        for old in frames_dir.glob("*.png"):
            old.unlink()               # else the contact sheet tiles stale frames
    frames_dir.mkdir(exist_ok=True)
    paths = []
    for m in side["milestones"]:
        png = frames_dir / f"{m['t_proof']:07.2f}-{m['milestone']}.png"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(m["t_proof"]),
                            "-i", str(video), "-frames:v", "1", str(png)],
                           capture_output=True, text=True)
        if r.returncode != 0 or not png.exists() or png.stat().st_size == 0:
            print(f"  !! frame extraction FAILED at {m['t_proof']}s "
                  f"({m['milestone']}): {r.stderr.strip()[:120]}", flush=True)
            continue
        paths.append(png)
    return paths


def contact_sheet(frames, side):
    """All milestones tiled into ONE image, so inspection is a single Read.

    Gates 2 and 3 both hinge on an agent actually looking at frames - the step
    most likely to be silently skipped when it costs N reads. Make it cost one.
    """
    if len(frames) < 2:
        return None
    out = OUT_DIR / f"{side['name']}-contact.png"
    on_disk = sorted((OUT_DIR / f"{side['name']}-frames").glob("*.png"))
    if len(on_disk) != len(frames):    # never tile a set we cannot account for
        return None
    cols = min(3, len(frames))
    rows = math.ceil(len(frames) / cols)
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-pattern_type", "glob",
         "-i", str(OUT_DIR / f"{side['name']}-frames" / "*.png"),
         "-vf", f"scale=640:-1,tile={cols}x{rows}:padding=8:color=0x222222",
         "-frames:v", "1", str(out)], capture_output=True, text=True)
    return out if r.returncode == 0 and out.exists() else None


def finish(side):
    side = reconcile(side)
    frames = extract_frames(side)
    (OUT_DIR / f"{side['name']}.json").write_text(json.dumps(side, indent=2))
    print(f"\nDONE -> {OUT_DIR}/{side['name']}.mp4  "
          f"({side['video_duration']}s, spin-up {side['spin_up_seconds']}s)")
    print(f"  {'cue':>7}  {'proof':>7}  milestone")
    for m in side["milestones"]:
        print(f"  {m['t_video']:7.2f}  {m['t_proof']:7.2f}  {m['milestone']}")
    print("\n  Sync narration to the CUE column; the PROOF column is where the "
          "beat's claim is visible.")
    sheet = contact_sheet(frames, side)
    print("\nGATE 3 - Read these as images and confirm each shows the screen "
          "its beat claims:")
    if sheet:
        print(f"  {sheet}   <- all milestones, one read")
    for p in frames:
        print(f"  {p}")
    if side.get("timestamps_suspect"):
        print("\n  !! timestamps_suspect=true - do NOT hand this sidecar to "
              "pitch-craft until the frames above are confirmed by eye.")
    return side


def verify(name):
    """Re-reconcile an existing take (after a manual re-encode, or to re-check)."""
    side = json.loads((OUT_DIR / f"{name}.json").read_text())
    side["name"] = name
    finish(side)


async def run(cdp_port):
    targets = json.loads(urllib.request.urlopen(
        f"http://127.0.0.1:{cdp_port}/json").read())
    page = next(t for t in targets if t.get("type") == "page")
    _id = 0
    milestones = []
    if not BEATS:
        raise SystemExit("BEATS is empty - nothing to record")
    if SMOKE:
        # Run THROUGH the first beat that actually drives something. A smoke take
        # that only renders beat 1 cannot catch a dead selector - and a dead
        # selector surviving into the full take is the failure Gate 2 exists for.
        first_action = next((i for i, b in enumerate(BEATS) if b.get("js")), 0)
        beats = [{**b, "hold": min(b["hold"], 4),
                  "ready_timeout": min(b.get("ready_timeout", 30), 10)}
                 for b in BEATS[:first_action + 1]]
    else:
        beats = BEATS

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

        ff = None
        try:
            ff = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-video_size", f"{W}x{H}", "-framerate", str(FPS),
                 "-f", "x11grab", "-draw_mouse", "0", "-i", f"{DISPLAY}.0",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF),
                 "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                 str(OUT_DIR / f"{OUT_NAME}.mp4")],
                env={**os.environ, "DISPLAY": DISPLAY})
            t_popen = time.time()      # anchor for the duration-based reconcile
            time.sleep(1.2)            # ffmpeg spin-up (estimated - corrected later)
            if ff.poll() is not None:
                raise SystemExit(
                    f"ffmpeg exited immediately (code {ff.returncode}) - it never "
                    f"captured. Usual cause: the framebuffer is not {W}x{H} because "
                    f"a foreign Xvfb already held {DISPLAY}. Nothing was recorded.")

            # Re-navigate ON camera so the entry animation is in the take.
            await send("Page.navigate", {"url": URL})
            t0 = time.time()

            def mark(label):
                milestones.append({"t_wall": round(time.time() - t0, 2),
                                   "milestone": label})
                print(f"  {milestones[-1]['t_wall']:6.2f}s  {label} (wall)", flush=True)

            for beat in beats:
                if beat.get("js"):
                    await send("Runtime.evaluate", {"expression": beat["js"]})
                mark(beat["label"])
                if beat.get("ready"):  # condition-poll for variable latency
                    deadline = time.time() + beat.get("ready_timeout", 30)
                    while time.time() < deadline:
                        if await evaluate(beat["ready"]):
                            break
                        await asyncio.sleep(0.5)
                # The mark is the narration CUE point (beat start). The beat's PROOF
                # only exists once the action's result has rendered - after the ready
                # condition plus the entry animation. Record that separately, or Gate
                # 3 checks a half-drawn frame and calls a correct timestamp broken.
                settle = min(beat.get("settle", 0.6), beat["hold"])
                await asyncio.sleep(settle)
                milestones[-1]["t_settled"] = round(time.time() - t0, 2)
                await asyncio.sleep(beat["hold"] - settle)
            mark("END")
            t_sigint = time.time()
        finally:
            # ffmpeg outlives the interpreter if we don't stop it, and a take
            # killed without SIGINT has no moov atom - unplayable, unprobeable.
            if ff is not None and ff.poll() is None:
                ff.send_signal(signal.SIGINT)
                try:
                    ff.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    ff.kill()

    finish({"name": OUT_NAME, "res": f"{W}x{H}", "fps": FPS, "smoke": SMOKE,
            "storyboard": GATE_META,
            "wall_popen_to_sigint": round(t_sigint - t_popen, 3),
            "t0_since_popen": round(t0 - t_popen, 3),
            "milestones": milestones})
    if SMOKE:
        print("\nSmoke take only - run the checklist in recording.md before "
              "the full capture.")


def main():
    global GATE_META
    GATE_META = check_gates()          # Gates 1 and 2 - refuses before any capture
    profile = pathlib.Path(f"/tmp/rec-profile-{OUT_NAME}")
    # A reused profile still holds the PREVIOUS run's DevToolsActivePort. Reading
    # it back would hand us a dead port (or worse, a live one from another run) -
    # so clear it and only trust a file this Chrome writes.
    (profile / "DevToolsActivePort").unlink(missing_ok=True)
    # Pre-write prefs so the "Save password?" bubble never covers the frame.
    (profile / "Default").mkdir(parents=True, exist_ok=True)
    (profile / "Default" / "Preferences").write_text(json.dumps(
        {"credentials_enable_service": False,
         "profile": {"password_manager_enabled": False}}))

    xvfb = chrome = None
    try:
        xvfb = subprocess.Popen(
            ["Xvfb", DISPLAY, "-screen", "0", f"{W}x{H}x24", "-nolisten", "tcp"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Readiness = the X SOCKET, not pgrep (self-match trap) and not mere
        # existence: a leaked run leaves a plain file there, and adopting a
        # foreign display films the wrong size (or nothing).
        sock = pathlib.Path(f"/tmp/.X11-unix/X{DISPLAY.lstrip(':')}")
        for _ in range(40):
            if sock.exists() and stat.S_ISSOCK(sock.stat().st_mode):
                break
            if xvfb.poll() is not None:
                raise SystemExit(f"Xvfb died on {DISPLAY} (display already in use?)")
            time.sleep(0.25)
        else:
            raise SystemExit(f"no X socket for {DISPLAY} after 10s")

        chrome = subprocess.Popen(
            [CHROME, "--no-first-run", "--no-default-browser-check",
             "--disable-infobars", "--disable-features=Translate",
             "--force-device-scale-factor=2", "--force-color-profile=srgb",
             "--hide-scrollbars", "--kiosk", "--window-position=0,0",
             f"--window-size={CSS_W},{CSS_H}",
             "--remote-debugging-port=0", "--remote-allow-origins=*",
             f"--user-data-dir={profile}", f"--app={URL}"],
            env={**os.environ, "DISPLAY": DISPLAY},
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Port 0 + read it back from OUR profile dir. A hardcoded port is
        # adopted-not-owned: a leaked Chrome from another run answers on it and
        # you drive that browser instead, filming a display it isn't on.
        port_file = profile / "DevToolsActivePort"
        port = None
        for _ in range(60):
            if chrome.poll() is not None:
                raise SystemExit("Chrome exited before opening a CDP port")
            if port_file.exists():
                head = port_file.read_text().split("\n")[0].strip()
                if head.isdigit():
                    port = int(head)
                    break
            time.sleep(0.25)
        if port is None or not wait_port(port):
            raise SystemExit("Chrome CDP port did not come up")
        time.sleep(1.5)
        asyncio.run(run(port))
    finally:
        for proc in (chrome, xvfb):
            if proc is not None:
                try:
                    proc.terminate()
                except Exception:
                    pass


if __name__ == "__main__":
    if "--verify" in sys.argv:
        if not _args:
            raise SystemExit("--verify needs the take name: "
                             "`python3 record_template.py NAME --verify`")
        verify(OUT_NAME)              # honours --smoke, so NAME --smoke --verify works
    else:
        main()
