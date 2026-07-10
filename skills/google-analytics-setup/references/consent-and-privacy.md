# GA4 privacy, PII, and consent — proportionate setup

Do the basics always; add heavier compliance only when your traffic/region requires it. Don't over-build before you have visitors, but the basics are non-negotiable because they're cheap and protect you.

## The hard rule: no PII to Google
GA4's terms **prohibit personally identifiable information** in any hit — email, phone, name, full address, government IDs. Violations can get your data purged and the property flagged. This is why the skill's event examples pass **buckets/categories** (persona, plan, value band), never the person's identity. It's also all analysis needs — you segment by cohort, not by individual.

If your URLs can contain PII (e.g. `?email=...`), turn on **Admin → Data streams → your stream → Redact data** to strip email/query-param values before they're stored.

## Baseline (every site collecting a form)
- A one-page **privacy policy** linked near the form.
- A short **consent/purpose note** ("we'll use this to contact you about X") + an opt-out path.
- Honor deletion/opt-out requests.

That's proportionate for a simple waitlist or contact form.

## When you need more — Consent Mode v2
If you have **EU/EEA/UK traffic** (GDPR), or you run Google Ads and want modeled conversions to work, wire **Google Consent Mode v2**. It gates analytics/ad storage on the visitor's consent choice and lets Google model the gap. Setup:
- A consent banner (many CMPs do this: Cookiebot, Osano, Termly, or a GTM consent template).
- Set default consent to denied, update to granted on user opt-in, before the GA config runs.
- Reference: https://developers.google.com/tag-platform/security/guides/consent

## Regional quick notes
- **EU/UK (GDPR):** consent required before non-essential cookies; Consent Mode v2 strongly recommended.
- **California (CPRA):** honor opt-out of sale/share; a "Do Not Sell/Share" link.
- **Malaysia (PDPA), Singapore (PDPA), Indonesia (PDP):** consent + purpose notice + honor withdrawal. A DPO is only mandatory above high data-subject thresholds — a pre-launch waitlist is far below, so consent + notice + opt-out suffices.

The through-line: collect the minimum, tell people why, let them leave, and never hand Google their identity.
