/**
 * Typed SSE event taxonomy for agentic systems.
 *
 * One typed union for every event a runner / foreman / sub-agent can emit, plus
 * a single `formatSseEvent` encoder that produces the wire format. The big
 * lesson from Brandling Appendix A item 1: **single-source-of-truth event
 * schema** — eliminate ad-hoc `send(type, payload)` re-encoding scattered
 * across route handlers; one encoder + one typed client-side reducer.
 *
 * Lifted from Brandling `src/lib/agents/events.ts:52`. Hardened changes:
 *   - `AgentTraceRole` is now a generic type parameter so consumers can
 *     extend it without forking the file. Brandling baked role names like
 *     `brand_critic` directly into the union — fine for one app, wrong for
 *     a reusable toolkit.
 *   - `phase` on `phase_change` / `phase_status` is also a generic so HAZOP /
 *     finance / tutorial-gen pipelines can name their phases naturally.
 *   - `formatSseEvent` is unchanged in semantics (`data: {type, payload}\n\n`)
 *     so existing client reducers keep working.
 *
 * Default UI render policy (a hint, not enforcement — UIs decide):
 *   - phase_change / phase_status / mutation_field → visible by default
 *   - agent_step (tool_call / tool_result / reasoning) → inspector drawer
 *   - agent_error → inline + inspector
 */

/**
 * Generic role type. Default is `string` so callers can use literal-typed
 * unions when they want type-narrowed events:
 *
 * ```ts
 * type MyRoles = 'foreman' | 'cfo' | 'auditor' | 'compliance';
 * type MyEvent = AgentSseEvent<MyRoles, MyPhase>;
 * ```
 */
export type AgentTraceRole = string;

/**
 * Generic phase type. Same idea as `AgentTraceRole` — keep it open so HAZOP
 * pipelines can name phases like `'guideword' | 'consequence' | 'lopa'`
 * without forking the toolkit.
 */
export type AgentPhase = string;

/**
 * What the model is doing on a given step. Common to all domains.
 */
export type AgentStepAction =
  | 'tool_call'
  | 'tool_result'
  | 'reasoning'
  | 'finalize';

/**
 * The full event union. All members are flat objects (no nested `payload`)
 * to keep `formatSseEvent` reversible — see the encoder below.
 */
export type AgentSseEvent<
  TRole extends AgentTraceRole = AgentTraceRole,
  TPhase extends AgentPhase = AgentPhase,
> =
  | { type: 'phase_change'; phase: TPhase }
  | { type: 'phase_status'; phase: TPhase; message: string }
  | {
      type: 'agent_step';
      agent: TRole;
      action: AgentStepAction;
      tool?: string;
      argsSummary?: string;
      resultSummary?: string;
      stepIndex?: number;
      /**
       * Nesting depth for hierarchical sub-agents.
       *   - 0 = foreman / top-level (default if absent)
       *   - 1 = persona / critic running its own tool-loop
       *   - 2 = specialist sub-agent spawned by a critic (Brandling's depth-3
       *         pattern: Critic → Specialist)
       *   - 3+ = enforced by the runner; runner refuses to spawn deeper than
       *         its configured `MAX_DEPTH`.
       *
       * Inspector renderers indent rows by `24px * depth`.
       */
      depth?: number;
      /**
       * Role of the agent that spawned this one. Lets the inspector group
       * spawn-trees visually and render `└─` prefixes on nested rows.
       */
      parentAgent?: TRole;
    }
  | {
      type: 'agent_error';
      agent: TRole;
      reason: string;
      /**
       * `true` when the parent agent can fall back / retry; `false` for hard
       * failures that should halt the pipeline. Runners should default to
       * `true` and only emit `false` when the failure invalidates downstream
       * state.
       */
      recoverable: boolean;
      depth?: number;
      parentAgent?: TRole;
    }
  | {
      type: 'mutation_field';
      field: string;
      decision: 'kept' | 'mutated';
      reason: string;
      from?: string;
      to?: string;
    };

/**
 * Format an `AgentSseEvent` into the SSE wire format `data: {type, payload}\n\n`.
 *
 * The wire format separates `type` from `payload` so client reducers have
 * exactly one parsing path: `if (msg.type === 'agent_step') { ...msg.payload }`.
 * Lifted from Brandling `formatSseEvent` (line 107) — semantics unchanged so
 * existing clients keep working.
 *
 * Note: this is the *only* encoder. The Appendix-A lesson is to never
 * hand-roll `send(type, payload)` calls in route handlers — always go
 * through this function.
 */
export function formatSseEvent<
  TRole extends AgentTraceRole = AgentTraceRole,
  TPhase extends AgentPhase = AgentPhase,
>(event: AgentSseEvent<TRole, TPhase>): string {
  const { type, ...payload } = event;
  return `data: ${JSON.stringify({ type, payload })}\n\n`;
}

/**
 * Convenience: an event sink callback. Pass one of these into runners /
 * personas / sub-agents and they'll bubble events up the spawn tree without
 * caring whether the consumer is an SSE controller, a test harness, or
 * stdout.
 */
export type AgentEventSink<
  TRole extends AgentTraceRole = AgentTraceRole,
  TPhase extends AgentPhase = AgentPhase,
> = (event: AgentSseEvent<TRole, TPhase>) => void;
