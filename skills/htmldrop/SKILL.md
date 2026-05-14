---
name: htmldrop
description: Share HTML files as hosted links with one command. Use when the user asks to "share this HTML", "publish HTML", "get a link for this file", "share this report", "make this shareable", or wants to publish any HTML artifact for others to view. Wraps Surge.sh for zero-cost hosting with guided privacy options.
---

# htmldrop - Share HTML as Hosted Links

Publish any HTML file and get a shareable URL instantly. Wraps Surge.sh via the `htmldrop` CLI with guided privacy and sharing options.

---

## Quick Start

**User just asks:**
```
"Share this HTML file"
"Publish this report"
"Get me a link for this"
"Make this shareable"
"/share filename.html"
"Upload this HTML"
```

**Claude Code will:**
1. Verify `htmldrop` is installed and initialized
2. **Ask the user about their sharing preferences** (see Guided Sharing Flow)
3. Push the HTML file with appropriate settings
4. Return the shareable URL (+ password if private)

---

## Prerequisites

- Node.js >= 18
- `npm install -g htmldrop`
- Run `htmldrop init` once (sets up Surge account + subdomain)

---

## Critical Rules

1. **Always check prerequisites first** - htmldrop must be installed and initialized before any push
2. **Never store credentials** - all auth is handled by Surge via `~/.netrc`
3. **ALWAYS ask about sharing preference before pushing** - never assume public or private
4. **For password-protected files** - always show the user both the URL AND the password
5. **If generating HTML + sharing** - generate the HTML file first, verify it exists, then push
6. **Prefer absolute paths** when calling `htmldrop push`

---

## Guided Sharing Flow (MANDATORY)

**Every time a user asks to share a file, follow this guided flow:**

### Step 1: Check Prerequisites

```bash
# Check if htmldrop is installed
which htmldrop

# Check if initialized
test -f ~/.htmldrop/config.json && echo "initialized" || echo "not initialized"
```

If not set up, guide them through first-time setup (see Flow: First-time Setup below).

### Step 2: Ask Sharing Preference

**Always ask the user:**

> "How would you like to share this?"
>
> 1. **Public** — Anyone with the link can view it. Fast, no friction for viewers.
> 2. **Password-protected** — Viewers need a password to unlock. Content is encrypted (AES-256) before upload — crawlers and AI agents cannot index it.

Wait for user's answer before proceeding.

### Step 3a: If Public

Ask one follow-up:

> "Should I block search engines and AI crawlers from indexing this? (adds robots.txt disallow)"
>
> - **Yes** — Adds `noindex` meta tag. Won't appear in search results, but anyone with the direct link can still view.
> - **No** — Fully public and indexable.

Then push:

```bash
# Public, indexable
htmldrop push /path/to/file.html

# Public, but blocks crawlers
htmldrop push --noindex /path/to/file.html
```

### Step 3b: If Password-Protected

Ask:

> "What password would you like? Or I can generate a memorable one for you."

Options:
- User provides a password → use it
- User says "generate one" → generate a 3-word memorable password (e.g., `coral-sunset-42`, `blue-river-88`)

Then push:

```bash
htmldrop push --password <password> /path/to/file.html
```

### Step 4: Return Results

**For public files:**
```
Published! Your link: https://yoursite.surge.sh/report.html
```

**For public + noindex files:**
```
Published! Your link: https://yoursite.surge.sh/report.html
(Search engines and AI crawlers are blocked from indexing this page)
```

**For password-protected files:**
```
Published with password protection!

  URL: https://yoursite.surge.sh/spec.html
  Password: coral-sunset-42

Share both the URL and password with your recipients.
The content is AES-256 encrypted — only someone with the password can view it.
```

---

## Privacy & Security Levels Explained

Use this to answer user questions about what each option provides:

| Protection Level | Crawlers blocked? | Casual visitors blocked? | Content encrypted? | Who can view? |
|-----------------|-------------------|-------------------------|-------------------|---------------|
| Public | ❌ | ❌ | ❌ | Anyone with link |
| Public + noindex | ✅ | ❌ | ❌ | Anyone with link (but they need to know the URL) |
| Password-protected | ✅ (encrypted blob) | ✅ | ✅ (AES-256) | Only people with password |

**If user asks "how secure is the password protection?":**
- Content is encrypted with AES-256 before upload
- Surge only hosts the encrypted ciphertext + a password prompt page
- Decryption happens entirely in the viewer's browser
- No server-side auth (Surge free tier limitation)
- Good enough for: internal specs, reports, proposals, non-public designs
- NOT suitable for: highly sensitive data (financial, medical, credentials)

