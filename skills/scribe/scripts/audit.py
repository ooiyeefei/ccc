#!/usr/bin/env python3
"""
Audit normalized transcripts before anyone summarizes them.

    audit.py TRANSCRIPT_DIR [--low-confidence 0.60] [--json]

Two checks, both of which catch failures a summarizer physically cannot:

  RECORDING GAPS -- a recorder stopped and restarted mid-meeting drops content
    silently. The summary that results looks complete and is not. Detected by
    a file whose final segment runs to the very end of its audio without
    terminal punctuation, i.e. it was cut off mid-sentence.

  RISKY SPANS -- numbers and proper nouns sitting on low-confidence audio.
    This is where ASR noise turns into business fact: a garbled span becomes
    "~8,000 users" once a summarizer tidies it up, and nothing downstream can
    tell that apart from a real figure. Flag them here or never.
"""

import argparse, json, re, sys
from pathlib import Path

from _thresholds import DEFAULT_THRESHOLD, describe, resolve_threshold

TERMINAL = tuple(".!?\"')]")
RUNS_TO_EOF_S = 1.0       # speech still going this close to EOF == the file was cut
LATE_START_S = 5.0        # silence before first speech; a restart leaves none
LONG_SILENCE_S = 45.0     # unexplained quiet stretch inside one file
PUNCT_USABLE = 0.20       # below this rate, mid-sentence detection is unavailable

NUMBERISH = re.compile(
    r"(\d[\d,._]*\s*(?:%|k\b|m\b|bn?\b)?)"          # 8,000  30%  5k
    r"|((?:RM|USD|SGD|MYR|\$|€|£)\s*\d[\d,._]*)"    # RM2,000  $40
    r"|(\b\d+\s*(?:ringgit|dollars?|users?|customers?|tonnes?|tons?)\b)",
    re.I,
)
# Capitalised token that is not sentence-initial: a weak proper-noun signal.
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-zA-Z]{2,}(?:\.[a-z]{2,})?)\b")

STOP = {"I", "The", "And", "But", "So", "Yeah", "Okay", "OK", "Because",
        "This", "That", "There", "Then", "What", "When", "Who", "How", "Why",
        "We", "You", "They", "It", "If", "No", "Yes", "My", "Like"}


def load(directory):
    docs = []
    for p in sorted(Path(directory).glob("*.json")):
        if p.name == "manifest.json":
            continue
        docs.append(json.loads(p.read_text()))
    return docs


def punctuation_rate(segs):
    """How often this provider ends a segment with terminal punctuation.

    Local Whisper often punctuates almost nothing, which makes "ends
    mid-sentence" meaningless. Measure it rather than assume it.
    """
    if not segs:
        return 0.0
    return sum(1 for s in segs if s["text"].rstrip().endswith(TERMINAL)) / len(segs)


def check_gaps(doc):
    """Was this file cut off, restarted, or hiding a long silence?

    The load-bearing signal is speech still running when the audio ends. A
    recording that stopped naturally has trailing silence; one that was cut
    does not. Punctuation is only a corroborating signal, and only when the
    provider punctuates at all.
    """
    findings = []
    segs = doc.get("segments") or []
    dur = doc.get("audio", {}).get("duration_s", 0.0)
    name = Path(doc.get("audio", {}).get("path", "?")).name
    if not segs:
        return [{"kind": "empty", "file": name,
                 "detail": "no segments decoded at all"}]

    last = segs[-1]
    text = last["text"].rstrip()
    tail_silence = dur - last["end"]
    if tail_silence < RUNS_TO_EOF_S:
        detail = (f"speech runs to the last {tail_silence:.1f}s of a "
                  f"{dur/60:.1f} min file -- a recording that ended naturally "
                  f"leaves trailing silence, so this one was almost certainly "
                  f"cut. Whatever was said next is not in this audio.")
        if punctuation_rate(segs) >= PUNCT_USABLE and not text.endswith(TERMINAL):
            detail += " The final segment also breaks mid-sentence."
        findings.append({"kind": "truncated", "file": name,
                         "at": round(last["end"], 1), "detail": detail,
                         "tail": text[-90:]})

    first = segs[0]
    if first["start"] > LATE_START_S:
        findings.append({
            "kind": "late_start", "file": name, "at": round(first["start"], 1),
            "detail": f"first speech at {first['start']:.0f}s -- may be a restart",
        })

    for a, b in zip(segs, segs[1:]):
        if b["start"] - a["end"] > LONG_SILENCE_S:
            findings.append({
                "kind": "silence", "file": name, "at": round(a["end"], 1),
                "detail": (f"{b['start']-a['end']:.0f}s of no speech at "
                           f"{a['end']/60:.1f} min"),
            })
    return findings


