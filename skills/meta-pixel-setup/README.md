# Meta Pixel Setup - Facebook/Instagram ads tracking, wired right

Set up the Meta Pixel on a website and fire a conversion event (Lead, CompleteRegistration, Purchase) end to end - then verify it before running FB/IG ads. Steers you past the two things Meta's own wizard gets people wrong: the Conversions-API push and the sensitive-data category trap.

---

## What It Does

Meets you wherever you are and takes you to a verified conversion:

1. **Asks what you already have** - Facebook Page? Business Suite? an existing Pixel/Dataset ID? It reuses an existing pixel rather than fragmenting data.
2. **Makes the two key decisions for you:**
   - **Pixel-only vs Conversions API** - start with the browser Pixel; CAPI is a post-launch optimization that needs PII + a server, so don't let the wizard push you into it on day one.
   - **The dataset "category"** - leave it blank unless it truly fits; picking "Financial service" and similar can *throttle or block* your ads.
3. **Gets you the Dataset ID** (the ~16-digit number - Meta renamed "Pixel" to "Dataset").
4. **Installs the base code** for your stack - Next.js, HTML, WordPress, Shopify, GTM.
5. **Fires the conversion** with a standard event, only on real success, **no PII**.
6. **Verifies with the Meta Pixel Helper** before any spend - the gate that stops you optimizing toward the wrong audience.

## Why it exists

Meta's setup flow aggressively recommends the Conversions API (server-side, needs personal data) and prompts you to declare a data category - both easy to get wrong in ways that cost money or leak PII. This skill encodes the safe defaults and the pre-spend verification most people skip.

## Installation

```bash
/plugin marketplace add ooiyeefei/ccc
/plugin install ccc-skills@ccc
```

## Usage

Trigger it naturally:

```
"Help me add the Meta pixel to my landing page"
"Set up Facebook Pixel to track my waitlist signups"
"Where do I get my Pixel / Dataset ID?"
"Meta's asking me to set up the Conversions API - do I need it?"
"My Facebook Pixel events aren't showing in Events Manager"
```

## What you'll be asked

- Whether you already have a Facebook Page / Business Suite / Pixel (paste the Dataset ID if you have it)
- The one conversion that matters (lead, signup, purchase)
- Your site's stack + domain

## Structure

```
meta-pixel-setup/
├── SKILL.md
└── references/
    ├── install-by-platform.md   # base-code install for Next.js, HTML, WordPress, Shopify, GTM
    ├── standard-events.md       # Meta standard event names + params per conversion
    ├── conversions-api.md       # what CAPI is, when it's worth it, PII/consent guardrails
    └── verify-checklist.md      # the pre-spend verification gate (Pixel Helper, Test Events)
```

## Note on "set it up for me"

The Page / Business Suite / Pixel creation needs your own Meta login, so that's a short UI walk (the skill guides it) - getting the Dataset ID is your one job. The assistant *can* write the base code + event into your site once it has the ID, and will steer you away from the CAPI wizard and sensitive categories.
