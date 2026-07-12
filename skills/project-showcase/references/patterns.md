# Build patterns

Three pieces: a **gallery** (filter bar + grid), a **card** (concise), and a **detail page** (rich). Build them in the site's own components and design tokens — this is a layout pattern, not a theme.

## The gallery

- A **filter bar**, then a responsive card grid (`1 / 2 / 3` columns is a safe default).
- **Track filter first.** It is the primary axis, so it leads the bar: `all · products · hackathons · r&d`. Secondary filters (kind, tier, status) come after, and are optional — don't add them unless the catalog is big enough to need them.
- Filter on `trackOf(item)` (see `schema.md`), not `item.track`.
- Show a live count ("showing 7") so an empty filter isn't confusing.
- Filtering is client-side state over a static list — no data fetching. Keep it a pure `items.filter(...)`.

## The card — concise, not a confession

The card is a **hook**, not the story. It shows only:

- `name` + `status`
- the one-line `description`
- two or three `stack` tags (not all of them)
- one CTA (`cta` → `ctaHref`)
- a `ribbon` if present

The whole card links to `/projects/<slug>`. **Do not put the long write-up on the card.** If you're tempted to add a third sentence, that sentence belongs on the detail page. The card answers "what is this and should I click?" in about five seconds.

## The detail page — the proof

One page per `slug`. Order that reads well:

1. `name` + `status` + the one-line `description`, `ribbon`, tags.
2. **Buttons** from `links[]` (primary = `ctaLabel ?? cta`), opening in a new tab.
3. **Media** (only if present): the `video` first (it's the demo), then the `heroImage` (a diagram/screenshot) with its `heroCaption`.
4. `whatItIs` — the 2–4 sentence "what it is".
5. Stack / meta, then a back link.

### Embedding media well

- **Video:** a native `<video controls playsInline preload="metadata">` with a `poster`. Always set the poster — without it the player opens as a black box. A clean first-frame screenshot makes a good poster; grab one with `ffmpeg -ss <time> -i clip.mp4 -frames:v 1 poster.png`.
- **Image/diagram:** a plain responsive `<img>` (`width:100%`, `loading="lazy"`) in a bordered frame, with a caption. Architecture diagrams and product screenshots both work here.
- **Slides / deck:** don't embed a heavy deck inline — link to it. If the deck is a self-contained HTML file, publish it as a public static page (the `htmldrop` skill does this in one command) and add it to `links[]` as `{ label: "Slides", url }` with `cta: "slides"`.

## Writing rules (both card and page)

- **Say what it is, not how you feel about it.** "An AML triage tool that auto-clears the benign bulk and escalates the rest." Not a paragraph about the journey.
- One-line `description` ≤ ~20 words. `whatItIs` ≤ ~4 sentences.
- Lead with the outcome, not the tech. Tech goes in `stack` tags.
- No hype adjectives ("revolutionary", "cutting-edge"). Let the thing speak.

## Responsive & accessible

- Grid collapses to one column on mobile; the filter bar wraps.
- Cards are real links (keyboard-focusable); the whole card is clickable but the CTA text still reads as the action.
- Images have `alt`; the video has `controls`.
- Don't let long tag rows or titles cause horizontal overflow — wrap them.

## Adding one project to an existing showcase

If the catalog already exists: read the current data file, copy the shape of a neighbouring entry exactly, set an explicit `track`, add media paths if the site serves static assets (e.g. `public/`), and stop. Do not refactor the schema or restyle the cards to add one item.
