---
name: help-center-tutorial
description: Author help-centre tutorials - a task article with numbered steps, screenshots and a short video, all generated from one scripted step sheet ("record once, publish three"), organised domain then task, and kept fresh by replaying the sheets when the UI changes. Use whenever someone wants a help article, knowledge-base page, how-to, tutorial video or "how do I ... in the app" write-up for users, a help-centre or learn-section structure, a translation of help articles, or docs screenshots and clips that keep going stale. Not for films for strangers (marketing-video) or pitches (pitch-package).
---

# Help-centre tutorial - one task, one step sheet, three outputs

The reader is a user with one task to finish, in the app or in the help centre. The tutorial ends when the task is done on their own screen. Three leading words, used the same way throughout:

- **task** - one goal a user finishes in one sitting, named with a verb ("Block time in your calendar"). Not a feature, not a screen.
- **step sheet** - the single source for a task: a machine-readable script. The video, the screenshots and the article text are all generated from it, so they cannot disagree.
- **drift** - the app, the pictures and the words disagreeing. Recording once and publishing three stops the three drifting from each other. Replaying the sheet stops them drifting from the app.

## Which branch

| You are asked for | Go to |
|---|---|
| a new task's article, screenshots and clip | the steps below |
| a structure, a template, where videos live | `references/information-architecture.md`, then `references/article.md` |
| screenshots and clips that are already wrong, an existing corpus, a UI change | `references/keeping-fresh.md` |
| a translation | `references/localisation.md` |

A request that spans rows reads each row's reference. A user finishing a task is a tutorial. Persuading a stranger is `marketing-video`; a booked slot is `pitch-package` (`film-line`, section 1). Tutorials are keyed by domain and task, never by industry: reuse the staged workspace that exists, and tag the example data instead of forking the article.

## Steps for a new task

### 1. Place the task

Domain, then task, then article: `references/information-architecture.md`. Search the existing sheets and the help-centre index by title and by the user's other words first. A near-duplicate is a second place for drift, so update its sheet instead.

### 2. Write the step sheet - blocking

One sheet per task and platform, in the format of `references/step-sheet.md` (a worked example is `references/example-sheet.yaml`). Take labels, proof text and selectors from the running product with a read-only look. What you could not read stays marked `TODO`, and `scripts/derive.py lint --draft` reports how many remain. A recorder is not briefed until `lint` passes with none.

Show the approver one table per platform, `id | step | UI label | proof text | writes`, with the goal, the result and the troubleshooting. The `do`, `caption` and `result` sentences are the article's own words, so this is where the approver reads the article.

Completion criteria, each checkable:

- every step is one action in the imperative with the exact UI label;
- every step has proof text that the step caused, and a step with none is merged or cut;
- every step that writes is marked, and the task says it writes;
- the result is a visible state, "You should see ...";
- troubleshooting items come from refusals the product really gives;
- the sheet says what the article does not cover.

Show the table and stop. Nothing is staged or recorded before the nod. A step added or reordered later reopens this gate. A renamed label or a moved selector, and a `TODO` filled in after the nod, are maintenance edits, shown to the approver as one diff per domain. If the product or feature named in the request cannot be found, ask before drafting anything.

### 3. Stage and record

Stage per `film-line` (staging, the guard, the write ledger). Run `scripts/derive.py plan` for `recording-plan.json` and `beats.json`. Record with `demo-video`, passing `recording-plan.json` as the storyboard: the harness stamps its hash into the take's sidecar, and that hash proves later that the take still matches the sheet. A smoke take runs on the twin and stops at the first write. A writing task is rehearsed on the twin, then recorded once, guarded and logged.

### 4. Derive and verify

Open `references/derive-and-publish.md` only now, after the take is verified from the delivered file. `scripts/derive.py derive` makes the article, the screenshots, the clips, the captions and the chapters. Look at every screenshot: each shows its step's result. Then follow the article text alone, step by step, on the film workspace.

### 5. Publish

Article format and writing rules: `references/article.md`. Gate on the media, not the page: tutorial video and clips are for signed-in users by default.

## What stays out

The marketing story, hooks and music beds. A tour of every option on a screen: document the path through the task, not the screen.

## References

- `references/information-architecture.md` - domain, task, article types, naming, links, URLs, access.
- `references/step-sheet.md` - the sheet's fields, rules and how it drives the harness.
- `references/article.md` - the article units, step writing, alt text, captions.
- `references/derive-and-publish.md` - deriving the three outputs, verifying, publishing.
- `references/keeping-fresh.md` - replay on a UI change, an existing corpus, mass failure.
- `references/localisation.md` - a locale from the same sheet.
- `references/example-sheet.yaml` - a complete sheet that passes `lint`.
- `scripts/derive.py` - lint, plan, derive, queue, distance.
