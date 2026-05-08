/**
 * Example: full-mutation-pipeline
 *
 * Pattern demonstrated: the full Brandling-style flow end-to-end —
 *   research → DNA extraction → council debate → mutation → rerun. This is
 *   the canonical case study from §5.1 of the design doc. Combines Pattern
 *   #1 (Tool-Loop), Council shape #3 (Foreman-Worker), Pattern #6 (Spawning),
 *   AND the per-field DNA evolution loop.
 *
 * Use case: a marketing copywriter for a small DTC brand. The agency owns a
 *   Brand DNA (audience, tone, visualWorld, taboo, goals). A user asks for a
 *   new Instagram caption with a directional hint ("more playful, less
 *   corporate"). The pipeline:
 *
 *     1. Research the brand (cache-first; live web_search on miss).
 *     2. Extract / refresh the Brand DNA from the research brief.
 *     3. Run a 5-persona Foreman council on the user's prompt + DNA →
 *        produces caption + hashtags + CTA + posting time.
 *     4. Mutation Engine evolves the DNA per-field along the user's hint.
 *     5. Rerun the council with the mutated DNA → produces a second caption
 *        showing the directional shift.
 *
 *   The user can A/B the two outputs and pick. Mutated DNA is the next run's
 *   default. NB: this is NOT learning yet — see the lesson at the bottom.
 *
 * What this shows:
 * - `Provenanced<T>` at every stage. Research is `_source: "cached"` (note:
 *   the canonical taxonomy uses "cached", not "cache") or "live"; DNA carries
 *   the same stamp; the caption inherits from its DNA; the mutated DNA is
 *   `_source: "live"` (model-evolved); the second caption inherits from the
 *   mutated DNA. The full audit chain.
 * - The mutation engine evolves DNA field-by-field with `read_dna_snapshot`
 *   → `mutate_field` (n times) → `keep_field` (n times) → `finalize`. Each
 *   field carries its own reasoning. Brandling pattern from §5.1 +
 *   `mutation-engine.ts`.
 * - The same council pipeline reruns with no code changes — only the DNA
 *   input differs. This is what makes the rerun "free" architecturally.
 *
 * Lessons from Brandling baked in (Appendix A of the design doc):
 * - Provenance required at type level: every output has `_source`.
 * - Continuity anchor sourced from DNA, not regex on visualWorld.
 * - Dirty-set computation for mutation reruns: only re-run stages whose
 *   inputs depend on mutated fields. (Stub here; toolkit owns the real
 *   dependency graph.)
 *
 * THE BIG LESSON (§5.1): The Mutation Engine is a STATE CACHE, not real
 * learning. To close the loop you need an external feedback signal —
 * engagement metrics, brand-fidelity LLM-judge, A/B win-rate — that
 * causally informs WHICH direction to mutate next. Without that signal, you
 * are evolving DNA based on the user's vibes, not on what works. This is
 * Skill B's territory; this example shows the shape of the cache, not the
 * shape of the learning loop.
 */

import { z } from "zod";
import { generateText, tool, hasToolCall, stepCountIs } from "ai";

import { createGateway } from "../src/gateway";
import { defineRegistry } from "../src/models-registry";
import { runCouncil, type PersonaDefinition } from "../src/council-state-machine";
import { runSubAgent } from "../src/sub-agent-runner";
import { withProvenance, type Provenanced } from "../src/provenance";
import type { AgentSseEvent } from "../src/events";

// ---------------------------------------------------------------------------
// Inline registry — every role this end-to-end pipeline needs. Composing the
// full set in one place makes it obvious how the cost profile lands.
// ---------------------------------------------------------------------------

const gateway = createGateway({
  baseURL: process.env.TOKENROUTER_BASE_URL!,
  apiKey: process.env.TOKENROUTER_API_KEY!,
});

