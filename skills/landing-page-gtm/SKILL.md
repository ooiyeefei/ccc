---
name: landing-page-gtm
description: Build and update high-converting SaaS landing pages with GTM-aware marketing copy, competitive positioning, and sales psychology. Use when creating new landing pages, rewriting feature cards, updating marketing copy, launching product pages, or transforming technical features into customer-facing sales language. Triggers on "build landing page", "update feature cards", "rewrite marketing copy", "create product page", "launch page", "GTM", "sales copy", "competitive positioning", or when converting product features into conversion-focused web pages.
---

# Landing Page GTM

Build conversion-focused landing pages that sell — not just describe. Combine product research, competitive positioning, sales copywriting, and frontend implementation into a single workflow.

## Intake — Always Ask First

Before any work, collect these inputs:

| Input | Question |
|-------|----------|
| **Target URL** | "What URL or route is this for?" (e.g., `myapp.com/pricing`) |
| **Codebase path** | "Where's the source code?" (e.g., `/home/user/project/src`) |
| **Product/feature** | "What product or feature is this page selling?" |
| **Audience** | "Who's the buyer? (role, company size, pain level)" |
| **Competitors** | "Who do they compare you against?" |
| **Constraints** | "Existing design system, form provider, CTA destination?" |

If the page already exists, read it first. Never propose changes to code you haven't read.

## Workflow

### Phase 1: Research the Product

Study the actual product before writing a single word of copy. Never invent features.

1. **Read the codebase** — Search for the feature's implementation. Use git log to find recent changes.
2. **Validate claims** — For every claimed feature, confirm it exists in code. Report gaps: "X exists. Y is partial. Z not found."
3. **Identify differentiators** — What does this do that competitors genuinely don't? Architectural advantages > surface features.
4. **Find the self-improving angle** — Any learning/adaptive behavior is marketing gold. Understand the mechanism so you can describe it without jargon.

### Phase 2: Competitive Positioning

Frame every section as "why us, not them" without naming competitors.

**Positioning formula:**
```
Pain they feel daily
+ What competitors do about it (poorly)
+ What you do differently
+ Outcome they'll experience
```

**Anti-generic test** — If copy could appear on a competitor's site unchanged, rewrite it:
- "AI-powered" → What does the AI actually DO?
- "Smart automation" → What specifically gets automated?
- "Easy to use" → Compared to what painful alternative?

**Competitor dismissal patterns:**
- "Every [category] app claims [buzzword]. Most just [what they do]. We're different."
- "Not [old approach]. Real [new approach] that [concrete outcome]."
- "Other tools stay static. Ours [how it evolves]."

### Phase 3: Write Sales Copy

Transform features into desire. Think like a buyer, not an engineer.

**Voice by audience:**

| Audience | Tone | Example |
|----------|------|---------|
| SME owner | Warm, direct | "Snap a receipt. Done." |
| Finance manager | Outcome-driven | "Every match shows you exactly why." |
| Enterprise | Trust-building | "Control without complexity." |
| Technical | Precise, credible | "Gets measurably smarter every week." |

**Copy rules:**
1. **Lead with pain** — "Stop filling forms one by one" > "Automated form filling"
2. **One sentence, one idea** — Short. Punchy. Scannable.
3. **Concrete > abstract** — "Reply in 10 seconds" > "Fast response times"
4. **"I want this" test** — Read each card aloud. Does the buyer think "I need this"? If not, rewrite.
5. **End with outcome** — "Never lose a sale to a slow reply" > "Uses NLP to generate responses"

**Talking about AI/tech without jargon:**

| Technical reality | Say instead |
|---|---|
| ML model retrains weekly | "Gets smarter every week from your feedback" |
| Internal optimization framework | Never mention. Say "learns from corrections" |
| LLM / GPT / Claude | "AI assistant" or just "your assistant" |
| API integration | "Connects to your existing tools" |
| Training data from user corrections | "Every correction teaches it something new" |
| Accuracy gating prevents regression | "Can only get better — never worse" |
| Explainable AI / reasoning traces | "Shows you exactly why each decision was made" |

### Phase 4: Design the Page

**Conversion-focused page anatomy:**

```
1. Hero         — Headline + subheadline + primary CTA
2. Pain Points  — 3-4 scenarios the buyer FEELS (red/warm tones)
3. Solution     — Transformation cards, not feature lists
4. Social Proof — Testimonials or metrics
5. How It Works — 3 steps max (reduce perceived complexity)
6. Pricing      — vs. status quo comparison, not just a table
7. FAQ          — Objection handling disguised as helpfulness
8. Final CTA    — Urgency + form (repeat primary CTA)
```

Not every page needs all sections. Match to product complexity:
- **New product launch**: All sections
- **Feature card update**: Cards + new section if needed
- **Product in portfolio**: Cards in drawer/grid, link to dedicated page

**CTA and forms:**
- Primary CTA at hero AND bottom — two chances to convert
- Minimum fields. Each extra field kills ~10% conversion.
- Lead capture minimum: name + email + company. Add phone only if product requires it.
- Use existing form infra (Formspree, Resend, etc.) — don't add dependencies.
- Add hidden `_source` field to distinguish which page the lead came from.

**Early Access / Waitlist pattern:**
- Colored badge signals exclusivity (e.g., purple "Early Access")
- Minimal inline form (2-3 fields) directly on the feature card
- Lower friction than separate page — capture interest at moment of discovery

### Phase 5: Build and Ship

1. **Match existing patterns** — Read 2-3 existing pages. Match imports, layout, routing, design system.
2. **Reuse the design system** — Existing UI components only. Don't introduce new frameworks.
3. **Mobile-first** — Every section must work at 375px width.
4. **Register the route** — Add to router with import.
5. **Type-check** — Run type checker before committing. Zero new errors.
6. **Multi-codebase consistency** — If product appears on multiple sites, update ALL with consistent messaging.

### Phase 6: Ship Checklist

Before pushing:

- [ ] Every feature in copy exists in actual product code
- [ ] No jargon (scan for: API, SDK, LLM, model, algorithm, pipeline, container)
- [ ] Every card passes the "I want this" test
- [ ] CTA buttons work (scroll to form or link to sign-up)
- [ ] Form submits correctly with `_source` field
- [ ] Mobile responsive at 375px
- [ ] Type-checks pass
- [ ] All codebases updated if product is multi-site
- [ ] Competitor copy test: could this appear on a competitor's site? If yes, rewrite.

## Reference Files

- [references/copy-formulas.md](references/copy-formulas.md) — Headline formulas, card patterns, CTA text, FAQ templates
- [references/page-archetypes.md](references/page-archetypes.md) — Templates for product launch, feature update, comparison, waitlist pages
