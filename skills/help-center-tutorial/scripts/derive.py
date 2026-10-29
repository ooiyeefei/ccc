#!/usr/bin/env python3
"""One step sheet, one take, three outputs: the video, the screenshots, the article.

    derive.py lint   SHEET [--draft] [--strings strings.json]
    derive.py plan   SHEET --out DIR [--hold 4] [--strings strings.json]
    derive.py derive SHEET --take take.mp4 --sidecar take.json --out DIR
                     [--build X] [--date YYYY-MM-DD] [--strings strings.json]
                     [--scale 2] [--no-video] [--allow-drift]
    derive.py queue  SHEETS_DIR --changed PATH [PATH ...]
    derive.py distance HASH_A HASH_B

SHEET is YAML (needs PyYAML) or JSON; format in references/step-sheet.md.

lint     fails on anything the article could not stand behind: a step with no proof text, caption or
         alt text; duplicate ids; a label that is not in its sentence; a proof that only repeats what
         the step typed; a writing step in a task that does not say it writes; a TODO or PLACEHOLDER
         left in any field. --draft allows placeholders (the sheet is going to an approver, not to
         a recorder) and prints how many remain.
plan     writes DIR/recording-plan.json (only the fields that change what is RECORDED, plus the
         locale and platform) and DIR/beats.json (the demo-video harness's BEATS list). Pass
         recording-plan.json as the harness's --storyboard: the harness stamps its hash into the
         take's sidecar.
derive   reads the take and its sidecar (one milestone per step id, with t_video and t_proof) and
         writes, with a stem of task[.platform][.locale]: <stem>.md, <stem>.article.json,
         <stem>.vtt (captions), <stem>.chapters.vtt, img/<stem>-<id>.png (the frame at t_proof, with
         a highlight when the sidecar holds a bbox), clips/<stem>-<id>.mp4 for steps that ask for
         one, <stem>.mp4, <stem>.derived.json (with an average hash per screenshot when Pillow is
         installed). It refuses when the sidecar's plan hash differs from the sheet's current plan
         hash: an action, proof text or locale changed since the take, so re-record. Editing a
         caption, alt text or any article wording changes nothing recorded and never forces a
         re-record. --strings swaps wording or a whole locale by step id; a locale take is recorded
         from `plan --strings`, so its own plan hash is what gets stamped.
queue    lists the sheets whose `surfaces` match any changed path: the replay queue.
distance prints the Hamming distance between two screenshot hashes.

Why: references/derive-and-publish.md and references/keeping-fresh.md.
"""
import argparse
import datetime
import fnmatch
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ID_RX = re.compile(r"^[a-z][a-z0-9_-]*$")
REQUIRED_TOP = ["task", "title", "domain", "goal", "path", "result", "steps"]
REQUIRED_STEP = ["id", "do", "proof", "caption", "alt"]
TOP_STRINGS = ("title", "goal", "result", "path", "who", "before", "troubleshooting", "related", "not_covered", "locale")
STEP_STRINGS = ("do", "caption", "alt", "label", "proof", "action")
HEADINGS = {"who": "Who can do this", "path": "Path", "before": "Before you start", "steps": "Steps",
            "result": "You should see", "trouble": "If something goes wrong", "related": "Related",
            "not_covered": "Not covered here", "checked": "Checked against build {build} on {date}.",
            "source": "Source"}


def load_sheet(path):
    p = pathlib.Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        raise SystemExit("PyYAML is needed to read a .yaml sheet (pip install pyyaml), or save the sheet as .json")
    return yaml.safe_load(text)


def with_strings(sheet, strings):
    """Wording or locale overrides keyed by step id. do, caption, alt and label are wording. proof,
    action and locale are recorded fields: override them only for a take recorded in that locale,
    whose own plan (plan --strings) is what the harness stamped."""
    if not strings:
        return sheet
    out = json.loads(json.dumps(sheet))
    for k in TOP_STRINGS:
        if k in strings:
            out[k] = strings[k]
    if "_headings" in strings:
        out["_headings"] = strings["_headings"]
    for s in out["steps"]:
        s.update({k: v for k, v in (strings.get(s["id"]) or {}).items() if k in STEP_STRINGS})
    return out


