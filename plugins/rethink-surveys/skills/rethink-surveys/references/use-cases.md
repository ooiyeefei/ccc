# Use-case templates

Three full templates, ready to fork. Each includes research goal, target respondent, hypotheses being tested, the question set, branching, and output schema.

Loaded when the user names a use case that matches one of these (or wants to fork from one).

## Table of contents

- [Template 1 — Event organizers](#template-1--event-organizers)
- [Template 2 — Startup founders](#template-2--startup-founders-customer-discovery)
- [Template 3 — Gig-economy workers](#template-3--gig-economy-workers)

---

## Template 1 — Event organizers

**Use when:** designing a pre-event survey to understand attendee needs, or a post-event survey to capture lessons.

### Research goal

(Pick one — don't try to do both in the same instrument.)

- **Pre-event:** "Identify the top 5 friction points attendees expect during event week, and the top 3 attendees who are highest-leverage for live concierge testing."
- **Post-event:** "Identify which moments delighted vs. frustrated attendees, ranked by frequency × severity, with quotes that can drive next-event design."

### Target respondent

Pre-event: registered attendees, 1–4 weeks out from the event. Reached via email + WeChat.
Post-event: attendees who actually showed up, within 48 hours of event close.

### Top hypotheses

Pre-event:
1. Language friction (translation in-meeting) is the most cited concrete worry, but is NOT the most severe — getting around / navigation will rate higher on severity.
2. "Family with me" attendees have qualitatively different needs (kid-friendly food, partner activities) and are under-served.
3. Willingness-to-pay clusters at "up to ~¥300 / $40" — below that, attendees self-serve; above that, they don't believe the service exists.

Post-event:
1. Most surprising delights are unscheduled connections (a stranger introduced them to X) — not the curated programming.
2. Most cited frustrations are logistical (transport, where to go between sessions), not content quality.

### Pre-event question set (~75s honest)

```
Q1. Who are you coming as? (single-select)
   - International visitor
   - Domestic (other Chinese city)
   - Local in Shanghai
   - Organizer / crew
   - Partner / sponsor
   - Other

Q2. Who's coming with you? (single-select) [NEW]
   - Just me
   - Coworker / cofounder
   - Partner
   - Partner + kids
   - Meeting people there

Q3. Been to [city] before? (single-select)
   - First time
   - 1-2 times
   - I know it well
   - I live here

Q4. What's the one thing you're most worried about handling on your own during event week?
   [Open — text/voice/chat tri-modal; ≤ 2 min recording]

Q4b. (Branched on Q3)
   - Q3 ∈ {known, live} → "Last time you needed help with this kind of thing here, what did you do?"
   - Q3 ∈ {first, 1-2} → "What's your fallback plan right now?"
   [Optional, ≤120 chars]

Q4c. Severity (1-5, behavioral anchors)
   - "Annoying but I'd shrug it off"
   - "I'd lose ~30 minutes figuring it out"
   - "I'd lose half a day or miss something"
   - "It would wreck a meeting or a day"
   - "I'd consider not coming or leaving early"

Q4d. Willingness-to-pay (single-select, dual currency)
   [See question-library.md for the standard 5-bucket scale]

Q5. Mandarin level (1-5, auto-skip if Q3=live_here)

Q6. Would you test the concierge during the event? (single-select)
   - Yes — use me as a tester
   - Maybe — depends on what
   - Not now, another time
   - No thanks

Q7. Contact + split consent (shown if Q6 ≠ no)
   - Contact field (email or WeChat)
   - ☐ OK to contact me about testing the concierge
   - ☐ OK to contact me for a 15-min research call
```

### Branching

- Q3 = `live_here` → skip Q5 (auto-set to 5).
- Q4b copy branches on Q3 (returning vs first-time).
- Q6 = `no` → skip Q7, go to thanks.
- Q6 ≠ `no` AND Q7 contact missing → require contact.

### Output schema (Supabase event_v1)

```sql
-- Top-level columns
respondent_type TEXT,
segment TEXT,                 -- derived from respondent_type → b2c_visitor / b2c_local / b2b
willingness_to_test TEXT,     -- Q6 ID
contact TEXT NULL,
consent BOOLEAN,              -- Q7 first checkbox
consent_research_call BOOLEAN,-- Q7 second checkbox
capture_mode TEXT,            -- text|chat|voice for Q4
voice_url TEXT NULL,
transcript TEXT NULL,
transcript_language TEXT NULL,

-- response_data JSONB
{
  "prior_visit": "first_time|one_to_two|known|live_here",
  "group_composition": "solo|coworker|partner|family|meeting_there",
  "worry_text": "<the open-ended response>",
  "workaround_text": "<optional Q4b answer>",
  "severity": 1-5,
  "willingness_to_pay": "not_paying|under_15|under_40|under_140|whatever",
  "mandarin_level": 1-5
}

-- Derived (LLM enrichment, post-hoc)
pain_cluster_id TEXT,
cluster_label TEXT,
specificity_score NUMERIC,
interview_score NUMERIC
```

### Anti-patterns to avoid for this use case

- Asking for **dietary restrictions** in the pre-survey — they'll forget by the event. Ask in the day-before reminder email instead.
- Asking which **sessions they plan to attend** — agendas change; this data ages immediately.
- Combined consent — split it. Always.

---

## Template 2 — Startup founders (customer discovery)

**Use when:** doing customer discovery interviews / surveys for an early-stage product. Translates Mom Test rules into a survey instrument.

### Research goal

"Identify the top 1–2 painful problems my target customer experiences in domain X, validated against past behavior (not hypothetical interest), and ranked by severity × frequency × willingness-to-pay."

### Target respondent

Specific customer hypothesis. Don't survey "founders" — survey "founders raising their first round of pre-seed in 2026 in domain X." Specificity in respondent definition is what makes the data useful.

### Top hypotheses

Examples (you'll have your own):
1. The worst friction in [my problem domain] is X, severity ≥ 3 for most respondents.
2. Respondents currently solve X by [hacky workaround] — which means they're already paying (in time/money) for a worse version of what I'd build.
3. Willingness-to-pay clusters at [some bucket] — below it, the problem isn't real; above it, respondents are existing customers of an incumbent I haven't found yet.

### Question set (~3 minutes honest, AI-interviewer mode recommended)

This template uses **AI-interviewer mode** — the best fit for founder customer discovery. The LLM probes follow-ups based on prior answers.

```
Stage 1: Open discovery
"Tell me about the last time you ran into [the problem domain]. Walk me
through what happened and what you actually did."
[Voice or chat. Listen for: severity cues, workaround mentioned, time/money cost.]

Stage 2: AI follow-ups (Tourangeau probes)
- If severity is unclear → "What was the worst part of that for you?"
- If workaround mentioned → "How well did that work? What would have made it work better?"
- If they didn't mention cost → "Did that end up costing you anything — time, money, a deal?"

Stage 3: Frequency check
"How often does something like that come up?"
[Forced-choice: Once or never / Few times a year / Monthly / Weekly / Daily]

Stage 4: Magnitude
"If a service handled this perfectly for you, what would that be worth?"
[Forced-choice: dual-currency WTP buckets]

Stage 5: Substitutes
"What have you tried for this so far? Even hacky stuff."
[Open, voice or text. Critical for finding incumbents.]

Stage 6: Segmentation (if you don't know respondent already)
- Role: founder / operator / investor / other
- Stage: pre-seed / seed / Series A+ / not raising
- Domain: <whatever segments matter for your product>

Stage 7: Follow-up qualification
"Open to a 20-minute follow-up call?"
[Yes/No + email if yes. SINGLE consent — research call only, no marketing tail.]
```

### Branching

- AI-interviewer follow-ups are dynamic (LLM decides) — no fixed branching.
- Stage 6 questions ONLY if you don't already know the respondent (cold survey vs. warm list).
- Stage 7 = no → drop, no further questions. Don't waste their time.

### Output schema

```sql
-- Top-level
respondent_id UUID,
research_goal TEXT,            -- which research goal this row maps to
created_at TIMESTAMP,

-- Per-stage capture
stage1_transcript TEXT,
stage2_followups JSONB,        -- array of {question, answer} pairs
frequency TEXT,                -- once / few_year / monthly / weekly / daily
willingness_to_pay TEXT,       -- bucket ID
substitutes_text TEXT,
role TEXT NULL,
stage TEXT NULL,
domain TEXT NULL,

-- Follow-up
research_call_consent BOOLEAN,
contact TEXT NULL,

-- Derived (LLM enrichment)
severity_inferred NUMERIC,     -- LLM rates from stage1+stage2 transcript
problem_cluster_id TEXT,
incumbent_named TEXT NULL,     -- LLM extracts named substitutes
mom_test_violation_flag BOOLEAN -- did the respondent answer hypothetically vs. about past behavior?
```

### Anti-patterns to avoid for this use case

- **DON'T pitch your idea before the survey.** The respondent will tell you what you want to hear. Pitch ONLY after stage 5.
- **DON'T ask "Would you use my product?"** The Mom Test forbids it. The data is worthless.
- **DON'T offer paid incentives** to founders specifically — biases responses toward people-who-take-paid-surveys.
- **DON'T conflate "interest" with "demand."** Lots of people will say "interesting product" — only past behavior + WTP + named substitutes prove demand.

---

## Template 3 — Gig-economy workers

**Use when:** designing a survey for the supply side of a marketplace (drivers, freelancers, contract workers, gig workers).

### Research goal

(Pick one.)

- **Onboarding diagnosis:** "Identify what blocks new workers from completing onboarding, and where they drop off in the first 7 days."
- **Pay-fairness diagnosis:** "Surface the moments workers feel unfairly paid, ranked by frequency, with verbatim quotes for product fix prioritization."
- **Retention diagnosis:** "Identify the top 3 reasons workers reduce hours / quit, with leading indicators that show 2+ weeks before the drop."

### Target respondent

Active workers on the platform. **Critical:** segment by tenure, because new workers and veterans have qualitatively different complaints. Don't bundle them.

### Top hypotheses

Examples for pay-fairness:
1. Workers most-cite specific moments (not abstract "low pay") — "I drove 20 minutes for a $4 trip" beats "pay is too low."
2. Trust in the algorithm matters more than the absolute pay number — explainability beats pay raises.
3. Workarounds exist (multi-apping, declining trips) and reveal what workers actually value.

### Question set (~2 min honest, mobile-first)

```
Q1. How long have you been [driving/freelancing/etc.] on [platform]?
    - Less than a month
    - 1-6 months
    - 6 months - 2 years
    - 2+ years

Q2. In the last week, what's the moment that frustrated you the most?
    [Open, voice/text. Critical that this be open — workers know best.]

Q2b. Severity of that moment (1-5 with anchors):
    1. Annoying but normal
    2. Cost me 30 min or one trip
    3. Cost me half a day's earnings
    4. Made me question continuing today
    5. Made me consider quitting / multi-apping

Q3. How often does something like that happen?
    [Frequency scale]

Q4. What did you do about it?
    [Open, optional. Workarounds reveal alternatives.]

Q5. If [platform] could fix one thing about how you get paid, what would it be?
    [Forced-choice + Other text:
     - Pay rate per [trip/task]
     - Predictability of how much I'll earn per hour
     - Knowing why I got rejected for trips
     - Bonus / surge clarity
     - Tip transparency
     - Other → text]

Q6. Compared to other platforms / gigs, how do you feel about [this one]?
    [-2 to +2 with anchors:
     -2: Way worse, I'm minimizing time here
     -1: Worse but stuck for now
      0: About the same
     +1: Better than most
     +2: This is my main gig and it's the best option]

Q7. Demographic / segmentation
    [Only what affects routing — e.g., city, vehicle type for drivers, work category
    for freelancers. SKIP age/gender/race unless you have a specific anti-bias
    audit need that justifies asking.]

Q8. Open to a 30-minute paid call to talk about this?
    [Yes/No + contact. Pay them for their time — gig workers are time-strapped.]
```

### Branching

- Q1 = "Less than a month" → swap Q2 to "What's confused you most so far?" (different cognitive frame for new workers).
- Q2b ≥ 4 (high severity) → add Q2c open prompt: "What would it have taken to make that moment OK for you?"
- Q5 = "Other" → require text fill-in.

### Output schema

```sql
worker_id TEXT,                -- their platform ID, hashed
tenure_bucket TEXT,
moment_text TEXT,              -- Q2
moment_severity INT,
moment_frequency TEXT,
workaround_text TEXT NULL,
top_pay_fix TEXT,              -- Q5 ID
top_pay_fix_other TEXT NULL,
platform_comparison INT,       -- Q6 -2 to +2
city TEXT NULL,
vehicle_type TEXT NULL,        -- if relevant
research_call_consent BOOLEAN,
contact TEXT NULL,

-- Derived
moment_cluster_id TEXT,        -- LLM clusters Q2 transcripts
sentiment_score NUMERIC,
risk_of_churn_score NUMERIC    -- composite from severity + comparison + tenure
```

### Anti-patterns to avoid for this use case

- **DON'T ask "How fairly do you feel paid?"** as a 1-10 scale. Workers will satisfice; you'll get noise. Ask about specific moments instead.
- **DON'T make it long.** Gig workers are between trips. >2 minutes = mass abandonment.
- **DON'T offer the survey "for free" — pay them.** $5 or local equivalent. Treat their time the way you treat your own product team's time.
- **DON'T survey them via the worker app's main flow** without their consent — interrupting a session = unfair pay friction = your survey IS now an example of platform unfairness. Use email or push notifications with opt-out.
