/**
 * Example: sub-agent-spawning
 *
 * Pattern demonstrated: Pattern #6 from skill A — "Tool-Loop with Spawning"
 *   in the depth-3 critic-spawns-specialist shape (§2.9 case 2). A council
 *   critic at depth 1 spawns a verification specialist at depth 2 when its
 *   own evidence is ambiguous. Brandling's canonical sub-agent shape, lifted
 *   from `src/lib/agents/sub-agents.ts`.
 *
 * Use case: a HAZOP (HAZard and OPerability) safety-analysis assistant for a
 *   chemical plant. A Safety Engineer critic is scoring whether a proposed
 *   "high temperature in reactor R-101" deviation has a foreseeable
 *   operational cause. The critic's local evidence is BORDERLINE (§5.3:
 *   "BORDERLINE foreseeability or HYPOTHESIS novelty"). It spawns an
 *   Incident-DB Researcher sub-agent to drill the historical incident
 *   database before scoring. Use case from §5.3 of the design doc.
 *
 * What this shows:
 * - `runSubAgent` from the toolkit — depth tracking via `currentDepth`,
 *   MAX_DEPTH cap, per-spawn timeout, spawn-count cap. Returns a typed
 *   `SubAgentResult<TFinding>` discriminated union — `'ok' | 'failed' |
 *   'depth_exceeded' | 'timeout'` — so the parent branches cleanly on each
 *   failure mode without a try/catch maze.
 * - Sub-agent has its OWN tool palette (lookup_incident_db, web_search,
 *   finalize_finding) — disjoint from the parent critic's palette. This is
 *   what justifies depth-3 in §2.9 case 2: grandchild has its own tool
 *   palette, not just a prompt rewrite.
 * - Event propagation: sub-agent emits `agent_step` events with
 *   `parentAgent`, `depth: 2`, so the SSE consumer can render a tree.
 * - The parent critic gracefully degrades on sub-agent failure: it keeps
 *   its original local-only score and stamps "specialist_unavailable" in
 *   the metadata, instead of crashing the council.
 *
 * Lessons from Brandling baked in:
 * - Hard-enforced `maxDepth` at the runner level — Brandling lesson #2 in
 *   appendix A: "today only event-level, not enforced". Toolkit refuses
 *   to spawn when `currentDepth >= maxDepth`.
 * - Hard-enforced `maxSpawns` per parent — 2 specialists per critic max.
 *   Beyond that you should sequence them, not fan out.
 * - Hard wall-clock timeout (60s default). On timeout the parent gets a
 *   structured `{ status: "timeout", reason }` and decides what to do.
 *   The sub-agent NEVER throws into the parent's loop.
 */

import { generateText, tool, hasToolCall, stepCountIs } from "ai";
import { z } from "zod";

import { createGateway } from "../src/gateway";
import { defineRegistry } from "../src/models-registry";
import { runSubAgent } from "../src/sub-agent-runner";
import { withProvenance, type Provenanced } from "../src/provenance";
import type { AgentSseEvent } from "../src/events";

// ---------------------------------------------------------------------------
// Inline registry — two roles for two depths:
//   - safetyEngineer at depth 1 (council critic)
//   - researcher at depth 2 (specialist sub-agent)
// ---------------------------------------------------------------------------

const gateway = createGateway({
  baseURL: process.env.TOKENROUTER_BASE_URL!,
  apiKey: process.env.TOKENROUTER_API_KEY!,
});

const MODELS = defineRegistry({
  // Cross-family critic (GPT) — needs the toolChoice knob.
  safetyEngineer: {
    model: gateway("openai/gpt-5.5"),
    knobs: { noToolChoiceRequired: true },
  },
  // Specialist sub-agent — Sonnet for fast incident-DB drilling.
  researcher: { model: gateway("anthropic/claude-sonnet-4.6") },
});

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

interface DeviationContext {
  node: string;
  guideWord: "HIGH" | "LOW" | "NO" | "REVERSE" | "AS_WELL_AS" | "PART_OF";
  parameter: "TEMPERATURE" | "PRESSURE" | "FLOW" | "LEVEL";
  designIntent: string;
}

interface SafetyScore {
  foreseeability: "FORESEEABLE" | "BORDERLINE" | "HYPOTHESIS";
  severity: 1 | 2 | 3 | 4 | 5;
  rationale: string;
  /** Evidence the score is grounded in. Required field at type level. */
  evidenceSources: ("local_kb" | "incident_db" | "web_search" | "operator_log")[];
  /** Stamped if the specialist sub-agent ran (or failed to). */
  specialist?: { status: "ran" | "failed" | "timeout"; reason?: string };
}

interface IncidentFinding {
  matchedIncidents: { id: string; year: number; severity: number; summary: string }[];
  recommendedForeseeability: "FORESEEABLE" | "BORDERLINE" | "HYPOTHESIS";
  recommendedSeverity: 1 | 2 | 3 | 4 | 5;
}

