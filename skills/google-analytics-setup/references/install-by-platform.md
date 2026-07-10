# GA4 tag install, by platform

Pick the section matching the user's stack. The goal is identical everywhere: the gtag.js snippet loads on every page, once, as early as possible, and `window.gtag` exists before any custom event fires. Replace `G-XXXXXXXXXX` with the real Measurement ID throughout.

Note on Subresource Integrity: do NOT add an `integrity="sha384-..."` hash to the gtag.js `<script>`. Google serves that loader from a versioned URL it updates in place, and it is not published with a stable hash — an SRI attribute will break the tag. This is the documented, expected way to load it.

## Plain HTML / static site
Paste the base snippet (from SKILL.md §2) right after `<head>` on every page. If pages share a header include/partial, put it there once. Done.

## Next.js (App Router)
Use `next/script`, not a raw `<script>`, so Next controls load order and hydration.

- **Whole app:** put it in `app/layout.tsx` inside the `<body>`.
- **One route only** (e.g. a `/waitlist` landing you don't want tracking the whole authed app yet): put it in that route's `page.tsx` / segment layout. Promote to the root layout later when you want site-wide GA.

```tsx
import Script from 'next/script'
const GA_ID = 'G-XXXXXXXXXX'

<Script src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`} strategy="afterInteractive" />
<Script id="ga4-init" strategy="afterInteractive">
  {`window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', '${GA_ID}');`}
</Script>
```

`strategy="afterInteractive"` is deliberate: it guarantees `window.gtag` exists before user interactions (like a form submit) can fire your event. For custom events in a component, call `window.gtag?.('event', ...)` guarded with `?.` so it no-ops safely if a blocker prevented the script loading.

Pages Router: the same two `<Script>` tags go in `pages/_app.tsx`.

## WordPress
Two clean options:
- **Plugin:** "Site Kit by Google" (official) or "GA4 by MonsterInsights" — paste the Measurement ID in the plugin settings; it injects the tag site-wide. Easiest for non-developers.
- **Manual:** add the base snippet to the theme's `header.php` right after `<head>`, or via a "header scripts" option if the theme has one. Use a child theme so a theme update doesn't wipe it.

## Shopify
- Newer stores: **Settings → Customer events → Add custom pixel**, paste the base snippet. This is sandboxed and survives theme changes.
- Or **Online Store → Themes → Edit code → `theme.liquid`**, paste after `<head>`.
- Shopify also has a native GA4 integration under **Settings → Apps and sales channels → Google** — fine for standard e-commerce events, but a custom pixel gives you control over custom events.

## Google Tag Manager (GTM)
If the site already runs GTM, don't hard-code gtag — add GA4 through the container so all tags live in one place:
1. In GTM, **Tags → New → Google Analytics: GA4 Configuration**, enter the Measurement ID, trigger = **All Pages**.
2. For the conversion, add a **GA4 Event** tag (event name e.g. `generate_lead`) with a trigger that matches the action (a form-submit trigger, a thank-you page view, or a custom `dataLayer.push`).
3. Submit + publish the container. GTM adds a layer of indirection but is worth it once you have more than a couple of tags.

Only use GTM if it's already in place or the user expects to manage many tags — for a single conversion on a simple site, the direct gtag snippet is less overhead.
