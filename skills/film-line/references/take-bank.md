# Take bank - recording for many films

Capture mechanics (Xvfb, CDP, smoke take, timestamps) belong to `demo-video`. This file is what a recorder is told, and the discipline around writes. Each take is silent and carries a sidecar, so any number of films can be cut from it later.

## The recorder brief

Give each recorder lane one brief. Fill every field; an empty field is a decision nobody made. If the plan is not approved or staging is not done, fill what is known, mark the rest `TODO`, and say the brief cannot go to a recorder until none remain.

```
Goal         the take name and the approved plan it records (path; the harness hashes it)
Output       silent mp4 + sidecar json (t_video, t_proof per step id) + proof frames, in <out dir>
Not yours    narration, cards, band: a later lane adds them
Workspace    the intended workspace id; the twin id for smoke takes
Logins       persona names; session files made by the re-login script
Documents    only files from the data pack
Dates        read the day from the screen's default or the captain's note; never invent
Forbidden    screens (avatar menu, team list, e-mail columns), words, known defects to film around
Locks        own lock file, own display number, own browser profile; at most N recordings at once (N is 1 until two have been smoked together)
Retake       which steps may be retaken freely and which are one-shots
Machine      no builds, type checks or test runs while recording
Hand back    see below
```

The captain is whoever runs the line: assigns locks and displays, owns the write ledger, and decides when a wrong document is voided. Split a film across lanes by retake cost: one lane for the read-only steps, which retakes freely, and write lanes that are one-shots in story order. Two lanes never write to one workspace at once, because document numbers interleave on screen.

## Rules of the road

- A smoke take runs on the twin and stops at the first write. Inspect its contact sheet as an image before any full take. A task that writes is rehearsed on the twin, then recorded once, guarded and logged.
- Real clicks, real typing, one cursor, no teleporting. Every step has a readiness check on its proof text, so a take never records a spinner as the payoff.
- Wait out OCR and loading off the timeline: record the wait, mark `cut` windows in the sidecar, and let the editor drop them.
- Warm every page first. A cold load shows skeletons for seconds.
- Hide docked chat panes and any presenter or staff overlay.
- Read-only takes first. A write take is a one-shot: if it goes wrong, say so and stop. Do not create duplicates to "redo"; a wrong document is voided or reversed by the captain, then the step is retaken.
- The **guard** is code, not a habit, with the four layers in `staging.md`: an allow-list of one id, a read of the server's active workspace before each write, a read of the written record's workspace after, and a negative test seen to refuse. The sidecar carries both reads. Reading the header is not a guard.
- Do not press the button that sends, files or submits something outside the workspace unless the plan says so and the address is on the film domain.
- Film around a known defect unless its fix has landed and deployed. Never imply, in framing, a capability the product lacks: read the plan's "does not show" list.
- Every take is also an acceptance test. A flicker, a blank, a slow load, a wrong number, a console error or a step the narration could not honestly claim goes into the defect log with a timestamp and a frame path.

## Cost of a retake

A resettable workspace: minutes. A workspace that cannot be reset: twenty minutes or more, plus traces. Choose which steps to film once and which to film freely on that basis, and write the choice into the brief.

## Hand back (one message per take)

The script path; the mp4 and sidecar paths; the beat table with `t_video` and `t_proof` read from the MP4; the frames you looked at; every defect with its timestamp and frame; any step you changed from the plan and why; what is blocked and by what; the write ledger rows you added. If a lane is stopped by a usage limit, keep scripts and notes saved so it can be revived.