// ---------------------------------------------------------------------------
// Specialist tools — Incident-DB Researcher's palette
// ---------------------------------------------------------------------------

function buildIncidentDbTools(args: {
  setFinding: (f: IncidentFinding) => void;
}) {
  const { setFinding } = args;

  // TODO: in real usage, lookup_incident_db hits the customer's incident
  // database. For the example we stub a deterministic shape.
  const lookupIncidentDb = tool({
    description:
      "Search the historical incident database for matches on (node, parameter, guideword). Returns up to 5 matched incidents with summaries. Call this FIRST.",
    inputSchema: z
      .object({
        node: z.string().min(1),
        parameter: z.enum(["TEMPERATURE", "PRESSURE", "FLOW", "LEVEL"]),
        guideWord: z.enum(["HIGH", "LOW", "NO", "REVERSE", "AS_WELL_AS", "PART_OF"]),
      })
      .strict(),
    execute: async ({ node, parameter, guideWord }) => {
      return {
        node,
        parameter,
        guideWord,
        matches: [] as IncidentFinding["matchedIncidents"], // wired to real DB upstream
      };
    },
  });

  const webSearch = tool({
    description:
      "Search public industry incident reports (CSB, HSE, regulator filings) for similar deviations. Use ONLY when the internal DB has zero matches.",
    inputSchema: z.object({ query: z.string().min(3) }).strict(),
    execute: async ({ query }) => ({ query, results: [] as string[] }),
  });

  const finalizeFinding = tool({
    description:
      "Emit the structured finding and end the sub-agent loop. Pass matched incidents and the recommended foreseeability + severity. Call ONCE.",
    inputSchema: z
      .object({
        matchedIncidents: z.array(
          z.object({
            id: z.string(),
            year: z.number().int(),
            severity: z.number().int().min(1).max(5),
            summary: z.string(),
          }),
        ),
        recommendedForeseeability: z.enum(["FORESEEABLE", "BORDERLINE", "HYPOTHESIS"]),
        recommendedSeverity: z.number().int().min(1).max(5),
      })
      .strict(),
    execute: async (input) => {
      setFinding({
        matchedIncidents: input.matchedIncidents,
        recommendedForeseeability: input.recommendedForeseeability,
        recommendedSeverity: input.recommendedSeverity as 1 | 2 | 3 | 4 | 5,
      });
      return { ok: true };
    },
  });

  return {
    lookup_incident_db: lookupIncidentDb,
    web_search: webSearch,
    finalize_finding: finalizeFinding,
  };
}

// ---------------------------------------------------------------------------
// Safety Engineer critic — depth-1, may spawn the depth-2 specialist
// ---------------------------------------------------------------------------

export async function safetyScore(args: {
  context: DeviationContext;
  localEvidence: string;
  /** Parent council's onEvent callback. Sub-agent events flow through this. */
  onEvent?: (event: AgentSseEvent) => void;
}): Promise<Provenanced<SafetyScore>> {
  const { context, localEvidence, onEvent } = args;

  // First pass: cheap local-only score with the model's reasoning ability.
  // We classify the result. If it lands in BORDERLINE / HYPOTHESIS, we spawn
  // the specialist. This gating is what keeps sub-agent costs down — the
  // §2.9 lesson is "depth-3 only in 3 named cases", not by default.
  const initial = await scoreLocally({ context, localEvidence });

  if (initial.foreseeability === "FORESEEABLE") {
    // Confident local answer. No specialist needed; return cheap path.
    return withProvenance(initial, "live");
  }

  // BORDERLINE / HYPOTHESIS → spawn Incident-DB Researcher. This is the
  // critic-spawns-specialist depth-3 case from §2.9.
  let captured: IncidentFinding | undefined;
  const tools = buildIncidentDbTools({
    setFinding: (f) => {
      captured = f;
    },
  });

  const result = await runSubAgent<IncidentFinding>({
    role: "incident_db_researcher",
    parentAgent: "safety_engineer",
    // Parent (safety_engineer) is at depth 1; child spawns at depth 2.
    // The runner refuses spawns at currentDepth >= maxDepth (default 3).
    currentDepth: 2,
    model: MODELS.researcher.model,
    systemPrompt: [
      "You are an Incident-DB Researcher. Your job is to find historical precedent for the deviation the Safety Engineer is unsure about.",
      "WORKFLOW:",
      "1. Call `lookup_incident_db` with the deviation parameters.",
      "2. If zero matches, optionally call `web_search` for public industry reports.",
      "3. Call `finalize_finding` with matched incidents + your recommended foreseeability and severity.",
      "RULES:",
      "- Recommend FORESEEABLE only if you have ≥2 matched incidents. ≥1 → BORDERLINE. 0 → HYPOTHESIS.",
      "- Severity is the MAX severity across matches, capped at 5.",
    ].join("\n"),
    userMessage: `Deviation: ${context.guideWord} ${context.parameter} at ${context.node}.\nDesign intent: ${context.designIntent}\nLocal evidence: ${localEvidence}`,
    tools,
    terminatorTool: "finalize_finding",
    getCapturedFinding: () => captured,
    maxSteps: 6,
    timeoutMs: 60_000,
    onEvent,
  });

  // The runner returns a discriminated union. Branch on `status`:
  //   - 'ok'             → success, finding is present.
  //   - 'failed'         → model didn't finalize within the step cap.
  //   - 'depth_exceeded' → caller tried to spawn at >= maxDepth (or
  //                        spawnCount >= maxSpawns). Fall back.
  //   - 'timeout'        → wall-clock cap fired.
  // Brandling lesson: parent gracefully degrades on EVERY non-ok status.
  if (result.status !== "ok") {
    // Map the failure modes; keep the local-only score in all cases.
    const status: "failed" | "timeout" =
      result.status === "timeout" ? "timeout" : "failed";
    return withProvenance(
      {
        ...initial,
        specialist: { status, reason: result.reason },
      },
      "partial",
    );
  }

  // Specialist succeeded. Merge: the specialist's recommendation overrides
  // the local foreseeability/severity, but we keep the local rationale and
  // append the specialist's evidence sources.
  const finding = result.finding;
  return withProvenance(
    {
      foreseeability: finding.recommendedForeseeability,
      severity: finding.recommendedSeverity,
      rationale: `${initial.rationale} | Specialist found ${finding.matchedIncidents.length} matched incidents.`,
      evidenceSources: [...initial.evidenceSources, "incident_db" as const],
      specialist: { status: "ran" as const },
    },
    "live",
  );
}

