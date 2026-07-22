# Brand-match - use the product's real identity, not an approximation

A marketing film that is off-brand reads as fake and undoes itself. Before building any scene,
find the product's REAL font, logo, wordmark, and palette in its own repo and wire them in verbatim.
Do not eyeball a "close enough" font or a similar blue.

## Where the assets actually live

Search the product repo, in this order:

- **Font.** `next/font` in a layout (`import { Geist } from "next/font/google"`), or a
  `tailwind.config` `fontFamily`, or an `@font-face` in the global CSS pointing at a local woff2/otf.
  Grep: `next/font|fontFamily|@font-face|--font-`. The variable name (e.g. `--font-geist-sans`) tells
  you the family. Load it in Remotion via `@remotion/google-fonts` (see `remotion.md`) or embed the
  local file.
- **Logo mark + wordmark.** Grep `logo|wordmark|<Logo|brand`. Often an inline SVG (sometimes a
  base64 data-URI in a hero component) and a PNG/SVG wordmark in `public/`. Copy the wordmark into
  the Remotion project's `public/` and use `staticFile()`; inline the SVG mark as a component.
- **Palette.** The landing/marketing page and the global CSS/tailwind tokens carry the real hexes.
  Grep the marketing component for `#[0-9A-Fa-f]{6}` and sort by frequency - the top few are the
  brand colours. Note which is the primary (actions), which is reserved for positive/semantic use,
  and the real surface/ink neutrals. Do not invent neutrals; a chosen off-neutral reads as
  considered, a default mid-grey reads as unconsidered.

## Wire it into `theme.ts`

One tokens module every scene imports, so nothing drifts:

```ts
import { loadFont } from '@remotion/google-fonts/Geist';
const geist = loadFont('normal', { weights: ['400','600','700'], subsets: ['latin'] });

export const T = {
  paper: '#F8FAFD', ink: '#101623', muted: '#667085', line: '#DCE4EF',
  blue: '#2469D9',        // primary / actions
  green: '#13956E',       // positive outcome ONLY
  sans: geist.fontFamily, // the real brand family, not a stand-in
  mono: /* GeistMono */ '',
};
```

## Name and voice

If the product has a name, use it. A film that says "it" and "the assistant" throughout feels
generic; naming the product in the on-screen copy and any narration puts it front and centre and is
what a viewer remembers. Match the product's own tone (its landing page is the reference), and keep
to any house rules the repo documents (e.g. no em dashes, no emoji, active voice, no compliance
overclaims).