def placeholders(node, where="sheet"):
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            found += placeholders(v, f"{where}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found += placeholders(v, f"{where}[{i}]")
    elif isinstance(node, str) and (node.startswith("TODO") or "PLACEHOLDER" in node):
        found.append(where)
    return found


def lint(sheet, draft=False):
    errs = []
    for k in REQUIRED_TOP:
        if not sheet.get(k):
            errs.append(f"sheet is missing '{k}'")
    seen = set()
    writes_any = False
    for i, s in enumerate(sheet.get("steps") or [], 1):
        sid = s.get("id", f"#{i}")
        if sid in seen:
            errs.append(f"duplicate step id '{sid}'")
        seen.add(sid)
        if not ID_RX.match(str(s.get("id", ""))):
            errs.append(f"step {i}: id must match {ID_RX.pattern}")
        for k in REQUIRED_STEP:
            if not s.get(k):
                errs.append(f"step {sid}: missing '{k}'" + (" (every step needs text the screen must show)" if k == "proof" else ""))
        if s.get("alt") and len(str(s["alt"]).split()) < 3:
            errs.append(f"step {sid}: alt text should say what the picture shows")
        if s.get("label") and s.get("do") and str(s["label"]) not in str(s["do"]):
            errs.append(f"step {sid}: label '{s['label']}' does not appear in its sentence, so it cannot be bolded")
        typed = ((s.get("action") or {}).get("type") or {}).get("text")
        if typed is not None and s.get("proof") is not None and str(typed).strip() == str(s["proof"]).strip():
            errs.append(f"step {sid}: proof only repeats the typed text; use something the step caused (a total, a label, a state)")
        writes_any = writes_any or bool(s.get("writes"))
    if writes_any and not sheet.get("writes"):
        errs.append("a step writes but the task does not declare 'writes: true'")
    left = placeholders(sheet)
    if left and not draft:
        errs.append(f"{len(left)} placeholder(s) remain (TODO or PLACEHOLDER): {', '.join(left[:6])}" + (" ..." if len(left) > 6 else ""))
    return errs


def stem(sheet):
    return ".".join(str(x) for x in (sheet["task"], sheet.get("platform"), sheet.get("locale")) if x)


def plan(sheet):
    """Only what changes what is recorded. Wording edits stay out, so they never force a re-record."""
    return [{"id": s["id"], "action": s.get("action") or {}, "proof": s["proof"], "writes": bool(s.get("writes")),
             "mark": (s.get("shot") or {}).get("mark")} for s in sheet["steps"]]


def plan_bytes(sheet):
    body = {"locale": sheet.get("locale"), "platform": sheet.get("platform"), "steps": plan(sheet)}
    return json.dumps(body, sort_keys=True, indent=1, ensure_ascii=False).encode("utf-8")


def plan_hash(sheet):
    return hashlib.sha256(plan_bytes(sheet)).hexdigest()[:16]


def js_has_text(text):
    return "((document.body||{}).innerText||'').includes(" + json.dumps(text) + ")"


def beats(sheet, hold=4):
    """The harness's BEATS list: label is the step id, so the sidecar's milestone names are step ids."""
    out = []
    for s in sheet["steps"]:
        a = s.get("action") or {}
        b = {"label": s["id"], "hold": s.get("hold", hold), "ready": js_has_text(s["proof"])}
        if a.get("click") or a.get("tap"):
            b["click"] = a.get("click") or a.get("tap")
        if a.get("type"):
            b["type"] = a["type"]
        if a.get("js"):
            b["js"] = a["js"]
        mark = (s.get("shot") or {}).get("mark")
        if mark and not (b.keys() & {"click", "type", "js"}):
            b["motion"] = f"__cine.spotlight({json.dumps(mark)})"
        out.append(b)
    return out


def vtt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{cmd[0]} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def duration(video):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]).strip())


def bold_label(do, label):
    return re.sub(re.escape(label), f"**{label}**", do, count=1) if label and label in do else do


def average_hash(png):
    """64-bit average hash as 16 hex digits, or None when Pillow is not installed."""
    try:
        from PIL import Image
    except ImportError:
        return None
    px = list(Image.open(png).convert("L").resize((8, 8)).getdata())
    avg = sum(px) / 64
    return f"{sum(1 << i for i, p in enumerate(px) if p >= avg):016x}"


