---
name: htmldrop
description: >-
  Reach for this skill when an HTML artifact — report, deck, brief, mockup, dashboard, proposal, spec, or landing page, whether the user already has it or you just generated it — needs to reach other people or get tightened before it ships. Three situations: (1) they want a shareable link — public, or password-protected so only a client or specific people can open it; (2) they want reviewers to comment/annotate on it, then pull that feedback back to answer, fold, or synthesize into a revised version; (3) they want to co-edit it with you live and locally first — pointing at sections and commenting while you edit in real time, nothing deployed — to polish before sending. Cues: share, publish, get a link, password-protect, send to the client, collect or incorporate feedback, review it together, iterate in edit mode. Not for deploying apps/frameworks (Vercel, Next.js, npm), CSS/layout debugging, PDF annotation, A/B testing, or emailing screenshots.
---

# htmldrop — Share HTML as Hosted Links

Publish any HTML file and get a shareable URL instantly via the `htmldrop` CLI. Three modes:

- **Simple share** (Surge.sh hosting) — get a public or password-protected link to a static page.
- **Collaborative feedback + converge** — publish with an embedded annotation widget so reviewers can highlight text and comment with no account, then pull the feedback, add evidence-backed comments programmatically, and synthesize an improved version with AI.
- **Edit mode** (local, pre-publish) — serve the file on `127.0.0.1` and iterate on it live *with the user*: they annotate and comment on one surface; you edit the file (it hot-reloads), reply, or ask them a question. No hosting, nothing published. This is the loop to firm a doc up before sharing it — or between rounds of external feedback. See **`references/edit-mode.md`**.

**Design applies to every mode:** before generating or serving any HTML, match the design system of the project the artifact is about, so it looks like the real product rather than a generic page. See **`references/design-and-visuals.md`** — read it whenever you author or edit HTML here.

---

## MUST DO BEFORE WRITING ANY HTML (all modes)

This fires **automatically**, whether the user runs simple share, feedback, or edit mode — and whether or not they ever type a `htmldrop playbook`/`htmldrop design` command. It is the default behavior of this skill, not an opt-in. Do both, in order, before you write or edit a single line of HTML:

1. **Match the look first (theme + styling).** Detect and adopt the design system of the project the artifact is *about* (not necessarily your current working dir), in this priority:
   1. a look/system the user named → use exactly that;
   2. the target project's design system → Tailwind/theme config, `:root` CSS variables/design tokens, an in-use component library, or brand assets (logo, palette, fonts) on an existing styled page;
   3. nothing to match → a clean, deliberate neutral default (small palette, system font stack, generous spacing, clear hierarchy).
   When you deliver, state which source you used in one line ("styled with the project's Tailwind theme" / "no theme found — neutral default"). **Never ship a generic template when a real design system was discoverable.**

