# Landing Page GTM - Pages That Sell, Not Describe

Build conversion-focused SaaS landing pages with GTM-aware marketing copy, competitive positioning, and sales psychology — implemented directly in your existing codebase and design system.

---

## What It Does

This skill turns Claude Code into a combined product marketer + frontend engineer that follows a 6-phase workflow:

1. **Research the Product** — reads your actual codebase, validates every claimed feature against the code (never invents features), and finds the genuine differentiators
2. **Competitive Positioning** — frames every section as "why us, not them" and rewrites anything that could appear unchanged on a competitor's site
3. **Write Sales Copy** — transforms features into desire: lead with pain, concrete over abstract, end with outcome, zero jargon
4. **Design the Page** — conversion-focused anatomy (hero → pain points → solution → social proof → how it works → pricing → FAQ → final CTA), matched to what the page actually needs
5. **Build and Ship** — reuses your design system and form infrastructure, mobile-first at 375px, registers routes, type-checks
6. **Ship Checklist** — every feature verified in code, every card passes the "I want this" test, CTAs and forms tested

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Usage

Trigger the skill naturally:

```
"Build a landing page for this product"
"Rewrite the feature cards as sales copy"
"Update the pricing page with competitive positioning"
"Turn these technical features into customer-facing copy"
```

The skill always starts with a short intake — target URL, codebase path, product, audience, competitors, constraints — and reads existing pages before proposing changes.

## How It Works

### Copy Rules

- **Lead with pain** — "Stop filling forms one by one" beats "Automated form filling"
- **Concrete > abstract** — "Reply in 10 seconds" beats "Fast response times"
- **The "I want this" test** — every card is read aloud; if the buyer wouldn't think "I need this," it gets rewritten
- **No jargon** — ships with a translation table (e.g., "ML model retrains weekly" → "Gets smarter every week from your feedback")

### Voice by Audience

| Audience | Tone |
|----------|------|
| SME owner | Warm, direct — "Snap a receipt. Done." |
| Finance manager | Outcome-driven — "Every match shows you exactly why." |
| Enterprise | Trust-building — "Control without complexity." |
| Technical | Precise, credible — "Gets measurably smarter every week." |

### Anti-Generic Test

If the copy could appear on a competitor's site unchanged, it gets rewritten: "AI-powered" → what does the AI actually *do*? "Easy to use" → compared to what painful alternative?

## Skill Structure

```
landing-page-gtm/
├── SKILL.md                      # The 6-phase workflow + copy rules
├── README.md                     # This file
└── references/
    ├── copy-formulas.md          # Headline formulas, card patterns, CTA text, FAQ templates
    └── page-archetypes.md        # Page layouts by product type and launch stage
```

See [SKILL.md](./SKILL.md) for the full workflow, copy rules, and ship checklist.
