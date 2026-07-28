# Edit Mode — Local Real-Time Iteration

Edit mode turns an HTML file into a live, local review surface on `127.0.0.1`. The user annotates and comments in the browser; you receive their input by polling, edit the file, and it hot-reloads. Nothing is hosted or published. It's the pre-publish loop — firm a doc up with the user before sharing, or iterate between rounds of external feedback.

**One surface.** The page shows the document with the annotation widget plus a small control bar. A page-level comment is a message to you; a threaded reply is your answer. Selecting text auto-opens the comment box, or the **▢** area button in the comments panel starts an area-box drag; ⌘⏎ / Ctrl+Enter submits. A **Live ⇄ Async** toggle in the control bar controls delivery: **Live** = each comment pings your poll in real time; **Async** = comments are held on the page until the user clicks "Send N to agent". Either way the comment is saved on the page — the mode only changes *when* you're pinged. In-artifact decision forms (the **input** playbook) deliver the user's choice through this same channel: a submitted decision arrives on your poll as a comment, so treat it as an actionable request, not just context.

It is **author-facing** (the user and you), distinct from `push --feedback`, which is for **async external reviewers**. When the doc is ready, publish with `push --feedback`.

**Publishing from the browser.** The control bar has a **🚀 Publish** button. When the user is done editing, they click it and pick **Public link** or **Password-protected**. It does *not* publish directly (the browser has no shell) — it sends *you* a publish request that arrives on your next `edit poll` as a message. Act on it: run the matching push (`htmldrop push <file>` for public, or `htmldrop push <file> --generate-password` for password-protected), then `edit reply` with the URL (and the generated password). Treat it as the user's explicit "ship it" signal.

## Prerequisites

None beyond the CLI. Edit mode is fully local — no `htmldrop init`, no Surge account, no author key. If `htmldrop` isn't found: `npm install -g @yeefeiooi/htmldrop@latest`.

## Commands

| Command | Purpose |
|---------|---------|
| `htmldrop edit start <file>` | Serve the file locally + open the browser. `--with-feedback` loads the published doc's reviewer comments into the session; `--no-open` skips the browser |
| `htmldrop edit poll <file> [--json]` | **The listen call.** Blocks until the user sends a chat message or leaves a comment, then returns them plus current layout warnings. Re-run after each reply |
| `htmldrop edit reply <file> --text "<t>"` | Post your response into the conversation after editing (the user sees it in the control bar; the reloaded page reflects your change) |
| `htmldrop edit ask <file> --text "<q>" [--options "A\|B\|C"]` | Ask the user a question in the browser. Pops a card (prompt + clickable options + free-text note); the answer returns on your next `poll` as `{choice, text}`. Use for decisions you can't make alone (e.g. "iOS-first or Android-first?") instead of guessing |
| `htmldrop edit layout <file> [--json]` | Report layout issues (overflow, clipped/overlapping text) in the rendered page, on demand |
| `htmldrop edit end <file>` | End the session |
| `htmldrop edit stop` | Shut the background edit server down |

Always use absolute paths. A file argument resolves to one session by its real path, so `start`/`poll`/`reply` on the same file share state.

## The Listen Loop

This is the heart of edit mode — treat `edit poll` like any long-poll: leave it running, and re-run it after you reply.

1. **Start:** `htmldrop edit start /abs/doc.html` — tell the user the local URL it prints and that they can chat + annotate there.
2. **Listen:** `htmldrop edit poll /abs/doc.html --json` — it blocks silently (this is correct — no output means "waiting", not "broken"). If your harness time-limits foreground commands, run it in the background; if it's killed, just re-run it — queued input is never lost.
3. **Act:** edit `/abs/doc.html` to address what you received. The page live-reloads; annotations re-anchor to the changed text automatically.
4. **Reply:** `htmldrop edit reply /abs/doc.html --text "tightened the intro and added a timeline"` so the user sees what changed.
5. **Repeat** from step 2 until the user is satisfied. Then publish: `htmldrop push /abs/doc.html --feedback`.

## Poll Payload

`edit poll --json` returns a JSON object. When there's input, `status` is `"feedback"` and it carries any of:

- `answer` — the user's reply to a question you asked via `edit ask`: `{ choice, text, question }`. Highest priority; delivered once.
- `newComments` — comments/annotations just left on the page (delivered once each). Each has an `anchor` (`selectedText` for text, `capturedText`+`rect` for an area, or `page_level`), `content.text`, and `author.displayName`. In Async mode these arrive only when the user sends the batch.
- `messages` — free-text messages from the user (transient; each delivered once), each optionally with a `context` `{ text, selector }`.
- `comments` — the full current comment set, as standing context.
- `layoutWarnings` — current render problems (see below).

Other statuses: `"ended"` (session closed — stop polling) and `"missing"` (no session — run `edit start` first).

Treat `messages` and `newComments` as **the user's actionable requests**; `comments` and `layoutWarnings` as **context** to inform your edits.

## Layout QA

The page self-audits its rendered layout (after load and on resize) and reports issues you can't see from the source: horizontal overflow, elements wider than the viewport, and text clipped by fixed-size containers. Each warning is `{ selector, kind, detail, severity, text }`. They arrive on the poll as `layoutWarnings`, or on demand via `htmldrop edit layout <file>`. Fix `high`-severity ones (especially page/element overflow) as part of the same edit — they're common in rich artifacts and hard to notice at desk width.

## Design & Theme

Edit mode serves the file as-authored. When you generate or edit the page, match the design system of the project the artifact is about — see **`design-and-visuals.md`**. This is what makes a mock look like the real product instead of a generic page.

The control bar has a **light/dark theme toggle** (☀/☾). It stamps the standard `data-theme` (+ `color-scheme`) on the page and remembers the user's choice, so the theme they pick **survives every live reload** instead of snapping back to the artifact's default when you edit and it hot-reloads. Artifacts that honor the `data-theme` convention (see `design-and-visuals.md`) respond fully; parts keyed only to the OS `prefers-color-scheme` still follow the system, which no page script can override.

## Re-Engaging an Ended Session

If a session ended (or the user's message arrived while you weren't polling), the user can just type again in the browser — sending reopens the session and queues the message. The composer stays usable and honestly shows whether a listener caught it ("working") or it's queued for your next poll. So: when you come back, run `edit poll` again and you'll receive anything queued while you were away.

## Notes

- **One surface:** comments (persistent annotations that stay on the page) are the primary channel; each new one is delivered to you once via `edit poll`. Your `edit reply` and `edit ask` are how you talk back.
- **Ask instead of guessing:** when a change hinges on a decision only the user can make, `edit ask` with options is better than picking one silently — you get a structured answer back.
- **Localhost only + reliable:** the server binds loopback (rejects non-local requests), serves only `.html`/`.htm`, uses a stable port so the user's tab survives your restarts, persists sessions on disk, and self-shuts after idle. The user's unsent text survives a live-reload, and a failed save shows them a retry toast rather than vanishing.
