---
name: meta-pixel-setup
description: Set up the Meta Pixel (Facebook/Instagram ads tracking) on a website and fire a conversion event (Lead, CompleteRegistration, Purchase) end to end. Guides the user through Business Suite / Events Manager, creating or finding the Pixel/Dataset ID, installing the base code, firing a standard event, and verifying it with the Meta Pixel Helper BEFORE running ads. Use whenever someone wants to add the Meta/Facebook Pixel, track FB/IG ad conversions, install "the pixel", find their Pixel/Dataset ID, set up a Lead or Purchase event for Meta ads, debug why Pixel events aren't firing, or is being pushed by Meta's wizard toward the Conversions API and isn't sure if they need it. Meets the user wherever they are — always asks what they've already set up (Facebook Page? Business Suite? a Pixel ID?) first.
---

# Meta Pixel Setup

Get the Meta Pixel tracking a real conversion on a website, verified, so Facebook/Instagram ad optimization has something true to learn from. Two things trip people up and this skill front-loads both: **the Pixel-vs-Conversions-API decision** (Meta's wizard aggressively pushes the heavier one) and **which data category to declare** (a wrong choice can throttle your ads).

Naming note: Meta renamed "Pixel" to **"Dataset"** in the UI. A dataset contains the pixel and its **Dataset ID = Pixel ID** (a ~15–16 digit number). Treat the two words as the same thing.

## Start where the user is

Setup is a chain: **Facebook Page → Business portfolio → Events Manager → Pixel/Dataset (get the ID) → base code on site → conversion event → verify.** People arrive mid-chain. Ask first, then jump in — don't re-create what exists (a business often already has a pixel; reuse it rather than fragmenting data across two).

Ask (adapt to what they've said):
1. Do you have a **Facebook Page** and **Meta Business Suite / Business portfolio** set up already?
2. Do you already have a **Pixel / Dataset** (in Events Manager)? If yes, what's the **Dataset ID** (the ~16-digit number)? Paste it — that may be all that's needed.
3. What's the **one conversion** that matters (a lead/waitlist submit, a signup, a purchase)? This is what ads optimize toward.
4. The site's **stack + domain** (Next.js, plain HTML, WordPress, Shopify) — decides how the code goes in.

If they already have the Dataset ID and a Page, skip straight to install (§3). Do not walk them back through account creation they've done.

## Decision 1: Pixel only, or + Conversions API? (start with Pixel only)

Meta's setup wizard shows **"Conversions API and Meta Pixel (Recommended)"** with a shiny stat. Don't reflexively take it. Here's the honest trade-off:

- **Meta Pixel (browser)** — a code snippet on the site sends events from the visitor's browser. Simple, no backend, works today. **This is all you need to launch.**
- **Conversions API (CAPI)** — your *server* sends events directly to Meta. It's server-to-server, **"developer support required,"** and to actually help it needs **customer PII** (email, phone, IP) sent to Meta for matching. That's more build **and** a bigger privacy/compliance surface (GDPR/PDPA/CCPA).

So: **launch with the browser Pixel.** Add CAPI later, only if browser signal loss (ad-blockers, iOS ATT) is measurably hurting you and you've resolved the PII/consent question. Treat CAPI as a post-launch optimization, not a setup step. Read `references/conversions-api.md` before ever wiring it — it exists to stop you sending personal data to Meta by accident.

## Decision 2: the Dataset "category" — leave it blank unless it clearly fits

When creating the dataset, Meta asks to "select any applicable categories." **This is a trap for finance/health/sensitive products.** The dialog warns: *"depending on the category and location, data sharing may be limited or blocked."* Categories like **"Financial service," "Economic vulnerability," "Personal hardship," "Nationality"** trigger Meta's restricted-data handling and can **throttle or block your ad optimization**.

Rule: **only tick a category if it accurately and unavoidably describes you, and you understand it restricts data.** A budgeting/productivity/SaaS tool is *software*, not a "financial service" (that category is for lenders, credit reports, consumer finance). When in doubt, **leave categories empty** (it's optional) — empty means no restriction, which is what a normal waitlist/signup test wants.

## 1. Create or find the Pixel/Dataset (get the ID)

In [Events Manager](https://business.facebook.com/events_manager):
1. Left rail → **Connect data** (green +) → **Web** → **Meta Pixel** → Connect. (Or if a dataset exists, click it — the ID is right under its name.)
2. Name it after the business (e.g. "Acme Web"). For category, see Decision 2 (usually leave blank).
3. **Copy the Dataset ID** — the ~16-digit number under the name. Also always visible later under **Events Manager → Datasets**.
4. If it launches a "set up / connect your website" wizard offering Conversions-API vs Pixel-only — you can **close/skip it**. You only need the ID; the code goes in by hand (§3). If you do proceed, choose **Meta Pixel only** (Decision 1).

## 2. (Optional) Reuse an existing pixel
A pixel is **not** a hard reporting wall like a GA4 property. **One pixel can cover a whole domain** — the main app *and* a `/waitlist` landing page. Distinguish funnels by the event + custom params (e.g. `content_name: 'waitlist'`), not by a second pixel. If the business already has one, reuse its ID.

## 3. Install the base code

Paste in `<head>` on every page, replacing `YOUR_PIXEL_ID`. It fires `PageView` automatically. (Copy your exact snippet from Events Manager — it has the ID pre-filled — or use this canonical form.)

```html
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window,document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', 'YOUR_PIXEL_ID');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
  src="https://www.facebook.com/tr?id=YOUR_PIXEL_ID&ev=PageView&noscript=1"/></noscript>
<!-- End Meta Pixel Code -->
```

Do NOT add an `integrity`/SRI hash — `fbevents.js` is a versioned loader Meta updates in place and doesn't publish a stable hash for; SRI will break it. Framework-specific install (Next.js `next/script`, WordPress, Shopify, GTM) is in `references/install-by-platform.md`.

## 4. Fire the conversion event on the action

Use a **standard event** so Meta's optimization and reporting recognize it — `Lead` (waitlist/contact), `CompleteRegistration` (signup), `Purchase` (sale). Full list + when to use each: `references/standard-events.md`. Fire it **only after the action truly succeeded**, never on a caught error.

```html
<script>
form.addEventListener('submit', async function (e) {
  e.preventDefault();
  try {
    await saveTheLead(/* ... */);          // 1. persist FIRST — the real success
    if (window.fbq) fbq('track', 'Lead', { // 2. only then, count it (guard for blockers)
      content_name: 'waitlist',            // segmentable, NON-PII params only
      value_bucket: 'high'
    });
    window.location.href = '/thank-you';
  } catch (err) {
    showError('Something went wrong, please try again.');  // no event, no fake success
  }
});
</script>
```

### PII rule — do not send personal data through the browser Pixel
Never pass email, phone, name, or address as event parameters. Send **categories/buckets** (content_name, a value band, a persona) — enough to segment, not to identify. (The one place Meta *does* use hashed PII is CAPI's Advanced Matching, which is a deliberate, consented, server-side choice — see `references/conversions-api.md`, not something to sprinkle into browser events.)

## 5. Verify BEFORE you spend — the gate
Do a **real conversion on the live/preview site**, then confirm:
- Install the **Meta Pixel Helper** Chrome extension. Load the page → it shows the pixel + `PageView`. Submit the form → it shows the `Lead` event **with your params**.
- Or **Events Manager → your dataset → Test events**, enter the site URL, and watch events arrive live.
- **Only fires on success:** cause a failure and confirm the event does NOT fire.

Only after you can see the conversion fire correctly should ad budget go live. A miswired conversion makes Meta optimize toward the wrong people and you can't tell from the dashboard. Full checklist: `references/verify-checklist.md`.

## "Can you set this up for me?"
The **account/Page/Business-Suite/Pixel creation** needs the user's own Meta login — can't be done on their behalf; that's a short UI walk (this skill guides it). Getting the **Dataset ID** is the user's one job. The assistant *can* write the base code + event into the site once it has the ID. Split it that way — and steer them away from the CAPI wizard and sensitive categories per the two decisions above.

## Reference files
- `references/install-by-platform.md` — base-code install for Next.js, HTML, WordPress, Shopify, GTM.
- `references/standard-events.md` — Meta standard event names + params for common conversions.
- `references/conversions-api.md` — what CAPI is, when it's worth it, and the PII/consent guardrails BEFORE wiring it.
- `references/verify-checklist.md` — the pre-spend verification gate (Pixel Helper, Test Events, common failures).
