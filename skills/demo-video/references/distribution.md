# Purpose, guardrails and distribution

Ask these with the storyboard, before any capture. The answers decide what gets burned into the film (cards, label, band, company mark) and where the file may live. Every one of them changes frames, and re-rendering a label is a full re-encode, so settle them first. They are optional guardrails the user chooses; the questions are not optional.

## The questions (ask, do not assume)

1. **Purpose and audience.** Internal review, one named prospect or client, a private showcase on our own website, public marketing, a submission?
2. **Third-party branding in the frame.** Does the app or the film show someone else's name or logo (a bank, a client, a partner)? A white-labelled tenant counts: the logo is in the header of nearly every frame, and no trim can remove it.
3. **Disclaimer card.** Generic ("for demonstration purposes only") or personalised, naming the recipient as the evaluator? Start only, or start and end?
4. **Persistent label.** "Demo purposes only" on every frame? In the caption band under the picture, or over it? (Measure the corners first; app content usually lives there.)
5. **Rights line and company mark.** "Demonstration film · © <year> <company> · Not for redistribution" in the band and in the file metadata. Which company name and logo, or none?
6. **Distribution.** A private streaming link (permanent, extendable, revocable, no download control), our website's unlisted showcase page, a plain file handover (WhatsApp, email), or a public platform?
7. **Shapes and captions.** 16:10 with the caption band (phone-first; the app fills the width), 16:9 for fixed embeds, burned-in captions or a sidecar file.

Record the answers in the brief next to the storyboard, and read them back before Gate 1.

## Rules that follow from the answers

- **A third party's logo or name in the frame** means: personalised card at the start and end naming them as the evaluator, the persistent label, and private distribution only (streaming link or direct handover). Never a page on our public domain. Assume no contract or consent exists unless the user says otherwise.
- **A public website showcase** means an unbranded tenant only (fictitious names such as "Bank Contoh"), the generic card, and no client reference anywhere in the film, the page copy, the link preview, or the file metadata.
- **Guardrails travel with the file.** A page, a caption or a chat message around the file protects nothing once the file is forwarded. Burn them in.
- **Unlisted YouTube is not private.** The title, thumbnail and metadata are readable by anyone with the video ID, and brand owners have a complaint form. Do not use it for third-party-branded films.
- **Keep the clean encode.** Cards are joined by stream copy; the label needs a picture re-encode (libx264 CRF 18, audio copied). With the labelled encode kept, a card-only change takes minutes per film.

## Approved wording (2026-10-14)

Generic card, unbranded films:

> For demonstration purposes only. Names, documents and figures shown are fictitious or specimen samples. No affiliation with, or endorsement by, any institution is implied.

Personalised card, one bank or client:

> Personalised demonstration prepared for [Bank] to evaluate.
> For demonstration purposes only. Names, documents and figures shown are fictitious or specimen samples.
> Not a statement of any existing relationship with, or endorsement by, [Bank].

Card: solid #172d43, white Manrope, centred, no logo, about 4 s at the start and 3 s at the end, silent.
Label: "Demo purposes only", dark rounded pill, white text at 70 percent, Manrope 600, in the caption band on the right, never over the app.

## Distribution pipeline (Argonaut)

Private streaming links are managed in the argo-website repo (README section "Private demo links"): `scripts/publish-demo.sh <mp4>` packages adaptive HLS into a private S3 bucket behind CloudFront on an anonymous address; `scripts/demo-link.sh create|extend|revoke|list` manages permanent token links checked at the edge by a CloudFront Function against a key-value store. The website's unlisted showcase page streams the unbranded film through the same pipeline.

Hand-off to the website session: H.264 High + AAC-LC, faststart, native resolution, one file per shape; report duration, resolution, size, the exact card wording, and a sampled-frame check confirming the card at both ends and the label on every film frame.
