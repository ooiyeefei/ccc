---
description: Jarrett-style critique of an existing survey — finds leading questions, satisficing bait, missing structure, and proposes concrete rewrites
allowed-tools: Read, WebFetch, AskUserQuestion
---

# Critique Survey

Take an existing survey (pasted text, URL, or file) and return a Jarrett-style review with:
- A punch-list of issues (severity-ranked)
- Concrete rewrites for the worst 3–5
- A verdict on the overall instrument

## Usage

```
/critique-survey
```

The user will paste, link, or attach. If they paste a URL, fetch it (WebFetch). If a file path, read it. If they paste text directly, work from that.

## Process

Always invoke the `rethink-surveys` skill first.

### Step 1 — Catalog the questions

Read every question. Number them. For each, capture:
- The question text (verbatim)
- Answer format (open / single / multi / scale / etc.)
- Position in flow (early / mid / late)
- Any branching shown
- Any consent or contact treatment

If the survey is long (>15 Qs), summarize structurally before diving in.

### Step 2 — Apply the seven principles

For each question, check against:

1. **Past behavior, not hypotheticals.** Flag any "Would you..." / "Will you..." / "Do you think..."
2. **No pre-signaling the right answer.** Flag "Most people..." / loaded adjectives in option labels / leading question stems.
3. **Open-ended before narrowing.** Is there at least one open question early? Is it forced into a checkbox structure?
4. **Screening / diagnosis / segmentation separation.** Are demographic questions polluting the diagnostic flow?
5. **No double-barreled questions.** Flag any "X and Y?" question.
6. **Behavioral anchors over Likert.** Flag any 1-5/1-7 with vague anchors ("strongly agree"). Suggest behavioral replacements where possible.
7. **Honest length claim.** If a length is stated, estimate the actual time and flag mismatch.

### Step 3 — Apply the 4-part structural check

Tag each Q with which part it serves: discovery / diagnostic / intent / segmentation. Then check:

- **Discovery missing?** Survey is checkbox-only — won't capture novelty. Recommend adding one open Q at start.
- **Diagnostic missing or shallow?** Won't be analyzable across users — recommend adding severity/frequency.
- **Intent missing?** Won't surface demand signal. Recommend adding WTP buckets or top-3 priority.
- **Segmentation missing?** Won't enable cohorting. Recommend at minimum a single respondent-type Q.
- **Same part hit by 3+ questions?** Survey is bloated in one direction. Recommend cuts.

### Step 4 — Anti-pattern scan

Per [`references/design-principles.md`](../skills/rethink-surveys/references/design-principles.md), look for:

- "Rate your excitement / satisfaction / interest 1-10" → satisficing bait
- Demographic questions without routing rationale
- Combined consent checkbox (one for everything)
- Optional questions at the bottom (perceived as throwaway)
- Long matrices (rows × columns of Likert)
- "Other" without a text input

### Step 5 — Severity ranking

For each issue found, classify:

- **🔴 Blocker** — fundamentally broken (leading question, double-barreled, mom-test violation). Data is unusable.
- **🟡 Quality drag** — analysis still possible but signal is degraded.
- **🟢 Polish** — minor improvements possible.

### Step 6 — Concrete rewrites

For each 🔴 issue (and the top 🟡 if there are no 🔴), propose:

```
Original:
  <verbatim text>

Issue:
  <one sentence — which principle violated>

Rewrite:
  <new text>

Why this is better:
  <1-2 sentences>
```

Don't rewrite everything — focus the user on the 3–5 highest-leverage fixes. Death by a thousand suggestions is its own anti-pattern.

### Step 7 — Verdict

Close with a one-paragraph judgment:

```
Overall: <ship-ready | needs-work | rebuild-from-scratch>

The instrument's strongest decision is: <the best part>

The instrument's weakest decision is: <the worst part>

Next move: <one concrete next step>
```

## Output format

Single Markdown document. Use this skeleton:

```markdown
# Critique: <survey name or URL>

**Reviewed:** <date>
**Verdict:** <ship-ready | needs-work | rebuild>

## Summary
<2–3 sentences: top issues, structural shape, recommendation>

## Punch list
🔴 N blockers · 🟡 N quality drags · 🟢 N polish

### 🔴 Blockers
1. Q3 — leading framing: "Most people find X useful, do you?"
2. Q7 — double-barreled: "Was the food fast and cheap?"

### 🟡 Quality drags
1. ...
2. ...

### 🟢 Polish
1. ...

## Concrete rewrites (top 3)
1. **Q3**
   - Original: "..."
   - Issue: pre-signals the right answer (Principle #2)
   - Rewrite: "..."
   - Why: ...

2. **Q7** ...

3. **Q12** ...

## Structural assessment
- Part 1 (discovery): ✅ / ⚠️ / ❌
- Part 2 (diagnostic): ✅ / ⚠️ / ❌
- Part 3 (intent): ✅ / ⚠️ / ❌
- Part 4 (segmentation): ✅ / ⚠️ / ❌

## Length
Stated: <Xs>
Estimated actual: <Ys>
Honest? <yes/no>

## Verdict
<closing paragraph>
```

## Edge cases

- **User pastes a URL behind auth** → ask them to paste the questions directly instead.
- **Survey is in a language other than English** → critique in that language too where helpful (especially for ZH parallel translations — flag if the translation is transliterated rather than naturally phrased).
- **Survey has clear research-goal alignment but breaks principle (e.g., NPS as the only Q)** → critique still applies, but acknowledge the operator's constraint and suggest the smallest-viable improvement rather than a full rebuild.
