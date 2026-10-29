# film-line

The front door and production line for **product films**. It names the family with one question (what is the viewer doing the moment the film ends?), then runs the line every family shares: stage a fictitious workspace, brief the recorders, rebuild once, pass the QA gates.

Leading words: **write ledger** (every write recorded once), **guard** (server truth before and after a write), **take bank** (takes are inventory, films are cuts), **one rebuild**.

## Use this, not that

- Use film-line when the kind of film is unclear, or when a film needs staging, a recorder brief, a write guard, a manifest rebuild or a QA pass.
- A pitch in a booked slot -> `pitch-package`. A film for strangers -> `marketing-video`. A task for a user -> `help-center-tutorial`.
- Capture, smoke take, timestamps, soundtrack, structure -> `demo-video`. Words against a clock -> `pitch-craft`. Rendered scenes -> `motion-video`.

## Structure

- `SKILL.md` - the family question, the phases and their gates, the invariants, the hand-back
- `references/staging.md`, `take-bank.md`, `post.md`, `narration.md` - one per phase
- `references/house-rules-groot.md` - the one company-specific file; swap it for another company's
- `scripts/narration_scan.py` - pace per window and the patterns that read as machine-written
- `scripts/frame_scan.py` - OCR the output frames for banned words, off-domain addresses, brands
- `tests/test_scans.py` - `python -m unittest skills/film-line/tests/test_scans.py`

Requires `ffmpeg` and `tesseract` for the frame scan.
