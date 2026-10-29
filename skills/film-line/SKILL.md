---
name: film-line
description: The front door and production line for product films. Use first when someone asks for a video about a product and has not said whether it is a pitch, a marketing film or a help-centre tutorial, and whenever a film needs a fictitious workspace staged and cast before recording, a recorder brief, a write guard and a write ledger, takes cut into several films, a manifest-driven rebuild, or a QA pass on a finished film (banned words on screen, narration read-back, loudness). Not for what a film says (marketing-video, help-center-tutorial, pitch-package) or how it is captured and mixed (demo-video).
---

# Film line - stage once, record once, cut many

A body of product films is a production line, and its expensive failures happen before the camera runs: a wrong workspace written to, a test word on screen, a number burned by exploring.

Four leading words, used the same way everywhere:

- **write ledger** - the file listing every write made to the film workspace, once each, with before, after and undo. It is not the product's own accounting ledger.
- **guard** - before every write the script reads the server's active workspace and aborts unless it is the intended one; afterwards it reads the record's own workspace. A business name in the page header is not a guard (`references/staging.md`).
- **take bank** - recorded takes are inventory. Films are cuts from the bank, so a take is recorded silent, with a sidecar of cues.
- **one rebuild** - swaps collect in a manifest and the film is rebuilt once, at the end.

## 1. Name the family

Skip this section when the request already names the family or asks for a later phase (a recorder brief, a QA pass, a swap): enter at that phase and, if its inputs from earlier phases are missing, produce what can be produced, mark each missing input `TODO` and name it, instead of inventing it.

Otherwise ask the one question: **what is the viewer doing the moment the film ends?** In plain words: who is watching, and what do they do next? Give your recommended answer with it, drawn from what the request does say; a bare feature with no audience named defaults to marketing. "Go with your recommendation" is an answer. One answer per film; if it is two, those are two films sharing a take bank.

| The viewer is | Family | Skill |
|---|---|---|
| deciding on us, now, in a booked slot (judges, investors, a buying committee) | pitch | `pitch-package` |
| a stranger deciding whether the problem is theirs and the product is for them; also the long "a month in the life of one industry" film | marketing | `marketing-video` |
| a user with one task to finish, signed in or in a help centre | tutorial | `help-center-tutorial` |

Once the answer is in, hand off to the family skill. Industry (a cattle farm, a shop, a clinic) is a parameter of a film, never a fourth family: it chooses the staged business, the cast and the vocabulary.

## 2. The phases

Open the reference for the phase you are in and no other. A stager who can see the recording steps rushes the data.

| Phase | Done when | Reference |
|---|---|---|
| A. Plan (family skill) | the storyboard or step sheet is approved. **Blocking**: nothing is staged, recorded or rendered before it | the family skill |
| B. Stage | the preflight finds zero banned words; the cast signs in; the write ledger exists; a rehearsal on a twin is written down | `references/staging.md` |
| C. Record | smoke take inspected, then full take; every cue read from the delivered file | `references/take-bank.md`, then `demo-video` |
| D. Post | the manifest builds once; every QA gate in `post.md` passes | `references/post.md`, `references/narration.md` |
| E. Hand back | the report below is sent | this file |

A changed beat list reopens phase A, and so does a rehearsal that finds a beat cannot be staged. Four of six approved beats shipped silently is the usual way this goes wrong.

## 3. Invariants

These hold in every phase and every family. The references explain them.

1. Film the real product. Annotate, never substitute (`demo-video`, rule 1).
2. Fictitious data only. The words test, demo, sample, UAT and probe appear nowhere on screen, in typed data, in file names, in subtitles or on an end card. E-mail addresses belong to a film domain you control. No personal address on any frame.
3. A guard stands in front of every write. Prefer read-only takes; each write beat is filmed once and logged.
4. A form that autosaves a draft burns a number during exploration. Explore on the twin.
5. A plan's draft lines size the beats. The words that ship are written after the take, to the verified frames (`pitch-craft` for the clock).
6. Claim only what a frame shows. State a limit once, plainly. Keep the "does not show" list beside the plan.
7. Scripts are the source of truth. A film must be re-recordable when the UI changes.
8. A placeholder is written `TODO:<name>` until replaced, and the build refuses a marked one.
9. A recording day, deadline or ETA is stated only if the owner named it. A default date in a data pack is a placeholder, so call it one.
10. Announce each phase change in one line: approved, staged, recorded, built.

Company wording (band, end card, voice, banned words, honest-claim lines): `references/house-rules-groot.md`. Swap that file for another company's; nothing else here is company-specific.

## 4. Hand back

When a phase ends, report in plain words: what was made and where (exact paths); how to view it (the command); what to look for; how to spot an error; what was left behind in the workspace (the write ledger rows); what is blocked and by what. A take's own hand-back is in `references/take-bank.md`.

## References

- `references/industry-brief.md` - the industry parameter: one brief that planners and stagers share.
- `references/staging.md` - the film workspace, cast, data pack, rehearsal twin, dates, the guard, the write ledger, undo.
- `references/take-bank.md` - the recorder brief, take discipline, defect log.
- `references/post.md` - the manifest pipeline, one rebuild, placeholders, the QA gates.
- `references/narration.md` - plain narration written to the frame, with the scan.
- `references/house-rules-groot.md` - one company's wording and constraints.
- `scripts/narration_scan.py` - words per second per window, banned patterns, digits, repeated openers, a jargon list.
- `scripts/frame_scan.py` - OCR the output frames, or scan text files, for banned words, off-domain addresses, brands and stale figures.
