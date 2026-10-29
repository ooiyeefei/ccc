#!/usr/bin/env python3
"""OCR the frames of a finished film for words and addresses that must not be on screen.

    python frame_scan.py film.mp4 [--fps 1] [--ban demo,test,sample,uat,probe]
                         [--allow-domain film.example.com ...] [--brands brands.txt]
                         [--figure 21,456 ...] [--workdir DIR] [--workers 2] [--out report.json]
    python frame_scan.py --text FILE [FILE ...] [same word, domain, brand and figure options]

Extracts one frame per 1/fps seconds with ffmpeg, reads each with tesseract, and flags: a banned
word, an e-mail address whose domain is not allowed, a brand or bank name from --brands (one per
line), a figure from --figure (a stale number, comma-tolerant, whole number only), a raw record id,
a browser download banner. Prints every hit with its second and exits 1 if there is any. A frame OCR
could not read is not a pass: it is counted and reported.

--text scans the text that never reaches a frame (subtitle and chapter files, file names, an upload's
title and description, page-text dumps taken before filming) with the same rules, one line at a time.

Words are matched whole, in any language you list; the default list is English, so add the other
languages' equivalents. The brand check is off unless --brands FILE is given (one name per line;
none is supplied here), and every e-mail address is a hit unless its domain is in --allow-domain.

Frames go under --workdir (default ./.frame-scan next to where you run it), never /tmp, and are
deleted after reading. Needs ffmpeg and tesseract on the PATH. Why this gate exists: references/post.md.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

DEFAULT_BAN = "demo,demos,test,tests,testing,sample,samples,uat,probe,presenter,designated"
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
RAW_ID = re.compile(r"\b[a-z0-9]{32}\b|\bjs[a-z0-9]{22,}\b")
OTHER = {
    "download_banner": re.compile(r"download\s+started", re.I),
    "pdf_viewer_copy_suffix": re.compile(r"\(\d\)\s*\.pdf", re.I),
}


def word_list(spec):
    """Words from a list or from a string split on commas, pipes and whitespace, so a natural
    'demo|test' or 'demo test' is read as two words instead of one that matches nothing."""
    parts = spec if isinstance(spec, (list, tuple)) else re.split(r"[,|\s]+", spec)
    return [w.strip() for w in parts if w.strip()]


def ban_regex(words):
    ws = [re.escape(w) for w in word_list(words)]
    return re.compile(r"(?<![A-Za-z])(" + "|".join(ws) + r")(?![A-Za-z])", re.I) if ws else None


def brand_regex(names):
    ns = [re.escape(n.strip()) for n in names if n.strip()]
    return re.compile(r"(?<![A-Za-z])(" + "|".join(ns) + r")(?![A-Za-z])", re.I) if ns else None


def figure_regex(figures):
    """Each figure as a whole number, tolerant of thousands commas: 21,456 matches 21456 and 21,456
    but not 121,456 or 21,4567."""
    pats = []
    for f in figures:
        whole, dot, frac = f.replace(",", "").partition(".")
        if not whole.isdigit():
            continue
        pats.append(",?".join(whole) + (re.escape(dot + frac) if dot else ""))
    return re.compile(r"(?<![\d,.])(" + "|".join(pats) + r")(?!\d)") if pats else None


def scan_text(text, ban, allow_domains=(), brands=None, figures=None):
    """Hits found in one frame's OCR text, as {kind: [matches]}."""
    hits = {}
    if figures:
        for m in figures.finditer(text):
            hits.setdefault("stale_figure", []).append(m.group(0))
    if ban:
        for m in ban.finditer(text):
            hits.setdefault("banned_word", []).append(m.group(0))
    if brands:
        for m in brands.finditer(text):
            hits.setdefault("brand", []).append(m.group(0))
    allowed = tuple(d.lower() for d in allow_domains)
    for m in EMAIL.finditer(text):
        domain = m.group(0).split("@", 1)[1].lower().rstrip(".")
        if not any(domain == d or domain.endswith("." + d) for d in allowed):
            hits.setdefault("email", []).append(m.group(0))
    for m in RAW_ID.finditer(text):
        hits.setdefault("raw_id", []).append(m.group(0))
    for kind, rx in OTHER.items():
        for m in rx.finditer(text):
            hits.setdefault(kind, []).append(m.group(0))
    return hits


