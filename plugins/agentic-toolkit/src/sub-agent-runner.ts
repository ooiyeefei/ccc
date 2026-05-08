/**
 * Hardened sub-agent runner — depth + spawn + timeout enforced at the runner
 * level.
 *
 * Lifted from Brandling `src/lib/agents/sub-agents.ts` (~214 LOC, esp.
 * `runSubAgent` at line 89). Brandling Appendix A item 2: **hard-enforced
 * configurable depth limit**. Brandling tracked `depth` only in events;
 * the runner itself happily spawned to whatever depth the model asked for.
 * This version refuses to spawn beyond `maxDepth`, refuses to spawn more than
 * `maxSpawns` per parent, and returns a typed `SubAgentResult` so the parent
 * can branch cleanly on each failure mode.
 *
 * ## Why a runner instead of inlining `generateText`?
 *
 *   - Defense-in-depth: spawn caps at the runner level survive prompt
 *     regressions where the model "forgets" the depth-2 rule.
 *   - Consistent SSE shape: every sub-agent emits a synthetic `spawn`
 *     event + uniform `agent_step` events with `parentAgent` set, so the
 *     inspector indents reliably.
 *   - Closure-captured terminator output: the model "ends" by calling a
 *     designated tool whose `execute()` return value is the structured
 *     finding. The runner doesn't care what shape the finding has —
 *     `TFinding` is a generic.
 *
 * ## Hard caps (defaults reflect Brandling production)
 *
 *   - `maxDepth: 3`  — depth-3 (parent → critic → specialist) is the design
 *                      doc's documented sweet spot; deeper requires
 *                      out-of-process isolation (worktree / cloud worker).
 *   - `maxSpawns: 2` — per-parent. Two specialists per critic is enough for
 *                      Brand Critic + Engagement Critic patterns and stops
 *                      runaway fan-out.
 *   - `timeoutMs: 30_000` — wall-clock. Brandling production used 60s
 *                      because it embedded web search; 30s is the safer
 *                      default for runs without external I/O.
 *   - `maxSteps: 6`  — tool-loop step cap.
 *
 * ## Failure semantics
 *
 * The runner returns one of four typed shapes (`SubAgentResult<TFinding>`):
 *   - `{ status: 'ok', finding }`      — success, terminator was called.
 *   - `{ status: 'failed', reason }`   — model failed to finalize OR threw.
 *   - `{ status: 'depth_exceeded' }`   — caller tried to spawn at >= maxDepth.
 *   - `{ status: 'timeout' }`          — wall-clock cap fired.
 *
 * Parent code is expected to branch on `status` and decide whether to retry,
 * fall back to scoring without the sub-agent, or escalate. The runner never
 * throws — judges scoring agentic execution want "agent attempted, recovered"
 * not "agent crashed the pipeline".
 */

import {
  generateText,
  hasToolCall,
  stepCountIs,
  type LanguageModel,
  type Tool,
} from 'ai';
import type {
  AgentEventSink,
  AgentSseEvent,
  AgentTraceRole,
} from './events';

/**
 * Configuration for one sub-agent spawn.
 *
 * `TFinding` is the structured output type returned by the terminator tool's
 * `execute()`. Caller is responsible for capturing that value via closure
 * inside the tool definition and exposing it through `getCapturedFinding`.
 */
