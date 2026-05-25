# Collaborative Feedback & Converge — Deep Dive

This reference covers the feedback annotation system and the AI converge loop in detail. The summary lives in `SKILL.md`; read this when you need the full mechanics, the agent loop step-by-step, or troubleshooting.

## What this system is

`htmldrop` can publish an HTML document with an **embedded annotation widget**. Anyone with the link can highlight text on the page and leave comments — like Google Docs comments, but on a standalone HTML artifact and with no sign-in. The author (and Claude, acting on the author's behalf) can then pull those comments, answer them with researched evidence, and run an AI **converge** pass that rewrites the document to address the feedback.

This turns a one-way "here is a report" into a collaborative review loop.

## The single-URL model (important)

When you run:

```bash
htmldrop push /path/to/doc.html --feedback
```

the CLI prints **one** URL:

```
https://htmldrop-feedback.htmldrop.workers.dev/doc/<uuid>
```

That `/doc/<uuid>` URL is the whole thing. There is no separate reviewer link and author link.

- **Reviewers**: open the link → read the doc → select/highlight text → type a comment → submit. **No account required.** Comments are anonymous by default; there is an optional name field they can fill in. They can also reply to existing comments.
- **Author / Claude**: opens the same link to see comments inline, and uses the CLI (`feedback pull`, `feedback add`, `converge`) to work with the feedback programmatically.

### Why the link is stable

Each file maps to a persistent `docId`. Re-pushing the **same file** with `--feedback` reuses that `docId`:

- The URL stays identical — you never have to re-share it.
- Existing comments stay attached to the document.

This stability is what makes the agent loop possible: you publish once, share the link once, and then keep updating the document at that same URL as feedback arrives.

To deliberately start over with an empty document and a brand-new link, add `--new-doc`:

```bash
htmldrop push /path/to/doc.html --feedback --new-doc
```

Use this sparingly — it abandons the old link and its comments.

## Prerequisites

1. **Author API key** — run once:
   ```bash
   htmldrop auth setup
   ```
   This generates an author key stored in `~/.htmldrop/config.json`. It identifies you as the document owner for write operations (adding comments as the author, clearing feedback, converging). Regenerate with `--force` if the key is lost or compromised:
   ```bash
   htmldrop auth setup --force
   ```

2. **For `converge` only** — the synthesis step calls an LLM. It supports **Anthropic, OpenAI, or Gemini**, and auto-detects the provider from the key prefix (`sk-ant-` → Anthropic, `AIza` → Gemini, `sk-` → OpenAI). Set whichever you have:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...   # or OPENAI_API_KEY / GEMINI_API_KEY / LLM_API_KEY
   ```
   No SDK install is needed (it uses raw fetch). Override provider/model explicitly with `--provider anthropic|openai|gemini` and `--model <id>` if desired. `--dry-run` needs no key — it only prints the prompt.

## The agent loop, step by step

This is the core new workflow. Assume Claude generated `report.html` and the user wants collaborative review.

### 1. Publish with feedback

```bash
htmldrop push /home/user/report.html --feedback
```

Capture the printed Feedback URL and give it to the user. Tell them reviewers can just open it and comment — no login needed.

### 2. Let reviewers comment

Reviewers highlight text and leave comments through the widget. Nothing for Claude to do here except wait until the user asks to check or synthesize.

### 3. Pull the feedback

When the user asks "what did reviewers say?" or before synthesizing:

```bash
htmldrop feedback pull /home/user/report.html
```

Add `--json` for structured output you can parse to find comment IDs, anchor text, authors, and replies:

```bash
htmldrop feedback pull /home/user/report.html --json
```

Use `htmldrop feedback list` to see which of your published files currently have feedback enabled.

### 4. Inject evidence-backed comments (the agent's superpower)

Claude can do more than read feedback — it can research a reviewer's question and post its findings back into the thread so the answer lives alongside the discussion. Two ways to place a comment:

**Anchor to specific text** with `--on` (the value is the exact text the comment responds to):

```bash
htmldrop feedback add /home/user/report.html \
  --text "Checked the latest spec: OAuth token TTL is 1h, so the 24h figure here is stale." \
  --name "AI Research" \
  --on "tokens are valid for 24 hours"
```

**Reply to an existing comment** with `--parent-id` (get the ID from `feedback pull --json`):

```bash
htmldrop feedback add /home/user/report.html \
  --text "Confirmed — the benchmark used a warm cache. Cold-start adds ~120ms." \
  --name "AI Research" \
  --parent-id 42
```

If you omit both `--on` and `--parent-id`, the comment is attached at the page level (general, not tied to any text). The `--name` flag sets the author label; use something clear like "AI Research" so humans can tell agent comments apart from reviewer comments.

### 5. Converge — synthesize into an improved document

```bash
htmldrop converge /home/user/report.html
```

This pulls all feedback, sends the document plus the comments to Claude, and writes an improved copy to `report.html.converged.html` (it does NOT overwrite your source). Inspect the result, and once it looks right, promote it to the working file:

```bash
cp /home/user/report.html.converged.html /home/user/report.html
```

To preview what would be sent to the model without spending an API call:

```bash
htmldrop converge /home/user/report.html --dry-run
```

This prints the assembled prompt (document + feedback) so you can sanity-check it.

### 6. Re-push to update the same link

```bash
htmldrop push /home/user/report.html --feedback
```

Because the `docId` is reused, reviewers see the updated document at the **same URL**, with their existing comments still attached. The loop can repeat: pull new feedback → answer/converge → re-push.

## Converge Studio

For a visual alternative to the CLI, launch the local dashboard:

```bash
htmldrop studio
```

Options:
- `--port <n>` — run on a specific port
- `--no-browser` — start the server without auto-opening a browser tab

The Studio lets you review incoming feedback and trigger AI insights from a web UI instead of the command line. It is a convenience layer over the same feedback data the CLI commands use.

## Reviewing a teammate's doc (no ownership)

When the doc was published by someone else, you don't have it in your manifest and you aren't the owner — but you can still fully review it from just the link they shared (plus the password, if it's a private doc). This is the teammate / second-agent flow:

```bash
# Read the document content (decrypts a password-protected page so you can analyze it)
# Bare --password reads $HTMLDROP_PASSWORD or prompts hidden, keeping the secret out of shell history.
htmldrop fetch https://their-subdomain.surge.sh/spec.html --password

# Read every reviewer comment — by the /doc/<id> link or a bare docId, no key needed
htmldrop feedback read https://htmldrop-feedback.htmldrop.workers.dev/doc/<id>

# Add your own comment, optionally anchored to exact text
htmldrop feedback add --doc-id <id|url> \
  --text "Have we considered rate-limiting here?" \
  --on "the exact phrase from the doc" \
  --name "Reviewer name"
```

`feedback read`, `feedback add --doc-id`, and `fetch` all work without the author key or a local manifest entry — they only need the link. What you **cannot** do as a non-owner is `converge` or `feedback clear`; those stay with whoever published the doc (they hold the author key). So a teammate's agent contributes feedback freely, while synthesis/cleanup remains the owner's decision.

## Clearing feedback

To wipe all comments for a document (author only):

```bash
htmldrop feedback clear /home/user/report.html
```

This is destructive and cannot be undone — confirm with the user before running it.

## Troubleshooting

| Issue | Cause / Fix |
|-------|-------------|
| Feedback command rejected / "no author key" | Run `htmldrop auth setup` once to create the author key in `~/.htmldrop/config.json`. |
| Author key seems wrong or leaked | Regenerate with `htmldrop auth setup --force`. |
| `converge` errors about API key | Set an LLM key in the environment: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `LLM_API_KEY`. |
| `converge` can't determine the provider | The key prefix is unrecognized — pass `--provider anthropic\|openai\|gemini` explicitly. |
| Feedback URL changed unexpectedly | You passed `--new-doc`; omit it so the stable `docId` (and existing comments) are reused. |
| Reviewers say they can't comment | Confirm the doc was pushed with `--feedback` (plain `push` produces a static Surge page with no widget). |
| Comment landed at page level instead of on text | Pass `--on "<exact anchor text>"`; without it, comments are general/page-level. |
| Want to see comment IDs for replies | `htmldrop feedback pull <file> --json`, then use the ID with `--parent-id`. |
| `converge` output not appearing in the live doc | Converge only writes `<file>.converged.html`. Promote it to the source file, then re-push with `--feedback`. |

## Mental model summary

- One `--feedback` push = one stable link that both reviewers and the author share.
- Reviewers need nothing but the link.
- Claude reads feedback (`pull`), answers it with researched evidence (`add --on`), and rewrites the doc (`converge`).
- Re-pushing the same file keeps the link and comments — that's the loop.
