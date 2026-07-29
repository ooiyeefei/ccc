#!/usr/bin/env python3
"""
Provider-agnostic speech-to-text that normalizes every backend onto one schema.

    transcribe.py AUDIO [AUDIO...] --out DIR [options]

Providers (--provider, default: auto = first one with a key, else local):
    elevenlabs  Scribe            diarization + per-word logprob
    deepgram    Nova              diarization + per-word confidence
    openai      /v1/audio/...     no diarization; any OpenAI-compatible base URL
                                  (Groq, LiteLLM, OpenRouter, vLLM) via --base-url
    local       faster-whisper    no diarization; runs offline, nothing uploaded

Per input file it writes:
    <out>/<stem>.json   normalized schema (see NORMALIZED_SCHEMA below)
    <out>/<stem>.txt    [MM:SS] (SPEAKER) text, low-confidence spans wrapped in <?...?>

Env: ELEVENLABS_API_KEY | DEEPGRAM_API_KEY | OPENAI_API_KEY (+ optional STT_BASE_URL)
"""

import argparse, json, math, os, subprocess, sys
from pathlib import Path

import httpx

from _thresholds import DEFAULT_THRESHOLD, describe, resolve_threshold

NORMALIZED_SCHEMA = """
{
  "provider": str, "model": str, "language": str|null,
  "audio": {"path": str, "duration_s": float},
  "confidence_source": "word_logprob"|"word_thresholds"|"avg_logprob"|"none",
  "segments": [
    {"start": float, "end": float, "speaker": str|null,
     "text": str, "confidence": float|null}
  ]
}
"""

# Grouping thresholds for providers that return words rather than segments.
SEG_MAX_GAP_S = 1.0     # a pause longer than this starts a new segment
SEG_MAX_LEN_S = 20.0    # hard cap so one monologue doesn't become one blob

TIMEOUT = httpx.Timeout(connect=30.0, read=1800.0, write=1800.0, pool=30.0)


# ---------------------------------------------------------------- helpers