const MODELS = defineRegistry({
  // Foreman + Review Council — Opus for orchestration / final judgement.
  foreman: { model: gateway("anthropic/claude-opus-4.7") },
  // Drafters: Marketing Head + Content Creator — Sonnet for fast structured drafts.
  drafter: { model: gateway("anthropic/claude-sonnet-4.6") },
  // Brand Critic — cross-family OpenAI for self-preference mitigation.
  brandCritic: {
    model: gateway("openai/gpt-5.5"),
    knobs: { noToolChoiceRequired: true },
  },
  // Engagement Critic — Gemini Flash for hook-strength scoring.
  engagementCritic: {
    model: gateway("google/gemini-3-flash-preview"),
    knobs: { strictSchemaOnly: true },
  },
  // Researcher — Sonnet for cheap web-search drilling.
  researcher: { model: gateway("anthropic/claude-sonnet-4.6") },
  // DNA synthesizer — Sonnet again; structured output, no nuance ceiling.
  synthesizer: { model: gateway("anthropic/claude-sonnet-4.6") },
  // Mutation Engine — Opus + higher token cap because rationales are long.
  mutationEngine: {
    model: gateway("anthropic/claude-opus-4.7"),
    knobs: { defaultMaxOutputTokens: 4096 },
  },
});

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

export interface BrandDNA {
  audience: string;
  tone: string;
  visualWorld: string;
  taboo: string;
  goals: string;
}

interface ResearchBrief {
  brandSummary: string;
  topPosts: { caption: string; engagement: number }[];
  recentNews: string[];
}

interface CaptionOutput {
  caption: string;
  hashtags: string[];
  cta: string;
  bestPostingTime: string;
}

interface MutationResult {
  evolvedDNA: BrandDNA;
  changedFields: (keyof BrandDNA)[];
  reasoningPerField: Record<keyof BrandDNA, string>;
}

interface PipelineResult {
  before: { dna: Provenanced<BrandDNA>; caption: Provenanced<CaptionOutput> };
  after: { dna: Provenanced<BrandDNA>; caption: Provenanced<CaptionOutput> };
  mutationLog: MutationResult;
}

// ---------------------------------------------------------------------------
// Stage 1 — Research (cache-first, live fallback)
// ---------------------------------------------------------------------------

async function researchBrand(args: {
  brandHandle: string;
  onEvent?: (e: AgentSseEvent) => void;
}): Promise<Provenanced<ResearchBrief>> {
  const { brandHandle, onEvent } = args;

  // TODO: real cache backend. Returning live shape for the example.
  const cached = await tryReadCache(brandHandle);
  // Note: canonical provenance is "cached" (not "cache"). See provenance.ts.
  if (cached) return withProvenance(cached, "cached");

  // Cache miss → live research sub-agent (depth-1 child of the pipeline root).
  let captured: ResearchBrief | undefined;
  const finalizeBrief = tool({
    description: "Emit the brand research brief and end. Call after at least one web_search.",
    inputSchema: z
      .object({
        brandSummary: z.string().min(40),
        topPosts: z.array(
          z.object({ caption: z.string(), engagement: z.number().int().min(0) }),
        ),
        recentNews: z.array(z.string()),
      })
      .strict(),
    execute: async (input) => {
      captured = input;
      return { ok: true };
    },
  });

  const webSearch = tool({
    description: "Search the public web for the brand's recent posts, news, and reviews.",
    inputSchema: z.object({ query: z.string().min(3) }).strict(),
    execute: async ({ query }) => ({ query, results: [] as string[] }),
  });

  const result = await runSubAgent<ResearchBrief>({
    role: "researcher",
    parentAgent: "pipeline_root",
    // Pipeline root is conceptually depth 0; research runs at depth 1.
    currentDepth: 1,
    model: MODELS.researcher.model,
    systemPrompt:
      "You are a brand researcher. Use web_search to gather the brand's positioning, top posts, and recent news. Then call finalize_brief.",
    userMessage: `Brand handle: ${brandHandle}`,
    tools: { web_search: webSearch, finalize_brief: finalizeBrief },
    terminatorTool: "finalize_brief",
    getCapturedFinding: () => captured,
    maxSteps: 8,
    timeoutMs: 90_000,
    onEvent,
  });

  if (result.status !== "ok") {
    // Brandling lesson: callers always want a structured result even when a
    // sub-agent failed. We DO surface a hard error here only because the
    // downstream stages literally have no input without a brief — there is
    // no graceful degradation path. In your own pipeline, prefer a fallback
    // brief over an exception.
    throw new Error(
      `Researcher failed for ${brandHandle}: ${result.status} (${result.reason})`,
    );
  }
  return withProvenance(result.finding, "live");
}

