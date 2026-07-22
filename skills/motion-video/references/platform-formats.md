# Platform formats - cut one film to every placement

A marketing film almost never ships as a single file. The same story goes out as a 16:9 YouTube
pre-roll, a 9:16 TikTok and Reel, a 4:5 feed post. This reference turns a target-platform list into
the **minimal set of renders**, the **safe zone** each placement demands, and the **Remotion recipe**
that produces them all from ONE set of scenes.

Two rules an agent under pressure breaks:

- **Reframe, never crop the extremes.** 16:9 to 9:16 throws away ~56% of the frame and makes
  landscape-sized text unreadable. Re-author the vertical layout: reposition the subject, rebuild
  titles, re-time. Only ADJACENT ratios (16:9 -> 4:5 -> 1:1, or 9:16 -> 4:5 -> 1:1) may be
  center-cropped.
- **Compose inside the safe box.** Platform UI - caption bars, action rails, CTA buttons - is painted
  OVER your video, not beside it. Any word or logo outside the keep-clear envelope gets covered.

## Step: pick the platforms (the "checkbox")

Before building scenes, ask which platforms and placements the film ships to. In Claude Code that is
an `AskUserQuestion` with `multiSelect: true`; present these options (each maps to a master ratio):

| Option label | Placements it covers | Master ratio |
|---|---|---|
| Instagram / Facebook Reels + Stories | IG Reels, IG Stories, FB Reels, FB Stories | 9:16 |
| TikTok | organic, In-Feed, Spark, TopView | 9:16 |
| YouTube Shorts | Shorts | 9:16 |
| Instagram / Facebook Feed | IG feed, FB feed | 4:5 |
| YouTube (long-form / pre-roll) | standard player, skippable/non-skippable/bumper | 16:9 |
| LinkedIn | feed + sponsored | 4:5 or 1:1 (+9:16 ad) |
| X (Twitter) | feed + promoted | 1:1 or 16:9 (+9:16 vertical) |
| Website hero / email / CTV | landscape embed | 16:9 |

Collapse the answers to the distinct master ratios needed, then render only those. Do not render
formats no selected placement uses.

## Master ratios - the minimal set

Everything reduces to a subset of four ratios.

| Placement | Master ratio |
|---|---|
| TikTok (all), IG/FB Reels + Stories, YouTube Shorts, X Vertical, LinkedIn 9:16 ad | **9:16** (1080×1920) |
| YouTube long-form / pre-roll, website hero, OLV/CTV, landscape feed | **16:9** (1920×1080) |
| IG feed, FB feed, LinkedIn feed, X ad | **4:5** (1080×1350) |
| X feed (square renders larger), LinkedIn traditional feed | **1:1** (1080×1080) |

Minimal covering set: **{9:16, 16:9, 4:5}**. Add **1:1** only if X-feed or LinkedIn-feed is a priority
channel (X recommends square; 1:1 is otherwise redundant with 4:5). The two extremes 9:16 and 16:9 are
non-negotiable and cannot be derived from each other by cropping.

## Safe zones

### One universal vertical master (survives every 9:16 placement at once)

Take the MAX keep-clear of every vertical platform, edge by edge. Instagram/Facebook Reels is the
strictest (35% bottom); TikTok's action rail sets the right edge. Keep all text and logos inside:

| Edge | Universal keep-clear | px on 1080×1920 |
|---|---|---|
| Top | 14% | ~270 |
| Bottom | **35%** | ~672 |
| Left | 6% | ~65 |
| Right | 13% | ~140 |

Usable band ~= 950 px wide × ~980 px tall, centered. That 35% bottom is severe - it leaves ~51% of the
height for content. It is the price of ONE master that plays everywhere. If instead you cut PER
placement, relax each to its own number:

| Placement (9:16) | Top | Bottom | Left | Right |
|---|---|---|---|---|
| IG / FB Reels + Stories | 14% | 35% | 6% | 6% |
| TikTok - organic | 7% | 17% | 5% | 13% |
| TikTok - paid (In-Feed / Spark) | 7% | 25% | 5% | 13% |
| YouTube Shorts | 10% | 22% | 4% | 12% |

Landscape 16:9: keep the bottom ~10% (~110 px on 1080) clear of key text - the player scrubber and
in-stream sponsored/CTA strip live there. YouTube end screens occupy the last 5-20 s (needs >=25 s
length). 4:5 and 1:1 feed placements paint no UI on the frame, but a 9:16 upload is center-cropped to
4:5 in feed, so keep content in the central 4:5 region.

