---
name: htmldrop
description: This skill should be used when the user asks to "share this HTML", "publish HTML", "get a link for this file", "share this report", "make this shareable", "upload this HTML", or wants to publish any HTML artifact for others to view. Wraps Surge.sh for zero-cost hosting with guided privacy options.
---

# htmldrop — Share HTML as Hosted Links

Publish any HTML file and get a shareable URL instantly via the `htmldrop` CLI and Surge.sh.

## Prerequisites

- Node.js >= 18
- `npm install -g htmldrop`
- Run `htmldrop init` once (sets up Surge account + subdomain)

## Critical Rules

1. **Check prerequisites first** — htmldrop must be installed and initialized before any push
2. **Never store credentials** — all auth is handled by Surge via `~/.netrc`
3. **Follow the guided sharing flow** — ask about privacy preference before pushing
4. **For password-protected files** — report both the URL and the password to the user
5. **Use absolute paths** when calling `htmldrop push`

## Guided Sharing Flow

Every share request follows this sequence:

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

## Commands Reference

| Command | Purpose |
|---------|---------|
| `htmldrop init` | One-time setup (subdomain + Surge login) |
| `htmldrop push <file>` | Publish a file (flags: `--password`, `--noindex`, `--open`) |
| `htmldrop list` | Show all published files with URLs |
| `htmldrop delete <file>` | Remove a file and redeploy |
| `htmldrop open <file>` | Open published file in browser |

## Generate Then Share

When the user asks to create an HTML artifact AND share it:

1. Generate the HTML file and write it to disk
2. Verify it exists: `test -f /path/to/file.html`
3. Follow the guided sharing flow above
4. Push with appropriate flags and return the URL

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `htmldrop: command not found` | `npm install -g htmldrop` |
| Not initialized | Run `htmldrop init` interactively |
| Auth error on push | Run `htmldrop init` to re-authenticate |
| File not found | Use absolute path |
| Change password | Re-push with new `--password` (overwrites) |

## Additional Resources

- **`references/privacy-levels.md`** — Detailed privacy/security comparison and user FAQ