async function tryReadCache(_handle: string): Promise<ResearchBrief | undefined> {
  return undefined; // TODO: wire to KV / Redis / file cache
}

// ---------------------------------------------------------------------------
// Stage 2 — DNA extraction (single-shot tool loop)
// ---------------------------------------------------------------------------

async function extractDNA(args: {
  brief: ResearchBrief;
  onEvent?: (e: AgentSseEvent) => void;
}): Promise<Provenanced<BrandDNA>> {
  let captured: BrandDNA | undefined;
  const finalizeDna = tool({
    description: "Emit the structured Brand DNA. Call ONCE after reading the brief.",
    inputSchema: z
      .object({
        audience: z.string().min(10),
        tone: z.string().min(10),
        visualWorld: z.string().min(10),
        taboo: z.string().min(5),
        goals: z.string().min(10),
      })
      .strict(),
    execute: async (input) => {
      captured = input;
      return { ok: true };
    },
  });

  await generateText({
    model: MODELS.synthesizer.model,
    system: [
      "You are a brand strategist. Extract a 5-field Brand DNA from the research brief.",
      "RULES:",
      "- audience: who the brand is FOR, in one sentence.",
      "- tone: voice and register, in one sentence with 2-3 adjectives.",
      "- visualWorld: shooting style, palette, props — one sentence.",
      "- taboo: words / claims / aesthetics the brand never uses.",
      "- goals: what THIS brand's content is trying to drive.",
      "- voice-neutral physical detail in visualWorld (per the extraction-layer rule).",
    ].join("\n"),
    prompt: `Brief:\n${args.brief.brandSummary}\n\nTop posts:\n${args.brief.topPosts.map((p) => `- ${p.caption} (${p.engagement})`).join("\n")}`,
    tools: { finalize_dna: finalizeDna },
    stopWhen: [hasToolCall("finalize_dna"), stepCountIs(3)],
    maxOutputTokens: 1024,
  });

  if (!captured) throw new Error("DNA extractor did not finalize");
  return withProvenance(captured, "live");
}

// ---------------------------------------------------------------------------
// Stage 3 — Council debate (Foreman + 5 personas via runCouncil)
//
// Persona handlers are stubbed inline so this file stands alone. In a real
// pipeline they would each be the leaf-agent shape from
// `foreman-with-3-personas.ts` (one generateText call with a tight system
// prompt). What matters here is the COUNCIL SHAPE, not persona internals.
// ---------------------------------------------------------------------------

interface CaptionDraft {
  caption: string;
  hashtags: string[];
  cta: string;
  bestPostingTime: string;
}

