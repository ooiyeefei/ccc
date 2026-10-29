#!/usr/bin/env python3
"""Scan plain narration for pace and for the patterns that make a voiceover read as machine-written.

    python narration_scan.py lines.json [--lo 2.2] [--hi 2.6] [--avoid ledger,accrual] [--json]

lines.json is a list of {"id": "2c", "text": "...", "window": 12.5, "allow": ["contrast"]} or
{"lines": [...]}. The window, in seconds, is "window" or "end" minus "start". "allow" lists approved
exceptions, each with its reason recorded in the plan (any finding name, hard or style). The id/text
shape is the one voice_lines.py takes. A line with no window is reported as "pace unchecked" and
counted, so silence never reads as a pass.

Exit 0 when no line has a HARD finding (a digit, a dash, pace outside the band, an exclamation).
Style hits are prompts to look, not verdicts, and are printed without changing the exit code.
--avoid lists words the viewer would not say (a marketing brief's jargon); each one found is a style hit.
Rules and reasons: references/narration.md.
"""
import argparse
import collections
import json
import re
import sys

HARD = {
    "digit": r"\d",
    "dash": r"[\u2013\u2014]| - ",
    "exclamation": r"!",
}

STYLE = {
    "contrast": r"\bnot (just|only|merely)\b|,\s*not\b|\bnot a\b[^.]*,\s*but\b|\bisn't\b[^.]*\bit's\b",
    "denial_stack": r"\bno \w+(?:\s\w+)?[,;.]\s*no \w+",
    "colon": r":",
    "semicolon": r";",
    "filler": r"\b(just|simply|really|very|actually|basically|literally|truly)\b|\brather than\b|\binstead of\b|\bat a glance\b",
    "signpost": r"\b(here is|here's|this is|here are) (everything|what|how|the)\b|\blet's (dive|take a look)\b",
    "flourish": r"\b(seamless(ly)?|effortless(ly)?|powerful|stunning|revolutionary|game-changing|cutting-edge|robust|supercharge)\b",
    "claim_check": r"\b(automatic(ally)?|connects? to your bank|files? (it )?for you|pays? (your|the)|guarantee[sd]?)\b",
}

WORD = re.compile(r"[A-Za-z']+(?:-[A-Za-z']+)*")
SENT = re.compile(r"(?<=[.?!])\s+")


def words(text):
    return len(WORD.findall(text))


def sentences(text):
    return [s for s in SENT.split(text.strip()) if s]


def first_word(sentence):
    m = WORD.search(sentence)
    return m.group(0).lower() if m else ""


def context(text, m, pad=28):
    a, b = max(0, m.start() - pad), min(len(text), m.end() + pad)
    return "..." + text[a:b].replace("\n", " ") + "..."


def scan_line(line, lo, hi, avoid=None):
    text = line["text"]
    allow = set(line.get("allow", []))
    out = {"id": line["id"], "words": words(text), "wps": None, "hard": [], "style": [], "allowed": []}
    window = line.get("window") or ((line["end"] - line["start"]) if "end" in line and "start" in line else None)
    if not window:
        out["unchecked"] = True
    if window:
        out["wps"] = round(out["words"] / float(window), 2)
        if not lo <= out["wps"] <= hi:
            (out["allowed"] if "pace" in allow else out["hard"]).append(
                ("pace", f"{out['wps']} w/s against a {lo}-{hi} band"))
    for name, rx in HARD.items():
        for m in re.finditer(rx, text):
            (out["allowed"] if name in allow else out["hard"]).append((name, context(text, m)))
    for name, rx in STYLE.items():
        for m in re.finditer(rx, text, re.I):
            (out["allowed"] if name in allow else out["style"]).append((name, context(text, m)))
    if avoid:
        for m in avoid.finditer(text):
            (out["allowed"] if "jargon" in allow else out["style"]).append(("jargon", context(text, m)))
    firsts = [first_word(s) for s in sentences(text)]
    for a, b in zip(firsts, firsts[1:]):
        if a and a == b:
            out["style"].append(("repeated_opener", f"two sentences in a row open with '{a}'"))
    return out, firsts


def avoid_regex(words):
    ws = [re.escape(w.strip()) for w in words if w.strip()]
    return re.compile(r"(?<![A-Za-z])(" + "|".join(ws) + r")(?![A-Za-z])", re.I) if ws else None


def scan(lines, lo=2.2, hi=2.6, avoid=()):
    results, openers = [], collections.Counter()
    rx = avoid_regex(avoid)
    for line in lines:
        res, firsts = scan_line(line, lo, hi, rx)
        results.append(res)
        openers.update(f for f in firsts if f)
    heavy = [(w, n) for w, n in openers.most_common() if n >= 6]
    return {"lines": results, "openers_6_plus": heavy, "pace_unchecked": sum(1 for r in results if r.get("unchecked")),
            "total_words": sum(r["words"] for r in results),
            "hard_findings": sum(len(r["hard"]) for r in results)}


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data["lines"] if isinstance(data, dict) else data


def report(res):
    lines = [f"{len(res['lines'])} lines, {res['total_words']} words"]
    for r in res["lines"]:
        head = f"  {r['id']:6s} {r['words']:3d}w" + (f"  {r['wps']} w/s" if r["wps"] is not None else "  pace unchecked (no window)")
        flags = [f"HARD {k}: {c}" for k, c in r["hard"]] + [f"{k}: {c}" for k, c in r["style"]]
        flags += [f"allowed {k}" for k, _ in r["allowed"]]
        lines.append(head)
        lines += [f"         {f}" for f in flags]
    lines.append(f"openers used 6+ times: {res['openers_6_plus'] or 'none'}")
    lines.append(f"pace unchecked on {res['pace_unchecked']} of {len(res['lines'])} lines")
    lines.append(f"hard findings: {res['hard_findings']}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("lines_json")
    ap.add_argument("--lo", type=float, default=2.2)
    ap.add_argument("--hi", type=float, default=2.6)
    ap.add_argument("--avoid", default="", help="comma-separated words the viewer would not say")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = scan(load(args.lines_json), args.lo, args.hi, args.avoid.split(","))
    print(json.dumps(res, indent=1) if args.json else report(res))
    return 1 if res["hard_findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
