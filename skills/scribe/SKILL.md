---
name: scribe
description: Turn meeting recordings into notes with an unbroken chain of custody from audio to claim. Use when the user has recordings or audio to transcribe or summarize, or when an existing transcript or auto-summary reads as garbled or untrustworthy.
---

A summariser cannot hear. Hand it a garbled span and it **launders** the noise into a clean fact — "some paying customer" becomes "~8,000 users" — and nothing downstream can separate that from a real figure. This skill holds a **chain of custody**: every claim in the notes traces back to audio the model actually heard well, and a claim whose custody is broken says so.

Scripts are in `scripts/`. They need a Python with `httpx`; `--provider local` also needs `faster-whisper`.

## 1. Establish the recording's context

Ask the user, or read it off the surrounding material — the files, the repo, an existing transcript:

- **Language** — the ISO code to pin. Left unpinned, per-window detection flaps on code-switched speech and the decoder emits fluent, confident text in the wrong language.
- **Speakers** — how many, plus names and roles.
- **Domain vocabulary** — product names, people, companies, jargon, currencies.

Done when you can state the language code, the speaker count, and at least five domain terms.

## 2. Transcribe

```
python scripts/transcribe.py AUDIO... --out DIR --language <code> --diarize --keyterms "term,term,..."
```

`--provider` selects the backend; `auto` takes the first with a key present. Setup, capability and cost per provider: [`references/providers.md`](references/providers.md).

Prefer a backend that diarizes. Speaker labels you derive yourself by reasoning about who-said-what are inference, and inference is a break in the chain of custody.

Done when every input file has a `.json` and `.txt` in DIR.

## 3. Audit before you read

```
python scripts/audit.py DIR
```

Two findings, both of which vanish once a transcript is flattened into prose:

- **Gaps** — a recorder stopped mid-meeting drops content in silence, and the notes that follow read as complete. A gap is a stretch of the meeting you hold no evidence for.
- **Risky spans** — numbers and proper nouns resting on low-confidence audio. This is where laundering happens.

Give every finding one of three dispositions: corroborated against a second transcript, confirmed with the user, or carried into the notes as a marked uncertainty.

Done when the count of dispositions equals the count of findings.

## 4. Corroborate against any second transcript

When the user has another transcript of the same audio — Granola, Otter, an earlier run — align it against yours.

Two independent decodes are the cheapest confidence signal available. A claim present in one and absent from the other is a divergence, not a fact, and inherits the lower confidence of the two. Where your audio has gaps, the other transcript may be the only evidence that exists; anything sourced that way stays marked as uncorroborated.

## 5. Write the notes

Group by topic, so each section stands on its own.

Every figure and every named entity carries its custody:

| Traced to | Written as |
|---|---|
| a span above threshold | stated plainly |
| a flagged span | stated with its marking and timestamp |
| a gap-filling second transcript only | marked uncorroborated |
| no source | absent |

Cite timestamps for anything a reader might challenge.

Done when every figure and named entity in the notes falls into one of those four rows.