async function runCaptionCouncil(args: {
  prompt: string;
  dna: BrandDNA;
  brief: ResearchBrief;
  dnaSource: Provenanced<BrandDNA>["_source"];
  onEvent?: (e: AgentSseEvent) => void;
}): Promise<Provenanced<CaptionOutput>> {
  // Closure-captured "current draft" so critics can score the latest.
  let draft: CaptionDraft | undefined;

  const personas: Record<string, PersonaDefinition> = {
    call_marketing_head: {
      description:
        "Strategy persona. Returns the angle and audience hook. Call FIRST so downstream personas have a brief.",
      inputSchema: z.object({}).strict(),
      handler: async () => ({
        angle: "playful authenticity",
        audienceHook: args.dna.audience,
      }),
      statusMessage: "Marketing Head sets the angle...",
    },
    call_content_creator: {
      description:
        "Drafts the caption + hashtags + CTA + posting time given the angle and DNA.",
      inputSchema: z.object({ angle: z.string() }).strict(),
      handler: async () => {
        // TODO: real draft via generateText. Stubbed shape for the example.
        draft = {
          caption: `Drafted under tone "${args.dna.tone}" for ${args.dna.audience}.`,
          hashtags: ["#draft", "#brand"],
          cta: "Tap to learn more.",
          bestPostingTime: "Tue 7pm",
        };
        return draft;
      },
      statusMessage: "Drafting caption...",
    },
    call_brand_critic: {
      description:
        "Scores the current draft on brand fidelity (1-10). Score ≤5 → request_revision.",
      inputSchema: z.object({}).strict(),
      handler: async () => ({ score: 7, feedback: "tone is on-brand" }),
      statusMessage: "Brand Critic scoring...",
    },
    call_engagement_critic: {
      description:
        "Scores the current draft on hook strength (1-10). Score ≤5 → request_revision.",
      inputSchema: z.object({}).strict(),
      handler: async () => ({ score: 8, feedback: "strong hook" }),
      statusMessage: "Engagement Critic scoring...",
    },
    call_review_council: {
      description:
        "Final review pass: confirms both critic scores cleared the bar before finalize.",
      inputSchema: z.object({}).strict(),
      handler: async () => ({ approved: true }),
      statusMessage: "Review Council confirming...",
    },
    finalize: {
      description: "Emit the final caption package. Args become the result.",
      inputSchema: z
        .object({
          caption: z.string(),
          hashtags: z.array(z.string()),
          cta: z.string(),
          bestPostingTime: z.string(),
        })
        .strict(),
      handler: async (a) => a as unknown as CaptionDraft,
    },
  };

  return runCouncil<Provenanced<CaptionOutput>>({
    foremanModel: MODELS.foreman.model,
    phase: "caption_council",
    mandatoryStartTool: "call_marketing_head",
    mandatoryEndTool: "finalize",
    maxRevisions: 3,
    maxToolCalls: 12,
    timeoutMs: 180_000,
    personas,
    userPrompt: `Prompt: ${args.prompt}\nBrand DNA: ${JSON.stringify(args.dna)}\nResearch summary: ${args.brief.brandSummary}`,
    systemPromptSuffix: [
      "Workflow: Marketing Head → Content Creator → Brand Critic + Engagement Critic →",
      "(if either ≤5, request_revision and re-call Content Creator) → Review Council → finalize.",
    ].join("\n"),
    onEvent: args.onEvent,
    assembleResult: (state) => {
      const finalArgs = state.finalArgs as CaptionDraft | undefined;
      // Caption inherits provenance from its DNA: a caption produced from
      // cached DNA is itself "cached"-derived; from live DNA → "live"; if the
      // foreman didn't finalize cleanly → "partial".
      const inherited = state.finalized ? args.dnaSource : "partial";
      const value =
        finalArgs ??
        draft ??
        ({
          caption: "(partial run — no caption captured)",
          hashtags: [],
          cta: "",
          bestPostingTime: "",
        } as CaptionDraft);
      return withProvenance(value, inherited);
    },
  });
}

// ---------------------------------------------------------------------------
// Stage 4 — Mutation Engine (per-field DNA evolution)
// ---------------------------------------------------------------------------

