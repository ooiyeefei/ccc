# Structure - opening, chapters, transitions, close, band

A demo film is one argument, and rule 1 of the contract keeps every beat on the running product. The pieces in this file sit *between* beats or *under* the picture: they shape how a viewer moves through the argument, and they are what a viewer from outside the domain notices first. Each is optional, each is the owner's call, and each goes into the storyboard as its own row, so it is approved before capture.

Settle purpose and distribution alongside these choices (`distribution.md`). Its rules for third-party branding and public copies still apply: optional opening, chapter and recap cards do not replace the required disclaimer cards or persistent label.

Why it matters: a non-expert watched a finished film and said it "switches people without saying so". The picture was right and the claims were right, and the film still lost them, because nothing told them where they were going.

## Questions to settle at the storyboard gate

Ask these with the storyboard, before any capture. Each one changes the cut or the frame and cannot be bolted on afterwards:

1. **Voice**: a model voice (the default, Kokoro `af_heart` at 1.0) or a human? Play one segment in two voices and let the owner choose. (`soundtrack.md`)
2. **Music**: a bed or none? Which track, and whose rights? (`soundtrack.md`)
3. **Opening and chapter cards**: a motion opening, cards between chapters, both, or neither?
4. **Closing**: a recap card and a call to action, or end on the last product screen?
5. **Branding and rights**: the company's logo under the picture? A copyright and distribution line, and in which words? Whose logo, when a prospect's brand is in the product? Ask; never assume. A brand that is in every frame cannot be trimmed out later.
6. **Captions**: burned in, a sidecar file, or both? (`soundtrack.md`)
7. **Platforms**: where does it play? A film with a band is 16:10 or taller and sits between black bars in a 16:9 player, so a YouTube cut is a separate deliverable.

Record the answers in the storyboard header. An unanswered choice stays unresolved until the gate; offer a default and get it confirmed. A late change costs a rebuild.

## The opening

Narrating the hook over the first screen's callouts "feels a bit weird" (owner): the viewer is being sold a promise while being asked to read a UI. Give the opening narration its own picture, about 25 seconds, then land on the product:

- empty slots in the shape of what the product takes in (for a document product, three document outlines);
- each input drops into its slot as the voice names it, using the film's own synthetic documents;
- a reading sweep passes over them;
- the title: the logo, the product name, its one-line promise; then clear to plain colour before the first card.

Times come from the narration's word times, so the picture lands on the words. This is an approved exception to rule 1, recorded in the storyboard as the opening row: a rendered sequence that introduces the product beats and never stands in for one.

## Chapter cards

One still card before each chapter: a kicker (the chapter's role or stage), a short headline in the film's voice, and a row of progress dots showing where the viewer is in the journey. In the film's theme, on the brand colour, or on the page colour for a light theme.

For a silent card, start with 2.6 s in all; the last frame of the shot before dissolves into the card over 0.4 s, the card holds, then dissolves into the first frame of the shot after over 0.4 s. Render both neighbours first, so each dissolve starts and ends on the exact frames either side. **No product narration is voiced over a silent card**: the narration pauses for it, as a speaker pauses between chapters, and the music swells into the gap (`soundtrack.md`).

## Transitions: say where we are going

The rule: add a spoken transition line **only where the film changes person, case or topic without saying so**. Four lines in a hundred fixed the film above; a line at every cut is signposting, and pitch-craft's human-voice pass strikes it. Each transition sits over an approved transition card between product beats.

A transition card is the exception to the silent-card rule: hold it for the measured line plus a breath, budget that time in the storyboard, and duck the music under the transition just as under other speech. Adding one changes the timeline; re-derive final timestamps and caption timings after assembly.

The patterns that worked, in the order a film uses them:

| Moment | Pattern | Example |
|---|---|---|
| Framing the journey, once, early | Name the thread the viewer will follow | "Let's follow one application from start to finish." |
| A handoff to a new person | Name the handoff from the thread's point of view | "Our application now waits for the branch manager." |
| The pivot to exceptions | Set an expectation the viewer already shares | "But we all know that not every application goes this smoothly." |
| A new topic | Preview it by what the viewer will see, not by its name | "Next, let's look at which rules the bank can change for itself." |
| The last chapter | Open with the question it answers | "Finally, can the bank prove all of this later?" |

Plain words over insider idiom: the owner struck "desk to desk" for "from start to finish". The picture names the person as the voice does: every persona's first beat opens with a callout on the signed-in role line.

The craft rules for these lines, and for the rest of the script, are pitch-craft's `references/storytelling.md`.

## The close

The last product line is the promise, in the throughline's words. Then a 0.4 s crossfade from the final screen into **one recap card**, held while the narration walks it:

- a solid box: what is built in;
- dashed boxes: the customer's own systems, each with the built-in stand-in it replaces;
- a strip: what is set up with the customer's team.

Each part lights 0.2 s before the voice names it, the rest dim to 22% opacity, and at the end everything is lit; about 44 s of narration. The call to action is the **last line heard**: "Start with one branch and one product, and we'll work with your team for four weeks, on your own real applications." The owner moved it there so the offer is what the viewer leaves with. After the last word the card holds about 2.9 s, fully lit, then the film ends. Never end on logistics or a thanks card.

A customer film closes on the ask; a hackathon film on the throughline and the name; an investor film on the ask (pitch-package's `references/audiences.md`).

## The band: logo, captions, rights

The owner asked for it unprompted: "embed the logo of our company, avoid people circulating this video and claiming it as their own, but don't risk blocking any words." Three rounds settled it:

- a frame around the picture: rejected, busy, and a white frame made the app's warm off-white look yellow;
- a wide white canvas: rejected;
- **a band below the picture only.** The picture stays full width, untouched. The band carries the company logo at the left, the burned captions in the middle, and at the right: `Demonstration film · © <year> <company> · Not for redistribution`.

The band is the app's page colour **as it lands in the encoded footage**: measure the pixels, because a served off-white shifts a level or two through the encodes, and when the band matches, the seam disappears. A hairline rule in the app's own border tone tops it. The logo and the notice line up with the app header's own insets.

Sizes that shipped: a 1920x1200 recording with a 56 px band (104 px with captions), so 1920x1304. For YouTube, which letterboxes anything taller than 16:9, make a 2560x1440 cut without re-recording: crop the edge artefacts first (a 1 px dark line at the right, a 2 to 4 px selection bar at the left), pad to the target width with `fillborders mode=smear` so the page appears to continue, then scale; check the margins at the opening, a card, a list screen and a callout. Cropping to 16:9 was rejected: it cuts the confirm button and the callouts.

A prospect's brand (a white-labelled UI) is used only for that prospect's own authorised demo, applied as local configuration, never committed, and only with their say-so. Keep an unbranded version for anything public.

## Disclaimer cards for a public copy

A self-hosted or public copy gets a silent card before (4 s) and after (3 s): "For demonstration purposes only. Names, documents and figures shown are fictitious or specimen samples. No affiliation with, or endorsement by, any institution is implied." Join them by stream copy, not a re-encode: encode the card with the film's exact x264 preset, profile, level and timescale and the same AAC parameters, then concat with `-auto_convert 0`, or every keyframe silently gains in-band headers. Expect a one-AAC-block (21 ms) shift, audio and video together. Every person, ID and document on screen is synthetic; ID images carry a SPECIMEN stamp.

## Thumbnail

For an upload platform, render the thumbnail from the film's own theme: the logo, the film's promise as the headline, the flow of steps in the narration's own words, the synthetic documents. Render at 2x, write a 1280x720 JPEG, and leave the bottom-right corner clear for the platform's duration badge.
