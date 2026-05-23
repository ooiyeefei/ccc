---
name: htmldrop
description: This skill should be used when the user asks to "share this HTML", "publish HTML", "get a link for this file", "share this report", "make this shareable", "upload this HTML", or wants to publish any HTML artifact for others to view. ALSO use it for collaborative review on an HTML doc/spec/report — triggers include "get feedback on this", "let reviewers comment", "collect feedback", "share for review", "let people annotate this", "synthesize the feedback", "converge the feedback", "what did reviewers say", "incorporate the comments", or "improve this from the feedback". Wraps Surge.sh for zero-cost hosting with guided privacy options, plus an embedded annotation + AI converge workflow.
---

# htmldrop — Share HTML as Hosted Links

Publish any HTML file and get a shareable URL instantly via the `htmldrop` CLI. Two modes:

- **Simple share** (Surge.sh hosting) — get a public or password-protected link to a static page.
- **Collaborative feedback + converge** — publish with an embedded annotation widget so reviewers can highlight text and comment with no account, then pull the feedback, add evidence-backed comments programmatically, and synthesize an improved version with AI.

## Prerequisites

- Node.js >= 18
- `npm install -g @ooiyeefei/htmldrop@latest` (the binary is still `htmldrop`)
- For **simple share**: run `htmldrop init` once (sets up Surge account + subdomain)
- For **feedback/converge**: run `htmldrop auth setup` once (generates an author API key in `~/.htmldrop/config.json`)

## Critical Rules

1. **Check prerequisites first** — the relevant setup must be done before any push
2. **Never store credentials** — Surge auth lives in `~/.netrc`; the feedback author key lives in `~/.htmldrop/config.json`
3. **For password-protected files** — report both the URL and the password to the user
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

**If password-protected** — ask for a password or offer to generate a memorable one (e.g., `coral-sunset-42`):
```bash
htmldrop push --password <pass> /path/to/file.html
```

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
Share both with your recipients.
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
| `htmldrop push <file>` | Publish a file (flags: `--password`, `--noindex`, `--open`) |
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

- **Reviewers** open it, highlight any text, and leave comments — **no account, no login**. They comment anonymously (an optional name field is available).
- **The author** uses the same link to see the page with all comments rendered inline.

There is no separate "viewer link" vs "author link." Share the one URL and you are done.

**The link is stable.** Re-pushing the *same file* with `--feedback` reuses its `docId`, so the URL never changes and existing comments stay attached. This is why the agent loop below works: you can keep updating the document at the same link as feedback comes in. Use `--new-doc` only when you deliberately want a fresh, empty doc.

### Prerequisites for this mode

- `htmldrop auth setup` run once (creates the author API key). Add `--force` to regenerate it.
- `converge` additionally needs `ANTHROPIC_API_KEY` in the environment and the optional SDK: `npm install @anthropic-ai/sdk`.

### Feedback & Converge Commands

| Command | Purpose |
|---------|---------|
| `htmldrop auth setup [--force]` | One-time: generate an author API key. Required before any feedback feature. |
| `htmldrop push <file> --feedback` | Publish with the annotation widget; prints a stable Feedback URL. Re-push same file → same link, comments preserved. |
| `htmldrop push <file> --feedback --new-doc` | Force a fresh feedback doc/link (clean slate). |
| `htmldrop feedback pull <file> [--json]` | Retrieve all feedback (comments + replies) for a file. |
| `htmldrop feedback list` | List which published files have feedback enabled. |
| `htmldrop feedback add <file> --text "..." [--name "..."] [--on "<anchor text>"] [--parent-id <id>]` | Post a comment programmatically (the agent write path). `--on` anchors to specific text; default is page-level. `--parent-id` replies to a comment. |
| `htmldrop feedback clear <file>` | Delete all feedback for a file (author only). |
| `htmldrop converge <file> [--dry-run]` | Pull all feedback → send to Claude → write `<file>.converged.html`. `--dry-run` prints the prompt without calling the API. |
| `htmldrop studio [--port <n>] [--no-browser]` | Open the local "Converge Studio" dashboard to review feedback + trigger AI insights. |

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

4. **Converge** — synthesize all comments into an improved document:
   ```bash
   htmldrop converge /path/to/doc.html
   ```
   This writes `/path/to/doc.html.converged.html`. Review it, then promote it to the working file (e.g., copy it over `doc.html`) once it looks right. Use `--dry-run` first to inspect the prompt without spending an API call.

5. **Re-push to the same link** — publish the improved version so reviewers see it update in place:
   ```bash
   htmldrop push /path/to/doc.html --feedback
   ```
   Same URL, comments intact. The loop can repeat as more feedback arrives.

For the detailed walkthrough, the single-URL mechanics, anchoring rules, and troubleshooting, read **`references/feedback-workflow.md`**.

---

## Generate Then Share

When the user asks to create an HTML artifact AND share/review it:

1. Generate the HTML file and write it to disk
2. Verify it exists: `test -f /path/to/file.html`
3. Pick the mode:
   - Just a link → follow the **Simple Share** guided flow
   - Collaborative review → use `--feedback` and follow the **Agent Loop**

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `htmldrop: command not found` | `npm install -g @ooiyeefei/htmldrop@latest` |
| Not initialized (simple share) | Run `htmldrop init` interactively |
| Auth error on push | Run `htmldrop init` to re-authenticate |
| Feedback command rejected / no author key | Run `htmldrop auth setup` once |
| `converge` fails | Ensure `ANTHROPIC_API_KEY` is set and `npm install @anthropic-ai/sdk` is done |
| Feedback link changed unexpectedly | You likely passed `--new-doc`; omit it to keep the stable link |
| File not found | Use absolute path |
| Change password | Re-push with new `--password` (overwrites) |

## Additional Resources

- **`references/feedback-workflow.md`** — Deep dive on the feedback + converge agent loop, single-URL model, auth setup, and troubleshooting
- **`references/privacy-levels.md`** — Detailed privacy/security comparison and user FAQ
