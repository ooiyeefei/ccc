# Privacy & Security Levels

## Comparison Table

| Protection Level | Crawlers blocked? | Casual visitors blocked? | Content encrypted? | Who can view? |
|-----------------|-------------------|-------------------------|-------------------|---------------|
| Public | No | No | No | Anyone with link |
| Public + noindex | Yes | No | No | Anyone with link (but they need to know the URL) |
| Password-protected | Yes (encrypted blob) | Yes | Yes (AES-256) | Only people with password |

## How Password Protection Works

The `--password` flag uses the StatiCrypt pattern:

1. Content is encrypted with AES-256 (via crypto-js) before upload
2. Surge hosts only the encrypted ciphertext + a password prompt page
3. Decryption happens entirely in the viewer's browser
4. No server-side auth (works on Surge free tier)

## The zero-knowledge guarantee

The single most important property: **htmldrop never stores the password** — not on disk, not on any server, not in `~/.htmldrop/config.json`. It's held in memory just long enough to encrypt the file at push time, then discarded. This is a deliberate guarantee, not a limitation. It's the reason a breach of Surge, the feedback Worker, or the local `~/.htmldrop` config can never expose a private doc: there is no password there to find.

The direct consequence is that **a forgotten password can't be recovered** — there's nothing to recover it from. That trade-off *is* the security property, so the workflow is to save the password at the moment you create it:

- **Generate one** — `htmldrop push file.html --password --generate-password` prints a memorable password (two words + a number) once; copy it straight into your manager.
- **Pipe it from your password manager** so it never touches shell history:
  ```bash
  htmldrop push file.html --password "$(op read op://vault/item/password)"   # 1Password CLI
  htmldrop push file.html --password "$(bw get password <id>)"               # Bitwarden
  htmldrop push file.html --password "$(pass show <name>)"                   # pass
  ```
- **Bare `--password`** reads from `$HTMLDROP_PASSWORD` or a hidden prompt, keeping a typed or pasted value out of shell history.

Lost the password? Re-push the file with a new one — the old encrypted version is overwritten.

## Security Assessment

**Good enough for:**
- Internal specs and reports
- Proposals and project plans
- Non-public designs and prototypes
- Team brainstorm outputs

**NOT suitable for:**
- Highly sensitive data (financial, medical, credentials)
- Compliance-regulated documents
- Data requiring audit trails

## Recoverable & managed access (a different tier)

The zero-knowledge guarantee answers "can a breach leak my private doc?" — no, the password isn't stored. Its flip side is that a forgotten password can't be recovered. If *you* lose the password to your own doc, re-push with a new one and re-share it.

A different need — "the **organization** can always regain access, and we can **revoke a specific person**" — is *not* something stored passwords would solve. Storing passwords to enable recovery would break the zero-knowledge guarantee for *every* doc and still wouldn't give per-person control. The right answer is **identity / role-based access**: access granted by *who you are* (an account, an email allowlist, a role), re-grantable by an owner and revocable per person, with no shared secret to memorize or leak.

This is a deliberate future direction for htmldrop, **not implemented today**. The password-as-capability model the Worker already speaks (see the htmldrop project's design doc `docs/plans/2026-05-25-password-capability-design.md`) points toward capability/role-based access. Note the trade-off it implies: identity-based content access means the server can decrypt your doc on demand to grant or revoke per person — which is exactly why it's a separate tier rather than a free upgrade to today's model.

**Which do you need today?**

- A trusted team sharing one link + password out of band (password manager, Slack, email) — today's model is sufficient and keeps the guarantee.
- Per-person control ("only Jane can open it; remove Alex when they leave") and org-level recoverability — identity-based access, a future tier. For now, rotate the password (re-push) when the team changes.

## FAQ

**Can AI agents read password-protected files?**
No. The actual HTML content is AES-256 encrypted ciphertext on the server. Crawlers see only the password prompt page and gibberish. Even if scraped, the content is unreadable without the key.

**How does noindex work?**
Injects `<meta name="robots" content="noindex, nofollow">` into the HTML. A site-level `robots.txt` with `Disallow: /` is also deployed during `htmldrop init`. This tells well-behaved crawlers to skip the content, but the page is still viewable by anyone with the direct link.

**Is client-side encryption safe?**
For the intended use case (sharing internal documents with specific people), yes. The content cannot be read without the password. The main limitation vs server-side auth is that there's no rate limiting on password attempts — but since each attempt requires downloading and decrypting in-browser, brute-force is impractical for any reasonably strong password.

**Can I change the password later?**
Re-push the file with a new `--password` value. The old encrypted version is overwritten.