async function mutateDNA(args: {
  prevDNA: BrandDNA;
  direction: string;
  onEvent?: (e: AgentSseEvent) => void;
}): Promise<{ result: MutationResult; evolvedDNA: Provenanced<BrandDNA> }> {
  const { prevDNA, direction } = args;
  const FIELDS: (keyof BrandDNA)[] = ["audience", "tone", "visualWorld", "taboo", "goals"];

  // Decisions accumulate per-field via tool calls; we assemble at the end.
  const decisions = new Map<keyof BrandDNA, { decision: "mutated" | "kept"; to?: string; reason: string }>();
  let finalized = false;

  const readSnapshot = tool({
    description:
      "Read the previous Brand DNA snapshot. Call this ONCE at the start so you can reason about each field.",
    inputSchema: z.object({}).strict(),
    execute: async () => prevDNA,
  });

  const mutateField = tool({
    description:
      "Mutate one DNA field along the user's directional hint. Pass the new value and a one-sentence reason. You may call this up to 5 times (once per field).",
    inputSchema: z
      .object({
        field: z.enum(FIELDS as unknown as [keyof BrandDNA, ...(keyof BrandDNA)[]]),
        to: z.string().min(5),
        reason: z.string().min(10),
      })
      .strict(),
    execute: async ({ field, to, reason }) => {
      decisions.set(field, { decision: "mutated", to, reason });
      return { ok: true };
    },
  });

  const keepField = tool({
    description:
      "Keep one DNA field unchanged. Pass a one-sentence reason. Use when the directional hint doesn't apply to this field.",
    inputSchema: z
      .object({
        field: z.enum(FIELDS as unknown as [keyof BrandDNA, ...(keyof BrandDNA)[]]),
        reason: z.string().min(10),
      })
      .strict(),
    execute: async ({ field, reason }) => {
      decisions.set(field, { decision: "kept", reason });
      return { ok: true };
    },
  });

  const finalizeEvolved = tool({
    description: "Emit the finalize signal once every field has a decision. Call ONCE.",
    inputSchema: z.object({}).strict(),
    execute: async () => {
      finalized = true;
      return { ok: true };
    },
  });

  await generateText({
    model: MODELS.mutationEngine.model,
    system: [
      "You are the Mutation Engine. Evolve the Brand DNA along the user's directional hint.",
      "WORKFLOW: read_dna_snapshot once → for EACH of the 5 fields call mutate_field OR keep_field → finalize_evolved_dna.",
      "RULES:",
      "- Direction is a hint, not an order. Some fields shouldn't move.",
      "- Mutated values stay voice-neutral physical detail in visualWorld (extraction-layer rule).",
      "- Never invent a brand-new aesthetic. Evolve from the prior value.",
    ].join("\n"),
    prompt: `Direction: ${direction}\n\nBegin by calling read_dna_snapshot.`,
    tools: {
      read_dna_snapshot: readSnapshot,
      mutate_field: mutateField,
      keep_field: keepField,
      finalize_evolved_dna: finalizeEvolved,
    },
    // No `toolChoice: required` — Brandling lesson: this combo can infinite-loop on GPT-class.
    stopWhen: [hasToolCall("finalize_evolved_dna"), stepCountIs(15)],
    maxOutputTokens:
      MODELS.mutationEngine.knobs?.defaultMaxOutputTokens ?? 2048,
  });

  // Assemble: prevDNA + recorded mutations. Field with no decision = keep.
  // Even on a partial run we return a coherent BrandDNA.
  const evolved: BrandDNA = { ...prevDNA };
  const changedFields: (keyof BrandDNA)[] = [];
  const reasoningPerField = Object.fromEntries(
    FIELDS.map((f) => [f, "No explicit decision; preserved prior value."]),
  ) as Record<keyof BrandDNA, string>;

  for (const f of FIELDS) {
    const d = decisions.get(f);
    if (!d) continue;
    reasoningPerField[f] = d.reason;
    if (d.decision === "mutated" && d.to) {
      evolved[f] = d.to;
      changedFields.push(f);
    }
  }

  if (!finalized) {
    console.warn(
      `[mutation-engine] model did not finalize; returning partial result with ${decisions.size}/${FIELDS.length} field decisions`,
    );
  }

  const evolvedDNA = withProvenance(evolved, finalized ? "live" : "partial");
  return {
    result: { evolvedDNA: evolved, changedFields, reasoningPerField },
    evolvedDNA,
  };
}

