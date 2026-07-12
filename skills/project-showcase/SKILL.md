---
name: project-showcase
description: Add a filterable, project-based showcase catalog to a personal or company site — the pattern where every project is one card that opens a detail page, and visitors filter by the KIND of project (a launched product vs a hackathon build vs an R&D experiment). Use when someone wants to build a portfolio / projects / "things I've built" page, a showcase grid with filters, or wants to add one new project to an existing showcase and isn't sure how to categorize or present it. Interviews you about your stack and what you already have before writing anything.
---

# Project Showcase

Turn a pile of projects into a catalog a visitor can *filter and scan*. One card per project, each opening a detail page, grouped by the **kind of project**. The framing that makes it work: **track is the primary axis** — a visitor does not care what stack you used, they care whether this is a real product to try, a competition build, or a lab experiment. Sort by that first, everything else second.

Keep two leading ideas in your reasoning the whole way through:

- **One card, one project.** Every project is a single card. The card is the hook; the detail page is the proof.
- **Interview before you build.** Never assume the stack, the categories, or what already exists. Ask, then build.

## Step 1 — Interview (before you write any code)

STOP. Do not design a schema or write a component until you have answers. Ask, adapting to what they've already said:

1. **What site is this going into?** Framework (Next.js / React, Astro, SvelteKit, plain HTML) and where projects would live — a data file, a CMS, or a database? This decides *how* everything below is built.
2. **Is there already a projects page or project data?** If yes, read it first and **extend it** — do not replace it. Match its existing field names and visual style.
3. **What kinds of projects do you have?** A sensible default track split is **product / hackathon / rnd**, but confirm it. Some people want "client work", "writing", or "open source" instead. The tracks are the primary filter, so get them right — they are the user's call, not yours.
4. **Per project, how much do you have?** A one-liner, a longer "what it is", a live URL, a repo, a demo video, a diagram or screenshot, slides? This decides which optional fields and media each card and page use.
5. **What is the one action per card?** Open the app, watch a demo, read the repo, view slides. That is the card's call-to-action.

Reflect their answers back in a sentence or two, then proceed. If they only want to **add one project** to an existing showcase, skip schema design entirely — read their existing data shape and write that one entry to match it.

## Step 2 — The data model

Read **`references/schema.md`** for the field-by-field model and the `trackOf()` derivation trick (so existing entries don't all need editing when you add the filter). The essentials: a flat list of items, each with a `slug`, `name`, one-line `description`, a richer `whatItIs`, a `track` (the primary filter), a `status`, a `stack[]`, `links[]`, and a single `cta`. Media fields are optional, per item.

## Step 3 — Build it

Read **`references/patterns.md`** for the card-vs-detail split, the filter bar, the media block, and the writing rules. The shape:

- A **gallery**: the filter bar (**track first**, then any secondary filters like kind/tier/status) + a responsive card grid.
- A **card**: concise — name, status, the one-line description, a couple of tags, one CTA. **Concise, not a confession** — a card says *what a thing is*; it is not a lengthy essay.
- A **detail page**, one per slug: the richer `whatItIs`, optional embedded video (with a poster image so it doesn't open black), an optional hero image / diagram, and the links rendered as buttons.

Match the site's existing design tokens and components. Do not invent a new visual language.

## Step 4 — Verify

Build or typecheck. Then confirm three things *actually* work, don't just assert them: the **track filter** narrows the grid, a **card opens its detail page**, and any **embedded media renders** (the video plays, the image loads). Show the user.

## Guardrails (confirm, don't assume)

- The **tracks are the user's** — surface a default, but let them decide the categories.
- **Extend an existing showcase**, never silently replace it.
- Keep card copy concise; the long form lives on the detail page.
