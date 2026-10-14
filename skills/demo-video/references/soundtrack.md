# Soundtrack - the voice, the music bed, the captions

The picture proves; the soundtrack carries. A film with a crisp capture and a hurried, flat or badly mixed voice reads as cheap, and the viewer blames the product. This file is the audio layer: how the narration is voiced, how music sits under it, how the two are mixed to a platform level, and how captions ride along. Every number here was measured on a shipped film; change one after hearing why it was set, not before.

Settle the audio questions at the storyboard gate (`structure.md` lists them). A voice or a music choice made after the cut is sized means re-cutting.

## 1. Voice

### Human or model

A model voice is the default for a product film: it re-records a changed line in seconds, which is what re-sync after a re-take needs. A human voice (the owner, a voice artist) is right when the speaker IS part of the pitch, and then the owner's rough edit is the source and the model voice only replaces it (section "Re-voicing an existing edit").

Kokoro and faster-whisper run inference locally, but first use can download model weights from Hugging Face and dependencies from package registries. Pre-cache approved assets before an offline run; local inference does not imply zero network access.

Kokoro (the open 82M model, `hexgrad/Kokoro-82M`) has carried every film so far: it runs on a CPU, sounds natural at speed 1.0, and costs nothing per character. Pin `kokoro==0.9.4` in a project-local virtualenv; a venv in a session scratchpad is wiped on restart, and the film's next re-voice then starts from nothing.

### Picking the voice

Voice one segment in two or three candidates and let the owner hear them before voicing the rest. The owner picks; do not pick for them. What has been chosen so far, and why:

| Voice | Character | Chosen when |
|---|---|---|
| `af_heart` | American female, warm, even | The customer-facing walkthrough: "seems better", more natural. The default. |
| `bf_emma` | British female, cooler, more clipped | Tried first at 0.92-0.95; replaced by af_heart for the customer film. |

`KPipeline(lang_code=VOICE[0])`: the first letter of a Kokoro voice id is its language code.

### One speed, and the cut follows the voice

Voice every line at **speed 1.0**, then size each shot to hold its line plus a breath, the last frame held if the line runs long. Nothing is hurried, and the narration sounds like a person with time. The other way round, fitting lines into windows cut from the footage, forces speed-ups, and the ear hears every one.

Speed up only when a line must land in a fixed slot (re-voicing an existing edit, a locked soundtrack): by the overrun ratio, **capped at 1.2x**, with the remaining drift carried into the next pause. In a 107-line film, six lines needed 1.04 to 1.2.

### Before synthesis: respell for the ear

The script is written for a reader; the voice needs a few words rewritten, by word-bounded regex, voice-only, never in the script the owner reads:

