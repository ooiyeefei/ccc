# Sub-Agent Runner with Defense-in-Depth — Canonical Example

A generic spawner for depth-N sub-agents that runs *its own* `generateText` tool-loop with its own palette and stop conditions, then returns a structured "finding" payload that the parent uses. Use this when a critic or planner needs a deeper investigation pass than its own context budget allows — and when you don't want sub-agent failures to crash the parent loop. Trade-off: every depth level multiplies cost and adds an event-pumping layer to the SSE stream; over-spawning is the failure mode to budget against.

## Source
Extracted from Brandling (marketing-agency), 2026 hackathon production code:
- File: `src/lib/agents/sub-agents.ts`
- Original line: 89 (`runSubAgent` body) — declared at line 108 of the conceptual spec, implemented at 89

## Code
```ts
// src/lib/agents/sub-agents.ts:89
export async function runSubAgent<TFinding>(
  config: SubAgentConfig<TFinding>,
): Promise<TFinding | { status: 'failed'; reason: string }> {
  const {
    role, parentAgent, model, systemPrompt, userMessage, tools,
    terminatorTool, getCapturedFinding,
    depth = 2, maxSteps = 6, timeoutMs = 60_000,
    maxOutputTokens = 2048, onEvent,
  } = config;

  const emit = (event: AgentSseEvent) => { if (onEvent) onEvent(event); };
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), timeoutMs);

  emit({
    type: 'agent_step', agent: role, parentAgent, depth,
    action: 'reasoning', tool: 'spawn',
    argsSummary: `parent=${parentAgent} maxSteps=${maxSteps} timeout=${Math.round(timeoutMs/1000)}s`,
  });

  try {
    await generateText({
      model, system: systemPrompt, prompt: userMessage, tools,
      stopWhen: [hasToolCall(terminatorTool), stepCountIs(maxSteps)],
      maxOutputTokens, abortSignal: ac.signal,
    });
  } catch (err) {
    const reason = err instanceof Error
      ? (ac.signal.aborted ? `timeout after ${timeoutMs}ms` : err.message)
      : String(err);
    emit({ type: 'agent_error', agent: role, parentAgent, depth, reason, recoverable: true });
    return { status: 'failed', reason };
  } finally {
    clearTimeout(timer);
  }

  const finding = getCapturedFinding();
  if (!finding) {
    emit({
      type: 'agent_error', agent: role, parentAgent, depth,
      reason: `sub-agent did not call terminator '${terminatorTool}' within ${maxSteps} steps`,
      recoverable: true,
    });
    return { status: 'failed', reason: `did not finalize via ${terminatorTool} in ${maxSteps} steps` };
  }
  return finding;
}
```

## Walk-through
- Generic `<TFinding>`: the runner doesn't know what the finding shape is — it's whatever the caller's terminator tool's `execute()` returned. Type-safe across specialists.
- `getCapturedFinding: () => TFinding | undefined`: the closure-capture pattern. The caller's terminator tool stashes its output in a closure variable; we hand that getter to the runner so it can read it after the loop ends. Avoids depending on the model's text output.
- `stopWhen: [hasToolCall(terminatorTool), stepCountIs(maxSteps)]`: dual terminator + step cap — same shape as Synthesizer/Foreman, scaled down to 6 steps for a focused investigation.
- `setTimeout(() => ac.abort(), timeoutMs)` (default 60s): wall-clock cap orthogonal to step count. Defense-in-depth: a single `web_search` tool call hanging won't deadlock the parent.
- `emit({ tool: 'spawn', depth, parentAgent })` *before* the loop: the Inspector drawer needs a visible marker that a sub-agent began. Without this synthetic event, the SSE stream would silently jump from the parent's tool_call to the sub-agent's first inner tool_call.
- `try/catch` returns `{ status: 'failed', reason }` instead of re-throwing: parent critics get a *typed* failure. They can decide to fall back to scoring without the sub-agent, retry, or escalate — all without `try/catch` themselves.
- Post-loop "did not finalize" branch: even on a clean (no-throw) loop, if `getCapturedFinding()` is `undefined` it means the model ran out of steps without calling the terminator. Same `{ status: 'failed', reason }` shape as a thrown error. Parents handle one failure shape.

## Trade-offs this excerpt embodies
- **Defense-in-depth is the headline trade-off:** step cap (`maxSteps=6`) + wall-clock (`timeoutMs=60s`) + per-critic spawn cap (enforced *outside* this function, in the parent critic — typically 1 spawn per critic per draft). Three independent budgets. Belt + braces + parachute.
- The runner is *tolerant* of failure by design — judges scoring agentic execution want to see "agent attempted, recovered" rather than "agent crashed the pipeline". Returning a typed failure is a feature, not a leak.
- The closure-capture pattern (`getCapturedFinding`) is convenient but couples the terminator tool to the caller's outer scope. Refactoring to a return-channel queue would be cleaner but more code.

## What we'd change if rebuilding
- Make `MAX_DEPTH` configurable, not just `MAX_SPAWNS` per parent. Currently sub-agents could in principle spawn sub-sub-agents (depth 3) — the runner accepts `depth` as a parameter — but there's no central registry enforcing a global depth ceiling. We'd add `if (depth >= MAX_DEPTH) return { status: 'failed', reason: 'depth cap' };` as the first guard.
- Surface the per-step token cost so the parent can early-abort if a sub-agent is burning tokens without progressing.
- Consider a built-in retry-once policy on `{ status: 'failed', reason: 'timeout' }` (specifically). Right now every parent reimplements its own retry; centralizing it would reduce drift.

## Related references
- See [council-shapes.md](../references/council-shapes.md) for shape selection
- See [patterns-catalog.md](../references/patterns-catalog.md) for the SOTA pattern this implements