def duration_s(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def p_from_logprob(lp):
    """Map a log probability onto [0,1]. Monotonic, not calibrated."""
    if lp is None:
        return None
    try:
        return max(0.0, min(1.0, math.exp(lp)))
    except OverflowError:
        return None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def group_words(words):
    """Words -> segments, splitting on speaker change, long pause, or length cap.

    `words` items: {"text","start","end","speaker","confidence"}
    """
    segments, cur = [], None
    for w in words:
        if not w["text"].strip():
            continue
        starts_new = (
            cur is None
            or w["speaker"] != cur["speaker"]
            or w["start"] - cur["end"] > SEG_MAX_GAP_S
            or w["end"] - cur["start"] > SEG_MAX_LEN_S
        )
        if starts_new:
            if cur:
                segments.append(cur)
            cur = {"start": w["start"], "end": w["end"], "speaker": w["speaker"],
                   "words": [w["text"]], "confs": [w["confidence"]]}
        else:
            cur["end"] = w["end"]
            cur["words"].append(w["text"])
            cur["confs"].append(w["confidence"])
    if cur:
        segments.append(cur)

    return [
        {"start": round(s["start"], 2), "end": round(s["end"], 2),
         "speaker": s["speaker"],
         "text": " ".join(s["words"]).replace("  ", " ").strip(),
         "confidence": mean(s["confs"])}
        for s in segments
    ]


def require_key(env_name):
    key = os.environ.get(env_name)
    if not key:
        sys.exit(
            f"error: {env_name} is not set.\n"
            f"  export {env_name}=...   (or add it to your shell profile)\n"
            f"  or run with --provider local to transcribe offline."
        )
    return key


# ---------------------------------------------------------------- providers

def run_elevenlabs(path, args):
    """POST /v1/speech-to-text — returns words[] with logprob and speaker_id."""
    key = require_key("ELEVENLABS_API_KEY")
    form = {
        "model_id": args.model or "scribe_v1",
        "timestamps_granularity": "word",
        "diarize": "true" if args.diarize else "false",
    }
    if args.language:
        form["language_code"] = args.language
    if args.num_speakers:
        form["num_speakers"] = str(args.num_speakers)
    if args.keyterms:
        # Vocabulary boost for domain nouns. Format has moved before now, so a
        # rejection here must not cost the whole transcription — see retry below.
        form["keyterms"] = json.dumps(args.keyterms)

    def post(fields):
        with open(path, "rb") as fh:
            return httpx.post(
                "https://api.elevenlabs.io/v1/speech-to-text",
                headers={"xi-api-key": key},
                data=fields,
                files={"file": (Path(path).name, fh, "application/octet-stream")},
                timeout=TIMEOUT,
            )

    r = post(form)
    if r.status_code == 422 and "keyterms" in form:
        print("  ! keyterms rejected by API; retrying without vocabulary boost",
              file=sys.stderr)
        form.pop("keyterms")
        r = post(form)
    r.raise_for_status()
    data = r.json()

    words = [
        {"text": w.get("text", ""), "start": w.get("start", 0.0),
         "end": w.get("end", 0.0),
         "speaker": w.get("speaker_id"),
         "confidence": p_from_logprob(w.get("logprob"))}
        for w in data.get("words", [])
        if w.get("type") == "word"
    ]
    return {
        "model": form["model_id"],
        "language": data.get("language_code"),
        "confidence_source": "word_logprob",
        "segments": group_words(words),
    }


def run_deepgram(path, args):
    """POST /v1/listen — utterances[] map straight onto our segment schema."""
    key = require_key("DEEPGRAM_API_KEY")
    model = args.model or "nova-3"
    params = {
        "model": model, "punctuate": "true", "smart_format": "true",
        "utterances": "true",
        "diarize": "true" if args.diarize else "false",
    }
    if args.language:
        params["language"] = args.language
    url = "https://api.deepgram.com/v1/listen"
    if args.keyterms:
        # keyterm repeats once per term; httpx encodes a list as repeated keys.
        params["keyterm"] = args.keyterms

    with open(path, "rb") as fh:
        r = httpx.post(url, params=params,
                       headers={"Authorization": f"Token {key}",
                                "Content-Type": "application/octet-stream"},
                       content=fh.read(), timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()

    utts = data.get("results", {}).get("utterances", [])
    segments = [
        {"start": round(u.get("start", 0.0), 2), "end": round(u.get("end", 0.0), 2),
         "speaker": (f"speaker_{u['speaker']}" if u.get("speaker") is not None else None),
         "text": u.get("transcript", "").strip(),
         "confidence": u.get("confidence")}
        for u in utts if u.get("transcript", "").strip()
    ]
    if not segments:
        # utterances=true can come back empty; fall back to the flat alternative.
        alts = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0]
        if alts.get("transcript"):
            segments = [{"start": 0.0, "end": duration_s(path), "speaker": None,
                         "text": alts["transcript"].strip(),
                         "confidence": alts.get("confidence")}]
    return {"model": model, "language": args.language,
            "confidence_source": "word_thresholds", "segments": segments}


def run_openai(path, args):
    """POST {base}/audio/transcriptions against any OpenAI-compatible gateway.

    verbose_json (segments + avg_logprob) is a whisper-1-era format; newer
    models reject it. We ask for it, and drop to plain json if refused --
    losing confidence, not the transcript.
    """
    key = require_key("OPENAI_API_KEY")
    base = (args.base_url or os.environ.get("STT_BASE_URL")
            or "https://api.openai.com/v1").rstrip("/")
    model = args.model or "whisper-1"

    def post(fmt):
        fields = {"model": model, "response_format": fmt}
        if args.language:
            fields["language"] = args.language
        if args.keyterms:
            # Whisper's `prompt` biases decoding toward these spellings.
            fields["prompt"] = ", ".join(args.keyterms)
        with open(path, "rb") as fh:
            return httpx.post(
                f"{base}/audio/transcriptions",
                headers={"Authorization": f"Bearer {key}"},
                data=fields,
                files={"file": (Path(path).name, fh, "application/octet-stream")},
                timeout=TIMEOUT,
            )

    r = post("verbose_json")
    conf_source = "avg_logprob"
    if r.status_code == 400:
        print(f"  ! {model} refused verbose_json; falling back "
              f"(no confidence scores)", file=sys.stderr)
        r = post("json")
        conf_source = "none"
    r.raise_for_status()
    data = r.json()

    if data.get("segments"):
        segments = []
        for s in data["segments"]:
            conf = p_from_logprob(s.get("avg_logprob"))
            # A high no_speech_prob means the model was decoding near-silence:
            # the classic source of confident hallucination.
            nsp = s.get("no_speech_prob")
            if conf is not None and nsp is not None:
                conf *= (1.0 - nsp)
            segments.append({
                "start": round(s.get("start", 0.0), 2),
                "end": round(s.get("end", 0.0), 2),
                "speaker": None, "text": s.get("text", "").strip(),
                "confidence": conf,
            })
    else:
        segments = [{"start": 0.0, "end": duration_s(path), "speaker": None,
                     "text": data.get("text", "").strip(), "confidence": None}]
        conf_source = "none"

    return {"model": model, "language": data.get("language") or args.language,
            "confidence_source": conf_source, "segments": segments}


def run_local(path, args):
    """faster-whisper. Nothing leaves the machine.

    The two settings that matter for code-switched speech:
      language=...                  pin it, or per-window detection flaps and
                                    the decoder emits fluent wrong-language text
      condition_on_previous_text=0  stop one bad window poisoning the next
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("error: pip install faster-whisper  (or use a hosted --provider)")

    model_name = args.model or "large-v3"
    model = WhisperModel(model_name, device="cpu", compute_type="int8",
                         cpu_threads=max(4, (os.cpu_count() or 8) // 2))
    segs, _info = model.transcribe(
        str(path),
        language=args.language,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200),
        condition_on_previous_text=False,
        temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        initial_prompt=(", ".join(args.keyterms) if args.keyterms else None),
    )
    segments = []
    for s in segs:
        conf = p_from_logprob(s.avg_logprob)
        if conf is not None and s.no_speech_prob is not None:
            conf *= (1.0 - s.no_speech_prob)
        segments.append({"start": round(s.start, 2), "end": round(s.end, 2),
                         "speaker": None, "text": s.text.strip(),
                         "confidence": conf})
    return {"model": model_name, "language": args.language,
            "confidence_source": "avg_logprob", "segments": segments}


PROVIDERS = {"elevenlabs": run_elevenlabs, "deepgram": run_deepgram,
             "openai": run_openai, "local": run_local}
KEY_FOR = {"elevenlabs": "ELEVENLABS_API_KEY", "deepgram": "DEEPGRAM_API_KEY",
           "openai": "OPENAI_API_KEY"}


def pick_provider():
    for name, env in KEY_FOR.items():
        if os.environ.get(env):
            return name
    return "local"


# ---------------------------------------------------------------- rendering

def render_text(doc, threshold):
    """[MM:SS] (SPEAKER) text -- spans below `threshold` wrapped in <? ?>.

    The marking is the point: it survives into whatever reads this file next,
    so a shaky number stays visibly shaky instead of being laundered into fact.
    """
    lines = []
    for s in doc["segments"]:
        ts = f"[{int(s['start']) // 60:02d}:{int(s['start']) % 60:02d}]"
        who = f" ({s['speaker']})" if s.get("speaker") else ""
        text = s["text"]
        c = s.get("confidence")
        if c is not None and c < threshold:
            text = f"<?{text}?>"
        lines.append(f"{ts}{who} {text}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--provider", default="auto",
                    choices=["auto"] + list(PROVIDERS))
    ap.add_argument("--model", help="provider-specific model id")
    ap.add_argument("--language", default=None,
                    help="ISO code. PIN THIS for code-switched speech.")
    ap.add_argument("--diarize", action="store_true",
                    help="speaker labels (elevenlabs/deepgram only)")
    ap.add_argument("--num-speakers", type=int)
    ap.add_argument("--keyterms", default=None,
                    help="comma-separated domain vocabulary (names, jargon)")
    ap.add_argument("--base-url", help="OpenAI-compatible gateway for --provider openai")
    ap.add_argument("--low-confidence", default=DEFAULT_THRESHOLD,
                    help='mark spans below this in the .txt render: percentile '
                         'of this recording ("p20", default) or absolute ("0.6")')
    args = ap.parse_args()

    args.keyterms = ([t.strip() for t in args.keyterms.split(",") if t.strip()]
                     if args.keyterms else None)
    provider = pick_provider() if args.provider == "auto" else args.provider
    if provider != "local" and not args.language:
        print("! no --language pinned: auto-detection is the main cause of "
              "wrong-language gibberish on code-switched audio", file=sys.stderr)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = []

    for path in args.audio:
        path = Path(path)
        print(f"[{provider}] {path.name} ...", file=sys.stderr)
        result = PROVIDERS[provider](path, args)
        doc = {
            "provider": provider,
            "audio": {"path": str(path.resolve()), "duration_s": duration_s(path)},
            **result,
        }
        confs = [s["confidence"] for s in doc["segments"]]
        threshold, thr_desc = resolve_threshold(args.low_confidence, confs)
        (outdir / f"{path.stem}.json").write_text(json.dumps(doc, indent=2))
        (outdir / f"{path.stem}.txt").write_text(render_text(doc, threshold))

        scored = [c for c in confs if c is not None]
        low = sum(1 for c in scored if c < threshold)
        print(f"  {len(doc['segments'])} segments, "
              f"{doc['audio']['duration_s']/60:.1f} min"
              + (f", {low} marked at {thr_desc}\n  {describe(confs)}" if scored
                 else ", no confidence scores"),
              file=sys.stderr)
        manifest.append(doc)

    (outdir / "manifest.json").write_text(json.dumps(
        {"provider": provider, "files": [
            {"path": d["audio"]["path"], "duration_s": d["audio"]["duration_s"],
             "segments": len(d["segments"])} for d in manifest]}, indent=2))
    print(f"\nwrote {len(manifest)} transcript(s) to {outdir}", file=sys.stderr)


if __name__ == "__main__":
    main()
