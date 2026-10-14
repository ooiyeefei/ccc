# Privacy & Security Levels

## Comparison Table

| Protection Level | Crawlers blocked? | Casual visitors blocked? | Content encrypted? | Who can view? |
|-----------------|-------------------|-------------------------|-------------------|---------------|
| Public | No | No | No | Anyone with link |
| Public + noindex | Cooperative crawlers only | No | No | Anyone with link (but they need to know the URL) |
| Password-protected | Yes (encrypted blob) | Yes | Yes (AES-256) | Only people with password |

## How Password Protection Works

The `--password` flag uses the StatiCrypt pattern:

1. Content is encrypted with AES-256 (via crypto-js) before upload
2. Surge hosts only the encrypted ciphertext + a password prompt page
3. Decryption happens entirely in the viewer's browser
4. No server-side auth (works on Surge free tier)

## Password handling

The CLI documents a design that holds the password in memory for encryption and does not persist it in local configuration or on the server. Verify that behaviour in the installed CLI; its implementation is not bundled here. This is not a confidentiality guarantee for attached assets, selected-text feedback or document context sent to a convergence model. Password protection of the HTML does not audit those separate paths.

The direct consequence is that **a forgotten password can't be recovered** — there's nothing to recover it from. That trade-off *is* the security property, so the workflow is to save the password at the moment you create it:

- **Generate and save one in your password manager**, then supply it through a hidden prompt. Do not use a generator mode that prints a password into agent or terminal logs.
- **Use a protected environment or hidden prompt** instead of expanding a password-manager secret into command arguments. Prepare the environment through the owner's secure tooling without echoing the value.
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

Not persisting the password means the service cannot recover it for you. If you lose it, re-push from your local source with a new password and re-share. A service breach can still expose whatever its other paths store; review assets, feedback and convergence separately.

A different need — "the **organization** can always regain access, and we can **revoke a specific person**" — is *not* something stored passwords would solve. Storing passwords to enable recovery would break the zero-knowledge guarantee for encrypted docs and still wouldn't give per-person control. The right answer is **identity / role-based access**: access granted by *who you are* (an account, an email allowlist, a role), re-grantable by an owner and revocable per person, with no shared secret to memorize or leak.

This is a deliberate future direction for htmldrop, **not implemented today**. The password-as-capability model the Worker already speaks (see the htmldrop project's design doc `docs/plans/2026-05-25-password-capability-design.md`) points toward capability/role-based access. Note the trade-off it implies: identity-based content access means the server can decrypt your doc on demand to grant or revoke per person — which is exactly why it's a separate tier rather than a free upgrade to today's model.

**Which do you need today?**

- A trusted team sharing one link + password out of band (password manager, Slack, email) — use today's model only for content allowed by the repository's sharing policy.
- Per-person control ("only Jane can open it; remove Alex when they leave") and org-level recoverability — identity-based access, a future tier. For now, rotate the password (re-push) when the team changes.

## FAQ

**Can AI agents read password-protected files?**
No. The actual HTML content is AES-256 encrypted ciphertext on the server. Crawlers see only the password prompt page and gibberish. Even if scraped, the content is unreadable without the key.

**How does noindex work?**
Injects `<meta name="robots" content="noindex, nofollow">` into the HTML. A site-level `robots.txt` with `Disallow: /` is also deployed during `htmldrop init`. This tells well-behaved crawlers to skip the content, but the page is still viewable by anyone with the direct link.

**Is client-side encryption safe?**
For the intended use case (sharing internal documents with specific people), yes. The content cannot be read without the password. An attacker can download the ciphertext once and attempt passwords offline, so there is no server-side rate limit protecting those attempts. Use a strong manager-generated password. This does not replace the repository's restrictions on sensitive material.

**Can I change the password later?**
Re-push the file with a new `--password` value. The old encrypted version is overwritten.
