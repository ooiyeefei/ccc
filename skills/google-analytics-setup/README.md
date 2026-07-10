# Google Analytics Setup - GA4 wired to a real conversion

Set up Google Analytics 4 on a website and wire a conversion event (form submit, signup, purchase) end to end - then verify it fires correctly **before** any ad money is spent.

---

## What It Does

Meets you wherever you are in the GA4 chain and takes you to a verified conversion:

1. **Asks what you already have** - account? property? a Measurement ID (`G-XXXXXXXXXX`)? It never re-creates what exists (duplicate GA4 properties can't be merged).
2. **Gets the structure right once** - one property per product, one stream per domain, sub-parts split by `page_path`/custom dimensions (not by extra properties).
3. **Installs the tag** for your stack - Next.js, plain HTML, WordPress, Shopify, or Google Tag Manager.
4. **Fires the conversion** with GA4's recommended event names, only on real success, with **no PII**.
5. **Marks it a Key Event** and **verifies it in DebugView** - the pre-spend gate that stops you optimizing against broken data.

## Why it exists

The most expensive analytics mistake is subtle: launching ads while the conversion event fires on failure, is missing its parameters, or never fires at all. You then optimize spend against noise and can't tell. This skill front-loads verification and keeps you compliant (no personal data sent to Google).

## Installation

```bash
/plugin marketplace add ooiyeefei/ccc
/plugin install ccc-skills@ccc
```

## Usage

Trigger it naturally:

```
"Help me set up Google Analytics on my site"
"Install GA4 and track my waitlist form submissions"
"Where do I find my Measurement ID?"
"My GA4 events aren't showing up - help me debug"
"How many GA4 properties should I have for my app + marketing site?"
```

## What you'll be asked

- Whether you already have an account / property / Measurement ID (paste it if so)
- The one conversion that matters most (a form submit, signup, purchase)
- Your site's stack + domain (so the tag goes in correctly)

## Structure

```
google-analytics-setup/
├── SKILL.md
└── references/
    ├── install-by-platform.md    # tag install for Next.js, HTML, WordPress, Shopify, GTM
    ├── recommended-events.md     # GA4 recommended event names + params per conversion
    ├── verify-checklist.md       # the pre-spend verification gate
    └── consent-and-privacy.md    # PII rules, Consent Mode v2, regional basics
```

## Note on "set it up for me"

GA4 account/property creation needs your own Google login and can't be done on your behalf - so that stays a quick UI click-through (the skill guides you). The assistant *can* write the tag + event code into your site. The skill splits the work that way.
