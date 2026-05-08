/**
 * Generic council debate state machine — a domain-agnostic foreman runner.
 *
 * Distilled from Brandling `src/lib/agents/council-foreman.ts:41`. The
 * Brandling foreman hardcoded marketing-domain personas (Marketing Head /
 * Content Creator / Brand Critic / Engagement Critic / Review Council) into
 * a 7-tool palette. This version generalizes:
 *
 *   - Personas are passed in as a record of `{ name → PersonaCallable }`.
 *   - `mandatoryStartTool` and `mandatoryEndTool` are configurable so HAZOP
 *     can require `call_facilitator` first / `submit_consequences` last;
 *     finance can require `call_cfo` first / `sign_off` last.
 *   - Revision bookkeeping (`maxRevisions`, request_revision tool) is
 *     optional — pipelines without revision loops just don't pass the cap.
 *   - The system prompt is templated from these constraints so the model is
 *     told the same rules the runner enforces (defense-in-depth: prompt +
 *     `stopWhen` agree).
 *
 * ## What this gives you over hand-rolling a foreman
 *
 *   - One `stopWhen` invariant: `hasToolCall(mandatoryEndTool) ||
 *     stepCountIs(maxToolCalls)`. Tested once, reused everywhere.
 *   - Consistent SSE: every tool call emits `agent_step` events with the
 *     foreman's role + step index. The same inspector renders every
 *     domain.
 *   - Failure tolerance: foreman catches its own errors, returns the
 *     best-available state, never throws.
 *
 * ## What you still write per domain
 *
 *   - Persona implementations (`callMarketingHead`, etc.). They're plain
 *     async functions; this runner doesn't care what's inside.
 *   - The `assembleResult` callback that turns captured state into your
 *     domain output type.
 *   - Domain-specific phase names for `phase_change` events (passed in).
 *
 * ## Usage
 *
 * ```ts
 * import { runCouncil } from '@agentic-toolkit/council-state-machine';
 *
 * type MarketingResult = { caption: string; hashtags: string[]; ... };
 *
 * const result = await runCouncil<MarketingResult>({
 *   foremanModel: MODELS.foreman.model,
 *   phase: 'council',
 *   mandatoryStartTool: 'call_marketing_head',
 *   mandatoryEndTool: 'finalize',
 *   maxRevisions: 3,
 *   maxToolCalls: 12,
 *   timeoutMs: 180_000,
 *   personas: {
 *     call_marketing_head: { description: '...', schema: ..., handler: ... },
 *     call_content_creator: { ... },
 *     call_brand_critic: { ... },
 *     call_engagement_critic: { ... },
 *     call_review_council: { ... },
 *   },
 *   userPrompt: 'Brief: launch our new bottle.',
 *   onEvent,
 *   assembleResult: (state) => ({ caption: state.final.caption, ... }),
 * });
 * ```
 */

import {
  generateText,
  hasToolCall,
  stepCountIs,
  tool,
  type LanguageModel,
} from 'ai';
import { z, type ZodTypeAny } from 'zod';
import type {
  AgentEventSink,
  AgentSseEvent,
  AgentTraceRole,
} from './events';

/**
 * One persona definition. The handler is a plain async function — the runner
 * wraps it in an AI SDK `tool` and emits SSE events on either side.
 */
export interface PersonaDefinition<
  TArgs extends Record<string, unknown> = Record<string, unknown>,
  TResult = unknown,
> {
  /** Tool description shown to the foreman model. Write like product copy:
   *  "Invoke X to do Y. Returns Z." Brandling lesson: vague descriptions
   *  cause foreman to skip critical personas. */
  description: string;
  /** Zod schema for the input args. Pass `z.object({}).strict()` if no args. */
  inputSchema: ZodTypeAny;
  /** The persona implementation. Receives parsed args, returns a result. */
  handler: (args: TArgs) => Promise<TResult>;
  /** Optional: short status message emitted as `phase_status` when invoked. */
  statusMessage?: string;
}

export interface CouncilState<TPersonaResults = Record<string, unknown>> {
  /** Per-persona last result. Indexed by tool name. */
  results: TPersonaResults;
  /** Number of revision loops the foreman has requested so far. */
  revisionCount: number;
  /** Whether the foreman called the mandatory end tool. */
  finalized: boolean;
  /** Final captured args passed to the end tool. */
  finalArgs?: Record<string, unknown>;
  /** Monotonic step counter used by SSE for ordering. */
  stepIndex: number;
}

export interface RunCouncilConfig<
  TResult,
  TRole extends AgentTraceRole = AgentTraceRole,
  TPhase extends string = string,
