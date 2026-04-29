# Multimodal UX & Implementation

UX patterns and code scaffolds for survey apps that support typed / tap / voice / AI-interviewer modalities.

Loaded when running `/turn-into-app`.

## Table of contents

- [Modality decision tree](#modality-decision-tree)
- [Form-mode UX (mobile-first)](#form-mode-ux-mobile-first)
- [Voice-mode UX](#voice-mode-ux)
- [AI-interviewer mode UX](#ai-interviewer-mode-ux)
- [Storage schemas](#storage-schemas)
- [Stack recommendations](#stack-recommendations)
- [Reference scaffolds](#reference-scaffolds)

## Modality decision tree

| Context | Modality | Length |
|---|---|---|
| QR scan at venue, low attention | Pure form, tap-to-select | ≤60s |
| Pre-event email, moderate engagement | Form + optional voice on key Q | ≤90s |
| Warm research list, willing respondents | AI-interviewer (LLM probes) | 3–5 min |
| Accessibility / language flexibility | Voice-note only, single open prompt | open |

## Form-mode UX (mobile-first)

**Layout rules:**

- One question per screen.
- Question headline: `text-lg sm:text-xl` mobile (18-20px). NOT `text-2xl` or larger — that's hero-page-only.
- Option cards: ≥48px tap target (Apple HIG minimum), ≤56px height (any larger and 4 options scroll on iPhone SE).
- Auto-advance on single-select after 180ms (lets the user see their selection register).
- Multi-select with cap (e.g., "pick up to 3"): show `(N/M)` counter on the Continue button + dim un-selected options once cap hit.
- Progress bar at top showing `(current/total)` step count. Be honest — auto-skipped steps still count or you confuse the user.

**Type vs. tap vs. voice on the worry/discovery question:**

The Proxymate `TaskCapture` pattern offers all three modalities for the single most-important open question:

```
[ Type ] [ Chat ] [ Talk ]
```

- **Type** — a textarea. Default. Fastest for desktop / fluent typists.
- **Chat** — scripted 3-turn conversation, each turn is a textarea. Best for users who prefer prompting over blank-page paralysis.
- **Talk** — push-to-talk MediaRecorder → upload to storage → transcribe (Deepgram or equivalent) → editable text appears. Best for slow typers / non-native English / multitasking respondents.

All three end in the same `text` field on the response. Capture `capture_mode` so you know which path was used (downstream analysis differs by mode).

**Anti-patterns to avoid in form mode:**

- ❌ Long matrices (rows × columns of Likert) — forces straight-lining
- ❌ "Other (please specify)" without a visible text field — user doesn't know it'll appear
- ❌ Optional Q at the bottom — perceived as throwaway
- ❌ Hover-only validation hints on mobile

## Voice-mode UX

**Recording UI:**

- Big circular mic button. Tap to start, tap to stop. NOT push-and-hold (push-and-hold breaks if user drops thumb to scroll).
- Visible elapsed timer.
- Visible language hint: "Speak in any language — English, 中文, or whatever's natural."
- After stop: auto-upload + transcribe → editable transcript appears below.
- "Re-record" button always visible.
- Continue button DISABLED while transcribing — don't let user submit empty transcript by racing past.

**Transcription:**

- Deepgram nova-3 with `language=multi` for code-switched audio. NOT `detect_language=true` (single-language path).
- Extract `alternatives[0].languages` array as the language signal — channel-level `detected_language` is undefined in multi mode.
- Set client-side timeout aggressively (8s) — on timeout, show "transcription is taking a while; you can type a note or continue." Save the audio regardless.

**Privacy:**

- Always disclose voice is being uploaded + transcribed.
- Don't auto-record — explicit user action to start.

## AI-interviewer mode UX

The most powerful modality, but the easiest to do badly.

**Flow:**

1. Open with a single broad question (Stage 1, like `/design-survey` template).
2. LLM probes 1–3 follow-ups based on the answer. Each follow-up is ONE question, not a wall of text.
3. After each respondent message, LLM extracts structured fields silently (severity, workaround, frequency, etc.).
4. After ~6–10 turns or sufficient signal, LLM closes with: "I have what I need. Just two quick wrap-up questions."
5. Final 2 forced-choice questions (segmentation + follow-up consent) shown as form fields, NOT chat.

**Implementation pattern (Anthropic SDK, Claude Sonnet 4.6):**

```typescript
// Pseudocode — this is the loop, not a complete app
const systemPrompt = `You are a customer research interviewer. Your job is to
understand what's actually painful for the respondent — not pitch a product,
not lead them to an answer.

Rules (follow strictly):
1. Ask about specific past behavior, not hypothetical opinions.
2. ONE question per turn. Never lists.
3. After 6 turns, you must close out. Say: "Got it, I have what I need."
4. Extract structured signals into a hidden JSON block at the end of each turn.

Research goal: ${researchGoal}
Hypotheses: ${hypothesesList}

Format each response as:
[respondent-facing text]

<extract>
{ "severity_evidence": "...", "frequency_evidence": "...", "workaround_named": "..." }
</extract>`;

// Per turn:
const response = await anthropic.messages.create({
  model: "claude-sonnet-4-6",
  system: systemPrompt,
  messages: turnHistory,
  max_tokens: 500,
});

// Strip <extract> from user-facing text, save to DB
const userFacing = response.split("<extract>")[0].trim();
const extracted = JSON.parse(response.match(/<extract>(.*)<\/extract>/s)[1]);
```

**Critical UX details:**

- Each LLM turn shows a typing indicator while loading.
- User can edit/retry their last answer (research integrity > flow purity).
- Show progress: "About halfway" / "Last question" — the user needs an exit signal.
- Disable AI follow-ups after turn 8 — hard cap protects against runaway probing.
- Save **every turn** to DB, not just the final state. Drop-off mid-conversation IS the data.

**Anti-patterns:**

- ❌ Open-ended chat with no exit signal (respondents wonder when it ends)
- ❌ AI summarizing back to user before closing ("So what I'm hearing is...") — feels patronizing
- ❌ AI suggesting the answer ("Was it the language?") — that's leading, exact opposite of the goal

## Storage schemas

### Form-mode (Supabase, mirrors Proxymate)

```sql
CREATE TABLE survey_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  survey_version TEXT NOT NULL,        -- 'event_v1', 'founder_v1', etc.
  source TEXT NOT NULL,                 -- 'qr', 'email', 'manual'
  locale TEXT NOT NULL,                 -- 'en', 'zh', etc.
  respondent_type TEXT,
  segment TEXT,                          -- derived
  capture_mode TEXT,                     -- 'text'|'chat'|'voice'
  voice_url TEXT,                        -- storage path if voice
  transcript TEXT,
  transcript_language TEXT,              -- e.g., 'en', 'multi:en,zh'
  conversation_log JSONB,                -- chat-mode turn list
  response_data JSONB NOT NULL,          -- the structured Q answers
  willingness_to_test TEXT,              -- single ID
  contact TEXT,
  consent BOOLEAN NOT NULL DEFAULT false,
  consent_research_call BOOLEAN NOT NULL DEFAULT false,
  -- LLM enrichment columns (populated post-hoc)
  pain_cluster_id TEXT,
  cluster_label TEXT,
  specificity_score NUMERIC,
  interview_score NUMERIC,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_survey_interview_score
  ON survey_responses (interview_score DESC NULLS LAST);
```

### AI-interviewer mode (extends form schema)

```sql
CREATE TABLE survey_interview_turns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  survey_response_id UUID NOT NULL REFERENCES survey_responses(id),
  turn_index INT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('assistant', 'user')),
  content TEXT NOT NULL,
  extracted_signals JSONB,             -- only on assistant turns
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (survey_response_id, turn_index)
);

CREATE INDEX idx_interview_turns_response
  ON survey_interview_turns (survey_response_id, turn_index);
```

## Stack recommendations

| Stack | When to pick | Trade-offs |
|---|---|---|
| **TanStack Start + Supabase** (Proxymate stack) | You want voice + multilingual + low-friction deploy. Best for production-grade. | More moving parts; need to manage Cloudflare/Vercel deploy + Supabase migrations. |
| **Next.js + Supabase** | Your team already lives in Next, and you don't need TanStack Start's specific features. | Slightly heavier than TanStack Start for survey-only apps. |
| **Static HTML + Supabase Edge Functions** | One-off survey, no team, no auth, no i18n complexity. | Voice mode is harder to wire; AI-interviewer needs a tiny serverless function. |
| **Reboot.ai (full-stack agentic)** | AI-interviewer is the primary modality and you want durable agent state. | Newer ecosystem; learning curve. Best for the "AI is the survey" use case. |

## Reference scaffolds

These don't ship in `assets/` — see the Proxymate repo at `https://github.com/ooiyeefei/shanghai-lovable-survey` for a full TanStack Start + Supabase implementation including:

- Tri-modal `TaskCapture` component
- Deepgram edge function with `language=multi`
- Two surveys at `/survey` (60s) and `/survey/full` (90s) sharing component library
- Admin dashboard with cluster aggregation
- Wenjix's signal-and-demand schema migration

When `/turn-into-app` runs, this implementation is the reference — adapt question text & options, keep architecture.
