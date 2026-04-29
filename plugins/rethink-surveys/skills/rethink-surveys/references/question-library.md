# Question Library

Battle-tested question patterns organized by the 4-part hybrid structure. Each pattern includes EN+ZH text, the analytic purpose, what NOT to do, and the trade-off you're making by using it.

Loaded when proposing specific questions during `/design-survey`.

## Table of contents

- [Part 1 — Discovery (open-ended)](#part-1--discovery-open-ended)
- [Part 2 — Diagnostic (structured)](#part-2--diagnostic-structured)
- [Part 3 — Intent & prioritization](#part-3--intent--prioritization)
- [Part 4 — Segmentation & follow-up](#part-4--segmentation--follow-up)
- [Cross-cutting: bilingual & accessibility](#cross-cutting-bilingual--accessibility)

## Part 1 — Discovery (open-ended)

The job: capture the respondent's authentic frame in their own words. ONE primary question, optionally one branched follow-up.

### Pattern: "The one thing"

**EN:** "What's the one thing you're most worried about / struggling with / hoping to figure out?"
**ZH:** "你最担心 / 最困扰 / 最想搞清楚的一件事是什么?"

- **Purpose:** captures the top-of-mind concern. LLM-clusterable post-hoc.
- **Why "one":** prevents list-making (which is satisficing in disguise). Forces the respondent to commit to the most salient issue.
- **Modality:** voice + chat + text (Proxymate `TaskCapture` pattern).
- **Pair with:** a subtitle that nudges specificity: "One specific moment. The more concrete, the better."
- **Don't:** ask "what are some things you're worried about" — that's a list prompt.

### Pattern: "Last time X"

**EN:** "Last time [the relevant situation] happened, what did you actually do?"
**ZH:** "上次 [相关情境] 发生时,你当时是怎么做的?"

- **Purpose:** Mom Test rule #2 — past behavior over hypotheticals. Reveals real workarounds, real friction.
- **Modality:** text or voice.
- **Branched copy:** for first-timers / never-encountered, swap to "What's your fallback plan right now if it happens?"
- **Don't:** "What would you do if X happened?" — invites imagined-self answers.

### Pattern: "If you could wave a magic wand"

**EN:** "If you could wave a magic wand and change one thing about [domain], what would it be?"
**ZH:** "如果能用魔法改变 [领域] 的一件事,你会改什么?"

- **Purpose:** captures aspirational frame. Especially good for product-discovery surveys where current behavior is constrained by what exists.
- **Use sparingly:** this IS a hypothetical, but a deliberately broad one. Pair with at least one past-behavior question elsewhere.

## Part 2 — Diagnostic (structured)

The job: make responses analyzable across users. 2–4 questions max in this section.

### Pattern: Severity with behavioral anchors

**EN/ZH paired:**

| Score | EN | ZH |
|---|---|---|
| 1 | Annoying but I'd shrug it off. | 有点烦但能忍。 |
| 2 | I'd lose ~30 minutes figuring it out. | 大概要花 30 分钟解决。 |
| 3 | I'd lose half a day or miss something. | 会浪费半天或错过事情。 |
| 4 | It would wreck a meeting or a day. | 会毁掉一场会议或一整天。 |
| 5 | I'd consider not coming / leaving / quitting. | 我可能会考虑不来 / 离开 / 放弃。 |

- **Purpose:** universal interpretation. "I'd lose 30 minutes" means the same thing to a CEO and a gig worker.
- **Why anchors > Likert:** "Somewhat annoying" varies by individual + day; "30 minutes lost" doesn't.
- **Adapt the anchors** to the domain — "lose half a day" is event-week specific; "miss a deadline" is workplace specific. The pattern is anchors-with-consequences, not these exact strings.
- **Auto-advance on select** — feels fast, reduces commitment friction.

### Pattern: Frequency with rate anchors

**EN:**

- Once or never
- Few times a year
- Monthly-ish
- Weekly
- Daily / multiple times a day

**ZH:**

- 几乎从未
- 一年几次
- 每月一次左右
- 每周
- 每天 / 一天好几次

- **Purpose:** combine with severity for `pain × frequency` heatmaps.
- **Don't:** use "rarely / sometimes / often / always" — too fuzzy.

### Pattern: Workaround text (optional, branched)

**EN (branched on prior_visit / experience-with-domain):**

- For experienced respondents: "Last time something like this came up, what did you do?"
- For first-timers: "What's your fallback plan right now?"

**ZH:**

- 有经验的: "上次遇到类似情况,你是怎么处理的?"
- 第一次遇到的: "你目前的备选方案是什么?"

- **Purpose:** surface substitutes (what the user is replacing with your product). Critical demand signal.
- **Optional + ≤120 chars:** forcing this drops completion. Keep it short; let post-hoc LLM extract patterns.
- **Modality:** text only. Voice transcripts are too long for this prompt.

### Pattern: Diagnosis-via-AI-interviewer

When using AI-interviewer mode, replace the structured diagnostic with a conversational sequence:

1. **Probe stage 2 (retrieval):** "Tell me about the most recent time this happened. Walk me through what was going on."
2. **Probe stage 3 (judgment):** "Why was that the worst part for you?"
3. **Probe stage 4 (response):** "If you'd had a magic helper at that exact moment, what would they have done first?"

Each turn = one Tourangeau stage. AI extracts severity / frequency / workaround into the structured fields post-hoc.

## Part 3 — Intent & prioritization

The job: turn pain signals into demand signals. 1–3 questions.

### Pattern: Willingness-to-pay (bucketed, currency-localized)

**EN:** "If someone reliably handled this for you, what would that be worth?"
**ZH:** "如果有人能可靠地帮你处理这件事,值多少钱?"

| ID | EN | ZH |
|---|---|---|
| `not_paying` | Not worth paying for | 不值得花钱 |
| `under_15` | Up to ~¥100 / $15 | 100 元 / 15 美元 以内 |
| `under_40` | Up to ~¥300 / $40 | 300 元 / 40 美元 以内 |
| `under_140` | Up to ~¥1000 / $140 | 1000 元 / 140 美元 以内 |
| `whatever` | Whatever it takes | 多少钱都行 |

- **Why dual-currency:** bilingual audiences shouldn't have to do mental conversion.
- **Why buckets, not numeric input:** numeric input invites satisficing ("$10" or "$100") and anchoring on round numbers. Buckets force a real comparison.
- **Don't:** use NPS (-100 to +100). NPS is a marketing-funnel metric, not a demand signal.

### Pattern: Top-3 priority ranking

**EN:** "If we paired you with someone local, what matters most? (pick up to 3)"
**ZH:** "如果给你匹配本地人帮忙,最看重什么?(最多 3 项)"

- **Purpose:** the respondent literally tells the matching algorithm how to rank candidates.
- **Why top-3 not unlimited:** forcing prioritization is the whole point. "Pick all that apply" is checkbox-approval, not prioritization.
- **UX detail:** dim un-selected options once 3 are picked — visible cap signal.

### Pattern: Time-window / urgency

**EN:** "When would help be most useful?"
**ZH:** "什么时候最需要?"

(Adapt buckets to the domain — pre-event/during/after for events; weekday-morning/evening/weekend for consumer apps.)

- **Multi-select allowed.** Some respondents have multiple windows.
- **Why this beats "how urgent":** urgency is a feeling; time-window is a commitment.

## Part 4 — Segmentation & follow-up

The job: cohort the respondent + qualify for follow-up calls. 2–4 questions.

### Pattern: Respondent type (single-select)

**Always include an "honestly not sure" option.** Satisficer escape valve. Flagging that response as lower-trust in your analysis is correct; not having the option is worse.

```
🛠️ Builder / engineer
🚀 Founder
🧭 Operator at a startup
🏢 At a larger company / investor
🎓 Student / researcher / curious
🤷 Honestly, I'm not sure yet
```

### Pattern: Group composition

**EN:** "Who's coming with you / Who's involved?"
**ZH:** "你跟谁一起?"

- **Purpose:** changes downstream routing. Solo vs. with-family is a big signal.
- **Use case:** event surveys, anything where the respondent's social context affects their needs.

### Pattern: Mandarin / language comfort (1–5)

For bilingual contexts:

| Score | EN | ZH |
|---|---|---|
| 1 | Zero — I'll need help for most things | 零 — 大部分事情需要帮助 |
| 2 | A few phrases | 会几句 |
| 3 | Conversational | 日常交流没问题 |
| 4 | Comfortable in meetings | 能用于会议 |
| 5 | Native / fluent | 母语 / 流利 |

### Pattern: Split consent (the most-skipped best-practice)

Almost every survey uses **one combined consent checkbox**. This is wrong.

Show two checkboxes, each defaulting unchecked:

- ☐ "OK to contact me about [the actual product/service]" → maps to `consent_test` or similar
- ☐ "OK to contact me for a 15-minute research call" → maps to `consent_research_call`

- **Submit allowed if:** at least one checkbox is checked AND contact ≥3 chars (when willingness ≠ "no").
- **Why split:** forces the respondent to opt in to specific channels, which makes follow-up legitimate. Combined consent gets opt-out spikes when you actually contact them.
- **DB schema:** two boolean columns, never one.

### Pattern: Willingness frame (the close)

**EN:** "Would you actually try this if we lined it up?"
**ZH:** "如果我们安排好了,你会真的来用吗?"

Options (all four needed):

| ID | EN | ZH | Maps to |
|---|---|---|---|
| `at_event` | Yes — use me as a tester | 好 — 我愿意试 | High-intent, contact required |
| `maybe` | Maybe — depends on who/what | 看情况 | Medium-intent, contact required |
| `this_week` | Not now, but another time | 这次不,下次可以 | Low-intent, optional contact |
| `no` | No thanks | 不用了 | Drop, no contact |

## Cross-cutting: bilingual & accessibility

- **Always render BOTH languages** if your audience is bilingual. Don't make people switch.
- **Respect cognitive overhead of language-switching:** keep questions parallel in structure across languages, not just translated. The Chinese should feel native, not transliterated.
- **Voice mode should auto-detect language** (use Deepgram `language=multi` or equivalent).
- **For accessibility:** every form should also be navigable by keyboard. Auto-advance on select is great UX, but provide a back button.
