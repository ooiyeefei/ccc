# STT providers

Backends for `scripts/transcribe.py --provider`. All four normalize onto one schema, so
everything downstream is identical whichever you pick.

| | env var | diarization | confidence | audio leaves the machine |
|---|---|---|---|---|
| `elevenlabs` | `ELEVENLABS_API_KEY` | yes | per-word `logprob` | yes |
| `deepgram` | `DEEPGRAM_API_KEY` | yes | per-word `confidence` | yes |
| `openai` | `OPENAI_API_KEY` | **no** | segment `avg_logprob` | yes |
| `local` | — | **no** | segment `avg_logprob` | no |

Choose on two axes, in this order:

1. **Diarization** — without it, speaker attribution is your inference, which
   breaks the chain of custody. This alone usually decides it.
2. **Where the audio may go** — a call covering equity, customers or salaries may
   not be uploadable to a vendor. `local` is the answer when it isn't. Note that
   a cloud note-taker already in the workflow (Granola, Otter) means the audio
   has left the machine regardless.

Raw accuracy is a weaker axis than either. For long-tail languages and heavy
code-switching, a specialised local fine-tune can beat a general hosted model —
hosted vendors optimise aggregate WER across every customer, a fine-tune
optimises your distribution. Measure on your own audio rather than trusting a
published number.

## Reading the confidence numbers

Every provider is normalised to 0–1, but the scales are not interchangeable and
none of them is calibrated. `exp(logprob)` is monotonic — it ranks spans within
one recording — and that is all it is good for. Across recordings the whole
distribution shifts with audio conditions: three calls from the same speakers
came out with medians of 0.62, 0.61 and 0.51.

So `--low-confidence` defaults to **`p20`**, the bottom fifth of *this*
recording's own scores, not a fixed value. A fixed cutoff of 0.60 flagged 32% of
one of those calls and 61% of another — the middle of the second distribution
rather than its tail, which buries the real outliers in noise. Pass an absolute
value (`--low-confidence 0.5`) when you have a reason to.

Both scripts print the distribution alongside the resolved bar, so a flag can be
judged in context:

```
n=157 median=0.512 p10=0.448 p25=0.489 p75=0.657
low-confidence bar: p20 of this recording = 0.489
```

A percentile bar always flags roughly a fifth of segments, so treat the flags as
*where to look first*, not as a verdict. What makes a flag actionable is the
pairing in `audit.py`: low confidence **and** a number or proper noun in the
span. A flagged span carrying neither rarely bears on a claim.

## elevenlabs — Scribe

`POST https://api.elevenlabs.io/v1/speech-to-text`, header `xi-api-key`,
multipart. Models: `scribe_v1` (default here), `scribe_v2`.

Returns `words[]` with `text` / `start` / `end` / `type` / `speaker_id` /
`logprob`. `transcribe.py` keeps `type == "word"`, converts `exp(logprob)` to a 0–1
confidence, and groups words into segments on speaker change or a pause.

`--keyterms` maps to the API's `keyterms` vocabulary boost. That field's format
has changed before, so `transcribe.py` retries without it on a 422 rather than losing
the whole transcription.

## deepgram

`POST https://api.deepgram.com/v1/listen`, header `Authorization: Token ...`,
raw audio body, options as query params. Default model here: `nova-3`.

`transcribe.py` requests `utterances=true`, which returns
`results.utterances[]` — each already carrying `start`, `end`, `confidence`,
`transcript` and `speaker`, mapping straight onto the normalized schema. If
utterances come back empty it falls back to
`results.channels[0].alternatives[0]`.

`--keyterms` maps to the repeatable `keyterm` param.

## openai — and any OpenAI-compatible gateway

`POST {base}/audio/transcriptions`, header `Authorization: Bearer ...`.
Default model `whisper-1`.

Point `--base-url` (or `STT_BASE_URL`) at any gateway speaking the same
protocol — Groq, LiteLLM, OpenRouter, a local vLLM. That is the swap point when
credits move between vendors.

Confidence needs `response_format=verbose_json`, which returns `segments[]` with
`avg_logprob` and `no_speech_prob`. Newer transcription models reject that
format; `transcribe.py` asks for it, drops to plain `json` on a 400, and reports that
confidence is unavailable. A transcript with no confidence scores cannot support
risky-span detection — step 3 will say so.

No diarization on this path.

## local — faster-whisper

`pip install faster-whisper`. Default model `large-v3`, CPU int8. Roughly 3×
realtime on ~16 CPU threads; far faster on GPU.

Two settings carry the quality, both already applied:

- `language=...` — pinned. Unpinned, per-window detection flaps on
  code-switched speech and the decoder produces fluent wrong-language text,
  because the language token *steers generation* rather than labelling it.
- `condition_on_previous_text=False` — each window decodes independently, so one
  bad window cannot poison the next. This is what stops a single misdetection
  cascading into a run of gibberish.

`--keyterms` becomes `initial_prompt`, which biases spelling of domain nouns. It
can also induce the model to hallucinate the prompt's own content, so keep it to
terms that genuinely occur.

Pinning a language trades one error class for another: genuine speech in other
languages comes out as phonetic English rather than correct text. That trade is
worth taking — anglicised mush is visibly wrong and a reader who knows the
domain recovers it, where confident wrong-language text reads as real.
