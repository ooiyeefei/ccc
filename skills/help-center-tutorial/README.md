# help-center-tutorial

Help-centre **task articles** from one scripted step sheet: the video, the screenshots and the article text are generated together ("record once, publish three"), so they cannot drift from each other, and a replay when the UI changes keeps them from drifting from the app. Information architecture is domain, then task, then article.

Leading words: **task**, **step sheet**, **drift**.

## Use this, not that

- A user finishing one task, in the app or a help centre -> here.
- A film to persuade a stranger -> `marketing-video`. A pitch in a slot -> `pitch-package`.
- Staging, the write guard and QA gates -> `film-line`. Recording -> `demo-video`.

## Structure

- `SKILL.md` - place the task, write and approve the sheet, stage and record, derive, publish and keep fresh
- `references/information-architecture.md`, `step-sheet.md`, `article.md`, `derive-and-publish.md`
- `references/example-sheet.yaml` - a complete sheet that passes lint
- `scripts/derive.py` - `lint`, `plan` (recording plan and the harness BEATS), `derive` (article, screenshots, clips, captions, chapters)
- `tests/test_derive.py` - `python -m unittest skills/help-center-tutorial/tests/test_derive.py`

Requires `ffmpeg`; PyYAML to read a `.yaml` sheet (a `.json` sheet needs nothing).