def check_between_files(docs):
    """Content lost where one file was cut and another picks up.

    This is the failure that produces a summary reading as complete when a
    whole stretch of the meeting was never recorded.
    """
    findings = []
    ordered = sorted(docs, key=lambda d: d.get("audio", {}).get("path", ""))
    for cur, nxt in zip(ordered, ordered[1:]):
        segs = cur.get("segments") or []
        if not segs:
            continue
        dur = cur.get("audio", {}).get("duration_s", 0.0)
        if dur - segs[-1]["end"] < RUNS_TO_EOF_S:
            findings.append({
                "kind": "lost_between",
                "file": Path(cur["audio"]["path"]).name,
                "detail": (f"cut at its end, and "
                           f"{Path(nxt['audio']['path']).name} picks up "
                           f"elsewhere -- the meeting between them was never "
                           f"recorded. Treat that stretch as having no source."),
            })
    return findings


def check_risky(doc, threshold):
    """Numbers and proper nouns resting on audio the model was unsure about."""
    risky = []
    name = Path(doc.get("audio", {}).get("path", "?")).name
    for s in doc.get("segments") or []:
        c = s.get("confidence")
        if c is None or c >= threshold:
            continue
        text = s["text"]
        nums = [m.group(0).strip() for m in NUMBERISH.finditer(text)]
        props = [m.group(1) for m in PROPER.finditer(text) if m.group(1) not in STOP]
        if nums or props:
            risky.append({
                "file": name, "at": round(s["start"], 1),
                "timestamp": f"{int(s['start'])//60:02d}:{int(s['start'])%60:02d}",
                "confidence": round(c, 3),
                "numbers": nums, "proper_nouns": sorted(set(props))[:6],
                "text": text,
            })
    return risky


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("directory")
    ap.add_argument("--low-confidence", default=DEFAULT_THRESHOLD,
                    help='percentile of this recording ("p20", default) or an '
                         'absolute value ("0.6")')
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    docs = load(args.directory)
    if not docs:
        sys.exit(f"no transcript json found in {args.directory}")

    all_conf = [s["confidence"] for d in docs for s in d.get("segments") or []]
    threshold, thr_desc = resolve_threshold(args.low_confidence, all_conf)
    gaps = [f for d in docs for f in check_gaps(d)]
    gaps += check_between_files(docs)
    risky = [r for d in docs for r in check_risky(d, threshold)]
    total = sum(d.get("audio", {}).get("duration_s", 0.0) for d in docs)
    diarized = any(s.get("speaker") for d in docs for s in d.get("segments") or [])
    scored = any(s.get("confidence") is not None
                 for d in docs for s in d.get("segments") or [])
    punct = max((punctuation_rate(d.get("segments") or []) for d in docs),
                default=0.0)

    report = {
        "files": len(docs),
        "total_minutes": round(total / 60, 1),
        "diarized": diarized,
        "confidence_available": scored,
        "mid_sentence_detection": punct >= PUNCT_USABLE,
        "threshold": round(threshold, 4),
        "threshold_spec": thr_desc,
        "confidence_distribution": describe(all_conf),
        "gaps": gaps,
        "risky_spans": risky,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"{len(docs)} file(s), {total/60:.1f} min total")
    print(f"diarization: {'yes' if diarized else 'NO -- speakers unlabelled, '
                                                'attribution will be inference'}")
    print(f"confidence:  {'yes' if scored else 'NO -- cannot flag risky spans'}")
    if scored:
        print(f"  {describe(all_conf)}")
        print(f"  low-confidence bar: {thr_desc}")
    if punct < PUNCT_USABLE:
        print(f"mid-sentence detection: UNAVAILABLE (provider punctuates "
              f"{punct*100:.0f}% of segments) -- truncation judged on "
              f"trailing silence alone")

    print(f"\n-- coverage ({len(gaps)}) --")
    if not gaps:
        print("  clean: no truncation, late starts, or long silences")
    for g in gaps:
        print(f"  [{g['kind']}] {g['file']}: {g['detail']}")
        if g.get("tail"):
            print(f"      ...{g['tail']}")

    print(f"\n-- risky spans ({len(risky)}) --")
    if not risky and scored:
        print("  none: no numbers or names on low-confidence audio")
    for r in risky[:40]:
        bits = ", ".join(filter(None, [
            "nums: " + "/".join(r["numbers"]) if r["numbers"] else "",
            "names: " + "/".join(r["proper_nouns"]) if r["proper_nouns"] else "",
        ]))
        print(f"  {r['file']} {r['timestamp']} (conf {r['confidence']}) {bits}")
        print(f"      {r['text'][:120]}")
    if len(risky) > 40:
        print(f"  ... and {len(risky)-40} more (use --json for all)")

    if gaps or risky:
        print("\nEvery finding above needs a disposition: corroborate it against "
              "a second transcript, confirm it with the user, or carry it into "
              "the notes marked as uncertain.")


if __name__ == "__main__":
    main()
