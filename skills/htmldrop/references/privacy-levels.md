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

## FAQ

**Can AI agents read password-protected files?**
No. The actual HTML content is AES-256 encrypted ciphertext on the server. Crawlers see only the password prompt page and gibberish. Even if scraped, the content is unreadable without the key.

**How does noindex work?**
Injects `<meta name="robots" content="noindex, nofollow">` into the HTML. A site-level `robots.txt` with `Disallow: /` is also deployed during `htmldrop init`. This tells well-behaved crawlers to skip the content, but the page is still viewable by anyone with the direct link.

**Is client-side encryption safe?**
For the intended use case (sharing internal documents with specific people), yes. The content cannot be read without the password. The main limitation vs server-side auth is that there's no rate limiting on password attempts — but since each attempt requires downloading and decrypting in-browser, brute-force is impractical for any reasonably strong password.

**Can I change the password later?**
Re-push the file with a new `--password` value. The old encrypted version is overwritten.
