---
name: google-analytics-setup
description: Set up Google Analytics 4 (GA4) on a website and wire a real conversion event (form submit, signup, purchase) end to end. Guides the user through account/property/data-stream creation, installing the gtag.js tag, firing a conversion event, marking it as a Key Event, and verifying it in DebugView BEFORE spending on ads. Use whenever someone wants to add GA4, "install Google Analytics", track a form submission or signup, set up conversion tracking, find their Measurement ID (G-XXXXXXXXXX), debug why GA4 events aren't showing, or decide how many GA4 properties/streams they need. Meets the user wherever they are — always asks what they've already set up first.
---

# Google Analytics 4 Setup

Get GA4 tracking a real conversion, verified end to end, so ad spend is measured against something trustworthy. GA4's model is different from old Universal Analytics, and the single most common failure is spending money before confirming the conversion event actually fires. This skill front-loads that.

## Start where the user is

GA4 setup is a chain: **account → property → data stream → tag on site → conversion event → mark as Key Event → verify**. People arrive at different points in that chain. Guessing wastes their time and risks duplicate properties (which cannot be merged later). So **always ask first** what already exists, then jump in at the right link:

Ask (adapt to what they've said):
1. Do you already have a **Google Analytics account / property**? If yes, what's it called?
2. Do you have a **data stream** for this site yet, and a **Measurement ID** (looks like `G-XXXXXXXXXX`)? If yes, paste it.
3. What's the **one conversion** that matters most (a waitlist/contact form submit, a signup, a purchase)? Everything downstream optimizes for this.
4. What's the site — a framework (Next.js, plain HTML, WordPress, Shopify) and the domain? This decides *how* the tag goes in.

Then go straight to the relevant section below. Skip what they've already done. Do NOT re-create anything that exists.

## Property and stream structure — decide once, correctly

Getting the hierarchy wrong fragments data permanently, so settle it before creating anything.

- **A GA4 property is a hard reporting boundary. Data does not flow across properties** (cross-property analysis needs BigQuery or paid GA360). So: **one property per _product_**, not per page, per feature, or per plan tier.
- **A data stream is per _domain_, not per path.** One web stream captures every path on that hostname automatically. A page like `/pricing` or `/waitlist` does NOT get its own stream — it shares the site's stream, and you tell pages apart by `page_path`.
- **Distinguish sub-parts inside one property** with `page_path` (automatic) or a **custom dimension** (e.g. `plan_tier`, `product_area`) on events — never with separate properties.
- Only make a **second stream** for a genuinely **different domain** (e.g. a separate marketing site on its own hostname).

The reason this matters: the whole point of GA4 is following a user's journey (ad → landing → signup → activation). Splitting that journey across properties severs it, and you can't un-split it.

## 1. Create the property + stream

In [analytics.google.com](https://analytics.google.com) → **Admin** (gear):

1. **Create → Property.** Name it after the product. Set the reporting time zone and currency to the business's own (this affects how days bucket and how revenue displays — a wrong time zone quietly misaligns daily reports).
2. Platform → **Web** → enter the site URL, name the stream (e.g. "Main Web"), **Create stream**.
3. On the stream page, copy the **Measurement ID** — `G-XXXXXXXXXX`. This is the one value the site's tag needs. Find it again anytime under **Admin → Data streams → [your stream]**.
4. Leave **Enhanced measurement** ON — it auto-captures page views, scrolls, and outbound clicks for free. (One caution: it warns "ensure no PII is sent" — see the PII rule below.)

## 2. Install the gtag.js tag

Paste this immediately after the opening `<head>` on every page, replacing `G-XXXXXXXXXX` with the real ID. A `page_view` fires automatically on load — you don't code that.

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**Framework-specific install** (Next.js App Router, WordPress, Shopify, plain HTML, Google Tag Manager) is in `references/install-by-platform.md` — read it for the user's stack rather than guessing, because a mis-scoped tag (e.g. loaded on the wrong Next.js boundary) is a common silent failure.

## 3. Fire the conversion event on the action

Use GA4's recommended event name for the action so it maps to built-in reports (e.g. `generate_lead` for a lead/waitlist, `sign_up` for account creation, `purchase` for a sale — full list in `references/recommended-events.md`). Fire it **only after the action truly succeeded** — after a durable write / a 2xx response — never on a caught error, or you will count failures as conversions and make the whole test lie.

```html
<script>
document.getElementById('myForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  try {
    await saveTheLead(/* ... */);      // 1. persist FIRST — the real success
    gtag('event', 'generate_lead', {   // 2. only then, count it
      // segmentable, NON-PII params only (see PII rule):
      persona: 'driver',
      value_bucket: 'high',
      currency: 'USD'
    });
    window.location.href = '/thank-you';
  } catch (err) {
    // show a friendly error — do NOT fire the event, do NOT fake success
    showError('Something went wrong, please try again.');
  }
});
</script>
```

### PII rule — do not send personal data to GA
Never put email, phone, name, or full address into event parameters. GA4's terms prohibit PII, and Enhanced measurement's own warning says the same. Send **categories and buckets** (persona, plan, a price band) that let you segment, not the person's identity. This keeps you compliant (GDPR/PDPA/CCPA) and is genuinely all you need for analysis.

## 4. Mark it as a Key Event (GA4's word for "conversion")

An event you fire is just an event until you promote it. Fire a test submit first, then in **Admin → Events**, toggle **Mark as key event** on your event row. Since 2024 GA4 calls conversions "key events" — same idea.

## 5. Verify BEFORE you spend — the gate

This is the step people skip and regret. Do a **real submit on the live (or preview) site**, then confirm the event actually landed:

- **Admin → DebugView** (add `?debug_mode=1` to the URL, or install the *GA Debugger* Chrome extension). You should see your event appear in real time, **with the right parameter values**.
- Or **Reports → Realtime** to see it within seconds.

Only once you can see the conversion fire with correct data should any ad budget go live. A conversion tracked wrong (fired on failure, missing its params, or never firing) silently invalidates every downstream number — you'd optimize against noise. The full checklist is in `references/verify-checklist.md`.

## Privacy / consent — do the proportionate thing
A simple site collecting a form needs: a one-page privacy policy linked near the form, a consent note, and honoring opt-out. For heavier compliance (EU traffic, sensitive categories) wire **Consent Mode v2** — details in `references/consent-and-privacy.md`. Don't over-build this before you have traffic, but don't skip the basics.

## "Can you set this up for me programmatically?"
Honestly, no — and it isn't worth it. GA4 has an Admin API, but it needs the user's own Google OAuth + a Google Cloud project + service account, which is more work than the ~5-minute UI click-through and can't be done on their behalf without their credentials. Do the account/property/stream creation in the UI. What you (the assistant) *can* do is write the tag + event code into their site. Split it that way.

## Reference files
- `references/install-by-platform.md` — exact tag install for Next.js, plain HTML, WordPress, Shopify, and Google Tag Manager.
- `references/recommended-events.md` — GA4 recommended event names + params for common conversions (lead, signup, purchase, add-to-cart).
- `references/verify-checklist.md` — the pre-spend verification checklist (DebugView, Realtime, common "no data" causes).
- `references/consent-and-privacy.md` — PII rules, Consent Mode v2, regional basics.
