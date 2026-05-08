# Multi-Model Router (TokenRouter Gateway) — Canonical Example

A single `createOpenAICompatible` provider points at TokenRouter — a unified `/v1/chat/completions` gateway that fronts Anthropic, OpenAI, and Google. A central `MODELS` registry maps each agent role to a model string. Use this whenever you want (a) one-line family swaps for cost/latency tuning, (b) heterogeneous model families across personas to cover blind-spots one family alone misses, and (c) a single auth/quota surface to monitor. Trade-off: every request hops through one extra service, and the lowest-common-denominator schema (OpenAI Chat Completions) clips some family-specific features (e.g. Anthropic's prompt caching needs explicit pass-through).

## Source
Extracted from Brandling (marketing-agency), 2026 hackathon production code:
- Files:
  - `src/lib/agents/provider.ts` (line 15) — gateway binding
  - `src/lib/agents/models.ts` (line 16) — per-role registry

## Code
```ts
// src/lib/agents/provider.ts:15
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

/**
 * Single OpenAI-compatible provider wired to TokenRouter.
 * TokenRouter exposes a unified `/v1/chat/completions` endpoint that fronts
 * Anthropic, OpenAI, and Google models. Every agent in this codebase reaches
 * its model through this provider so that swapping families (cost / latency)
 * is a one-line edit in `models.ts`.
 */
export const tokenrouter = createOpenAICompatible({
  name: 'tokenrouter',
  baseURL: process.env.TOKENROUTER_BASE_URL!,
  apiKey:  process.env.TOKENROUTER_API_KEY!,
});

// src/lib/agents/models.ts:16
import { tokenrouter } from './provider';

/**
 * Per-role model registry.
 * Multi-family heterogeneity is intentional — see design doc section 7.
 *   - Foreman / Content Creator / Review Council / Mutation Engine: Claude Opus 4.7
 *   - Marketing Head / Synthesizer: Claude Sonnet 4.6 (cheaper, fast structured output)
 *   - Brand Critic: GPT-5.5 (different family — caught Claude blind-spots in audit)
 *   - Engagement Critic: Gemini 3 Flash Preview (fast, multi-modal, cheap)
 */
export const MODELS = {
  foreman:           tokenrouter('anthropic/claude-opus-4.7'),
  marketingHead:     tokenrouter('anthropic/claude-sonnet-4.6'),
  contentCreator:    tokenrouter('anthropic/claude-opus-4.7'),
  brandCritic:       tokenrouter('openai/gpt-5.5'),
  engagementCritic:  tokenrouter('google/gemini-3-flash-preview'),
  reviewCouncil:     tokenrouter('anthropic/claude-opus-4.7'),
  mutationEngine:    tokenrouter('anthropic/claude-opus-4.7'),
  synthesizer:       tokenrouter('anthropic/claude-sonnet-4.6'),
} as const;

export type AgentRole = keyof typeof MODELS;
```

## Walk-through
- `createOpenAICompatible({ baseURL, apiKey })`: a single AI-SDK provider, configured once. Every agent gets its `LanguageModel` by calling `tokenrouter('<family>/<model>')`. Auth/quota live in one place.
- `process.env.TOKENROUTER_BASE_URL!` / `..._API_KEY!`: required at module load. We use the non-null assertion intentionally — if the env vars are missing, fail fast at boot rather than producing cryptic 401s on first request.
- The registry binds *roles* (`foreman`, `brandCritic`) to *model strings* (`anthropic/claude-opus-4.7`, `openai/gpt-5.5`). The role layer is the stable contract; the model string is a knob.
- `as const`: gives us `AgentRole = keyof typeof MODELS` so callers can type-safely reference roles. Misspelling `MODELS.frmean` is a compile error, not a runtime miss.
- **Multi-family heterogeneity by design**: Brand Critic on GPT-5.5, Engagement Critic on Gemini, everyone else on Claude. In our pre-launch audit, single-family councils kept missing the same kinds of failures — drafts that all three Claude critics rated 8/10 had taboo violations a fresh-eyes GPT-5.5 caught. Intentional family diversity covers blind-spots no individual family knows it has.
- Sonnet for Marketing Head and Synthesizer: these are *structured-output* roles where Sonnet's speed and cost beat Opus, and the structural rigor is enforced by Zod schemas anyway.
- Opus for Foreman / Content Creator / Mutation Engine: open-ended planning + creative generation, where the extra capability per-token pays off.

## Trade-offs this excerpt embodies
- **One-line family swaps**: `foreman: tokenrouter('anthropic/claude-opus-4.7')` → `tokenrouter('openai/gpt-5.5')` is a single character-class change. No code branches, no per-family adapters. We A/B-tested this for the Foreman in week 2 of the build.
- **Lowest-common-denominator API surface**: the OpenAI Chat Completions schema doesn't natively express Anthropic's prompt-caching headers or Gemini's structured-output mode. TokenRouter forwards what it can; family-specific features need explicit opt-in. Acceptable for a hackathon; would be a real cost in a year-long deployment.
- **Single point of failure**: if TokenRouter is down, *all* model traffic stalls. We mitigated by stubbing each persona with a fallback string in its `try/catch`, but a real deployment would want a direct-to-provider failover.

## What we'd change if rebuilding
- Add a per-role *primary + fallback* pair: `foreman: { primary: 'anthropic/claude-opus-4.7', fallback: 'openai/gpt-5.5' }` so a TokenRouter outage on one family auto-fails over.
- Ship a tiny "model-fitness probe" cron that pings each registered model once an hour with a known-good prompt and records latency / cost / output-quality drift. The registry is great for swaps; we currently swap by hunch, not data.
- Tag every TokenRouter request with the `AgentRole` so the dashboard can show "Brand Critic spent $X on GPT-5.5 this week" — right now we infer that from prompts after the fact.

## Related references
- See [council-shapes.md](../references/council-shapes.md) for shape selection
- See [patterns-catalog.md](../references/patterns-catalog.md) for the SOTA pattern this implements
