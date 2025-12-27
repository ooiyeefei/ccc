# WINNING Filter - Detailed Scoring Guide

The WINNING filter is the core prioritization framework. It transforms subjective "this feels important" into objective, defensible decisions.

## Formula

```
WINNING Score = Pain + Timing + Execution + Fit + Revenue + Moat
Maximum: 60 points (6 criteria × 10 points each)
```

## Scoring Thresholds

| Score | Recommendation | Action |
|-------|----------------|--------|
| 40-60 | **FILE** | High conviction - create GitHub Issue |
| 25-39 | **WAIT** | Monitor - revisit in 30-60 days |
| 0-24 | **SKIP** | Not worth pursuing now |

---

## Criterion 1: Pain Intensity (1-10)

**Question:** How much does this problem hurt users RIGHT NOW?

**Scorer:** Claude suggests based on evidence

**Evidence sources:**
- User reviews mentioning the problem
- Support ticket frequency
- Social media complaints
- Churn reasons (if available)
- Competitor reviews praising their solution

### Scoring Guide

| Score | Description | Evidence Pattern |
|-------|-------------|------------------|
| 9-10 | **Hair on fire** | Users actively seeking solutions, willing to switch products |
| 7-8 | **Significant pain** | Frequent complaints, workarounds exist |
| 5-6 | **Moderate annoyance** | Occasional mentions, not blocking |
| 3-4 | **Nice to have** | Rare requests, low urgency |
| 1-2 | **Non-issue** | No evidence of user demand |

### Example

```
Pain Intensity: 8/10
Evidence:
- 47 G2 reviews mention "wish it had dark mode"
- 3 support tickets/week requesting dark mode
- Competitor X launched dark mode, reviews praise it
```

---

## Criterion 2: Market Timing (1-10)

**Question:** Are users actively seeking this solution NOW?

**Scorer:** Claude suggests based on research

**Evidence sources:**
- Google Trends for related terms
- Competitor launch timing (recent = hot market)
- Industry analyst reports
- Conference talk topics
- VC investment patterns in the space

### Scoring Guide

| Score | Description | Evidence Pattern |
|-------|-------------|------------------|
| 9-10 | **Peak demand** | Trending searches, multiple competitors launching |
| 7-8 | **Growing demand** | Upward trend, early adopter interest |
| 5-6 | **Stable demand** | Consistent interest, mature feature |
| 3-4 | **Declining interest** | Downward trend, may be commoditized |
| 1-2 | **No current demand** | Flat/no searches, no competitor activity |

### Example

```
Market Timing: 7/10
Evidence:
- "API webhooks" searches up 40% YoY
- Competitor A launched webhooks 3 months ago
- 2 other competitors announced webhooks on roadmap
- Developer community increasingly expects webhooks
```

---

## Criterion 3: Execution Capability (1-10)

**Question:** Can WE build this better/faster than alternatives?

**Scorer:** User scores (requires domain knowledge)

**Factors to consider:**
- Architecture fit (does current system support this?)
- Team expertise (have we built similar before?)
- Dependencies (what else needs to change?)
- Timeline (can we ship in reasonable time?)
- Quality bar (can we match/exceed competitors?)

### Scoring Guide

| Score | Description | Reality Check |
|-------|-------------|---------------|
| 9-10 | **Easy win** | Architecture ready, team experienced, <2 weeks |
| 7-8 | **Achievable** | Minor refactoring, team can learn, 2-4 weeks |
| 5-6 | **Challenging** | Significant work, some unknowns, 1-2 months |
| 3-4 | **Difficult** | Major changes, steep learning curve, 2-3 months |
| 1-2 | **Near impossible** | Complete rewrite, no expertise, 3+ months |

### Example

```
Execution Capability: 9/10
Reasoning:
- CSS variables already in place for theming
- Designer has dark mode mockups ready
- Similar feature shipped last quarter (theme system)
- Estimated effort: 3-5 days
```

---

## Criterion 4: Strategic Fit (1-10)

**Question:** Does this align with our product positioning?

**Scorer:** User scores (requires business knowledge)

**Factors to consider:**
- Target user alignment (does our ICP want this?)
- Brand positioning (does this fit our identity?)
- Product vision (does this move us toward goals?)
- Competitive positioning (how does this differentiate us?)

### Scoring Guide

| Score | Description | Strategic Reality |
|-------|-------------|-------------------|
| 9-10 | **Core to mission** | Directly advances primary goals |
| 7-8 | **Strong alignment** | Supports positioning, enhances value prop |
| 5-6 | **Neutral** | Neither helps nor hurts positioning |
| 3-4 | **Slight misalignment** | May confuse users about our focus |
| 1-2 | **Off-strategy** | Contradicts positioning, dilutes brand |

### Example

