# Design & Visuals — Match the Project, Make It Land

Applies to **every mode** — simple share, feedback, and edit. Read this before you author or edit any HTML through htmldrop. Good default styling is the difference between an artifact that reads as the real product and one that reads as a generic template.

## Match the Project's Design System First

Before writing HTML, decide the design direction in this order — only move on when a step truly yields nothing:

1. **The user named a look or system** — use exactly that.
2. **Inspect the project the artifact is about** — the subject/product it represents, which may differ from your current working directory. Adopt its design system so the artifact faithfully shows the product:
   - Tailwind config / theme config (`tailwind.config.*`, `theme.json`)
   - Shared CSS variables / design tokens (`:root { --… }`, tokens files)
   - A component library or UI kit already in use
   - Brand assets (logo, palette, fonts) and existing styled pages
   - If the artifact previews or mocks a specific app's UI, render it in **that app's** design system, even when you're running from a different repo.
3. **Nothing to match** — use a clean, deliberate default: a small neutral palette, system font stack, generous spacing, and clear visual hierarchy. Keep it self-contained (inline `<style>` or a single stylesheet copied beside the HTML).

When you deliver, briefly state which design source you used and why (e.g. "styled with the project's Tailwind theme" or "no theme found — used a neutral default").

**How to inspect quickly:** glance at the target project for `tailwind.config.*`, a `theme`/`tokens` file, a `:root` CSS-variable block, or an existing styled page, and reuse those values (colors, radii, spacing scale, font families) rather than inventing new ones.

## Asset Paths

If the HTML references local assets (images, CSS, fonts, scripts), copy them beside the HTML file and reference them with **relative** paths. Never prepend `/` — root-absolute paths won't resolve when the file is served or published.

## Make It Visual When It Helps

Any mode benefits from structure over prose — a shared report, a `--feedback` doc, an edit-mode draft. When the content warrants it, prefer:

- **Visual hierarchy** so the most important points, risks, tradeoffs, and next actions are obvious at a glance.
- **Structure over paragraphs** — sections, cards, tables, diagrams, annotated snippets, side-by-side comparisons — instead of long text.
- **Deliberate typography, spacing, colour, and layout** so the artifact has a clear point of view.
- **No horizontal overflow** — design narrow layouts intentionally; use `minmax(0, 1fr)` and `min-width: 0` for grid/flex children; wrap or truncate long labels. (Edit mode's layout QA flags overflow if it slips through.)

Match the *amount* of visual treatment to the task: a quick share can be simple; a plan, comparison, or dashboard deserves real structure. Don't over-decorate a one-paragraph note.

## Portability

Whatever styling you use must render correctly when the file is opened directly (published) or served locally (edit mode). Keep styles inline or in a co-located stylesheet, and avoid dependencies that only resolve in your dev environment.
