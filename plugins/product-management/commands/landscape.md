---
description: Research competitor landscape
argument-hint: [competitor-name] (optional)
allowed-tools: WebFetch, WebSearch, Read, Write, AskUserQuestion
---

# Competitive Intelligence

Research competitor landscape or deep-dive on specific competitor.

## Without Arguments - Market Landscape

1. **Identify Competitors**
   - Ask user: "Who are your top 3-5 competitors?"
   - Supplement with web research if user unsure

2. **For Each Competitor** research via WebFetch/WebSearch:
   - Website → features, pricing, positioning
   - Product Hunt → launch history
   - G2/Capterra → user reviews, ratings

3. **Create Market Overview**
   - Save to `.pm/competitors/_landscape.md`
   - Update `.pm/cache/last-updated.json`

## With Argument - Deep Dive on $ARGUMENTS

Use the **research-agent** for autonomous deep-dive:

1. Launch research-agent to analyze $ARGUMENTS
2. Research multiple sources:
   - Pricing page → feature tiers
   - Changelog/blog → velocity and direction
   - Reviews → user sentiment
   - Job postings → hiring signals

3. Categorize features:
   - **Tablestakes** - Everyone has these
   - **Differentiators** - Unique selling points
   - **Emerging** - New bets they're making
   - **Deprecated** - What they gave up on

4. Save profile to `.pm/competitors/$ARGUMENTS.md`

Reference `examples/competitor-profile.md` in the product-management skill for output format.
