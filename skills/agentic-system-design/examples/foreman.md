# Foreman Orchestration — Canonical Example

A "Foreman" is a top-level model-driven orchestrator whose entire job is to pick which persona speaks next. The model owns *order* (which critic first, whether to revise) but the system prompt + tool palette enforce *skeleton* invariants (must start with strategy, must end with council + finalize). Use this when you want emergent debate dynamics — model decides whether revision is needed — without giving up the reliability of a fixed bookend. Trade-off: more tokens than a hard-coded pipeline, and the prompt itself becomes load-bearing infrastructure.

## Source
Extracted from Brandling (marketing-agency), 2026 hackathon production code:
- File: `src/lib/agents/council-foreman.ts`
- Original line: 41 (system prompt) + 574 (`generateText` call with 7-tool palette)

## Code
```ts
// src/lib/agents/council-foreman.ts:41
const SYSTEM_PROMPT = [
  'You are the Council Foreman. You orchestrate a creative debate to produce one published caption.',
  '',
  'CONSTRAINTS:',
  '- You MUST start by calling `call_marketing_head` to get a strategic direction.',
  '- After that, you MUST call `call_content_creator` at least once to produce draft variants.',
  '- You MUST end by calling `call_review_council` and then `finalize`.',
  '- In between, decide who speaks: invoke critics in any order, request revisions, re-run a critic.',
  '- Maximum 3 revision loops, maximum 12 total tool calls. Stop when `finalize` is called.',
  '',
  'WORKFLOW HINTS:',
  '- After the critics score, if EITHER score is below 6, prefer `request_revision` ...',
  '- If both critics score 6+ on the first try, you may go straight to `call_review_council`.',
  '- The critics have their own verification sub-tools ... trust the score they return.',
].join('\n');

// ... 7 tool definitions (callMarketingHeadTool, callContentCreatorTool,
//     callBrandCriticTool, callEngagementCriticTool, requestRevisionTool,
//     callReviewCouncilTool, finalizeTool) — each captures shared State via closure ...

await generateText({
  model: MODELS.foreman,
  system: SYSTEM_PROMPT,
  prompt: [/* brief, persona name, brand DNA */, 'Begin by calling call_marketing_head. Then orchestrate the debate.'].join('\n'),
  tools: {
    call_marketing_head:    callMarketingHeadTool,
    call_content_creator:   callContentCreatorTool,
    call_brand_critic:      callBrandCriticTool,
    call_engagement_critic: callEngagementCriticTool,
    request_revision:       requestRevisionTool,
    call_review_council:    callReviewCouncilTool,
    finalize:               finalizeTool,
  },
  stopWhen: [hasToolCall('finalize'), stepCountIs(12)],
  maxOutputTokens: 2048,
  abortSignal: ac.signal,
});
```

## Walk-through
- "MUST start by calling `call_marketing_head`" + "MUST end by calling `call_review_council` and then `finalize`": the bookends. Everything between is the Foreman's call.
- "Maximum 3 revision loops, maximum 12 total tool calls": the tool itself (`request_revision`) tracks `revisionCount` and returns `{ ok: false, guidance: "Revision cap reached..." }` once exhausted. The model is told *what to do* when exhausted, not just denied.
- The 7-tool palette names are verbs, not nouns: `call_*`, `request_revision`, `finalize`. This nudges the model toward action-oriented planning.
- `stopWhen: [hasToolCall('finalize'), stepCountIs(12)]`: same dual-terminator pattern as the Synthesizer. `finalize` is the happy path; 12 is the cliff.
- Each tool emits paired `agent_step` SSE events (`tool_call` then `tool_result`), so the Inspector UI replays the Foreman's exact decision sequence — judges scoring "agentic execution" can *see* what the model picked.
- Per-tool `try/catch`: if `callMarketingHead` throws, the tool returns `{ status: 'unavailable', reason, strategicDirection: <fallback string> }`. The Foreman gets a structured failure to keep planning around, not an exception.
- After the loop: `if (!state.finalized)` → assemble fallback from `state.currentDraft || state.draftVariants[0] || <hardcoded last-ditch>`. The route always gets a coherent shape back, even if the Foreman aborts mid-flight.

## Trade-offs this excerpt embodies
- Bookend invariants are encoded *only* in the prompt; nothing in the harness blocks a model that decides to skip `call_marketing_head`. In practice, Opus-class models follow imperative MUSTs reliably; weaker models would need a state-machine wrapper.
- The 7-tool palette is wide enough to enable emergent revision sequences but small enough to fit one model context. Adding tools cheaply is tempting; we found 7 is already at the "the model sometimes wastes a step pondering which to call" threshold.
- The `request_revision` → `call_content_creator(revisionFeedback)` two-step is intentional friction. The model has to *commit* to revising before it can re-draft. Without it, the model would noodle indefinitely.

## What we'd change if rebuilding
- Encode the start-bookend in the harness too: pre-seed the conversation with a synthetic `call_marketing_head` tool result instead of *asking* the model to call it. Cheaper, faster, and deterministic.
- Make `MAX_REVISIONS` (currently 3) and the `stepCountIs(12)` cap configurable per brand-tier — premium brands probably deserve more iterations.
- The tool schemas use `.strict()` Zod objects, which is great for the Anthropic-family Foreman but trips occasional issues when other model families try to add unsolicited fields. A schema-relaxation layer at the boundary would help cross-family swaps.

## Related references
- See [council-shapes.md](../references/council-shapes.md) for shape selection
- See [patterns-catalog.md](../references/patterns-catalog.md) for the SOTA pattern this implements