**If user asks "can AI agents read my protected files?":**
- No. The actual HTML content is encrypted ciphertext on the server.
- Crawlers see only the password prompt page + gibberish.
- Even if scraped, the content is AES-256 encrypted and unreadable without the key.

---

## Flows

### Flow: First-time Setup

Before any push operation, if prerequisites are missing:

```
"htmldrop isn't set up yet. Let me help you get started:

1. Install the CLI:
   npm install -g htmldrop

2. Initialize (pick your subdomain + Surge login):
   htmldrop init

   This will ask you for:
   - A subdomain name (e.g., 'my-docs' → https://my-docs.surge.sh/)
   - Your Surge email and password (first time only — token saved for future use)

Once done, just ask me to share again!"
```

**Important:** `htmldrop init` must be run interactively by the user (Surge requires interactive email/password input on first login). Do NOT attempt to run init non-interactively.

### Flow: Share a File

Follow the Guided Sharing Flow above (Steps 1-4).

### Flow: List Published Files

```bash
htmldrop list
```

Shows all published files with their URLs, dates, sizes, and whether they're password-protected.

### Flow: Generate HTML then Share

When the user asks Claude to create an HTML artifact AND share it:

1. Generate the HTML file and write it to disk
2. Verify the file exists: `test -f /path/to/file.html`
3. Follow the Guided Sharing Flow (ask public/private preference)
4. Push with appropriate flags
5. Return the URL

---

## Example Interactions

### Example 1: Guided Public Share

```
User: Share report.html

Claude: How would you like to share this?
  1. Public — Anyone with the link can view it
  2. Password-protected — Encrypted, viewers need a password

User: Public is fine

Claude: Should I block search engines and AI crawlers from indexing this?
  - Yes (adds noindex)
  - No (fully public)

User: Yes block them

Claude:
  [runs: htmldrop push --noindex /home/user/project/report.html]

  Published! Your link: https://yoursite.surge.sh/report.html
  (Search engines and AI crawlers are blocked from indexing this page)
```

### Example 2: Guided Private Share

```
User: Share this spec with the team

Claude: How would you like to share this?
  1. Public — Anyone with the link can view it
  2. Password-protected — Encrypted, viewers need a password

User: Password protect it

Claude: What password would you like? Or I can generate a memorable one for you.

User: Generate one

Claude:
  [runs: htmldrop push --password blue-canyon-77 /home/user/spec.html]

  Published with password protection!

    URL: https://yoursite.surge.sh/spec.html
    Password: blue-canyon-77

  Share both the URL and password with your team.
  The content is AES-256 encrypted — only someone with the password can view it.
```

### Example 3: Generate + Share in One Step

```
User: Create a summary of this PR as HTML and share it privately

Claude:
  [generates HTML report, writes to /tmp/pr-summary.html]

  Done! I've created the PR summary. Now let's share it.

  Since you mentioned sharing privately, I'll password-protect it.
  What password would you like, or should I generate one?

User: Use "teamreview"

Claude:
  [runs: htmldrop push --password teamreview /tmp/pr-summary.html]

  Published with password protection!

    URL: https://yoursite.surge.sh/pr-summary.html
    Password: teamreview

  Share both with your team.
```

### Example 4: User Explicitly Says Public/Private

If the user already states their preference in the initial request, skip the question:

```
User: Share report.html publicly
→ Skip Step 2, go directly to public push

User: Share spec.html with password "hello123"
→ Skip Step 2 and password question, push with provided password

User: Publish this privately
→ Skip Step 2, go to password flow
```

---

## Integration with Other Skills

This skill pairs well with:

- **HTML generation** - Claude Code generates specs, reports, PR reviews as HTML, then shares instantly
- **excalidraw skill** - export diagrams to HTML and share
- **Any workflow producing HTML artifacts** - dashboards, documentation, visualizations

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `htmldrop: command not found` | Run `npm install -g htmldrop` |
| `Not initialized` | Run `htmldrop init` interactively |
| Push fails with auth error | Run `htmldrop init` again to re-authenticate with Surge |
| File not found | Use absolute path to the HTML file |
| Password forgotten | Re-push the file with a new password (overwrites previous) |
| Want to remove a file | Push will overwrite; to fully remove, use `surge teardown` on the domain |
