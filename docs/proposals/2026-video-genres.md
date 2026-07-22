# Proposal: from a "pitch suite" to a genre-aware "video suite"

Status: **draft for review** · Author: pairing session, 2026-07-21 · Scope: `skills/{pitch-package,demo-video,pitch-deck,pitch-craft}` + a new skill + `README.md` + `marketplace.json`

## 1. The problem

The four video skills are one tightly-coupled **pitch** system. Every layer assumes the
video's job is to *prove a claim to a skeptic*:

- `demo-video/SKILL.md`: "A demo is an argument: every beat on camera proves a claim." Rule 1
  bans "a title card, a slide interstitial, a **mocked screen**, a static hero image."
- `pitch-package`: "A pitch is one argument delivered through three instruments." Its interview
  asks audience / slot / inventory / live-vs-recorded — never *what kind of video*.
- `pitch-craft/human-voice.md`: bans promotional adjectives ("stunning", "seamless") outright.
- README frames all four as "the pitch suite."

That is excellent for a hackathon/VC/customer pitch. But it is the *only* genre supported.
Two common jobs have no home:

| Genre | Today | Gap |
|---|---|---|
| **Pitch demo** (prove it, to a judge/buyer) | fully supported | — |
| **Tutorial / walkthrough** (teach a task) | capture *plumbing* fits; editorial contract + tone fight it | no task-arc, no reproducibility model, instructional signposting is banned |
| **Marketing / brand film** (make them want it) | **absent, and partly prohibited** | mocked/rebuilt UI banned by Rule 1; promotional register banned; no motion-graphics engine at all |

The Groot Solo marketing film we just built had to be produced *outside* the suite (Remotion +
a Playwright/ffmpeg capture + hand-stitching), precisely because the suite had no genre for it.

## 2. The design principle (unchanged)

Keep the CCC skills as the **framework and method** — interview → budget the slot → storyboard
gate → build → verify against the delivered MP4 → narrate to the frame → assemble. That
discipline is genre-independent and is the suite's real value. What changes: **video genre
becomes a first-class branch**, chosen by interview, and each genre gets its own editorial
contract and its own build tools. Rendered/animated video (Remotion) becomes a *tool* the
marketing genre reaches for, the way the pitch genre reaches for the capture harness.

## 3. Proposed architecture

Four layers. Only the shaded rows are new/changed.

```
Layer 1  ORCHESTRATE   video-package        interview PURPOSE first, budget, route by genre, assemble
Layer 2  GENRE         genre-pitch          proof arc, claim-to-frame audit           (today's demo-video contract)
                       genre-tutorial  ★    task arc, reproducibility, teaching pace   (new)
                       genre-marketing ★    story arc, mocks-in-wrapper, brand match   (new)
Layer 3  BUILD         demo-video           real capture (harness) — genre-neutral, gains a "mode" switch
                       motion-video    ★    Remotion motion-graphics / rendered scenes (new skill)
                       pitch-deck           the HTML deck (a pitch artifact; can also wrap a film)
                       pitch-craft          timed script — gains tutorial + marketing registers
Layer 4  ASSEMBLE      stitching            ffmpeg xfade recipe — already genre-neutral
```

## 4. Concrete changes, skill by skill

### 4a. Orchestrator: generalize `pitch-package` → `video-package`

Add ONE question to the front of the interview, before audience/slot/inventory:

> **Purpose** — what is this video *for*? Pick one: **pitch** (prove it to a judge/buyer),
> **tutorial** (teach someone a task), **marketing** (make a prospect want it), **explainer**
> (make an idea click). This decides the arc, the tone, and the build tools; get it wrong and
> the rest of the plan is for the wrong film.

Then a routing table sends the build to the right genre playbook + tools:

| Purpose | Arc | Real vs rendered | Tools |
|---|---|---|---|
| pitch | hook → 101 → status-quo cost → reveal → demo → close | real capture is the proof | demo-video (proof mode), pitch-deck, pitch-craft |
| tutorial | goal → prereqs → steps → result → recovery | real capture, deliberate holds | demo-video (tutorial mode), pitch-craft (tutorial register) |
| marketing | pain → turn → proof → payoff → ask | rendered scenes wrap ONE real proof beat | **motion-video**, demo-video (one beat), pitch-craft (marketing register) |