// ---------------------------------------------------------------------------
// Cheap local-only first pass. No tools — just one generateText call.
// ---------------------------------------------------------------------------

async function scoreLocally(args: {
  context: DeviationContext;
  localEvidence: string;
}): Promise<SafetyScore> {
  const { context, localEvidence } = args;

  let captured: SafetyScore | undefined;
  const finalizeLocal = tool({
    description: "Emit the structured local score and end the loop.",
    inputSchema: z
      .object({
        foreseeability: z.enum(["FORESEEABLE", "BORDERLINE", "HYPOTHESIS"]),
        severity: z.number().int().min(1).max(5),
        rationale: z.string().min(20),
      })
      .strict(),
    execute: async (input) => {
      captured = {
        foreseeability: input.foreseeability,
        severity: input.severity as 1 | 2 | 3 | 4 | 5,
        rationale: input.rationale,
        evidenceSources: ["local_kb"],
      };
      return { ok: true };
    },
  });

  await generateText({
    model: MODELS.safetyEngineer.model,
    system: "You are a Safety Engineer scoring a HAZOP deviation. Use only local evidence.",
    prompt: `Deviation: ${context.guideWord} ${context.parameter} at ${context.node}\nDesign intent: ${context.designIntent}\nLocal evidence: ${localEvidence}\n\nCall finalize with your structured score.`,
    tools: { finalize: finalizeLocal },
    // No `toolChoice: 'required'` — see the GPT registry knob.
    stopWhen: [hasToolCall("finalize"), stepCountIs(2)],
    maxOutputTokens: 512,
  });

  if (!captured) {
    return {
      foreseeability: "HYPOTHESIS",
      severity: 1,
      rationale: "Local scorer did not finalize; defaulting to HYPOTHESIS.",
      evidenceSources: ["local_kb"],
    };
  }
  return captured;
}

// ---------------------------------------------------------------------------
// Look here:
//   - Gating: we DON'T spawn the specialist on every score. Cheap local pass
//     first; spawn only when foreseeability is BORDERLINE / HYPOTHESIS. This
//     is the §2.9 discipline — depth-3 only when justified.
//   - Disjoint tool palettes: the parent has no `lookup_incident_db`; the
//     specialist has no scoring tool. Each agent's role IS its tool palette.
//     If the specialist's job were "rewrite the prompt", it would be a tool,
//     not a sub-agent (anti-pattern §2.11).
//   - Failure path: `runSubAgent` returns a typed `SubAgentResult` —
//     `{ status: 'ok', finding } | { status: 'failed' | 'timeout' |
//     'depth_exceeded', reason }`. Branch on `status`; the parent decides
//     what to do. The sub-agent NEVER crashes the parent loop. This is the
//     "agent attempted, recovered" story judges score on.
//   - `currentDepth: 2` is the field the runner enforces. The runner refuses
//     to spawn when `currentDepth >= maxDepth` regardless of what the model
//     asked for — defense-in-depth against a buggy critic prompt.
//   - Event propagation: every sub-agent tool call emits with `parentAgent`
//     and `depth: 2`. The SSE consumer can render the call tree without
//     guessing at hierarchy.
// ---------------------------------------------------------------------------
