# htmldrop — Share HTML as Hosted Links (+ collaborative feedback & AI converge)

A Claude Code skill that publishes HTML files as shareable links, and — when you want review — embeds an annotation widget so others can comment, then synthesizes that feedback with AI. It wraps the `htmldrop` CLI; you just describe what you want in natural language.

Two modes:

1. **Simple share** — publish any HTML and get a public or password-protected link (free, via Surge.sh).
2. **Collaborative feedback + converge** — publish with `--feedback` so reviewers highlight text and comment (no account, one stable link), then pull and synthesize that feedback into an improved version.

---

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Prerequisites

```bash
# Install the htmldrop CLI (the skill drives this)
npm install -g @yeefeiooi/htmldrop@latest

# One-time: Surge login + subdomain (for simple share)
htmldrop init

# One-time: author key (for feedback/converge)
htmldrop auth setup
```

Requires Node.js ≥ 18.

### The AI key is optional (bring-your-own)

Sharing and the **whole feedback loop work without any LLM key** — publish, password-protect, enable `--feedback`, and collect/pull/add/reply/clear comments. You only need an LLM key for the **AI features**: `htmldrop converge` (synthesizing feedback into an improved doc) and the dashboard’s AI insights.

If you want those, set a key in your environment — `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `LLM_API_KEY`. The provider is auto-detected from the key prefix; no SDK install needed.

- **Your key, your cost.** You pay your provider (Anthropic / OpenAI / Gemini) directly at their rates — htmldrop adds no markup and has no key of its own.
- **It’s never stored.** The key is read from your terminal environment for a single run; the dashboard keeps it in browser session memory and clears it when you close the tab. Nothing is written to disk or any server.
- **Handle it securely.** Keep it in an environment variable on your own terminal, don’t commit it, and rotate it if exposed.

---

## How you use it: just talk to Claude Code

The skill recognizes intent from plain language and runs the right `htmldrop` command. The examples below are labeled (E1–E6) so you can follow a full review cycle, but each line works on its own.

### Simple sharing

| You say | What the skill does |
|---|---|
| **E1.** “Share this report publicly: report.html” | `htmldrop push report.html` → returns the URL |
| “Share spec.html but password-protect it” | asks for / generates a password, then `htmldrop push --password …` |
| “Block crawlers from indexing it” | adds `--noindex` |
| “List everything I’ve published” | `htmldrop list` |

### Collaborative review (the feedback loop)

| You say | What the skill does |
|---|---|
| **E2.** “Publish this spec so reviewers can comment on it” | `htmldrop push spec.html --feedback` → returns one stable Feedback URL |
| **E3.** “What did reviewers say?” | `htmldrop feedback pull spec.html` → summarizes the comments |
| **E4.** “Add a note backing up the Postgres choice, anchored to where it mentions PostgreSQL” | researches, then `htmldrop feedback add spec.html --on "PostgreSQL" --name "AI Research" --text …` |
| **E5.** “Synthesize all the feedback into a better version” | `htmldrop converge spec.html` → writes `spec.converged.html` |
| **E6.** “Publish the updated version” | re-push with `--feedback` → **same link**, comments intact |
| **E7.** (teammate) “Review this doc they shared: <link> — read the comments and add mine” | `htmldrop feedback read <link>`, then `htmldrop feedback add --doc-id <link> …` — no ownership needed |

In **E2**, the Feedback URL is the single link everyone uses: reviewers open it, **select text → “+ Comment”**, and leave anchored comments with no account. You open the same link to see them inline.

For a **private doc**, add `--password` to E2 (“publish it privately but still collect feedback”) — the widget appears after the viewer decrypts. In **E7**, a teammate's agent can also run `htmldrop fetch <link> --password <pw>` to read the protected content before commenting.

You can also use the direct command:

```
/share report.html
```

---

## Features

- **Instant sharing** — one request to publish any HTML file, free on Surge.sh
- **Password protection** — AES-256 client-side encryption; share URL + password. The password is stored **nowhere** (encrypts in memory, then discarded) — save it yourself, since a forgotten one can't be recovered (just re-push)
- **Works with generated HTML** — Claude Code can create a report/spec and share it in one step
- **Collaborative feedback** — `--feedback` embeds an annotation widget; reviewers highlight text **or drag a box over an area** (▢) and comment at one stable link, with replies and page-level notes
- **Private feedback** — combine `--feedback --password` so a password-protected doc still collects comments (widget appears after decryption)
- **Teammate / multi-agent review** — anyone with the link can read + comment via `feedback read`, `feedback add --doc-id`, and `fetch` (no ownership, no key); their Claude/Codex session participates the same way
- **Roles** — reviewers (link holders) read + comment; the owner (author-key holder) additionally `converge`s and clears — so synthesis stays with the publisher
- **Agent participation** — Claude can read feedback, post evidence-backed anchored comments, and reply
- **AI converge** — synthesize all feedback into an improved document; supports **Anthropic, OpenAI, or Gemini** (auto-detected from your key, overridable)
- **Converge Studio** — `htmldrop studio` opens a visual dashboard with segments, debate detection, and per-segment insights

---

## The agent loop

The reason the feedback features exist: an agent can run the whole cycle for you.

```
generate doc → push --feedback → share link
   → reviewers comment
   → pull feedback → add researched/anchored comments → converge
   → re-push (same link, comments intact) → repeat
```

Re-pushing keeps the **same URL** (the docId is reused), so the document iterates in place while reviewers keep the link they already have. See **`references/feedback-workflow.md`** for the full step-by-step.

---

## How it works

1. `htmldrop` wraps Surge.sh for static hosting (simple share).
2. Surge auth lives in `~/.netrc`; the feedback author key in `~/.htmldrop/config.json`.
3. Simple-share files publish to your subdomain on surge.sh.
4. `--feedback` documents are served from the feedback Worker at one stable `/doc/<uuid>` link used by both reviewers and the author.
5. AI features use a bring-your-own LLM key — in the dashboard it’s held in session memory only and cleared when you close the browser.

## Where comments live (data ownership)

Surge hosts the HTML (stores nothing); a Cloudflare Worker + KV stores the **comments** (a static page can't accept writes). You choose whose Worker:

- **Free tier (shared Worker):** zero setup; comments sit in *our* Cloudflare, **auto-expire after 90 days**, clearable anytime (`htmldrop feedback clear`), code is open-source. Honest caveat: convenient, but **not** zero-knowledge.
- **Own your data (self-host):** deploy the Worker to *your* free Cloudflare account (`cd worker && wrangler deploy`), then `export HTMLDROP_WORKER_URL=https://your-worker.workers.dev` — now we see nothing.
- **Comments in your repo (either tier):** `htmldrop feedback pull <file> --save` writes them to `<file>.feedback.json` — owned + versioned in your repo. Reviewers never need repo access; you sync.

No database to manage — storage is Cloudflare KV only (no Supabase/Postgres).

---

## License

MIT