// ---------------------------------------------------------------------------
// Top-level pipeline — research → DNA → council → mutation → council rerun
// ---------------------------------------------------------------------------

export async function runFullPipeline(args: {
  brandHandle: string;
  prompt: string;
  mutationDirection: string;
  onEvent?: (e: AgentSseEvent) => void;
}): Promise<PipelineResult> {
  const { brandHandle, prompt, mutationDirection, onEvent } = args;

  // 1. Research — cache-first, live on miss.
  const brief = await researchBrand({ brandHandle, onEvent });
  // 2. DNA extraction.
  const dnaBefore = await extractDNA({ brief, onEvent });
  // 3. First council run. The caption inherits provenance from its DNA.
  const captionBefore = await runCaptionCouncil({
    prompt,
    dna: dnaBefore,
    brief,
    dnaSource: dnaBefore._source,
    onEvent,
  });
  // 4. Mutate the DNA along the user's hint.
  const { result: mutationLog, evolvedDNA: dnaAfter } = await mutateDNA({
    prevDNA: dnaBefore,
    direction: mutationDirection,
    onEvent,
  });
  // 5. Rerun council with mutated DNA. (Toolkit will eventually expose a
  //    "dirty-set" optimization that skips stages whose inputs didn't change;
  //    here we naively rerun the whole council to keep the example clear.)
  const captionAfter = await runCaptionCouncil({
    prompt,
    dna: dnaAfter,
    brief,
    dnaSource: dnaAfter._source,
    onEvent,
  });

  return {
    before: { dna: dnaBefore, caption: captionBefore },
    after: { dna: dnaAfter, caption: captionAfter },
    mutationLog,
  };
}

// ---------------------------------------------------------------------------
// Look here:
//   - `Provenanced<T>` rides every stage. Inspect any output and you can
//     trace whether it's "cached" (research hit), "live" (live model call),
//     or "partial" (live call with some fallback fields). Brandling lesson #3
//     in Appendix A: provenance required at type level, not optional. The
//     canonical taxonomy is "cached" — NOT "cache". Get it wrong and
//     `assertProvenance` will throw at the boundary.
//   - Mutation Engine: 4 tools, no `toolChoice: required`, hard step cap.
//     Same shape as basic-tool-loop, but the closure accumulates per-field
//     decisions instead of a single terminator payload.
//   - The rerun in step 5 reuses `runCaptionCouncil` verbatim. The pipeline
//     is composable because the inputs (DNA, brief, prompt) are pure data;
//     the council doesn't know whether it's the first or second run.
//   - `runCouncil` returns `TResult` directly — whatever your `assembleResult`
//     builds. There is no `result.transcript` / `result.final` shape; if you
//     want ordering, listen on `onEvent` for `agent_step.stepIndex`.
//
//   THE BIG LESSON — DO NOT MISS THIS:
//   The Mutation Engine is a STATE CACHE labeled "learning". It evolves DNA
//   based on the USER's directional hint, not on a feedback signal from how
//   any caption actually performed. To turn this into REAL learning you
//   need (per Skill B):
//     1. An external signal: engagement deltas + brand-fidelity LLM-judge
//        + variant win-rate from A/B (composite reward, not pure CTR).
//     2. A feedback loop that causally informs the NEXT mutationDirection,
//        instead of asking the user to pick one.
//     3. An eval harness with 50-500 golden tuples + drift alarms.
//   Without that signal, this pipeline is a beautifully audited cache that
//   evolves on user vibes. Calling it "self-improving" is the §3.11
//   anti-pattern "Cache labeled 'memory'". Honest naming: this is a state
//   cache. Wire the signal first; THEN it learns.
// ---------------------------------------------------------------------------