The current pitch content moves into `references/genre-pitch.md` (verbatim; nothing is lost).
`audiences.md` and `stitching.md` stay. New `references/genre-tutorial.md` and
`references/genre-marketing.md`.

**Naming decision (needs your call — see §8).** Two ways to do this without breaking anything:
- **(A) Rename** `pitch-package` → `video-package`; leave a 3-line `pitch-package` skill whose
  description still fires on "pitch/hackathon/VC" and points into video-package's pitch branch.
- **(B) Additive router**: keep `pitch-package` as-is; add a thin new `video-package` above it
  that only interviews for purpose and routes (pitch → pitch-package unchanged).

Recommend **(A)** — one orchestrator, pitch as a branch, cleanest mental model. (B) is lower
churn but leaves two orchestrators.

### 4b. `demo-video`: add a Modes section (proof / tutorial)

The harness (`record_template.py`, `cinema.js`, Xvfb/ffmpeg recipe, the three gates) is already
genre-neutral and stays untouched. What is proof-specific is the *editorial contract*. Add:

- **Proof mode (default, current):** every beat proves a claim; journey = entry/setup/loop/payoff;
  claim-to-frame audit; Rule 1 (no poster/mock) in full force.
- **Tutorial mode:** journey = *task arc* (goal → prerequisites → each step → expected result →
  error recovery); the claim-to-frame audit is replaced by a **reproducibility check** ("could a
  viewer follow this and reach the same result?"); deliberate holds are *allowed* (they are a
  defect in proof mode, a feature here); chaptering/timestamps for navigation; keystroke/shortcut
  surfacing. Rule 1 still holds — a tutorial is *real product*, never a mock.

Scope Rule 1's wording so it clearly governs *proof and tutorial* (both are real capture) and
defers rendered scenes to the marketing genre + motion-video, instead of implying all rendered
frames are forbidden everywhere.

### 4c. New skill: `motion-video` (the Remotion tool)

The marketing genre's build engine, and the home for everything the current suite lacks: motion
graphics, mocked/rebuilt UI scenes, data-driven animated charts, brand-matched title design.
Spec in §5.

### 4d. `pitch-craft`: add two registers

Today it has "recorded" and "live" registers, both pitch-toned, and it bans promotional language.
Add:
- **Tutorial register:** second-person, instructional ("now click…"), signposting *allowed* (the
  human-voice ban on "here's what you need to know" is lifted for this register — in a tutorial it
  is a real connective, not slop).
- **Marketing register:** warm, benefit-forward, but the honesty pass stays universal. Soften the
  absolute adjective ban to "**earn the adjective on screen** — if the motion shows it, you may
  name it; if not, cut it."

The **honesty pass** ("claim only what's wired", "no frame no claim") stays mandatory in every
register. Marketing does not get a pass on truth; it gets a warmer voice.

### 4e. `pitch-deck`: unchanged, one note

A deck is a pitch artifact; leave it. Add one line that its two-part recording can also wrap a
*marketing* film, not only a demo film.

### 4f. README + marketplace: reframe

"The pitch suite" → "The video suite: pick a purpose, get the arc + tools." Decision table gains
tutorial and marketing rows. `marketplace.json` plugin description updated. `pitch-craft/evals`
gains a couple of non-pitch cases so the genre routing is exercised.

## 5. `motion-video` skill spec (new)

**One-liner:** *Build animated marketing / explainer video with Remotion — motion graphics,
mocked or rebuilt product UI, data-driven charts, brand-matched — then stitch it around real
capture from demo-video. Use for brand films, launch videos, website hero videos, animated
explainers, or any video that is mostly rendered scenes rather than a screen recording.*

Contents it must carry (all learned the hard way on the Groot film):

1. **When motion-video vs demo-video.** demo-video films the *real* product to *prove* it.
   motion-video *renders* scenes to *sell/explain* it. A marketing film is mostly motion-video
   with ONE real demo-video proof beat stitched in.

