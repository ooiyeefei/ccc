# Page Archetypes

Templates for common landing page types. Adapt sections to fit the product.

## 1. New Product Launch

Full conversion page for a brand-new product or service.

**Required sections:**
1. Hero (headline + subheadline + CTA)
2. Pain points (3-4 relatable scenarios)
3. Solution cards (5-6 transformation cards)
4. How it works (3 steps)
5. Social proof (testimonials or metrics)
6. Pricing or comparison
7. FAQ (5-6 objections)
8. Final CTA with urgency

**Design notes:**
- Product accent color throughout (not just brand blue)
- Pain section uses warm/red tones
- Solution section uses product color for icons
- Two CTA touchpoints minimum (hero + bottom)

**Form strategy:**
- Full contact form at bottom (name, email, phone if relevant, company)
- Hidden `_source` field with product name
- Success message promises response timeframe

## 2. Feature Card Update

Updating existing product cards on a portfolio or product page.

**Workflow:**
1. Read existing cards
2. Research new features in codebase
3. Identify which cards to update vs. replace
4. Write new copy with competitive positioning
5. Update all locations where cards appear (drawer, dedicated page, app landing page)

**Decision: Update vs. Replace a card?**
- **Update** if the core feature is the same but copy is weak
- **Replace** if a new feature is more compelling than what's there
- **Replace the weakest card** — usually "Reports" or generic utility cards
- Keep cards that serve distinct buyer personas (e.g., Enterprise Command Center)

**Card copy structure:**
```
Title: 3-5 words, benefit-oriented
Description: 2-3 sentences max
  Sentence 1: Pain or hook
  Sentence 2: What the product does
  Sentence 3: Outcome or differentiator
```

## 3. Comparison / Versus Page

Landing page that positions product against status quo or competitors.

**Sections:**
1. Hero — "[Your product] vs. [status quo]"
2. Side-by-side comparison table
3. Deep-dive on 3-4 key differences
4. Social proof from switchers
5. FAQ addressing switching concerns
6. CTA — "Make the switch"

**Comparison table rules:**
- Never name specific competitors (say "Traditional tools" or "Other solutions")
- Use checkmarks vs. X marks for visual clarity
- Lead with the rows where you win hardest
- Include a "self-improving" or "gets better over time" row if applicable — most competitors can't match this

## 4. Waitlist / Early Access Page

Minimal page for features not yet generally available.

**Sections:**
1. Hero with "Early Access" badge
2. Brief feature description (3-4 sentences)
3. Inline form (email + company, max 3 fields)
4. Social proof or metrics if available
5. FAQ (2-3 questions about timeline and access)

**Design notes:**
- Purple/violet accent for Early Access badge and CTA
- Keep the page short — urgency comes from scarcity, not length
- "Join Waitlist" CTA, not "Sign Up"

**Form strategy:**
- Absolute minimum fields (email + company name)
- Can be inline on a feature card (no separate page needed)
- Hidden `_source` field: "[feature-name]-waitlist"

## 5. Service / Consultation Page

For products sold through a sales conversation rather than self-serve.

**Sections:**
1. Hero — outcome-focused headline
2. Pain points — 4 daily frustrations
3. What they get — transformation cards (not feature cards)
4. How it works — 3-step onboarding
5. Social proof — testimonials emphasizing ROI and time saved
6. Pricing comparison — vs. hiring/status quo (no actual prices)
7. Contact form — name, email, phone, company
8. FAQ — objection handling
9. Final CTA — urgency

**Key differences from self-serve:**
- CTA is "Talk to us" or "Get set up", not "Start free trial"
- Pricing section compares cost vs. alternative (hiring staff), doesn't show prices
- Form collects phone number (sales team needs it)
- WhatsApp/chat button if applicable (meta: they experience the product by enquiring)

## Color Strategy by Page Type

| Page type | Primary accent | Pain section | CTA color |
|-----------|---------------|--------------|-----------|
| Product launch | Product brand color | Red/warm | Product color |
| Feature update | Existing brand blue | N/A | Brand blue |
| Comparison | Brand blue | Red for competitor column | Green for your column |
| Waitlist | Purple/violet | N/A | Violet |
| Service page | Product-specific (e.g., WhatsApp green) | Red/warm | Product color |
