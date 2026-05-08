# agentic-toolkit

Reusable infrastructure for building agentic systems with multi-model
councils, hierarchical sub-agents, and provenance-tracked tool loops.

Lifted from production code (Brandling, 2026 BytePlus Seedance Beta hackathon)
and hardened with the lessons documented in that codebase's "what we'd change"
appendix — depth caps enforced at the runner level, provenance required at
the type level, per-model knobs lifted into the registry, secretarial
summaries to combat context explosion in nested spawn trees.

This is a **reference TypeScript package**, not a tested library. The point is
to save a week of plumbing per new agentic project (groot-finance, yf-hazop,
tutorial-gen, …) by shipping the five things every Brandling-style system
ends up re-implementing.

## What's in here

```
agentic-toolkit/
├── .claude-plugin/
│   └── plugin.json
└── src/
    ├── gateway.ts               # multi-model gateway adapter
    ├── models-registry.ts       # per-role model registry with knobs
    ├── sub-agent-runner.ts      # depth + spawn + timeout enforced runner
    ├── events.ts                # typed AgentSseEvent + formatSseEvent
    ├── provenance.ts            # required _source tag + helpers
    └── council-state-machine.ts # generic foreman with mandatory start/end
```

### The five components

**1. Gateway adapter (`gateway.ts`).** A thin `createGateway({ baseURL,
apiKey, name? })` wrapper around `@ai-sdk/openai-compatible`. Keep one
provider for Claude / GPT / Gemini behind a unified endpoint (TokenRouter,
OpenRouter, LiteLLM, Vercel AI Gateway). The registry is the single seam
where "Opus is suddenly expensive" turns into a 1-character edit.

**2. Models registry (`models-registry.ts`).** A typed `ModelsRegistry`
binding role names to `{ model, knobs }` entries. Per-model knobs (e.g.
`noToolChoiceRequired: true` for GPT-class models that infinite-loop on
`toolChoice: 'required'`) live in the registry, not at every call site.
Ships with `defaultBrandlingRegistry` showing the 8-role marketing council
as a starting template.

**3. Sub-agent runner (`sub-agent-runner.ts`).** `runSubAgent` with depth
cap, per-parent spawn cap, wall-clock timeout, and a typed
`SubAgentResult` (`'ok' | 'failed' | 'depth_exceeded' | 'timeout'`). Ported
from Brandling's `runSubAgent` and hardened: Brandling tracked depth in
events only; this runner *refuses* to spawn beyond `maxDepth` so prompt
regressions can't blow past the limit.

**4. Events (`events.ts`).** The full `AgentSseEvent` typed union
(`phase_change`, `phase_status`, `agent_step` with depth + parentAgent,
`agent_error`, `mutation_field`) plus `formatSseEvent`. `AgentTraceRole`
and `AgentPhase` are generic so HAZOP / finance / tutorial-gen pipelines
can name their roles and phases without forking the file.

**5. Provenance (`provenance.ts`).** `GenerationSource` (`'live' | 'cached'
| 'partial' | 'demo' | 'user'`), `Provenanced<T>` wrapper, and
`assertProvenance` runtime guard. `_source` is **required** at the type
level — Brandling shipped it optional and got bitten by demo data
masquerading as live output downstream.

### The council state machine

**6. Council state machine (`council-state-machine.ts`).** A generic foreman
runner. Pass a persona palette, a `mandatoryStartTool`, a `mandatoryEndTool`,
revision/step caps, and an `assembleResult` callback; the runner handles the
tool-loop, SSE events, revision bookkeeping, partial-state fallback, and the
shared `stopWhen: [hasToolCall(end), stepCountIs(cap)]` invariant. Distilled
from Brandling's marketing-domain `runDebateAgentic` (council-foreman.ts:41).

## Hello world