```
Strategic Fit: 8/10
Reasoning:
- We position as "developer-first" - webhooks are table stakes for developers
- Enterprise customers (our growth segment) expect webhooks
- Aligns with Q1 goal: "Improve developer experience"
```

---

## Criterion 5: Revenue Potential (1-10)

**Question:** Will this drive revenue (directly or indirectly)?

**Scorer:** User scores (requires business knowledge)

**Revenue impact types:**
- **Direct:** Feature is paywalled, drives upgrades
- **Conversion:** Feature helps close deals
- **Retention:** Feature reduces churn
- **Expansion:** Feature enables upsells

### Scoring Guide

| Score | Description | Revenue Reality |
|-------|-------------|-----------------|
| 9-10 | **Revenue driver** | Directly paywalled or major conversion factor |
| 7-8 | **Strong impact** | Known deal-closer or retention factor |
| 5-6 | **Moderate impact** | Contributes to overall value, indirect effect |
| 3-4 | **Minimal impact** | Nice addition, won't change buying decisions |
| 1-2 | **No impact** | Purely cosmetic, no business value |

### Example

```
Revenue Potential: 6/10
Reasoning:
- Dark mode won't directly drive upgrades
- But 3 enterprise prospects mentioned it in calls
- May reduce churn for power users (late-night coders)
- Indirect conversion impact
```

---

## Criterion 6: Competitive Moat (1-10)

**Question:** Can we defend this advantage once built?

**Scorer:** User scores (requires strategic thinking)

**Moat factors:**
- **Data moat:** Does it leverage proprietary data?
- **Network effect:** Does value increase with users?
- **Integration depth:** Is it hard to switch away?
- **IP/patents:** Is it legally protectable?
- **Execution speed:** Can we iterate faster?

### Scoring Guide

| Score | Description | Moat Reality |
|-------|-------------|--------------|
| 9-10 | **Defensible** | Proprietary data, strong network effects |
| 7-8 | **Durable** | Significant switching costs, integration depth |
| 5-6 | **Temporary** | First-mover advantage, can be copied |
| 3-4 | **Weak** | Easy to replicate, commoditized |
| 1-2 | **None** | Table stakes, no competitive advantage |

### Example

```
Competitive Moat: 5/10
Reasoning:
- Dark mode is easily copied (no moat)
- But: Our theme system allows custom themes (slight differentiation)
- Score reflects "table stakes" nature
```

---

## Complete Scoring Example

**Feature: API Webhooks**

| Criterion | Score | Evidence/Reasoning |
|-----------|-------|-------------------|
| Pain Intensity | 8 | 23 support tickets, competitor reviews praise webhooks |
| Market Timing | 7 | Searches up 40% YoY, competitors launching |
| Execution Capability | 7 | Event system exists, 3-4 weeks estimated |
| Strategic Fit | 9 | Core to "developer-first" positioning |
| Revenue Potential | 8 | Enterprise deal-closer, reduces integration churn |
| Competitive Moat | 4 | Table stakes, no differentiation |
| **TOTAL** | **43/60** | **→ FILE (High Priority)** |

---

## Hybrid Scoring Process

The WINNING filter uses hybrid scoring:

1. **Claude suggests** (based on research):
   - Pain Intensity
   - Market Timing

2. **User scores** (domain knowledge):
   - Execution Capability
   - Strategic Fit
   - Revenue Potential
   - Competitive Moat

### Why Hybrid?

- Pain/Timing can be researched objectively (reviews, trends)
- Execution/Fit/Revenue/Moat require internal knowledge Claude doesn't have
- Prevents Claude from guessing about your business strategy

### Scoring Flow

```
Claude: "Based on research, I suggest:
         - Pain Intensity: 8/10 (47 reviews mention this)
         - Market Timing: 7/10 (searches trending up)

         Please score the remaining criteria:"

User:   "Execution: 9, Fit: 8, Revenue: 6, Moat: 5"

Claude: "Total WINNING Score: 43/60 → Recommend FILE"
```

---

## Common Scoring Mistakes

### Mistake 1: Inflating Pain Based on Vocal Minority
One loud user ≠ widespread pain. Look for patterns across multiple sources.

### Mistake 2: Overweighting Execution
"We can build it easily" doesn't mean we should. Low pain + easy execution = still a bad idea.

### Mistake 3: Ignoring Moat
Features without moats become table stakes. Prioritize defensible advantages.

### Mistake 4: Recency Bias in Timing
Recent competitor launch ≠ market timing. Check underlying demand trends.

### Mistake 5: Conflating Revenue and Strategic Fit
A feature can fit strategy but not drive revenue (brand features), or drive revenue but not fit strategy (cash grabs).

---

## Recalibration

Every 30-60 days, review closed/shipped features:

1. **Did the feature deliver expected value?**
2. **Were scores accurate in hindsight?**
3. **Adjust scoring calibration if needed**

This creates a feedback loop that improves scoring accuracy over time.