> {
  /** Foreman's role label for SSE events. Defaults to `'foreman'`. */
  foremanRole?: TRole;
  /** Language model that drives the foreman tool-loop. */
  foremanModel: LanguageModel;
  /** Phase name emitted on `phase_change`. */
  phase: TPhase;
  /**
   * Tool the foreman MUST call first. Encoded in both the system prompt
   * (so the model is told) and as informal advice (the AI SDK doesn't have
   * a "must call first" flag, so we rely on the prompt + the model's
   * step-1 attention).
   */
  mandatoryStartTool: string;
  /**
   * Tool the foreman MUST call last. Enforced by `stopWhen:
   * hasToolCall(mandatoryEndTool)` so the loop ends only when this tool
   * fires.
   */
  mandatoryEndTool: string;
  /** Hard cap on revision loops. Default 3 (Brandling's choice). */
  maxRevisions?: number;
  /** Hard cap on total tool calls. Default 12. */
  maxToolCalls?: number;
  /** Wall-clock cap. Default 180_000 (3 min — covers nested loops). */
  timeoutMs?: number;
  /** Output token cap. Default 2048. */
  maxOutputTokens?: number;
  /**
   * Persona palette. Keys are tool names exposed to the foreman; values are
   * the persona definitions. The runner wraps each in a `tool()` and emits
   * SSE events.
   */
  personas: Record<string, PersonaDefinition>;
  /** User-facing prompt content (the brief, the question, the input). */
  userPrompt: string;
  /** Optional system-prompt suffix appended after the runner's constraint
   *  block. Use for domain-specific style notes. */
  systemPromptSuffix?: string;
  /** Bubble-up SSE callback. */
  onEvent?: AgentEventSink<TRole>;
  /**
   * Build the final domain result from accumulated state. Called after the
   * loop ends regardless of whether `finalized` is true — implementations
   * should handle the partial-state fallback case.
   */
  assembleResult: (state: CouncilState) => TResult;
}

const DEFAULT_MAX_REVISIONS = 3;
const DEFAULT_MAX_TOOL_CALLS = 12;
const DEFAULT_TIMEOUT_MS = 180_000;
const DEFAULT_MAX_OUTPUT_TOKENS = 2048;

/**
 * Run a council debate to completion (or until caps fire). Returns whatever
 * `assembleResult` produces. Never throws — caps are enforced via
 * `stopWhen` + `AbortController` and partial state is always assembled.
 */
export async function runCouncil<
  TResult,
  TRole extends AgentTraceRole = AgentTraceRole,
  TPhase extends string = string,
