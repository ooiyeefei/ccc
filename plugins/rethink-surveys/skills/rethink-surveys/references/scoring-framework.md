# Scoring & Tagging Framework

The math for turning raw survey responses into actionable rankings: **interview shortlists**, **pain clusters**, **demand-signal heatmaps**.

Loaded when the user wants to rank/cluster/score responses, or when designing the analytics layer of a new survey.

## Table of contents

- [The data layers](#the-data-layers)
- [Tags Claude assigns post-hoc](#tags-claude-assigns-post-hoc)
- [Composite scores](#composite-scores)
- [Cluster assignment](#cluster-assignment)
- [How to use scores in the admin dashboard](#how-to-use-scores-in-the-admin-dashboard)

## The data layers

A response moves through three layers:

1. **Captured** — what the respondent literally answered. Raw text + structured fields.
2. **Tagged** — what an LLM enrichment job extracted from the raw fields. Cluster ID, specificity score, sentiment, named substitutes.
3. **Scored** — composite metrics derived from captured + tagged. Interview score, pain × demand rank, churn risk.

Layer 2 and 3 are **post-hoc** — you don't compute them at submission time. You run an enrichment job nightly (or on-demand) over new rows.

## Tags Claude assigns post-hoc

Run a Haiku 4.5 enrichment job over each new response. Cheap, fast, structured-output friendly.

### `pain_cluster_id` and `cluster_label`

Group similar pain points together so you can rank by frequency.

**Approach 1: pre-defined taxonomy.** If you already have product hypotheses, define 5–10 clusters upfront and have the LLM pick one (with confidence). Fastest, most actionable, but biased by your priors.

**Approach 2: discover-and-cluster.** First-pass: extract a 1-sentence canonical form of the pain. Second-pass: cluster these canonical forms (k-means on embeddings, or recursive LLM grouping). Slower, more labor, but surfaces clusters you didn't predict.

**Default for a new survey: start with Approach 2 for the first 20–30 responses, lock in clusters, switch to Approach 1.**

### `specificity_score` (0.0–1.0)

How concrete is the pain description? "I needed help" = 0.2; "I needed someone to call my Airbnb host on Tuesday morning because my reservation got cancelled and I don't speak Mandarin" = 0.95.

LLM rubric prompt:

```
Score 0.0–1.0 on specificity of this pain description.

1.0 = names a specific moment, time, place, person, or constraint
0.7 = names a clear scenario but without specific anchors
0.4 = describes a general problem
0.0 = vague or non-answer

Description: {worry_text}
Score: <number>
```

**Critical naming choice:** call it `specificity_score`, NOT `articulateness_score` or `quality_score`. Articulate-ness biases against non-native speakers in bilingual audiences. Specificity is about content, not fluency.

### `sentiment_score` (-1.0 to +1.0)

Standard sentiment over the open-text response. Useful for comparison surveys (e.g., gig-worker pay-fairness) where the sentiment of the moment IS the signal.

### `incumbent_named` (text or null)

For founder/customer-discovery surveys: did the respondent name an existing solution they're using? "I just use a spreadsheet" is gold. "I haven't found anything" is also gold (different signal). LLM extracts.

### `mom_test_violation_flag` (boolean)

For founder surveys with the AI-interviewer: did the respondent answer hypothetically when asked about past behavior? Hard to detect deterministically; LLM rubric works:

```
Did the respondent answer about specific past events (✓ flag=false)
or speculate about hypothetical future behavior (✗ flag=true)?

Question: {prompt}
Answer: {response}
Verdict: <true|false>
Reasoning: <one sentence>
```

Use this to filter out low-signal rows in analysis.

## Composite scores

### `interview_score` (the most-used composite)

Goal: rank respondents by who's most worth a 30-min research call. Formula:

```
interview_score =
    severity                      // 1-5, user-provided
  × specificity_score             // 0-1, LLM-derived
  × wtp_weight                    // see table below
  × consent_research_call         // 0 or 1
  × novelty_bonus                 // 1.0 default, 1.3 if cluster has <3 members
```

**WTP weight table:**

| WTP bucket | Weight |
|---|---|
| `not_paying` | 0 |
| `under_15` | 1 |
| `under_40` | 2 |
| `under_140` | 3 |
| `whatever` | 4 |

**Why each multiplier:**
- `severity` → high-pain people are more motivated for the call
- `specificity_score` → vague responders give vague calls; concrete responders give actionable calls
- `wtp_weight` → people willing to pay are more motivated to validate solutions (and you can ask about pricing)
- `consent_research_call` → MUST be 1; without it, the call is illegal/unethical
- `novelty_bonus` → small-cluster pains are higher-leverage to investigate (they might be your wedge)

**Maximum possible score:** 5 × 1 × 4 × 1 × 1.3 = 26.

**Sort interview shortlist DESC by interview_score**, top 10 = your call list.

### `pain_x_demand_rank`

Goal: rank pain *clusters* (not individuals) by which deserves product investment.

```
For each cluster:
  total_severity     = sum(severity for rows in cluster)
  avg_wtp_weight     = mean(wtp_weight for rows in cluster)
  cluster_size       = count(rows in cluster)
  
  pain_x_demand     = (total_severity × avg_wtp_weight) / cluster_size_log_normalized
```

(Dividing by log-normalized cluster size prevents large-but-shallow clusters from dominating.)

**Sort clusters DESC**; the top cluster is your highest-leverage product opportunity.

### `churn_risk_score` (gig-worker template)

For supply-side surveys diagnosing retention:

```
churn_risk_score =
    moment_severity × 1.0
  + (5 - platform_comparison) × 0.7   // platform_comparison is -2..+2
  + (recent_moment_count) × 0.5       // moments mentioned in last 7 days
  - (tenure_years × 0.3)              // veterans churn less from any single moment
```

Workers with `churn_risk_score ≥ 6` are 2-week-leading-indicator candidates.

## Cluster assignment

### Initial clustering (cold start)

For the first ~30 responses on a new survey:

1. Extract canonical 1-sentence pain from each response (LLM, Haiku).
2. Embed each canonical pain (OpenAI `text-embedding-3-small` or equivalent, 1536-dim).
3. Run k-means with k=5..10. Inspect cluster centroids.
4. Have a human label each cluster (one short noun phrase: "translation in meetings", "airport navigation").
5. Lock the cluster set.

### Steady-state assignment

Once clusters are locked, each new response gets routed via:

1. Embed the new pain text.
2. Cosine-similarity against each locked cluster centroid.
3. Assign to nearest cluster IF similarity > 0.7. Otherwise → `cluster_id = NEW_PENDING` for human review.

The `NEW_PENDING` rate is itself a quality metric — if >15% of new responses don't fit any cluster, your taxonomy is stale; re-cluster.

## How to use scores in the admin dashboard

A working admin should surface, in this order:

1. **KPIs row:** total responses, follow-ups opt-in count, interview-shortlist count (`interview_score >= some_threshold`), top pain cluster.
2. **"Interview shortlist" view:** rows sorted by `interview_score` DESC, with 1-line preview of the worry text. Click → full transcript.
3. **Pain cluster bar chart:** count per cluster, sorted by `pain_x_demand_rank` (not just count).
4. **WTP histogram:** bucket counts, segmented by cluster (which clusters have pricing power).
5. **Severity × Frequency heatmap:** for instruments that capture both. Cells deeper red = higher product-investment leverage.
6. **CSV export:** all fields, including derived. Researchers will want raw for their own analysis.

**Don't surface:**

- Single-respondent demographics (privacy + low signal)
- Raw scoring formulas in the UI (researchers should trust + verify, not tweak in production)
- Sub-rankings by less-meaningful fields (e.g., "rank by Mandarin level" — that's never the question)

## Configuration knobs to surface

For surveys that ship to non-technical operators, expose these knobs (with sane defaults):

- **Interview score threshold** — what counts as "shortlist"? Default: top-N by score.
- **WTP weight scale** — for surveys in different markets, weights might shift.
- **Cluster taxonomy** — locked vs. discoverable.
- **Mom Test violation filter** — show all / filter out / flag-but-include.

These live in app config (e.g., a `survey_config` table or a JSON file), not hardcoded.
