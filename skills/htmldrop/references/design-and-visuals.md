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

---

# The design contract (copy-paste, pinned)

This is the same content `htmldrop design` prints. Read it here (the skill path) or run the command (the standalone path) — either way it is the single source of truth. Prefer the user's or the target project's system first; use this neutral stack only when nothing is named or discoverable.

## Pinned CDN snippets (with integrity hashes)

A small neutral stack: a modern CSS reset/base, the pinned Mermaid renderer (same version the diagram shape uses), and a system font stack. Keep the `integrity` + `crossorigin` attributes.

```html
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/modern-normalize@3.0.1/modern-normalize.min.css"
  integrity="sha384-uo/9/s/Ns8DTg4kjkjex8GezUcgMlKD99gTqxvMkIsaG4lSUbeJ0dVELljipv94t"
  crossorigin="anonymous"
>
<script
  defer
  src="https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js"
  integrity="sha384-T/0lMUdJpd2S1ZHtRiofG3htU3xPCrFVeAQ1UUE2TJwlEJSV5NUwn30kP28n238E"
  crossorigin="anonymous"
></script>
<style>
  :root {
    color-scheme: light dark;
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.5;
    text-rendering: optimizeLegibility;
  }
</style>
```

## Layout-safety CSS block

Drop this into portable artifacts to prevent accidental horizontal overflow. For grids, prefer `repeat(auto-fit, minmax(0, 1fr))` so content is allowed to shrink.

```css
*,*::before,*::after{box-sizing:border-box}
html{overflow-x:hidden}
body{margin:0;min-width:0;overflow-x:hidden}
img,svg,video{max-width:100%;height:auto}
canvas,iframe,pre,code{max-width:100%}
pre{overflow:auto;white-space:pre-wrap}
.grid,.cards,[data-grid]{display:grid;grid-template-columns:repeat(auto-fit,minmax(0,1fr))}
.flex,.row,[data-flex]{display:flex;min-width:0}
.grid>*,.cards>*,.flex>*,.row>*,main,section,article,aside,header,footer{min-width:0}
p,li,figcaption,blockquote,td,th,.text,.copy,[data-text]{overflow-wrap:break-word}
.truncate{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
```

## Theme-aware Mermaid re-render

Initialize with `startOnLoad: false`, keep the diagram source as text, and re-render on every light/dark change. Mermaid never restyles an already-drawn SVG, so you must re-run `mermaid.render` with the new theme.

```html
<button type="button" data-theme-toggle>Toggle theme</button>
<script type="text/plain" id="diagram-source">
flowchart LR
  Idea[Source text] --> Render[mermaid.render]
  Render --> SVG[Theme-specific SVG]
</script>
<div id="diagram-output" aria-label="Theme-aware Mermaid diagram"></div>
<script>
  (() => {
    const root = document.documentElement;
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const source = document.getElementById('diagram-source').textContent.trim();
    const output = document.getElementById('diagram-output');
    let renderCount = 0;
    const isDark = () => root.dataset.theme === 'dark' || (!root.dataset.theme && media.matches);
    async function renderDiagram() {
      const theme = isDark() ? 'dark' : 'default';
      mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme });
      const { svg } = await mermaid.render(`diagram-${theme}-${++renderCount}`, source);
      output.innerHTML = svg;
    }
    document.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
      root.dataset.theme = isDark() ? 'light' : 'dark';
      renderDiagram();
    });
    media.addEventListener?.('change', () => { if (!root.dataset.theme) renderDiagram(); });
    if (document.readyState === 'loading') window.addEventListener('DOMContentLoaded', renderDiagram, { once: true });
    else renderDiagram();
  })();
</script>
```

---

# Pick the right shape (the playbook router)

Before writing HTML, match the content against these triggers and reach for the right structure. One artifact often combines several. This is the same guidance `htmldrop playbook <id>` prints; consult it automatically, don't wait to be asked.

- **`diagram`** — *relationships / flows / architecture / sequences.* Use a real Mermaid diagram, never hand-built `<div>` boxes (they drift out of alignment and break on small screens). Keep the Mermaid source as text and render into a mount; re-render on theme flip.
- **`comparison`** — *comparing options / tools / approaches / tradeoffs.* Aligned option cards side by side; make the cost as visible as the benefit. Never present only the upside.
- **`input`** — *a decision or answer is needed from the viewer, in the artifact.* Native form controls, local *selection* state, and exactly one explicit **send answer** per question that **delivers** the choice to the agent via the feedback channel (wakes the poll live in edit mode; a pullable comment when published) — not a local-only "queued" state that never arrives.
- **`plan`** — *proposing a change / roadmap / approach.* Structure: goal → current → proposed → risks → open questions. Mock the UI, don't describe it in prose.
- **`table`** — *dense structured data, many attributes across items.* A real `<table>` with aligned columns, no horizontal overflow (wrap/truncate long cells), and highlight the decision-relevant column.
- **`slides`** — *sequential narrative meant to be stepped through.* One idea per slide, large type, keyboard nav, progressive disclosure.
- **`explainer`** — *teaching a concept / mechanism / how something works.* The htmldrop teaching shape, and the one to reach for whenever the goal is understanding:
  1. lead with the **one idea** that explains everything, as a plain sentence before any detail;
  2. a **feel-the-difference micro-demo** with the smallest honest code (a 450ms `setTimeout` *is* network lag; a toggle *is* a mode switch; a counter *is* pressure) — let the reader feel the mechanism, don't just describe it;
  3. a **looping before/after** of the same scenario under both designs;
  4. a **cheat-sheet table last**, including the honest trade-off.