2. **The mock-vs-real boundary (reconciles with demo-video Rule 1).** Rendered/mocked scenes are
   legitimate *in the wrapper*; the one real capture is the *proof*. Never pass a rendered UI off
   as a live screen recording. State on screen when a figure is illustrative. This is the same
   "annotate never substitute" ethic, applied at the *film* level instead of the *frame* level.

3. **The Remotion setup that actually works.**
   - Isolated project (its own `package.json`) so it never touches the product's dep tree.
   - **`framer-motion` and any wall-clock animation do NOT work** — Remotion renders frame-by-frame
     against a synthetic clock; everything animates off `useCurrentFrame()`. This is the single
     biggest surprise; call it out first.
   - Brand fonts via `@remotion/google-fonts/<Family>` (constrain weights/subset or it makes 90+
     network requests per render). Pull the real font/logo/palette from the product repo, do not
     approximate.
   - Render at CRF 16; scenes are vector-crisp.

4. **Brand match is mandatory.** Find the product's real font, logo mark, wordmark, and palette in
   its repo (next/font config, tailwind tokens, an SVG/PNG logo) and use them verbatim. An
   off-brand film reads as fake.

5. **Accuracy guardrails.** Numbers on screen reconcile (a mocked ledger still balances). No
   fabricated success rates, prices the brand keeps private, or compliance claims. Nothing reveals
   *how* a sensitive capability works if the brand does not want it shown.

6. **Stitching.** rendered scenes + the real beat, ffmpeg `xfade` crossfades, timings measured
   from the delivered MP4 (same Gate-3 discipline as demo-video). Narration, if any, via
   pitch-craft's marketing register, timed to the encoded file.

7. **A starter scene structure** (the Groot film's `theme.ts` + a couple of scene components as a
   reference skeleton), plus the `stitch.mjs` xfade recipe.

## 6. `cinema.js` — the honest answer

The question was: *cinema.js went vestigial on the Groot film; is the CCC one deprecated; should we
replace it with the htmldrop one?*

**No — and the framing is off.** The two files are different *frameworks*, not two versions:

| | CCC `demo-video/scripts/cinema.js` | htmldrop `scripts/demo/cinema.mjs` |
|---|---|---|
| delivery | in-page global, injected once via CDP `addScriptToEvaluateOnNewDocument`, called `window.__cine.spotlight(...)` | ES module, functions take a Playwright `page`: `spotlight(page, ...)` |
| driver | raw CDP (`record_template.py`) | Playwright |
| extras | — | `Timeline` beat-marker class, `installChrome`, drag primitives, `fadeIn`/`fadeOut` pair |

Wholesale-replacing CCC's with htmldrop's would swap its whole driver model. Don't. What actually
went wrong is one shared bug worth fixing in the CCC file:

- **`spotlight` clones the target node and scales the clone.** On a *responsive multi-column*
  element (a `grid-cols-1 sm:grid-cols-3` row of cards), the clone reflows to a single stacked
  column — the exact "Earned/Spent/Kept stacked vertically and ugly" defect on the Groot film. The
  workaround was to stop cloning and scale the *real* element in place.

**Proposed cinema.js change:** add a **`frameRegion` / `zoomTo`** primitive that fits a *live*
element to a centred viewport region by transforming the real node (no clone), so responsive
layouts keep their true columns. Keep `spotlight` for single-node magnification, with a one-line
caveat pointing at `frameRegion` for multi-column targets. Optionally port htmldrop's `Timeline`
marker idea into `record_template.py` (it overlaps the existing milestone marking; low priority).

## 7. Rollout (phased, low-risk first)

- **Phase 1 (additive, no breakage, do now):**
  1. `cinema.js` gains `frameRegion`/`zoomTo` + the spotlight caveat.
  2. New `motion-video` skill (purely additive; unlocks marketing films immediately).
  3. This proposal doc.
- **Phase 2 (needs the §8 decision):** orchestrator generalization (rename or router), the two new
  genre reference files, demo-video Modes section, pitch-craft registers, README/marketplace
  reframe, eval cases.

Phase 1 is safe to land immediately. Phase 2 waits on the naming call.

## 8. Open decision

**How to generalize the orchestrator** — rename `pitch-package` → `video-package` with pitch as a
branch (recommended), or add a thin `video-package` router above an unchanged `pitch-package`.
Everything else follows from that choice.