>(config: RunCouncilConfig<TResult, TRole, TPhase>): Promise<TResult> {
  const {
    foremanRole = 'foreman' as TRole,
    foremanModel,
    phase,
    mandatoryStartTool,
    mandatoryEndTool,
    maxRevisions = DEFAULT_MAX_REVISIONS,
    maxToolCalls = DEFAULT_MAX_TOOL_CALLS,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    maxOutputTokens = DEFAULT_MAX_OUTPUT_TOKENS,
    personas,
    userPrompt,
    systemPromptSuffix,
    onEvent,
    assembleResult,
  } = config;

  const emit = (event: AgentSseEvent<TRole>) => {
    if (onEvent) onEvent(event);
  };

  const state: CouncilState = {
    results: {},
    revisionCount: 0,
    finalized: false,
    stepIndex: 0,
  };

  const tickStep = () => {
    state.stepIndex += 1;
    return state.stepIndex;
  };

  emit({ type: 'phase_change', phase });

  // -------------------------------------------------------------------
  // System prompt: encode the constraints the runner ALSO enforces. Both
  // the model and the runtime agree on the same rules. Brandling's
  // foreman prompt is the template (line 41 of council-foreman.ts).
  // -------------------------------------------------------------------
  const personaList = Object.keys(personas);
  const systemPrompt = [
    'You are the Council Foreman. You orchestrate a debate to produce one final output.',
    '',
    'CONSTRAINTS:',
    `- You MUST start by calling \`${mandatoryStartTool}\`.`,
    `- You MUST end by calling \`${mandatoryEndTool}\`.`,
    `- Maximum ${maxRevisions} revision loops, maximum ${maxToolCalls} total tool calls. Stop when \`${mandatoryEndTool}\` is called.`,
    `- Available tools: ${personaList.join(', ')}.`,
    '',
    'WORKFLOW HINTS:',
    '- Invoke critics in any sensible order.',
    '- If a critic flags problems, prefer requesting a revision before finalizing.',
    '- Trust each persona\'s returned score / verdict; do not relitigate it yourself.',
    ...(systemPromptSuffix ? ['', systemPromptSuffix] : []),
  ].join('\n');

  // -------------------------------------------------------------------
  // Wrap each persona in a tool() that emits SSE events around the
  // handler call. The `mandatoryEndTool` is special-cased: when called,
  // we set `finalized = true` and capture its args as `finalArgs`.
  // -------------------------------------------------------------------
  const wrappedTools: Record<string, ReturnType<typeof tool>> = {};

  for (const [name, definition] of Object.entries(personas)) {
    wrappedTools[name] = tool({
      description: definition.description,
      inputSchema: definition.inputSchema,
      execute: async (args: unknown) => {
        const idx = tickStep();
        emit({
          type: 'agent_step',
          agent: foremanRole,
          action: 'tool_call',
          tool: name,
          stepIndex: idx,
        });
        if (definition.statusMessage) {
          emit({
            type: 'phase_status',
            phase,
            message: definition.statusMessage,
          });
        }
        try {
          const result = await definition.handler(
            args as Record<string, unknown>,
          );
          (state.results as Record<string, unknown>)[name] = result;
          // Mandatory end tool — capture and mark finalized so the
          // post-loop assembly knows the foreman finished cleanly.
          if (name === mandatoryEndTool) {
            state.finalized = true;
            state.finalArgs = args as Record<string, unknown>;
          }
          emit({
            type: 'agent_step',
            agent: foremanRole,
            action: name === mandatoryEndTool ? 'finalize' : 'tool_result',
            tool: name,
            stepIndex: idx,
          });
          return result;
        } catch (err) {
          const reason = err instanceof Error ? err.message : String(err);
          emit({
            type: 'agent_error',
            agent: foremanRole,
            reason: `persona ${name} threw: ${reason}`,
            recoverable: true,
          });
          // Return a structured failure so the foreman sees it and
          // doesn't mistake a thrown error for a missing tool call.
          return { status: 'unavailable', reason };
        }
      },
    });
  }

  // -------------------------------------------------------------------
  // Optional: a built-in `request_revision` tool. Every council we've
  // built so far wants this; we expose it but a caller can override by
  // including their own persona named `request_revision`.
  // -------------------------------------------------------------------
  if (!wrappedTools['request_revision']) {
    wrappedTools['request_revision'] = tool({
      description:
        'Signal that the current draft needs another pass. Pass the combined critic reasons. Increments the revision counter; refused once the cap is hit.',
      inputSchema: z
        .object({ reasons: z.array(z.string()).min(1) })
        .strict(),
      execute: async ({ reasons }: { reasons: string[] }) => {
        const idx = tickStep();
        emit({
          type: 'agent_step',
          agent: foremanRole,
          action: 'tool_call',
          tool: 'request_revision',
          argsSummary: `${reasons.length} reason(s)`,
          stepIndex: idx,
        });
        const exhausted = state.revisionCount >= maxRevisions;
        if (!exhausted) state.revisionCount += 1;
        emit({
          type: 'agent_step',
          agent: foremanRole,
          action: 'tool_result',
          tool: 'request_revision',
          resultSummary: exhausted
            ? `revision cap reached (${maxRevisions}); proceed to finalize`
            : `revision queued (count=${state.revisionCount})`,
          stepIndex: idx,
        });
        return {
          ok: !exhausted,
          revisionCount: state.revisionCount,
          revisionCap: maxRevisions,
          reasons,
          guidance: exhausted
            ? `Revision cap reached. Do NOT request more revisions; proceed to ${mandatoryEndTool}.`
            : 'Now invoke the appropriate persona to act on the feedback, then re-score.',
        };
      },
    });
  }

  // -------------------------------------------------------------------
  // Run the foreman loop with the dual stop condition. Wall-clock cap
  // via AbortController. Errors caught — partial state always assembled.
  // -------------------------------------------------------------------
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), timeoutMs);

  try {
    await generateText({
      model: foremanModel,
      system: systemPrompt,
      prompt: userPrompt,
      tools: wrappedTools,
      stopWhen: [hasToolCall(mandatoryEndTool), stepCountIs(maxToolCalls)],
      maxOutputTokens,
      abortSignal: ac.signal,
    });
  } catch (err) {
    const reason =
      err instanceof Error
        ? ac.signal.aborted
          ? `timeout after ${timeoutMs}ms`
          : err.message
        : String(err);
    emit({
      type: 'agent_error',
      agent: foremanRole,
      reason,
      recoverable: true,
    });
    // Fall through — assembleResult handles partial state.
  } finally {
    clearTimeout(timer);
  }

  if (!state.finalized) {
    // Soft warning, not a throw. Brandling lesson: callers always want a
    // structured result even on a partial run.
    emit({
      type: 'agent_error',
      agent: foremanRole,
      reason: `foreman did not call ${mandatoryEndTool} within ${state.stepIndex} steps`,
      recoverable: true,
    });
  }

  return assembleResult(state);
}