export interface SubAgentConfig<TFinding, TRole extends AgentTraceRole = AgentTraceRole> {
  /** Sub-agent's role label, used on every emitted agent_step event. */
  role: TRole;
  /** Role of the parent that spawned this sub-agent (for SSE nesting). */
  parentAgent: TRole;
  /** Current spawn depth: parent's depth + 1. Runner enforces `< maxDepth`. */
  currentDepth: number;
  /** Hard depth cap. Default 3. */
  maxDepth?: number;
  /**
   * Max sub-agent spawns this parent has used so far (caller tracks). The
   * runner refuses if `spawnCount >= maxSpawns`. Pass current count + the
   * cap; the runner returns `depth_exceeded` (semantic overload — covers
   * "spawn budget exceeded" too) when the cap trips.
   */
  spawnCount?: number;
  /** Max spawns per parent. Default 2. */
  maxSpawns?: number;
  /** Language model from the registry. */
  model: LanguageModel;
  /** System prompt — defines persona, evidence rules, output format. */
  systemPrompt: string;
  /** User prompt — the question / parameters from the parent. */
  userMessage: string;
  /**
   * Tool palette. Must include exactly one terminator (matched by
   * `terminatorTool` name) whose `execute()` returns `TFinding`.
   */
  tools: Record<string, Tool>;
  /** Name of the tool that finalizes; calling it ends the loop. */
  terminatorTool: string;
  /**
   * Closure-captured output from the terminator tool. Caller wires this:
   *
   * ```ts
   * let captured: MyFinding | undefined;
   * const tools = {
   *   submit_finding: tool({
   *     ...
   *     execute: async (args) => { captured = args; return { ok: true }; },
   *   }),
   * };
   * await runSubAgent({ ..., getCapturedFinding: () => captured });
   * ```
   */
  getCapturedFinding: () => TFinding | undefined;
  /** Wall-clock cap in ms. Default 30_000. */
  timeoutMs?: number;
  /** Tool-loop step cap. Default 6. */
  maxSteps?: number;
  /** Output token cap. Default 2048. */
  maxOutputTokens?: number;
  /** Bubble-up SSE callback. */
  onEvent?: AgentEventSink<TRole>;
}

/**
 * Typed result. Parent code branches on `status`.
 */
export type SubAgentResult<TFinding> =
  | { status: 'ok'; finding: TFinding }
  | { status: 'failed'; reason: string }
  | { status: 'depth_exceeded'; reason: string }
  | { status: 'timeout'; reason: string };

const DEFAULT_MAX_DEPTH = 3;
const DEFAULT_MAX_SPAWNS = 2;
const DEFAULT_TIMEOUT_MS = 30_000;
const DEFAULT_MAX_STEPS = 6;
const DEFAULT_MAX_OUTPUT_TOKENS = 2048;

/**
 * Run one sub-agent tool-loop with depth + spawn + timeout enforcement.
 *
 * Returns a typed `SubAgentResult`. Never throws.
 *
 * @example
 * ```ts
 * let captured: VerificationFinding | undefined;
 * const result = await runSubAgent<VerificationFinding>({
 *   role: 'verification_specialist',
 *   parentAgent: 'brand_critic',
 *   currentDepth: 2,
 *   model: MODELS.synthesizer.model,
 *   systemPrompt: VERIFICATION_PROMPT,
 *   userMessage: `Verify claim: ${claim}`,
 *   tools: {
 *     web_search: webSearchTool,
 *     submit_finding: tool({
 *       inputSchema: z.object({ verdict: z.string(), evidence: z.array(...) }),
 *       execute: async (args) => { captured = args; return { ok: true }; },
 *     }),
 *   },
 *   terminatorTool: 'submit_finding',
 *   getCapturedFinding: () => captured,
 *   onEvent: parentOnEvent,
 * });
 *
 * if (result.status === 'ok') {
 *   useFinding(result.finding);
 * } else {
 *   fallbackScore();
 * }
 * ```
 */
export async function runSubAgent<
  TFinding,
  TRole extends AgentTraceRole = AgentTraceRole,