**Never burn your own CTA into the bottom zone on TikTok or Meta ads** - the platform renders its own
CTA button there and yours collides with it.

## Per-platform quick specs

Container is stable across all: **MP4, H.264/AVC, AAC >=128 kbps, 1080p baseline.** Details below;
full staged research (durations, text limits, sources) lives with the film project.

| Platform | Recommended ratios | Max ad file | Notable text limit | Watch-out |
|---|---|---|---|---|
| Meta (FB+IG) | 9:16 Reels/Stories, 4:5 feed, 16:9/1:1 in-stream | 4 GB | Primary 125; **IG Reels 44** | 35% bottom safe zone; awareness objective hides the footer |
| TikTok | 9:16 | 500 MB | caption 1-100 | paid bottom safe = 25%; platform owns the CTA button |
| YouTube | 16:9 long-form, 9:16 Shorts | hosted on YT | in-feed headline 40 | skippable: hook + brand in first 5 s; bumper = 6 s |
| LinkedIn | 1:1 / 4:5 feed, 9:16 ad, 16:9 | 500 MB (ad) | Intro 600, Headline 200 | **rejects MOV** - MP4 only |
| X (Twitter) | 1:1 / 16:9 feed, 9:16 vertical | 1 GB (<30 MB rec) | 280 (257 w/link) | logo upper-left; keep <30 MB for delivery |

## Export

One container satisfies every platform: **MP4, H.264/AVC video + AAC audio.** LinkedIn REJECTS
MOV/QuickTime, X accepts it, so always master to MP4. Baseline resolutions: 1080×1920 (9:16),
1920×1080 (16:9), 1080×1350 (4:5), 1080×1080 (1:1). Go to 4K only for the 16:9 hero if the source
supports it.

## Remotion recipe - one scene set, every ratio

Remotion reads dimensions from `useVideoConfig()`, so the SAME components render at any size. You
register one `<Composition>` per ratio and let scenes branch on orientation. No logic is duplicated.

```ts
// formats.ts - the ratios you actually need (subset per the platform picker)
export const FORMATS = [
  { id: 'yt-16x9',   width: 1920, height: 1080 }, // YouTube long-form, web hero
  { id: 'reel-9x16', width: 1080, height: 1920 }, // TikTok, Reels, Shorts, Stories
  { id: 'feed-4x5',  width: 1080, height: 1350 }, // IG/FB/LinkedIn feed
  { id: 'sq-1x1',    width: 1080, height: 1080 }, // X feed (optional)
] as const;
```

```tsx
// Root.tsx - register the master timeline once per format
import { FORMATS } from './formats';
{FORMATS.map((f) => (
  <Composition key={f.id} id={`Film-${f.id}`} component={Film}
    durationInFrames={TOTAL} fps={FPS} width={f.width} height={f.height} />
))}
```

```tsx
// inside a scene - branch layout on orientation, do not just scale
const { width, height } = useVideoConfig();
const vertical = height > width;
// vertical: stack rows and enlarge type; landscape: place side-by-side.
// A 16:9 two-column layout must become a 9:16 stack - re-author, never squish.
```

```tsx
// SafeArea.tsx - a DEV overlay so you compose inside the keep-clear box.
// Render it during authoring; drop it (or pass show={false}) for the final render.
import { AbsoluteFill, useVideoConfig } from 'remotion';
export const SafeArea: React.FC<{ show?: boolean }> = ({ show }) => {
  const { width, height } = useVideoConfig();
  if (!show || height <= width) return null; // vertical only
  return (
    <AbsoluteFill style={{ pointerEvents: 'none', zIndex: 9999 }}>
      <div style={{
        position: 'absolute', top: '14%', bottom: '35%', left: '6%', right: '13%',
        outline: '2px dashed rgba(255,64,64,.7)',
        boxShadow: '0 0 0 100vmax rgba(255,64,64,.06)',
      }} />
    </AbsoluteFill>
  );
};
```

Render every format with `scripts/render-formats.mjs` (a thin loop over the Remotion CLI), then run
each through `scripts/stitch.mjs` if you assemble from separate scene clips. Watch every output as an
image at its true ratio - a layout that reads in 16:9 can collapse in 9:16.

## Volatility + confirm before final render

Safe-zone pixels drift with every app redesign; character limits are A/B-tested; TikTok and YouTube
have both raised duration caps repeatedly. Treat every number here as a production-safe DEFAULT and
**confirm in each platform's Ads Manager creative preview** before the final render, especially the
vertical bottom safe zone (the single most common truncation) and per-placement text limits. Specs
current 2026-07-21; official sources are cited in the staged research files.
