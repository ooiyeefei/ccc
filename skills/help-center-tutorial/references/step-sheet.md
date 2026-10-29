# The step sheet

One file per task and platform, YAML (or JSON). It is the approved plan, the recorder's script and the article's source. `references/example-sheet.yaml` is a complete one; `scripts/derive.py lint` checks it.

## Task fields

| Field | Rule |
|---|---|
| `task` | the slug, stable; names the article, the media files and the sidecar |
| `platform` | `web` or `mobile`; one sheet per platform, same `task`; the page joins them as tabs. Omit for a task with one platform |
| `locale` | set only in a locale's strings file (`localisation.md`) |
| `title`, `goal` | a verb and object; one sentence on the outcome in the user's words |
| `domain`, `path` | the product's own navigation, written `Calendar > Add > Blocked time` |
| `who` | the roles that can do it |
| `before` | prerequisites; each may link to its own article |
| `surfaces` | what the task touches, so a change can find it: `route:/calendar`, `component:BlockedTimeDialog`, `file:src/app/calendar/**` (`keeping-fresh.md`) |
| `writes` | true if any step writes data; the guard and the write ledger apply (`film-line`) |
| `result` | the visible end state, written as what the user sees |
| `troubleshooting` | `when` / `then` pairs from refusals the product really gives |
| `not_covered` | the branches the article leaves out, so a reader is not surprised |
| `related` | up to three article slugs |

## Step fields

| Field | Rule |
|---|---|
| `id` | stable, lower case, never reused; the harness milestone, the screenshot name, the caption cue and the page anchor all use it |
| `do` | one action, imperative, verb first, the exact UI label named |
| `label` | the UI label to bold; it must appear word for word in `do` |
| `action` | what the driver does: `click: <selector>` (`tap` is an alias on a mobile sheet), `type: {selector, text}`, `js: <expression>`; a step with no action is a hold on a screen already reached. A gesture the harness cannot drive (long-press, swipe) is marked `TODO:gesture` and filmed by hand or cut. How a mobile take is captured (device emulation or the native app) is the recorder brief's choice |
| `proof` | text that must be on screen after the step; the harness waits for it, so a take never records a spinner as the result |
| `shot.mark` | the element to highlight in the screenshot |
| `clip` | `{seconds: N}` for a short looping clip of this step; omit for most steps |
| `caption` | the line shown in the subtitle track; short, readable muted |
| `alt` | what the picture shows and what to do, at least a phrase |
| `writes` | true if this step writes; marked in the recorder's brief and the write ledger |
| `hold` | seconds to stay on the result, default four |

## Rules

- **One action per step.** "Open X and click Y" is two steps. The linter cannot count actions; the approver does.
- **Proof the step caused.** The proof is something that did not exist before the step: a menu that opened, a total that updated, a state that changed. The text the step typed is not proof, and `lint` refuses it. A step that shows nothing new on screen is merged into its neighbour.
- **Recorded fields and wording are separate.** `action`, `proof`, `shot.mark`, `platform` and `locale` change what is recorded; `do`, `caption`, `alt`, `label`, the title and the troubleshooting do not. Only the first group enters the recording plan's hash, so a wording fix never forces a re-record and a changed action always does.
- **Stable ids.** Insert a step with a new id; never renumber.
- **Selectors survive redesigns when they are named for the thing.** Prefer a `data-testid` or an accessible name to a position or a class. Keep selectors shared across sheets (the main menu, the save button) in one named file the sheets reference, so one fix repairs many.
- **Placeholders are marked `TODO`.** `lint --draft` allows them for an approver; `lint`, `plan` and `derive` refuse them, so a guess never reaches a recorder.
- **Honest scope.** Fill `not_covered` when the task has branches the article leaves out.
- **Locale-formatted values come from the screen.** A time, number, date or currency in `proof` is copied from the target locale's own screen, never typed from memory.

## How it drives the recorder

`derive.py plan` writes two files. `recording-plan.json` holds only the recorded fields and is passed as the harness's storyboard, so the take's sidecar carries its hash. `beats.json` is the harness's BEATS list: each step becomes a beat whose `label` is the step id, whose `click` or `type` is the action, and whose `ready` waits for the proof text. A step whose action is empty but which names a `shot.mark` becomes a `__cine.spotlight` beat, so the highlight sits in the recorded frame. If the recorder also writes each target's bounding box into the sidecar as `bbox` (CSS pixels), `derive.py` draws the highlight on a clean frame instead and the video stays unmarked.
