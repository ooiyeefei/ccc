# Conversions API (CAPI) — what it is, when it's worth it, and the guardrails

Read this BEFORE wiring CAPI. Its main job here is to stop you sending personal data to Meta by accident and to help you decide whether you even need it yet.

## What it is
The browser Meta Pixel sends events from the visitor's browser. The **Conversions API** sends the same events from **your server**, directly to Meta, server-to-server. Meta pushes it hard ("Recommended", "17.8% lower cost per result") because browser signal is increasingly lost to ad-blockers, iOS App Tracking Transparency, and cookie/ITP restrictions — CAPI recovers some of that.

## Why NOT to start with it
- **It's more build.** Meta itself labels it "developer support required." You need a server endpoint that calls the Graph API with each event.
- **To actually help, it wants PII.** CAPI's value comes from **Advanced Matching**: sending **hashed** email / phone / IP / name so Meta can match events to accounts. That means personal data leaves your server for Meta — a real GDPR/PDPA/CCPA surface that needs a consent + privacy-policy basis you must set up deliberately.
- **The browser Pixel alone is enough to launch** and validate a campaign. Signal loss matters at scale, not on day one.

**So: launch Pixel-only. Add CAPI later, only when (a) you can show browser signal loss is hurting results, and (b) you've handled the consent/PII basis.** Treat it as a post-launch optimization.

## If/when you do add it — the guardrails
1. **Only hash-and-send PII you have a lawful basis + consent for.** Email/phone must be SHA-256 hashed before sending (Meta's SDKs do this). Never send raw PII. Never send data for users who opted out.
2. **Deduplicate against the browser Pixel.** Send the same logical event from both, sharing a common `event_id`, so Meta collapses them and doesn't double-count. Without this your conversion counts inflate.
3. **Send only the events that matter** (your core conversion), not everything — less data leaving your server, cleaner signal.
4. **Prefer a managed path over hand-rolling** if you can: Meta's **Conversions API Gateway**, or an integration via your CDP/Zapier/Segment, handles hashing + dedup correctly. Hand-building the Graph calls is where PII mistakes happen.
5. **Regional consent:** for EU/UK traffic, gate CAPI sends on consent (Consent Mode-style). For MY/SG/ID PDPA, ensure your privacy notice covers sharing hashed identifiers with Meta.

## The wizard trap
Meta's setup flow steers you into "Conversions API and Meta Pixel" and then into selecting **customer-information parameters** (Email, Phone, IP). If you're just trying to get the browser pixel live, that path will walk you into a PII/server setup you didn't intend. **Close/skip that wizard** and install the browser base code by hand (SKILL.md §3). Come back to CAPI as a separate, deliberate project.
