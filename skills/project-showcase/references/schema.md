# The data model

A showcase is a **flat list of project items**. Store it however the site already stores content (a `.ts`/`.js` data file, JSON, frontmatter, or a CMS/DB collection). The shape below is framework-agnostic; the TypeScript is only to name the fields precisely.

```ts
type Track = "product" | "hackathon" | "rnd";   // the PRIMARY filter axis — rename to fit
type Status = "live" | "beta" | "wip" | "archived";
type Cta = "open" | "watch demo" | "repo" | "slides";

interface ProjectItem {
  slug: string;          // url-safe id, unique — drives /projects/<slug>
  name: string;
  description: string;   // ONE line. The card shows this. Concise, not a confession.
  whatItIs: string;      // 2–4 sentences. The detail page shows this.
  track: Track;          // the primary filter. See "Track: the primary axis" below.
  status: Status;
  stack: string[];       // short tags: ["next", "postgres", "stripe"]
  links: { label: string; url: string }[];
  cta: Cta;              // the ONE action a card leads with
  ctaHref: string;       // where the primary button goes

  // --- all optional below ---
  ctaLabel?: string;     // override the primary button text on the detail page
  ribbon?: string;       // a small award/context banner, e.g. "hackathon: 1st place"
  featured?: boolean;    // surface on a home-page highlight grid
  // media, rendered on the detail page only:
  video?: string;        // path/URL to an mp4
  videoPoster?: string;  // still image shown before play (so it isn't black)
  heroImage?: string;    // a diagram or screenshot
  heroImageAlt?: string;
  heroCaption?: string;
}
```

## Track: the primary axis

`track` is the field that makes the showcase *scan-able*. A visitor filters by **what kind of thing this is**, not by tech. Offer a default split and let the user rename or extend it:

- **product** — a live app they're launching or testing for traction (a visitor might sign up).
- **hackathon** — a competition build (often has a `ribbon` and a demo, not a live product).
- **rnd** — an R&D / open-source experiment or tool (usually a repo, sometimes archived).

Do not hardcode these three as if they're universal. Some catalogs want `client-work`, `writing`, `talks`. Confirm in the interview.

## `trackOf()`: derive, don't re-edit

When you **add** a `track` filter to a catalog that already has items, you don't want to hand-edit every old entry. Set `track` explicitly on new items, and derive it for the rest from signals that already exist:

```ts
function trackOf(p: ProjectItem): Track {
  if (p.track) return p.track;                                  // explicit wins
  if (p.ribbon?.toLowerCase().includes("hackathon")) return "hackathon";
  if (p.isOss || p.stack.includes("oss")) return "rnd";
  return "product";
}
```

Filter and group on `trackOf(item)`, never on `item.track` directly, so both explicit and derived items work. Only set `track` explicitly where the derivation would be wrong.

## Status vs track — they answer different questions

`status` (live / beta / wip / archived) is *how finished* a thing is. `track` is *what kind* of thing it is. A hackathon build can be `status: "beta"` and `track: "hackathon"` at once. Keep them separate; don't collapse "it's a hackathon project" into a status.

## Naming rule

Field names are the site's, not this skill's. If the existing data calls it `title` not `name`, or `tags` not `stack`, **match what's there**. The point is the *shape and the track idea*, not these exact identifiers.
