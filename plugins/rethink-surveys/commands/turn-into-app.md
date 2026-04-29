---
description: Turn a finalized survey design into a working app scaffold (TanStack Start / Next.js / static, with Supabase or local storage)
allowed-tools: Read, Write, Bash, Edit, AskUserQuestion
---

# Turn Survey Into App

Take a finalized survey design (output from `/design-survey` or a Markdown spec the user provides) and emit a working app scaffold the user can `npm install && npm run dev` immediately.

## Usage

```
/turn-into-app
```

Or with a path to a design doc:

```
/turn-into-app from survey-design-2026-04-29.md
```

## Process

Always invoke the `rethink-surveys` skill first. Then load [`references/multimodal-ux.md`](../skills/rethink-surveys/references/multimodal-ux.md) for stack and code-pattern guidance.

### Step 1 — Confirm the design is final

Ask if not obvious:
*"Is this the final question set? If you're still iterating on questions, run `/design-survey` first — it's harder to fix questions after the app exists."*

### Step 2 — Stack selection

Ask the user to pick:

| Stack | Best for |
|---|---|
| **TanStack Start + Supabase** | Production-grade, voice support, multilingual, mobile web. (Proxymate stack — battle-tested.) |
| **Next.js + Supabase** | Team already on Next.js. Roughly equivalent capability. |
| **Static HTML + Supabase Edge Functions** | One-off survey, no team, minimal infra. |
| **Reboot.ai** | AI-interviewer is the primary modality. |

Default if user hasn't picked: **TanStack Start + Supabase** (Proxymate-style).

### Step 3 — Storage selection

Ask:

| Storage | When |
|---|---|
| **Supabase (managed Postgres + Storage + Edge Functions)** | Production. Standard. |
| **Local JSON file + simple express server** | Hackathon prototype, no online deps. |
| **Bring your own DB** | User has an existing schema/host they want to write into. |

Default: **Supabase**.

### Step 4 — Voice + AI mode

If the design includes voice or AI-interviewer mode, ask for relevant credentials:

- **Deepgram API key** for transcription (voice). Free tier covers $200, no card needed.
- **Anthropic API key** for AI-interviewer. Use Claude Haiku 4.5 for extraction, Claude Sonnet 4.6 for the conversation loop.

Don't bake credentials into code; emit env-var references and a `.env.example` file.

### Step 5 — Emit the scaffold

For TanStack Start + Supabase (the default):

1. **Project structure** based on Proxymate (`src/routes/survey.index.tsx` + components):
   - `src/routes/survey.index.tsx` — main survey flow
   - `src/routes/survey.thanks.tsx` — completion page
   - `src/routes/survey.admin.tsx` — admin dashboard
   - `src/components/survey/` — `OptionCard`, `StepShell`, `ProgressBar`, `LanguageToggle`, `TaskCapture` (if voice/multimodal)
   - `src/lib/event-survey-config.ts` — typed option lists
   - `src/lib/storage.ts` — Supabase client + insert builder
   - `src/lib/i18n.ts` — translation strings
   - `supabase/migrations/<datetime>_<survey_name>.sql` — DDL for the table
   - `supabase/functions/transcribe/` — Deepgram wrapper if voice enabled
   - `wrangler.jsonc` — Cloudflare Workers config (or `vercel.json` if Next.js)
   - `.env.example`, `README.md`, `package.json`

2. **Generate the question-driven code:**
   - For each question in the design, produce a step component
   - Wire branching rules from the design's "Branching" section
   - Build the Supabase INSERT shape from the design's "Output schema" section
   - Build the i18n strings from the design's question-set section (preserve EN/ZH parallel)

3. **Don't reinvent components.** Reuse Proxymate's `OptionCard`, `StepShell`, `TaskCapture` verbatim — they're already battle-tested for this use case. Reference the live repo: `https://github.com/ooiyeefei/shanghai-lovable-survey`.

4. **Migration first.** The migration must run before the app starts (or first INSERT 400s). Note this prominently in the README.

### Step 6 — Verification checklist

Before declaring "scaffold ready", run through:

- [ ] All questions from the design exist as step components
- [ ] Branching rules from the design are wired
- [ ] Output schema matches design — every JSONB key, every column
- [ ] Voice mode (if enabled) has Deepgram wired with `language=multi` for code-switching
- [ ] AI-interviewer (if enabled) has structured-output extraction in system prompt
- [ ] `.env.example` covers all secrets
- [ ] README has: install / migrate / run / deploy / test-flow steps
- [ ] Honest length claim on landing page matches design's length budget

### Step 7 — Test plan

Don't ship without it. Recommend (and offer to do):

- `npm run build` — type-check
- One end-to-end submission via Playwright or manual
- Verify a row lands in Supabase
- Verify voice transcription returns 200 (if voice enabled)

### Step 8 — Deploy guidance

Brief deploy notes per stack:

- **TanStack Start → Cloudflare Workers** via `wrangler deploy`
- **Next.js → Vercel** via `vercel deploy`
- **Static HTML → Vercel/Cloudflare Pages/Netlify** — pick based on user pref

## Anti-patterns to avoid in the emitted scaffold

- ❌ Hardcoding API keys → use `.env.local` and `.env.example`
- ❌ Mixing client and server Supabase keys (use anon for client, service role only for admin server functions)
- ❌ Single-language UI when design specifies bilingual
- ❌ Skipping the migration step in README
- ❌ Voice mode without `language=multi` if audience is bilingual
- ❌ Combined consent checkbox in code when design specifies split consent
- ❌ Optional questions at the bottom of the form (UX violation per design principles)

## Reference: copy/adapt from Proxymate

The plugin assumes the Proxymate repo (`shanghai-lovable-survey`) is the canonical reference implementation. Direct file mappings to copy from:

- `src/components/survey/TaskCapture.tsx` → multimodal capture (text/chat/voice)
- `src/components/survey/OptionCard.tsx` → tap-to-select option card
- `src/components/survey/StepShell.tsx` → question screen layout
- `src/components/survey/ProgressBar.tsx` → step indicator
- `src/components/survey/LanguageToggle.tsx` → EN/ZH toggle
- `src/lib/voice/recorder.ts` → MediaRecorder wrapper
- `src/lib/voice/transcribe.ts` → Deepgram client
- `supabase/functions/transcribe/index.ts` → Deepgram edge function
- `supabase/migrations/*` → schema migration template

These have already absorbed real-world bug-fixes (workaround NOT NULL, transcribe race, Deepgram `language=multi`, etc.). Don't re-derive them.