def ocr(path):
    r = subprocess.run(["tesseract", str(path), "-", "--psm", "11"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def extract(video, fps, outdir):
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(video),
                    "-vf", f"fps={fps}", str(outdir / "f%06d.png")], check=True)
    return sorted(outdir.glob("f*.png"))


def scan_files(files, ban, allow_domains, brands, figures):
    rows = []
    for f in files:
        for n, line in enumerate(pathlib.Path(f).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            hits = scan_text(line, ban, allow_domains, brands, figures)
            if hits:
                rows.append({"file": str(f), "line": n, "hits": hits})
    return rows


def scan_video(video, fps, ban, allow_domains, brands, workdir, workers, figures=None):
    workdir.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="scan-", dir=str(workdir)))
    frames = extract(video, fps, tmp)

    def one(f):
        idx = int(f.stem[1:]) - 1
        text = ocr(f)
        f.unlink()
        return idx / fps, text

    rows, unreadable = [], 0
    with ThreadPoolExecutor(workers) as ex:
        for t, text in ex.map(one, frames):
            if text is None:
                unreadable += 1
                continue
            hits = scan_text(text, ban, allow_domains, brands, figures)
            if hits:
                rows.append({"t": round(t, 2), "hits": hits})
    try:
        tmp.rmdir()
    except OSError:
        pass
    return {"video": str(video), "frames": len(frames), "unreadable": unreadable, "flagged": rows}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video", nargs="?")
    ap.add_argument("--text", nargs="+", metavar="FILE", help="scan text files instead of a video")
    ap.add_argument("--figure", action="append", default=[], help="a stale figure that must appear nowhere")
    ap.add_argument("--fps", type=float, default=1.0)
    ap.add_argument("--ban", default=DEFAULT_BAN)
    ap.add_argument("--allow-domain", action="append", default=[])
    ap.add_argument("--brands")
    ap.add_argument("--workdir", default=".frame-scan")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    brands = brand_regex(open(args.brands).read().splitlines()) if args.brands else None
    ban, figures = ban_regex(args.ban), figure_regex(args.figure)
    if ban is None:
        raise SystemExit("the banned-word list is empty: a scan with no words cannot fail. Pass --ban word,word")
    print("checks on: banned words" + (", brands" if brands else " (brand check OFF: pass --brands FILE)")
          + (", stale figures" if figures else "") + f", e-mail domains allowed: {args.allow_domain or 'none'}")
    if args.text:
        rows = scan_files(args.text, ban, args.allow_domain, brands, figures)
        for r in rows:
            print(f"  {r['file']}:{r['line']}  " + "; ".join(f"{k}: {sorted(set(v))}" for k, v in r["hits"].items()))
        print(f"{len(args.text)} file(s) scanned, {len(rows)} line(s) flagged")
        return 1 if rows else 0
    if not args.video:
        raise SystemExit("give a video, or --text FILE ...")
    res = scan_video(pathlib.Path(args.video), args.fps, ban, args.allow_domain, brands,
                     pathlib.Path(args.workdir), args.workers, figures)
    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(res, indent=1))
    print(f"{res['frames']} frames scanned, {res['unreadable']} unreadable, {len(res['flagged'])} flagged")
    for row in res["flagged"]:
        print(f"  t={row['t']:>7.2f}s  " + "; ".join(f"{k}: {sorted(set(v))}" for k, v in row["hits"].items()))
    return 1 if res["flagged"] or res["unreadable"] else 0


if __name__ == "__main__":
    sys.exit(main())