```ts
import { createGateway } from './gateway';
import { defineRegistry } from './models-registry';
import { runCouncil } from './council-state-machine';
import { withProvenance, type Provenanced } from './provenance';
import type { AgentSseEvent } from './events';
import { z } from 'zod';

// 1. Wire the gateway once.
const gateway = createGateway({
  baseURL: process.env.GATEWAY_BASE_URL!,
  apiKey: process.env.GATEWAY_API_KEY!,
});

// 2. Register the roles.
const MODELS = defineRegistry({
  foreman: { model: gateway('anthropic/claude-opus-4.7') },
  cfo: { model: gateway('anthropic/claude-sonnet-4.6') },
  auditor: {
    model: gateway('openai/gpt-5.5'),
    knobs: { noToolChoiceRequired: true },
  },
});

// 3. Two-persona council. Each persona is a plain async function.
type Decision = { recommendation: string; rationale: string };

const result: Provenanced<Decision> = await runCouncil<Provenanced<Decision>>({
  foremanModel: MODELS.foreman.model,
  phase: 'review',
  mandatoryStartTool: 'call_cfo',
  mandatoryEndTool: 'finalize',
  personas: {
    call_cfo: {
      description: 'Invoke the CFO to weigh the financial impact. Returns { weight: number, notes: string }.',
      inputSchema: z.object({}).strict(),
      handler: async () => ({ weight: 8, notes: 'aligns with Q3 plan' }),
    },
    call_auditor: {
      description: 'Invoke the Auditor to flag SoD / IFRS issues. Returns { violations: string[] }.',
      inputSchema: z.object({ proposal: z.string() }).strict(),
      handler: async () => ({ violations: [] }),
    },
    finalize: {
      description: 'Emit the final recommendation. Args become the result.',
      inputSchema: z
        .object({ recommendation: z.string(), rationale: z.string() })
        .strict(),
      handler: async (args) => args,
    },
  },
  userPrompt: 'Should we approve the Q3 capex proposal?',
  onEvent: (e: AgentSseEvent) => console.log(e.type),
  assembleResult: (state) =>
    withProvenance(
      (state.finalArgs as Decision) ?? {
        recommendation: 'defer',
        rationale: 'partial run',
      },
      state.finalized ? 'live' : 'partial',
    ),
});
```

## Design constraints (read these before extending)

These are lifted from Brandling Appendix A. They override convenience.

1. **Hard depth caps at the runner.** The runner refuses spawns at
   `currentDepth >= maxDepth` regardless of what the model asks for. Defense
   in depth: a buggy critic prompt should never be able to spawn at depth 5
   because we relied on prompt obedience. Default `maxDepth: 3`. Default
   `maxSpawns: 2` per parent.

2. **Provenance required, not optional.** `Provenanced<T>` requires
   `_source` at the type level. Brandling shipped `_source?: GenerationSource`
   and got bitten when demo output reached downstream UI without a
   "this is fake" tag. Fail at the boundary, not in the user's face.

3. **Per-model knobs in the registry.** GPT-5.5 infinite-loops on
   `toolChoice: 'required'`. Gemini rejects loose schemas. Cheap models
   truncate silently. These are model-family facts, not call-site facts —
   encode once in `ModelKnobs` and have runners read them. Brandling
   re-asserted "no toolChoice required" as a comment at every callsite;
   that's the smell the registry fixes.

4. **Secretarial summaries to combat context explosion.** When a sub-agent
   returns to its parent, pass a *summary* of the finding into the parent's
   next turn, not the full transcript. Sub-agents in the runner already
   isolate their context; the discipline on the parent side is to keep
   passing summaries, not raw histories. The toolkit doesn't enforce this
   (it's a structuring choice) but the design doc § 2.12 ("Context
   explosion" mitigation) makes it non-negotiable for production.

## Conceptual companions

This plugin is the *infrastructure* layer. The two skills it pairs with
walk users through the *design* layer:

- `/home/fei/fei/code/ccc/skills/agentic-system-design/SKILL.md` —
  prescriptive Q&A for shaping a council, picking from 7 SOTA patterns,
  deciding sub-agent depth, hardening the tool loop. Use this when starting
  a new agentic project.
- `/home/fei/fei/code/ccc/skills/self-improving-systems/SKILL.md` —
  prescriptive Q&A for adding memory, feedback loops, and closed-loop
  learning *only when justified*. Filters out the ~70% of "we need memory"
  requests that are actually state caches.

The skills point at this plugin: "use `@agentic-toolkit/sub-agent-runner`
instead of writing your own."

## Source / lineage

The canonical implementations are in Brandling at:

- `src/lib/agents/provider.ts` — TokenRouter `createOpenAICompatible`
- `src/lib/agents/models.ts` — `MODELS` registry (8 roles)
- `src/lib/agents/sub-agents.ts` — `runSubAgent` (~214 LOC)
- `src/lib/agents/events.ts` — `AgentSseEvent` + `formatSseEvent`
- `src/lib/agents/council-foreman.ts` — Foreman + 7-tool palette
- `src/lib/types.ts` — `GenerationSource`

Differences from Brandling are documented inline in each file's JSDoc, with
line numbers cited where the original is excerpted verbatim.