- Letter-by-letter acronyms get dots: `PEP` -> "P.E.P.", `CIF` -> "C.I.F.", product initials "I.D.P.".
- Acronyms said as a word get a hyphenated phonetic spelling: "C-toss", "C-Chris".
- Numbers are already words in the script (pitch-craft's rule): "fifty-five percent", "twenty twenty-four", so every voicing reads them the same way.
- A proper noun the model stresses wrongly gets Kokoro's inline phoneme override: `[Petaling Jaya](/pətˈɑːlɪŋ ʤˈɑːjə/)`.

Then listen before "fixing": a local word the model reads its own way (a currency name with a hard g) can be the transcriber's mishearing, not the voice's error.

### Trim and gap

Kokoro returns lead-in and tail silence. Trim at -42 dBFS, keeping 40 ms before and 80 ms after the speech, or every line starts late against its cue. Between the sentence chunks the pipeline returns for one line, insert 0.22 s of silence.

### QA every build, scripted

Transcribe each voiced line with faster-whisper (`small.en` for a few new lines, `medium` for a full pass) and score it against the text it should say (a difflib ratio on normalised words). Report the line count, the mean, the count at or above 0.85, and list the misses. Shipped films score a mean of 0.97 to 0.98; every miss so far was a number heard as digits ("60%" for "sixty percent"), which is the transcriber, not the voice. A miss on a product name or a figure needs a listening review: respell and re-voice that line.

A below-threshold read-back exits nonzero and writes the report. Do not dismiss a miss just because numbers often transcribe differently. Retained clips must match the current script; `--only` refuses stale or missing unselected lines.

`scripts/voice_lines.py` does the voicing, the respelling, the trim and the Whisper check in one pass. Run it with the Kokoro venv.

## 2. Music

### Rights first

No music without clear rights (owner rule). A free-commercial library track with no attribution clause is fine; anything "source unknown" is verified before shipping or dropped; a track the owner supplies is theirs to clear. Name the track and its licence in the handover.

### The bed: the music speaks when the voice does not

The pattern viewers describe as "it feels produced":

- Where nobody speaks, the music plays at its own level. The swells between chapters are the gaps, and a chapter card sits in one. The music "chiming in" when the voice stops is what makes the pause feel intended rather than empty.
- Under speech, the bed dips **8 dB**. The dip window is the line padded 0.3 s each side, with 0.3 s linear attack and release ramps (a box filter over the speech mask), so the music breathes back in rather than snapping.
- No chime, sting or whoosh in a product walkthrough. The card and the swell already mark the change, and a sting makes a real film sound like a slide deck. Reach for a soft sting only to mark a hard section change in a film that has no music bed at all, and only if the owner asks.

The mixer measures and normalises unducked music to -26 LUFS by default (`--music-lufs`), then applies the 8 dB dip. A supplied track can be arbitrarily loud, so ducking alone cannot establish a voice-first balance. Listen to the final master; change that explicit bed target when the track needs it.

Narration first, music second: the voice sits on top and the bed is set to it. Never set the music level by ear on a laptop speaker; measure.

### Levels

| Stem | Level | Why |
|---|---|---|
| Narration stem | about -23 LUFS before the master | Where the voice sits in the shipped films; a bed dipped 8 dB under it stays audible without competing |
| Master | **-16 LUFS integrated, -1.5 dBTP, LRA 11** | The platform level (YouTube, Vimeo and LinkedIn normalise to about -14 to -16); a quieter film is turned up with its noise floor, a louder one is limited |

The mixer writes floating-point pre-master audio so peaks are preserved before loudness normalisation. `narration.wav` is the normalised voice stem, `mix.wav` the pre-master mix, and `soundtrack.wav` and `soundtrack.m4a` the mastered deliveries.

Master with two-pass `loudnorm` (measure, then apply the measured values with `linear=true`), then AAC 192k at 48 kHz stereo.

Two traps, each measured the hard way:

- A mono loudnorm followed by a stereo upmix lands about 3 dB hot. Measure on the film as delivered, per channel, not on an intermediate.
- Smoothing a 48 kHz mask over a ten-minute film with `np.convolve` ran twenty minutes under load; a running-sum box filter gives the same numbers in seconds. `scripts/mix_soundtrack.py` uses the running sum.

### Re-voicing an existing edit

When the owner hands over their own rough cut (their voice, their music, picture final), keep their music and replace only the voice:

1. Whisper `medium` word times on the edit; split into sentence units where the owner spoke; correct misheard words by hand.
2. Demucs `htdemucs` two-stem separation; keep `no_vocals` as the music stem.
3. Voice each unit (section 1) and fit it to its slot: trim, place at the slot start or 0.12 s after the previous unit if that one is still speaking, speed-up capped at 1.2x, drift carried into the next pause, units starting more than 0.3 s late reported.
4. The bed: the edit's own audio where nobody speaks, the music stem under any speech old or new, the speech mask padded 0.12 s before and 0.3 s after so no breath of the old voice survives, mask edges crossfaded over 0.15 s.
5. Set the new voice to the old voice stem's loudness so the owner's balance survives; duck the bed 8 dB under any line added where their edit had no voice.
6. Master as above.

Ask for the owner's original music file: a rough edit usually carries a mono 24 kHz track.

## 3. One soundtrack, many pictures

When a film is re-skinned (a second brand, a theme change, a re-take of one scene), lock the cut: every beat keeps its place and length, the picture is rebuilt to fit, and the soundtrack and captions are reused byte for byte. One re-mix then updates every variant. Prove it: the audio packets' MD5 is identical across the variants.

Fitting a new take to a locked beat: hold the last frame where it runs short; where it runs long, first trim the static tail (ffmpeg `freezedetect n=0.0003 d=0.4`, cached per take), then speed up to at most 1.6x; refuse anything faster and cut the beat earlier instead. Two traps: a missing freeze cache makes the builder silently speed beats up (the plan still sums to the locked length, so nothing looks wrong), and a take's last keyframe can re-quantise a still frame just before its end, which freezedetect reads as motion. Diff the new plan's speeds and holds against the previous variant's before building; every difference needs a reason.

## 4. Captions

Captions make the film work on mute, which is how most feeds autoplay it. Two deliverables, never both inside one file:

- **Burned**: each caption rendered once as a PNG band by a headless browser (the brand font, none of the subtitle filter's quirks), an ffconcat list timed to the captions, stacked under the picture. Lines split at about 96 characters, timed to the speech from Whisper word times, never from the script's planned windows. The band itself: `structure.md`.
- **Sidecar `.srt`** beside the film, for upload platforms. Do not also mux a soft subtitle track into a film with burned captions: the viewer sees both.

## 5. Handover

Beside the film: the narration stem, the timed script (`Segment N | M:SS-M:SS | text`, whole-second cuts so the ranges are exact), the `.srt`, the 16:9 cut if a band was added, and one line naming the voice, the speed, the music track and its licence. The next person then re-voices one line without asking what you used.
