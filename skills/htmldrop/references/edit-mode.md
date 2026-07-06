# Edit Mode — Local Real-Time Iteration

Edit mode turns an HTML file into a live, local review surface on `127.0.0.1`. The user chats, annotates, and comments in the browser; you receive their input by polling, edit the file, and it hot-reloads. Nothing is hosted or published. It's the pre-publish loop — firm a doc up with the user before sharing, or iterate between rounds of external feedback.

It is **author-facing** (the user and you), distinct from `push --feedback`, which is for **async external reviewers**. When the doc is ready, publish with `push --feedback`.

## Prerequisites

None beyond the CLI. Edit mode is fully local — no `htmldrop init`, no Surge account, no author key. If `htmldrop` isn't found: `npm install -g @yeefeiooi/htmldrop@latest`.

## Commands

| Command | Purpose |
|---------|---------|
| `htmldrop edit start <file>` | Serve the file locally + open the browser. `--with-feedback` loads the published doc's reviewer comments into the session; `--no-open` skips the browser |
| `htmldrop edit poll <file> [--json]` | **The listen call.** Blocks until the user sends a chat message or leaves a comment, then returns them plus current layout warnings. Re-run after each reply |
| `htmldrop edit reply <file> --text "<t>"` | Post your response into the conversation after editing (the user sees it, and the reloaded page reflects your change) |
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

`edit poll --json` returns a JSON object. When there's input, `status` is `"feedback"` and it carries:

- `messages` — chat messages from the user (transient instructions; each delivered once). Each may have a `context` pinning it to selected text: `{ text, selector }`.
- `newComments` — comments/annotations just left on the page (delivered once each). Each has an `anchor` (`selectedText` for text, `capturedText`+`rect` for an area, or `page_level`), `content.text`, and `author.displayName`.
- `comments` — the full current comment set, as standing context.
- `layoutWarnings` — current render problems (see below).

Other statuses: `"ended"` (session closed — stop polling) and `"missing"` (no session — run `edit start` first).

Treat `messages` and `newComments` as **the user's actionable requests**; `comments` and `layoutWarnings` as **context** to inform your edits.

## Layout QA

The page self-audits its rendered layout (after load and on resize) and reports issues you can't see from the source: horizontal overflow, elements wider than the viewport, and text clipped by fixed-size containers. Each warning is `{ selector, kind, detail, severity, text }`. They arrive on the poll as `layoutWarnings`, or on demand via `htmldrop edit layout <file>`. Fix `high`-severity ones (especially page/element overflow) as part of the same edit — they're common in rich artifacts and hard to notice at desk width.

## Design & Theme

Edit mode serves the file as-authored. When you generate or edit the page, match the design system of the project the artifact is about — see **`design-and-visuals.md`**. This is what makes a mock look like the real product instead of a generic page.

## Re-Engaging an Ended Session

If a session ended (or the user's message arrived while you weren't polling), the user can just type again in the browser — sending reopens the session and queues the message. The composer stays usable and honestly shows whether a listener caught it ("working") or it's queued for your next poll. So: when you come back, run `edit poll` again and you'll receive anything queued while you were away.

## Notes

- **Two input channels, one purpose:** chat messages are transient (delivered once, then cleared); comments are persistent annotations that stay on the page and are delivered to you once when new. Both reach you via `edit poll`.
- **Localhost only:** the server binds loopback, rejects non-local requests, and serves only `.html`/`.htm`. Safe to leave running; it self-shuts after idle.
- **Draft safety:** the user's unsent text survives a live-reload, so your edits won't wipe what they were typing.
