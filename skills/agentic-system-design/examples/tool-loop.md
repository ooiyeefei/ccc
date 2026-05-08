# Tool-Loop with Explicit Terminator + Step Cap — Canonical Example

A model-driven tool-use loop that ends on a *named* terminator tool call OR a hard step cap, whichever fires first. The agent owns *what* and *when* to call; the harness guarantees the loop terminates and that every claim is grounded in evidence the agent had to ask for. Use this whenever you want the model to do open-ended investigation against a fixed corpus and emit structured output — and you want a budget you can defend in a postmortem. Trade-off: the system prompt has to do real work (tool order hints, finalize criteria), because there is no outer state machine to fall back on.

## Source
Extracted from Brandling (marketing-agency), 2026 hackathon production code:
- File: `src/lib/research.ts`
- Original line: 1447 (Synthesizer system prompt + `aiGenerateText` call at line 1494)

## Code
```ts
// src/lib/research.ts:1447
const systemPrompt = [
  "You are a brand research synthesizer.",
  "Synthesize a research brief from cached evidence. Read selectively, not everything.",
  "Finalize when you have at least 2 audience hypotheses, 2 positioning gaps, and 2 campaign angles.",
  "Each recorded item must cite at least one evidence ID — no claims without sources.",
  "",
  "Workflow:",
  "  1. read_evidence on the most promising 2-4 evidence pieces (not all of them).",
  "  2. Optionally query_competitor_data on 1-2 competitors that matter most.",
  "  3. record_audience_hypothesis (>= 2 times) with citations.",
  "  4. record_positioning_gap (>= 2 times) with citations.",
  "  5. record_campaign_angle (>= 2 times) — try to cover conversion, social, and premium types.",
  "  6. finalize_brief when minimums are met.",
  "",
  "Always emit a tool call. Do not respond in plain text only.",
].join("\n");

// ... user prompt assembled with the evidence inventory + competitor roster ...

const ac = new AbortController();
const timer = setTimeout(() => ac.abort(), 60_000);
try {
  const result = await aiGenerateText({
    model: MODELS.synthesizer,
    system: systemPrompt,
    prompt: userPrompt,
    tools,
    maxOutputTokens: 2048,
    stopWhen: [hasToolCall("finalize_brief"), stepCountIs(8)],
    abortSignal: ac.signal,
    onStepFinish: () => { stepCounter += 1; },
  });
  void result; // We rely on closure state, not text output.
} catch (err) { /* emit agent_error, fall through */ }
finally { clearTimeout(timer); }
```

## Walk-through
- `system: systemPrompt`: the prompt explicitly tells the model the *terminator* (`finalize_brief`) and the *minimum criteria* before it can fire. This is the contract.
- "Each recorded item must cite at least one evidence ID — no claims without sources": grounding rule. The `record_*` tools enforce this in their Zod schema (citations are required), so a hallucinated claim cannot enter state.
- "Always emit a tool call. Do not respond in plain text only": prevents the model from "narrating" instead of acting — every step has to be a recordable action.
- `stopWhen: [hasToolCall("finalize_brief"), stepCountIs(8)]`: dual terminators. The model *should* call `finalize_brief`; if it loops or stalls, step 8 ends it anyway.
- `abortSignal: ac.signal` + `setTimeout(..., 60_000)`: wall-clock cap orthogonal to step count — protects against a single tool call hanging.
- `void result`: we don't read the model's text output. State is mutated through tool `execute` closures (`audienceHypotheses.push(...)` etc.), so the loop's *side effects* are the result.
- `if (!finalized) { emit agent_error; }` + post-loop assembly: even if the agent runs out of steps without finalizing, downstream callers still get a brief built from whatever was captured. Failure is graceful, not silent.

## Trade-offs this excerpt embodies
- Step budget (8) and timeout (60s) are *fixed constants*, not adaptive. Predictable cost, but a complex brand may hit the cap.
- The terminator is enforced at the harness level (`hasToolCall`), but the *quality* of finalization depends on the prompt. A strong-willed model could call `finalize_brief` early; only the prompt's "at least 2 of each" rule discourages that.
- Tools mutate closure-captured state. This is convenient for single-shot use but makes parallel/streaming variants harder.

## What we'd change if rebuilding
- Make the step cap configurable per-evidence-corpus-size (e.g. `min(4 + corpusSize, 12)`) instead of a flat 8.
- Add a "minimum spend" pre-check before allowing `finalize_brief` to terminate — currently the prompt says "at least 2 hypotheses" but nothing in the harness blocks an early terminator.
- Consider streaming via `streamText` so the SSE log can show partial progress in real time, not just paired tool_call/tool_result events.

## Related references
- See [council-shapes.md](../references/council-shapes.md) for shape selection
- See [patterns-catalog.md](../references/patterns-catalog.md) for the SOTA pattern this implements