2. **Pick the right shape (the MUST-router).** Match the content against these triggers and reach for the right structure before writing. One artifact often combines several:
   - **relationships / flows / architecture / sequences** → a real **Mermaid diagram**, never hand-built `<div>` boxes. Re-render on light/dark flip (Mermaid never restyles an already-drawn SVG).
   - **comparing options / tools / approaches / tradeoffs** → aligned option cards; make the **cost as visible as the benefit** (don't hide the downside).
   - **teaching a concept / how something works** → the **explainer shape**: (a) lead with the one idea that explains everything; (b) a "feel-the-difference" micro-demo with the smallest honest code (a 450ms `setTimeout` *is* network lag; a toggle *is* a mode switch); (c) a looping before/after; (d) a cheat-sheet table last, including the honest trade-off.
   - **proposing a change / roadmap / approach** → goal → current → proposed → risks → open questions. Mock the UI, don't describe it.
   - **dense structured data / many attributes** → a real `<table>`, aligned columns, no horizontal overflow, highlight the decision-relevant column.
   - **a decision/answer needed from the viewer** → an in-artifact form with native controls and one explicit **send answer** per question that delivers the choice to the agent via the feedback channel (not a local-only "queued" state that never arrives).
   - **sequential narrative to step through** → slides: one idea each, large type, keyboard nav.

**The full contract lives in `references/design-and-visuals.md`** — ready-to-paste pinned CDN snippets (with integrity hashes), a layout-safety CSS block, a theme-aware Mermaid re-render snippet, and the per-shape guidance. Read it before authoring; it is the single source of truth for both the guardrail above and the optional commands below.

**Optional standalone commands (same content, on demand).** If you (or a non-skill agent, or a curious user) want the guidance without this skill loaded, the CLI exposes it directly — these are a convenience, not a replacement for the guardrail:
- `htmldrop design [--json]` — prints the design contract (priority rule, pinned snippets, layout-safety CSS, theme-aware Mermaid).
- `htmldrop playbook [id] [--json]` — lists the shapes, or prints one (`diagram`, `comparison`, `input`, `plan`, `table`, `slides`, `explainer`).

## Prerequisites

- Node.js >= 18
- `npm install -g @yeefeiooi/htmldrop@latest` (the binary is still `htmldrop`)
- For **simple share**: run `htmldrop init` once (sets up Surge account + subdomain)
- For **feedback/converge**: run `htmldrop auth setup` once (generates an author API key in `~/.htmldrop/config.json`)
- For **edit mode**: nothing — it's fully local (no `init`, no Surge, no auth key). Lowest-friction entry point.

## Critical Rules

1. **Check prerequisites first** — the relevant setup must be done before any push
2. **Never store credentials** — Surge auth lives in `~/.netrc`; the feedback author key lives in `~/.htmldrop/config.json`
3. **For password-protected files** — report the URL and password to the user, and remind them htmldrop stores the password nowhere (it's unrecoverable), so they should save it in a password manager now
4. **Use absolute paths** when calling `htmldrop push`

---

## Mode 1: Simple Share (Guided Flow)

This is the most common case — "just give me a link." Follow this sequence.

### Step 1: Verify Environment

```bash
which htmldrop
test -f ~/.htmldrop/config.json && echo "initialized" || echo "not initialized"
```

If not set up, direct the user to run `htmldrop init` interactively. The first deploy triggers Surge's interactive email/password login. After that, the token is saved in `~/.netrc` and future deploys are automatic.

### Step 2: Ask Privacy Preference

Present two options:

1. **Public** — Anyone with the link can view it
2. **Password-protected** — Content is AES-256 encrypted; viewers need a password to unlock

### Step 3: Handle Based on Choice

**If public** — ask one follow-up: "Block search engines and AI crawlers from indexing?"
- Yes → `htmldrop push --noindex /path/to/file.html`
- No → `htmldrop push /path/to/file.html`

**If password-protected** — ask for a password, offer to generate one, or pipe one from the user's password manager. htmldrop **never stores the password** (held in memory only to encrypt at push time, then discarded), so tell the user to save it in their password manager the moment it's created — a forgotten one can't be recovered (re-push with a new one). Three ways to supply it:

```bash
# 1. Let htmldrop generate a memorable one (two words + a number), printed once:
htmldrop push --password --generate-password /path/to/file.html

# 2. Pipe from a password manager so it never touches shell history:
htmldrop push --password "$(op read op://vault/item/password)" /path/to/file.html   # 1Password
htmldrop push --password "$(bw get password <id>)" /path/to/file.html               # Bitwarden
htmldrop push --password "$(pass show <name>)" /path/to/file.html                   # pass

# 3. A known value:
htmldrop push --password <pass> /path/to/file.html
```

A bare `--password` (no value) reads from `$HTMLDROP_PASSWORD` or a hidden prompt.

### Step 4: Report Results

**Public:**
```
Published: https://subdomain.surge.sh/filename.html
```

**Password-protected:**
```
Published with password protection!
  URL: https://subdomain.surge.sh/filename.html
  Password: coral-sunset-42
htmldrop never stores this password — it can't be recovered.
Save it in your password manager now, then share both with your recipients.
```

### Skip the Flow When Intent is Clear

If the user explicitly states preference in their request, skip the question:
- "Share report.html publicly" → push directly
- "Share spec.html with password hello123" → push with provided password
- "Publish this privately" → go to password flow

### Simple-Share Commands

| Command | Purpose |
|---------|---------|
| `htmldrop init` | One-time setup (subdomain + Surge login) |
| `htmldrop push <file>` | Publish a file (flags: `--password`, `--generate-password`, `--noindex`, `--open`) |
| `htmldrop list` | Show all published files with URLs |
| `htmldrop delete <file>` | Remove a file and redeploy |
| `htmldrop open <file>` | Open published file in browser |

---

## Mode 2: Collaborative Feedback & Converge

Use this when the user wants people to **review and comment** on an HTML doc, spec, or report — or when they want to **pull, answer, or synthesize** that feedback. Publishing with `--feedback` embeds an annotation widget in the page.

### The Single-URL Model

`htmldrop push <file> --feedback` prints **one** shareable Feedback URL like:

```
https://htmldrop-feedback.htmldrop.workers.dev/doc/<uuid>
```

That single `/doc/<uuid>` link serves everyone:

- **Reviewers** open it, highlight any text (or drag a box over an area via the **▢** toggle) and leave comments — **no account, no login**. They comment anonymously (an optional name field is available).
- **The author** uses the same link to see the page with all comments rendered inline.

There is no separate "viewer link" vs "author link." Share the one URL and you are done.

**The link is stable.** Re-pushing the *same file* with `--feedback` reuses its `docId`, so the URL never changes and existing comments stay attached. This is why the agent loop below works: you can keep updating the document at the same link as feedback comes in. Use `--new-doc` only when you deliberately want a fresh, empty doc.

### Prerequisites for this mode

- `htmldrop auth setup` run once (creates the author API key). Add `--force` to regenerate it.
- `converge` additionally needs an LLM API key (Anthropic, OpenAI, or Gemini) in the environment — `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `LLM_API_KEY`. The provider is auto-detected from the key; override with `--provider`/`--model`. No SDK install needed.

### Feedback & Converge Commands

| Command | Purpose |
|---------|---------|
| `htmldrop auth setup [--force]` | One-time: generate an author API key. Required before any feedback feature. |
| `htmldrop push <file> --feedback` | Publish with the annotation widget; prints a stable Feedback URL. Re-push same file → same link, comments preserved. |
| `htmldrop push <file> --feedback --password <pw>` | Feedback-enabled **private** doc — the widget appears after the viewer decrypts. Review link is the password-gated URL (reviewers need the password). |
| `htmldrop push <file> --feedback --new-doc` | Force a fresh feedback doc/link (clean slate). |
| `htmldrop feedback pull <file> [--json]` | Retrieve feedback for **your own** file (uses local manifest + author key). |
| `htmldrop feedback read <docId\|url> [--json]` | Read feedback for **any** doc by id or link — no ownership/manifest. Use this when reviewing a teammate's doc. |
| `htmldrop feedback list` | List which published files have feedback enabled. |
| `htmldrop feedback add [file] --text "..." [--doc-id <id\|url>] [--name "..."] [--on "<anchor>"] [--parent-id <id>]` | Post a comment (the agent write path). `--doc-id` comments on a doc you didn't publish; `--on` anchors to text; `--parent-id` replies. |
| `htmldrop feedback clear <file>` | Delete all feedback for a file (**owner only**). |
| `htmldrop pull <url> [--password <pw>] [--output <f>]` | Reconstruct the clean editable source from a published doc and re-link it to the **same** doc/link. A teammate pulls, edits, and `push --feedback` back to the same link with comments intact (no git). |
| `htmldrop identity export [--json]` / `htmldrop identity import <blob> [--force]` | Share one **team** identity so teammates publish to the same link. Use a dedicated team account, never a personal one. |
| `htmldrop fetch <url> [--password <pw>] [--out <f>]` | Fetch + decrypt a published doc so the agent can read its content (use with a teammate's link + password). |
| `htmldrop converge <file> [--dry-run]` | One-shot: pull all feedback → LLM → write `<file>.converged.html`, **auto-resolving** disagreements (**owner only**). `--dry-run` prints the prompt without calling the API. |
| `htmldrop studio [--port <n>] [--no-browser]` | Open the local "Converge Studio" dashboard to review feedback + trigger AI insights. |

**Roles:** anyone with the link is a **reviewer** (read + comment, via `feedback read` / `feedback add --doc-id` / `fetch` — no key). The **owner** (author-key holder who published) additionally runs `converge` and `feedback clear`. So a teammate's Claude/Codex session can fully review a shared doc, but only the owner synthesizes/converges it.

### The Agent Loop

When Claude generates a doc/spec/report and the user wants collaborative review, this is the workflow:

1. **Generate & publish** — write the HTML, then:
   ```bash
   htmldrop push /path/to/doc.html --feedback
   ```
   Share the printed Feedback URL with the user. Reviewers comment on it directly.

2. **Pull feedback** — when the user asks what reviewers said, or before synthesizing:
   ```bash
   htmldrop feedback pull /path/to/doc.html
   ```

3. **Inject researched answers (optional but powerful)** — Claude can respond to a comment with its own evidence after researching. Anchor the reply to the exact text being discussed:
   ```bash
   htmldrop feedback add /path/to/doc.html \
     --text "Verified against the 2026 pricing docs: the tier cap is 500 req/s, not 200." \
     --name "AI Research" \
     --on "the rate limit is 200 req/s"
   ```
   Use `--parent-id <id>` to reply directly under a specific reviewer comment instead of anchoring to text.

4. **Converge** — synthesize all comments into an improved document. Two paths:
   - **One-shot (automated):** `htmldrop converge /path/to/doc.html` pulls all feedback, calls an LLM, and writes `/path/to/doc.html.converged.html`. It **auto-resolves** disagreements itself. Review it, then promote it over `doc.html` once it looks right. Use `--dry-run` first to inspect the prompt without spending an API call.
   - **Interactive (human-in-the-loop):** when you edit the doc directly instead, work in two tiers — **fold in the clear wins** (objective improvements with nothing to decide, e.g. a vague success metric → a concrete, measurable target) but **leave judgment calls for the human** (genuine disagreements / strategic forks, e.g. "ship iOS-first vs Android-first"): don't silently pick one — leave that part unchanged and lay out both sides with a recommendation so the human decides.

5. **Close the loop — post resolutions back as replies.** After you fold in a comment or the human decides an open item, reply on that reviewer's comment so the resolution lives on the document (reviewer refreshes the link → sees their comment was addressed → and why):
   ```bash
   htmldrop feedback pull /path/to/doc.html --json   # get comment ids
   htmldrop feedback add /path/to/doc.html --parent-id <id> --name "<author>" --text "<how it was resolved>"
   ```
   For a **password-gated** doc, add `--password <pw>` to the reply (gated feedback requires the token derived from the password).

6. **Re-push to the same link** — publish the improved version so reviewers see it update in place:
   ```bash
   htmldrop push /path/to/doc.html --feedback
   ```
   Same URL, comments intact. The loop can repeat as more feedback arrives.

For the detailed walkthrough — single-URL mechanics, anchoring rules, the two-tier converge (clear wins vs. judgment calls), closing the loop with reply resolutions, and troubleshooting — read **`references/feedback-workflow.md`**.

---

## Mode 3: Edit Mode (Local, Real-Time Iteration)

Use this when the user wants to **refine an HTML doc or page with you, live, before publishing** — not to collect async feedback from others. It runs entirely on `127.0.0.1`; nothing is hosted.

The core is a listen loop: you serve the file, the user annotates/comments in the browser, and you **poll** to receive their input, edit the file, and it hot-reloads. Minimal shape:

```bash
htmldrop edit start /abs/path/doc.html        # serve locally; opens the browser
htmldrop edit ls [--json]                     # list all local edit sessions + which have unaddressed input
htmldrop edit poll /abs/path/doc.html --json  # BLOCKS until the user leaves a comment (or answers a question)
# → act on what you receive, edit doc.html (it live-reloads), then:
htmldrop edit reply /abs/path/doc.html --text "what you changed"
# → re-run `edit poll` and repeat. `edit ask` puts a question to the user;
#   `edit layout` checks render issues; `edit end` closes it.
```

Keep `edit poll` running like any long-poll — it stays silent until there's input, so re-run it after each reply. When the doc is ready, publish with `htmldrop push --feedback` (Mode 2) for external review. To iterate on feedback you already collected, `htmldrop edit start <file> --with-feedback` loads those reviewer comments into the session.

**Read `references/edit-mode.md` before running an edit session** — it has the full command reference, the poll payload shape (messages / comments / layout warnings), the listen-loop pattern, and how design/theme matching applies here.

---

## Generate Then Share

When the user asks to create an HTML artifact AND share/review it:

1. Generate the HTML file and write it to disk — first run the **MUST DO BEFORE WRITING ANY HTML** step above (match the theme, pick the right shape), per **`references/design-and-visuals.md`**
2. Verify it exists: `test -f /path/to/file.html`
3. Pick the mode:
   - Just a link → follow the **Simple Share** guided flow
   - Collaborative (async) review → use `--feedback` and follow the **Agent Loop**
   - Iterate live with the user first → **Edit mode** (`references/edit-mode.md`), then publish when ready

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `htmldrop: command not found` | `npm install -g @yeefeiooi/htmldrop@latest` |
| Not initialized (simple share) | Run `htmldrop init` interactively |
| Auth error on push | Run `htmldrop init` to re-authenticate |
| Feedback command rejected / no author key | Run `htmldrop auth setup` once |
| `converge` fails | Ensure an LLM key is set (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` / `LLM_API_KEY`); pass `--provider` if the key prefix is unrecognized |
| Feedback link changed unexpectedly | You likely passed `--new-doc`; omit it to keep the stable link |
| File not found | Use absolute path |
| Change password | Re-push with new `--password` (overwrites) |
| `edit poll` returns nothing | Correct — it blocks silently until the user acts. Leave it running; re-run after each reply |
| Edit session won't start / stale | `htmldrop edit stop`, then `htmldrop edit start <file>` again |

## Additional Resources

- **`references/edit-mode.md`** — Local real-time edit mode: commands, the listen loop, poll payload, layout QA, re-engaging an ended session
- **`references/design-and-visuals.md`** — Match the project's design system (all modes) + when to make an artifact more visual/dynamic, **plus the full design contract** (pinned CDN snippets, layout-safety CSS, theme-aware Mermaid) and the per-shape playbook router. Same content as `htmldrop design` / `htmldrop playbook`.
- **`references/feedback-workflow.md`** — Deep dive on the feedback + converge agent loop, single-URL model, auth setup, and troubleshooting
- **`references/privacy-levels.md`** — Detailed privacy/security comparison and user FAQ
