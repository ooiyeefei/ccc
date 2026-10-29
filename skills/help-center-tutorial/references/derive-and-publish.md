# Derive and publish

Read this after the take is recorded and verified from the delivered file. Until then it is not your concern.

## Derive

```
scripts/derive.py derive SHEET --take take.mp4 --sidecar take.json --out OUT --build <build> --date <day>
```

It writes, with a stem of `task[.platform][.locale]`: the article (`.md` and `.article.json`), a screenshot per step, a clip for each step that asks for one, the overview video, a captions track, a chapters track, and `.derived.json` with an average hash per screenshot. It stops with a reason when:

- the sheet fails `lint` (placeholders included);
- the take has no milestone for a step in the sheet;
- the sheet's plan hash differs from the one stamped in the sidecar. An action, proof text or locale changed since the recording, so the take no longer shows what the sheet says. Re-record. Wording edits never trip this.

`--allow-drift` exists for a deliberate, reviewed exception and is recorded nowhere else, so say so in the hand-back.

Cut windows (waits dropped from the timeline) shift cues. If the take has them, derive from the already-cut file and a sidecar re-based on it (`demo-video`, gate 3), never from the raw take with the original cues.

## Verify

1. Look at every screenshot as an image. Each shows its step's result and its highlight.
2. Run `film-line/scripts/frame_scan.py` on the clips and the overview, on the screenshots, and with `--text` on the captions and the article: no banned word, no address, no brand.
3. Follow the article text alone, on the film workspace, step by step. A step that cannot be followed is a defect in the sheet.
4. Check the caption cues against the video: each caption appears when its step starts.

## Publish

- **Access and place**: `information-architecture.md`, section Access. Check the gate on the media URL by requesting it signed out.
- **Footer**: "Checked against build X on date" is written by derive and updated by every passing replay (`keeping-fresh.md`). Build X is whatever version identifier the team already prints in its release notes (a tag, a commit, a deploy id), read at the time of the take.
- **Hand back**: the article path, the media paths, the commands to view them, what to look for, and any `--allow-drift` used.