>(
  config: SubAgentConfig<TFinding, TRole>,
): Promise<SubAgentResult<TFinding>> {
  const {
    role,
    parentAgent,
    currentDepth,
    maxDepth = DEFAULT_MAX_DEPTH,
    spawnCount = 0,
    maxSpawns = DEFAULT_MAX_SPAWNS,
    model,
    systemPrompt,
    userMessage,
    tools,
    terminatorTool,
    getCapturedFinding,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    maxSteps = DEFAULT_MAX_STEPS,
    maxOutputTokens = DEFAULT_MAX_OUTPUT_TOKENS,
    onEvent,
  } = config;

  const emit = (event: AgentSseEvent<TRole>) => {
    if (onEvent) onEvent(event);
  };

  // ---------------------------------------------------------------------
  // Defense-in-depth: refuse to spawn at or beyond maxDepth. Brandling
  // Appendix A item 2: this check existed only as event metadata, never
  // as enforcement. A buggy critic prompt could spawn at depth 5; the
  // runner would happily oblige until the wall-clock cap.
  // ---------------------------------------------------------------------
  if (currentDepth >= maxDepth) {
    const reason =
      `depth cap: tried to spawn at depth ${currentDepth}, max is ${maxDepth}. ` +
      `Restructure: this work probably belongs in a tool on the parent, not a sub-agent.`;
    emit({
      type: 'agent_error',
      agent: role,
      parentAgent,
      depth: currentDepth,
      reason,
      recoverable: true,
    });
    return { status: 'depth_exceeded', reason };
  }

  // ---------------------------------------------------------------------
  // Per-parent spawn cap. Same rationale: budget enforcement at the
  // runner, not buried in a critic's prompt.
  // ---------------------------------------------------------------------
  if (spawnCount >= maxSpawns) {
    const reason =
      `spawn cap: parent ${parentAgent} has already spawned ${spawnCount} ` +
      `sub-agents (max ${maxSpawns}). Score with available evidence.`;
    emit({
      type: 'agent_error',
      agent: role,
      parentAgent,
      depth: currentDepth,
      reason,
      recoverable: true,
    });
    return { status: 'depth_exceeded', reason };
  }

  const ac = new AbortController();
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    ac.abort();
  }, timeoutMs);

  // Synthetic spawn event so the inspector marks the boundary clearly. Tools
  // the sub-agent then calls emit their own agent_step events with depth +
  // parentAgent set.
  emit({
    type: 'agent_step',
    agent: role,
    parentAgent,
    depth: currentDepth,
    action: 'reasoning',
    tool: 'spawn',
    argsSummary:
      `parent=${parentAgent} depth=${currentDepth}/${maxDepth} ` +
      `maxSteps=${maxSteps} timeout=${Math.round(timeoutMs / 1000)}s`,
  });

  try {
    await generateText({
      model,
      system: systemPrompt,
      prompt: userMessage,
      tools,
      stopWhen: [hasToolCall(terminatorTool), stepCountIs(maxSteps)],
      maxOutputTokens,
      abortSignal: ac.signal,
    });
  } catch (err) {
    const reason =
      err instanceof Error
        ? timedOut
          ? `timeout after ${timeoutMs}ms`
          : err.message
        : String(err);
    emit({
      type: 'agent_error',
      agent: role,
      parentAgent,
      depth: currentDepth,
      reason,
      recoverable: true,
    });
    if (timedOut) return { status: 'timeout', reason };
    return { status: 'failed', reason };
  } finally {
    clearTimeout(timer);
  }

  const finding = getCapturedFinding();
  if (!finding) {
    const reason =
      `sub-agent did not call terminator '${terminatorTool}' within ` +
      `${maxSteps} steps`;
    emit({
      type: 'agent_error',
      agent: role,
      parentAgent,
      depth: currentDepth,
      reason,
      recoverable: true,
    });
    return { status: 'failed', reason };
  }

  return { status: 'ok', finding };
}

/**
 * Helper for specialists: emit a paired tool_call → tool_result event for an
 * inline (non-LLM) operation that doesn't go through `generateText`. Useful
 * for operations like `compare_visual_language` that the model "calls" but
 * which run as synchronous JS rather than a real sub-LLM step.
 *
 * Specialists don't have to use this — they can emit their own events — but
 * it keeps the SSE noise consistent.
 *
 * Lifted from Brandling `emitInlineToolStep` (line 182 in original
 * `sub-agents.ts`).
 */
export function emitInlineToolStep<TRole extends AgentTraceRole = AgentTraceRole>(args: {
  agent: TRole;
  parentAgent: TRole;
  depth: number;
  tool: string;
  stepIndex: number;
  argsSummary?: string;
  resultSummary?: string;
  onEvent?: AgentEventSink<TRole>;
}): void {
  const {
    agent,
    parentAgent,
    depth,
    tool,
    stepIndex,
    argsSummary,
    resultSummary,
    onEvent,
  } = args;
  if (!onEvent) return;
  onEvent({
    type: 'agent_step',
    agent,
    parentAgent,
    depth,
    action: 'tool_call',
    tool,
    argsSummary,
    stepIndex,
  });
  onEvent({
    type: 'agent_step',
    agent,
    parentAgent,
    depth,
    action: 'tool_result',
    tool,
    resultSummary,
    stepIndex,
  });
}
