# htmldrop - Share HTML as Hosted Links

Share any HTML file and get a hosted URL instantly. Powered by Surge.sh. Optionally publish with an embedded annotation widget so reviewers can comment, then synthesize that feedback with AI.

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
# Install the htmldrop CLI
npm install -g htmldrop@latest

# Initialize simple sharing (creates Surge account + picks your subdomain)
htmldrop init

# One-time setup for the feedback/converge features (generates an author key)
htmldrop auth setup
```

Requires Node.js >= 18. The `converge` command additionally needs `ANTHROPIC_API_KEY` and `npm install @anthropic-ai/sdk`.

## Quick Start

After installing, just ask Claude Code:

```
"Share this HTML file"
"Publish report.html"
"Get me a link for this"
"Make this shareable"
```

Or, for collaborative review:

```
"Share this spec so the team can comment on it"
"Get feedback on report.html"
"What did reviewers say?"
"Converge the feedback into a better version"
```

Or use the command directly:

```
/share report.html
```

Claude Code will push the file and return a shareable URL.

## Features

- **Instant sharing**: One command to publish any HTML file
- **Zero cost**: Hosted on Surge.sh for free
- **Password protection**: Optionally restrict access with a password
- **Works with generated HTML**: Claude Code can create an HTML report/spec and share it in one step
- **List published files**: See all your shared files and their URLs
- **Collaborative feedback**: Publish with `--feedback` to embed an annotation widget — reviewers highlight text and comment with no account, at one stable link
- **AI converge**: Pull all feedback and synthesize an improved version of the document with `htmldrop converge`

## Password Protection

To share a file with restricted access:

```
"Share spec.html but password-protect it"
```

Claude Code will ask for a password (or generate one), push the file, and give you both the URL and the password to share with recipients.

## Collaborative Feedback & Converge

Publish a doc, spec, or report with an embedded annotation widget so others can review it:

```
"Get feedback on report.html"
```

Claude Code pushes the file with `--feedback` and returns a single, stable Feedback URL. Reviewers open that link, highlight text, and comment — no account needed. Later, Claude can pull the feedback, post evidence-backed answers as comments, and run `htmldrop converge` to synthesize an improved version, then re-push to update the same link.

See `references/feedback-workflow.md` for the full agent loop.

## How It Works

1. `htmldrop` wraps Surge.sh for static file hosting (simple share)
2. Surge authentication is stored in `~/.netrc`; the feedback author key lives in `~/.htmldrop/config.json`
3. Simple-share files are published to your chosen subdomain on surge.sh
4. `--feedback` documents are served from the feedback worker at one stable `/doc/<uuid>` link that both reviewers and the author share

## License

MIT
