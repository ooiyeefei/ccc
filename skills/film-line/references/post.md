# Post - the manifest, one rebuild, the QA gates

Narration, cards, band, voice and mix follow `demo-video` (`soundtrack.md`, `structure.md`, `distribution.md`) and `pitch-craft`. This file is the pipeline around them, learned on a 60-line film cut from eighteen takes.

## Where things live

One film folder holds the manifest generator, the approved plan with its "does not show" list, the swaps file, the stale-figures list, the delivered files with their subtitle files and chapters, the upload's title and description, and the QA report. If the request does not say which film, ask for its folder; do not search for a likely one.

## The manifest

The film is an ordered list of segments, written by a generator script, never edited as JSON:

```
id | chapter | ranges [[take, from_s, to_s], ...] | text | cue | notes
```

- `ranges` are pieces of a take's delivered MP4. A gap between two pieces of one segment is a cut window, cross-faded 0.3 s.
- `cue` is the second inside the segment where the voice starts. `notes` says what was cropped, cut or left, so a reader can audit the choice.
- A per-take fixes table holds patches the take needs: a browser download banner covered from a clean frame of the same page, a file-name toolbar covered, a raw record id blurred. A patch is data, so a swapped take can reuse it.
- Moving or adding a segment changes nothing inside the others. Only chapter cards, music swells, chapters and timestamps are recomputed.

## One rebuild

Swaps accumulate. A swapped take is proposed by remapping the old ranges to the new take's milestones, then each range is checked on frames. Re-voice only the lines that changed, re-render only the segments that changed (cache each), concatenate, mix, and rebuild everything once at the end. A rebuild after every swap burns hours and hides which change broke what.

A swaps file lists what was swapped in, what wording changed and why, and how to redo it. A segment that still uses a stand-in take is marked `PLACEHOLDER` in the manifest and in the swaps file until replaced; the build and the QA gate refuse a marked one.

## Timestamps

Cues, chapters, captions and the sidecar subtitle file come from the delivered file after the cut, never from planned holds (`demo-video`, gate 3). Any hold, card or time-warp changes the timeline, so re-derive. Captions are rewritten from the manifest text at the final rebuild, so a late wording edit never leaves the burned text and the subtitle file different.

## QA gates

Run all of them on the output frames and audio of every delivered file, each speed variant included (pace excepted, gate 4). A gate that cannot run is reported as UNVERIFIED, never as passed.

1. **Frames and text**: OCR one frame per second (`scripts/frame_scan.py`) for banned words (the company's list, `house-rules-groot.md`), off-domain e-mail addresses, real brand and bank names, raw ids, a browser download banner. Sample at two frames per second across cuts and cross-fades, where a word can flash between samples. Then scan the text that never reaches a frame: the subtitle files, chapter titles, file names and the upload's title and description (`frame_scan.py --text`). Zero hits, or each hit explained in the report.
2. **Stale figures**: a list of figures that moved during staging appears in no frame (`frame_scan.py --figure`). Hold the list beside the manifest.
3. **Read-back**: transcribe every voiced line (faster-whisper, `medium` for a full pass, the match score as in `demo-video/scripts/voice_lines.py --check`) and score it against its text. Mean at or above 0.95, no line below 0.85; a miss on a name or a figure is listened to, respelled and re-voiced.
4. **Pace**: words per second per window between 2.2 and 2.6 for plain narration (`scripts/narration_scan.py`), scored on the normal-speed film. A speed variant is derived from it and reported as derived.
5. **Style**: the narration scan shows no unexplained hit (`narration.md`).
6. **Loudness**: -16 LUFS integrated, within 1 LU, measured per channel on every delivered file (ffmpeg `ebur128`, as in `demo-video/references/soundtrack.md`). A mono measure followed by a stereo upmix lands 3 dB hot.
7. **Contact sheet**: look at it as an image, one frame per beat (`demo-video`'s contact-sheet extraction). Each frame shows what its line says.
8. **Claims**: walk the narration against the plan's "does not show" list and the company's honest-claim lines. Any sentence that implies a listed gap is cut. A film with no such list cannot pass this gate: write the list first.
9. **Placeholders**: none left.
10. **Where it will live**: the family decides it. A tutorial is not for a public platform; a marketing film is.

The result is a per-beat report: the source take and range, the narration, words per second, the read-back score, the OCR result, what was cropped or cut. Publish only a film whose report has no failed row. UNVERIFIED blocks publishing until the owner accepts that gate by name.

## Variants

Cut the 16:9 and any speed variant from the same manifest, not from the finished file. Speed variants and the music rules are the owner's choice at the gate; the manifest makes either one a flag, not a re-edit.
