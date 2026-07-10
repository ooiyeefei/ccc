# Meta Pixel base-code install, by platform

Same goal everywhere: the base snippet loads once on every page, as early as possible, `window.fbq` exists before any custom event fires, and it sends `PageView` on load. Replace `YOUR_PIXEL_ID` throughout. Always prefer copying your exact snippet from Events Manager (it has the ID pre-filled).

Do NOT add an `integrity`/SRI hash to the `fbevents.js` script — it's a versioned loader Meta updates in place with no stable published hash, so SRI breaks it. This is the documented way to load it.

## Plain HTML / static site
Paste the base snippet (SKILL.md §3) right after `<head>` on every page (or in a shared header include). The `<noscript>` img goes right after it.

## Next.js (App Router)
Use `next/script` so load order is controlled and it survives hydration. Note: with `strategy="afterInteractive"` the inline init is injected **client-side after hydration** — so it won't appear in server-rendered HTML / `curl` output, only in a real browser. That's expected; verify with the Pixel Helper, not curl.

```tsx
import Script from 'next/script'
const PIXEL_ID = 'YOUR_PIXEL_ID'

<Script id="meta-pixel-init" strategy="afterInteractive">
  {`!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window,document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '${PIXEL_ID}');
fbq('track', 'PageView');`}
</Script>
<noscript>
  {/* eslint-disable-next-line @next/next/no-img-element */}
  <img height="1" width="1" style={{ display: 'none' }} alt=""
    src={`https://www.facebook.com/tr?id=${PIXEL_ID}&ev=PageView&noscript=1`} />
</noscript>
```

For custom events in a component, call `window.fbq?.('track', 'Lead', {...})` guarded with `?.` so it no-ops if a blocker stopped the script.

- **Whole app:** put the `<Script>` in `app/layout.tsx`.
- **One route only:** put it in that route's `page.tsx`. Promote to the root layout later for site-wide tracking.

## WordPress
- **Plugin:** "PixelYourSite" or Meta's "Facebook for WordPress" — paste the Pixel ID in settings; injects site-wide + maps common events.
- **Manual:** base snippet into the theme's `header.php` after `<head>` (use a child theme so updates don't wipe it).

## Shopify
- **Native:** Settings → Apps and sales channels → Facebook & Instagram → connect; it wires the pixel + standard e-commerce events automatically. Easiest for a store.
- **Custom pixel:** Settings → Customer events → Add custom pixel, paste the base snippet (sandboxed, survives theme changes) — use this when you need custom events beyond the standard commerce set.

## Google Tag Manager (GTM)
If GTM is already running the site:
1. There's no official Meta pixel tag template, so use a **Custom HTML** tag containing the base snippet, trigger = **All Pages**.
2. Add another **Custom HTML** tag with `fbq('track','Lead', {...})` for the conversion, triggered by the form-submit / thank-you-page trigger.
3. Submit + publish.
Only worth it if GTM is already the site's tag hub; otherwise the direct snippet is simpler.
