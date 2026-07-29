# Scribe — meeting notes with a chain of custody

Turn meeting recordings into notes where every claim traces back to audio the model actually heard well.

---

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

Then set a key for whichever backend you want — or set none and run fully local:

```bash
export ELEVENLABS_API_KEY=...     # diarization + per-word confidence
export DEEPGRAM_API_KEY=...       # diarization + per-word confidence
export OPENAI_API_KEY=...         # no diarization
```

**No keys are bundled with this skill.** Every backend reads its credential from
the environment at call time, so bring your own or use `--provider local`.

## Quick Start

Drop your recordings somewhere and ask:

```
"Summarize the recordings in ~/meetings/2026-08-04/"
"Transcribe this call and give me notes: standup.m4a"
"This Granola summary looks off — check it against the audio"
```

Or invoke it directly with `/scribe`.

### It will ask you three things first

This is the highest-leverage part, so answer properly rather than saying "just go":

| It asks | Why it matters |
|---|---|
| **Language** | Pinning the ISO code is the single biggest quality fix. Unpinned, per-window detection flaps on code-switched speech and the decoder emits fluent text in the *wrong language*. |
| **Speakers** | How many, names and roles. Without diarization this is what anchors attribution. |
| **Domain vocabulary** | Product names, people, companies, jargon, currencies. Feeds the provider's vocabulary boost so `LHDN` doesn't come back as `LHCM`. |

### What you get back

1. `transcripts/<name>.txt` — readable transcript, low-confidence spans wrapped in `<?…?>`
2. `transcripts/<name>.json` — normalized segments with timestamps, speaker, confidence
3. An audit of recording gaps and risky spans, printed before anything is summarized
4. Notes where every figure and named entity is either stated plainly, marked uncertain, marked uncorroborated, or absent

### Worked example

```bash
# 4 recordings from one meeting, Malaysian English, known participants
python scripts/transcribe.py ~/meetings/*.m4a --out transcripts \
    --language en --diarize \
    --keyterms "Groot,LHDN,ringgit,Cradle,EasyStore"

python scripts/audit.py transcripts
```

```
4 file(s), 113.1 min total
diarization: yes
confidence:  yes
  n=157 median=0.512 p10=0.448 p25=0.489 p75=0.657
  low-confidence bar: p20 of this recording = 0.489

-- coverage (2) --
  [truncated] part2.m4a: speech runs to the last 0.0s of a 4.9 min file -- a
    recording that ended naturally leaves trailing silence, so this one was
    almost certainly cut. Whatever was said next is not in this audio.
  [lost_between] part2.m4a: cut at its end, and part3.m4a picks up elsewhere --
    the meeting between them was never recorded.

-- risky spans (1) --
  part2.m4a 01:42 (conf 0.371) nums: 69/49
      they actually sell pretty well in korea so like 69 to like 69 is around 69 usd 49

Every finding above needs a disposition: corroborate it against a second
transcript, confirm it with the user, or carry it into the notes marked uncertain.
```

That gap between `part2` and `part3` is the failure this exists for. A summary
written without it reads as a complete account of the meeting, and is not.

## The problem it solves

A summariser cannot hear. Hand it a garbled span and it launders the noise into a
clean fact:

| in the audio | what a general-purpose ASR heard | what the summary said |
|---|---|---|
| "some paying customer" | "it's up to 8,000 glass" | **"~8,000 users"** |

Nothing downstream can separate that from a real figure. The transcript is gone by
the time anything reads it, there is no confidence signal attached, and the
summariser does the reasonable thing — it tidies the garble into a number.

Two failure classes cause most of it:

- **Wrong-language decoding.** Whisper-family models take the language as a
  *decoder input*, not an output label. Get it wrong and you don't get broken
  English, you get fluent, confident text in another language. Code-switched
  speech (Manglish, Singlish, Hinglish, Taglish) flips per-window detection
  constantly, and `condition_on_previous_text` then cascades one bad window into a
  run of them.
- **Silent recording gaps.** A recorder stopped and restarted mid-meeting drops
  content with no trace, and the resulting notes read as complete.

## What it does

1. **Establishes context first** — language code, speaker count and names, domain
   vocabulary. Pinning the language is the single highest-leverage fix and it
   cannot be derived from the audio.
2. **Transcribes** through a swappable backend, normalizing all of them onto one
   schema so everything downstream is provider-independent.
3. **Audits before reading** — flags recording gaps, and flags numbers and proper
   nouns sitting on low-confidence audio. That is where laundering happens.
4. **Corroborates** against any second transcript of the same audio. Two
   independent decodes are the cheapest confidence signal there is.
5. **Writes notes** where every figure and named entity carries its provenance —
   stated plainly, marked as uncertain, marked as uncorroborated, or absent.

## Providers

| `--provider` | credential | diarization | confidence | audio uploaded |
|---|---|---|---|---|
| `elevenlabs` | `ELEVENLABS_API_KEY` | yes | per-word `logprob` | yes |
| `deepgram` | `DEEPGRAM_API_KEY` | yes | per-word `confidence` | yes |
| `openai` | `OPENAI_API_KEY` | no | segment `avg_logprob` | yes |
| `local` | none | no | segment `avg_logprob` | **no** |

`--provider auto` (the default) picks the first backend with a key present, and
falls back to `local`.

`--provider openai` accepts `--base-url` (or `STT_BASE_URL`) so it works against
any OpenAI-compatible gateway — Groq, LiteLLM, OpenRouter, a local vLLM. That is
the swap point when credits move between vendors.

Prefer a backend that diarizes. Without speaker labels, every attribution in the
notes is inference, which is a break in the chain of custody.

## Running fully offline

```bash
pip install faster-whisper
```

Then `--provider local`. Nothing leaves the machine — the right choice for calls
covering equity, customers, or salaries. Roughly 3× realtime on ~16 CPU threads,
far faster on GPU.

For long-tail languages, a specialised local fine-tune can beat a general hosted
model: hosted vendors optimise aggregate accuracy across every customer, a
fine-tune optimises your distribution. Pass one via `--model`, e.g. a Malaysian
or Singlish Whisper fine-tune from the Hugging Face Hub.

## Requirements

- `ffmpeg` / `ffprobe` on PATH (duration probing)
- Python with `httpx`
- `faster-whisper` for `--provider local` only

## Usage outside the skill

Both scripts stand alone:

```bash
python scripts/transcribe.py recording.m4a --out transcripts \
    --language en --diarize --keyterms "Acme,LHDN,ringgit"

python scripts/audit.py transcripts
```

`transcribe.py` writes a normalized `.json` plus a human-readable `.txt` per input, with
low-confidence spans wrapped in `<?…?>`. `audit.py` reports gaps and risky
spans; `--json` for machine-readable output.