def distance(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def surface_matches(surface, path):
    """file:<glob> matches the path; route:/a/b matches when /a/b/ is a directory part of the path;
    component:Name matches when the name, lower-cased with - _ . removed, is inside the file's."""
    kind, _, token = str(surface).partition(":")
    low = path.lower().replace("\\", "/")
    if kind == "file":
        return fnmatch.fnmatch(low, token.lower())
    directory, _, base = low.rpartition("/")
    if kind == "component":
        flat = re.sub(r"[-_.]", "", low.rsplit(".", 1)[0] if "." in base else low)
        return re.sub(r"[-_.]", "", token.lower()) in flat
    if kind == "route":
        return ("/" + token.strip("/").lower() + "/") in ("/" + directory + "/")
    return False


def queue(sheets_dir, changed):
    base = pathlib.Path(sheets_dir)
    hits = []
    for p in sorted(list(base.glob("*.yaml")) + list(base.glob("*.yml")) + list(base.glob("*.json"))):
        sheet = load_sheet(p)
        matched = sorted({str(sf) for sf in sheet.get("surfaces", []) for c in changed if surface_matches(sf, c)})
        if matched:
            hits.append({"sheet": p.name, "task": stem(sheet), "matched": matched})
    return hits


def derive(sheet, take, sidecar, out, build, date, scale, make_video, allow_drift):
    errs = lint(sheet)
    if errs:
        raise SystemExit("sheet is not publishable:\n  " + "\n  ".join(errs))
    side = json.loads(pathlib.Path(sidecar).read_text())
    stamped = (side.get("storyboard") or {}).get("sha256")
    current = plan_hash(sheet)
    if stamped != current and not allow_drift:
        raise SystemExit(f"the sheet's recorded fields changed since the take (take {stamped}, sheet {current}): "
                         "an action, proof text or locale differs, so re-record. Wording edits alone never do this.")
    by_id = {m["milestone"]: m for m in side["milestones"]}
    missing = [s["id"] for s in sheet["steps"] if s["id"] not in by_id]
    if missing:
        raise SystemExit(f"the take has no milestone for step(s) {missing}: it does not match this sheet")
    out = pathlib.Path(out)
    (out / "img").mkdir(parents=True, exist_ok=True)
    (out / "clips").mkdir(exist_ok=True)
    name, total = stem(sheet), duration(take)
    H = {**HEADINGS, **(sheet.get("_headings") or {})}
    ends = [by_id[s["id"]]["t_video"] for s in sheet["steps"][1:]] + [by_id["END"]["t_video"] if "END" in by_id else total]
    shots, clips, hashes, vtt, chapters = {}, {}, {}, ["WEBVTT", ""], ["WEBVTT", ""]
    for n, (s, end) in enumerate(zip(sheet["steps"], ends), 1):
        m = by_id[s["id"]]
        png = out / "img" / f"{name}-{s['id']}.png"
        cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", f"{m['t_proof']:.3f}", "-i", str(take), "-frames:v", "1"]
        if m.get("bbox"):
            x, y, w, h = (v * scale for v in m["bbox"])
            cmd += ["-vf", f"drawbox=x={x:.0f}:y={y:.0f}:w={w:.0f}:h={h:.0f}:color=0xFF3B30@0.95:t=8"]
        run(cmd + [str(png)])
        shots[s["id"]] = png.name
        hashes[s["id"]] = average_hash(png)
        if s.get("clip"):
            secs = float((s["clip"] if isinstance(s["clip"], dict) else {}).get("seconds", 6))
            mp4 = out / "clips" / f"{name}-{s['id']}.mp4"
            run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-ss", f"{m['t_video']:.3f}", "-i", str(take),
                 "-t", f"{min(secs, max(end - m['t_video'], 1.0)):.3f}", "-an", "-vf", "scale=1280:-2",
                 "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)])
            clips[s["id"]] = mp4.name
        span = f"{vtt_time(m['t_video'])} --> {vtt_time(max(end, m['t_video'] + 0.5))}"
        vtt += [str(n), span, s["caption"], ""]
        chapters += [str(n), span, s["do"], ""]
    (out / f"{name}.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (out / f"{name}.chapters.vtt").write_text("\n".join(chapters), encoding="utf-8")
    if make_video:
        run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(take), "-an", "-vf", "scale=1920:-2",
             "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out / f"{name}.mp4")])
    lang = f' srclang="{sheet["locale"]}"' if sheet.get("locale") else ""
    md = [f"# {sheet['title']}", "", sheet["goal"], ""]
    if sheet.get("who"):
        md += [f"**{H['who']}:** {', '.join(str(w) if sheet.get('locale') else str(w).capitalize() for w in sheet['who'])}"]
    md += [f"**{H['path']}:** `{sheet['path']}`", ""]
    if make_video:
        md += [f'<video controls src="{name}.mp4"><track kind="captions" src="{name}.vtt"{lang} default>'
               f'<track kind="chapters" src="{name}.chapters.vtt"{lang}></video>', ""]
    if sheet.get("before"):
        md += [f"## {H['before']}", ""] + [f"- {b['text'] if isinstance(b, dict) else b}" for b in sheet["before"]] + [""]
    md += [f"## {H['steps']}", ""]
    for n, s in enumerate(sheet["steps"], 1):
        md += [f"{n}. {bold_label(s['do'], s.get('label'))}", f"   ![{s['alt']}](img/{shots[s['id']]})"]
        if s["id"] in clips:
            md += [f'   <video muted loop autoplay playsinline src="clips/{clips[s["id"]]}"></video>']
    last = sheet["steps"][-1]
    md += ["", f"## {H['result']}", "", sheet["result"], "", f"![{last['alt']}](img/{shots[last['id']]})", ""]
    if sheet.get("troubleshooting"):
        md += [f"## {H['trouble']}", ""] + [f"- **{t['when']}** {t['then']}" for t in sheet["troubleshooting"]] + [""]
    if sheet.get("not_covered"):
        md += [f"## {H['not_covered']}", "", str(sheet["not_covered"]), ""]
    if sheet.get("related"):
        md += [f"## {H['related']}", ""] + [f"- {r}" for r in sheet["related"]] + [""]
    md += ["---", f"{H['checked'].format(build=build or 'unknown', date=date)} {H['source']}: `{name}` {current}."]
    (out / f"{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    art = {"task": sheet["task"], "platform": sheet.get("platform"), "locale": sheet.get("locale"), "title": sheet["title"],
           "domain": sheet["domain"], "goal": sheet["goal"], "path": sheet["path"], "who": sheet.get("who", []),
           "result": sheet["result"], "checked_build": build, "checked_date": date, "surfaces": sheet.get("surfaces", []),
           "plan_hash": current,
           "steps": [{"id": s["id"], "do": s["do"], "label": s.get("label"), "image": f"img/{shots[s['id']]}", "alt": s["alt"],
                      "caption": s["caption"], "video_t": by_id[s["id"]]["t_video"], "clip": clips.get(s["id"])}
                     for s in sheet["steps"]]}
    (out / f"{name}.article.json").write_text(json.dumps(art, indent=1, ensure_ascii=False), encoding="utf-8")
    derived = {"task": name, "plan_hash": current, "take": str(take), "images": shots, "hashes": hashes, "clips": clips,
               "date": date, "build": build}
    (out / f"{name}.derived.json").write_text(json.dumps(derived, indent=1), encoding="utf-8")
    return derived


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["lint", "plan", "derive", "queue", "distance"])
    ap.add_argument("sheet", help="the sheet; for queue the sheets directory; for distance the first hash")
    ap.add_argument("other", nargs="?", help="distance: the second hash")
    ap.add_argument("--out")
    ap.add_argument("--take")
    ap.add_argument("--sidecar")
    ap.add_argument("--build")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--strings")
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--hold", type=float, default=4.0)
    ap.add_argument("--changed", nargs="*", default=[])
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--allow-drift", action="store_true")
    ap.add_argument("--draft", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "distance":
        print(distance(a.sheet, a.other))
        return 0
    if a.cmd == "queue":
        hits = queue(a.sheet, a.changed)
        print("\n".join(f"{h['task']}  ({h['sheet']})  matched {h['matched']}" for h in hits) or "no sheet names a changed surface")
        return 0
    sheet = with_strings(load_sheet(a.sheet), json.loads(pathlib.Path(a.strings).read_text()) if a.strings else None)
    if a.cmd == "lint":
        errs = lint(sheet, draft=a.draft)
        left = placeholders(sheet)
        print("\n".join(errs) if errs else f"ok: {len(sheet['steps'])} steps, plan {plan_hash(sheet)}"
              + (f", {len(left)} placeholder(s) remain (draft)" if left else ""))
        return 1 if errs else 0
    if a.cmd == "plan":
        errs = lint(sheet)
        if errs:
            raise SystemExit("sheet is not recordable:\n  " + "\n  ".join(errs))
        out = pathlib.Path(a.out or ".")
        out.mkdir(parents=True, exist_ok=True)
        (out / "recording-plan.json").write_bytes(plan_bytes(sheet))
        (out / "beats.json").write_text(json.dumps(beats(sheet, a.hold), indent=1), encoding="utf-8")
        print(f"plan {plan_hash(sheet)}: {out / 'recording-plan.json'}, {out / 'beats.json'}")
        return 0
    if not (a.take and a.sidecar and a.out):
        raise SystemExit("derive needs --take, --sidecar and --out")
    derived = derive(sheet, a.take, a.sidecar, a.out, a.build, a.date, a.scale, not a.no_video, a.allow_drift)
    print(f"derived {derived['task']}: {len(derived['images'])} screenshots, {len(derived['clips'])} clips -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
