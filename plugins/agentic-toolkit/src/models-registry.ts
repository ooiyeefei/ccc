/**
 * Per-role model registry.
 *
 * Every agent role (foreman, critic, synthesizer, ...) maps to a single
 * `LanguageModel` plus an optional bag of **per-model knobs** that control
 * call-site quirks. The registry is the single seam for cost / speed / family
 * swaps — change a model string here, every call site picks it up.
 *
 * Lifted from Brandling `src/lib/agents/models.ts` (line 16). The original was
 * a flat `as const` object; this version is a typed registry with per-entry
 * knobs because the production codebase ended up re-asserting the same
 * "no toolChoice: required for GPT-class models" comment at every call site.
 * That signal-as-comment is exactly the thing a registry should encode.
 *
 * ## Why per-model knobs?
 *
 * Different model families have different failure modes you only learn in
 * production:
 *
 *   - GPT-5.5 infinite-loops when invoked with `toolChoice: 'required'`
 *     because it interprets the constraint as "keep calling tools forever";
 *     Anthropic models honor the loop's natural stop condition.
 *   - Some Gemini variants have stricter JSON schema enforcement and reject
 *     `additionalProperties: true`.
 *   - Cheap models often cap `maxOutputTokens` invisibly; bake a default in.
 *
 * Lifting these into the registry means the runner / persona code becomes
 * generic: "ask the registry what knobs apply, splat them into the call."
 * That removes the per-site `// don't set toolChoice: 'required' or GPT loops`
 * comments that pollute Brandling today.
 *
 * ## Usage
 *
 * ```ts
 * import { defineRegistry } from '@agentic-toolkit/models-registry';
 * import { createGateway } from '@agentic-toolkit/gateway';
 *
 * const gateway = createGateway({ baseURL: ..., apiKey: ... });
 *
 * export const MODELS = defineRegistry({
 *   foreman: { model: gateway('anthropic/claude-opus-4.7') },
 *   brandCritic: {
 *     model: gateway('openai/gpt-5.5'),
 *     knobs: { noToolChoiceRequired: true },
 *   },
 * });
 *
 * // Then in a runner:
 * const entry = MODELS.brandCritic;
 * await generateText({
 *   model: entry.model,
 *   ...(entry.knobs?.noToolChoiceRequired ? {} : { toolChoice: 'required' }),
 * });
 * ```
 */

import type { LanguageModel } from 'ai';

/**
 * Per-model knobs that runners / personas should respect.
 *
 * All optional — the **absence** of a knob means "use AI SDK defaults". Keep
 * this list narrow; every knob added here is a knob every call site has to
 * remember to read. When in doubt, fix the call site instead.
 */
export interface ModelKnobs {
  /**
   * Don't set `toolChoice: 'required'` when calling this model. GPT-5.5 (and
   * earlier OpenAI tool-calling models) interpret `required` as "always emit
   * a tool call" and infinite-loop on the next turn. Anthropic models stop
   * naturally on `final_output`.
   *
   * Brandling lesson: the comment `// no toolChoice: required for GPT` was
   * copy-pasted across ~6 call sites. Lift to the registry.
   */
  noToolChoiceRequired?: boolean;
  /**
   * Default max output tokens for this model. Some cheap / fast variants
   * truncate silently below their advertised limit; bake a conservative
   * default here and let call sites override only when they need to.
   */
  defaultMaxOutputTokens?: number;
  /**
   * Don't set `additionalProperties: true` (or `strict: false`) on tool
   * schemas. Gemini 2.x rejects loose schemas at the boundary even when the
   * model itself would accept them.
   */
  strictSchemaOnly?: boolean;
  /**
   * Disable parallel tool calls. Some models hallucinate dependencies between
   * "parallel" calls and produce contradictory args; serialize when it
   * matters more than throughput.
   */
  noParallelToolCalls?: boolean;
}

/**
 * One registry entry: a model plus optional knobs.
 */
export interface ModelEntry {
  model: LanguageModel;
  knobs?: ModelKnobs;
}

/**
 * Generic shape: a registry maps role names (string keys) to `ModelEntry`.
 */
export type ModelsRegistry<TRoles extends string> = Record<TRoles, ModelEntry>;

/**
 * Factory — primarily an identity function with a type-narrowing tweak so
 * downstream code gets `keyof typeof MODELS` autocompletion. Keep it minimal:
 * the value here is the type, not runtime behavior.
 */
export function defineRegistry<TRegistry extends Record<string, ModelEntry>>(
  registry: TRegistry,
): TRegistry {
  return registry;
}

/**
 * Sample registry mirroring Brandling's 8-role council. Treat as a starting
 * point — copy + edit for your domain (HAZOP teams, finance councils,
 * tutorial-gen editorial boards).
 *
 * Reference: Brandling `src/lib/agents/models.ts:16`.
 *
 * Note: this exported sample requires the consumer to provide a `gateway`;
 * we don't bind to a global so the toolkit stays gateway-agnostic.
 */
export function defaultBrandlingRegistry(
  gateway: (modelId: string) => LanguageModel,
): {
  foreman: ModelEntry;
  marketingHead: ModelEntry;
  contentCreator: ModelEntry;
  brandCritic: ModelEntry;
  engagementCritic: ModelEntry;
  reviewCouncil: ModelEntry;
  mutationEngine: ModelEntry;
  synthesizer: ModelEntry;
} {
  return defineRegistry({
    // Foreman / orchestrator — top-of-the-line model for tool-loop control.
    foreman: { model: gateway('anthropic/claude-opus-4.7') },
    // Strategy persona — Sonnet is cheaper and fast for structured output.
    marketingHead: { model: gateway('anthropic/claude-sonnet-4.6') },
    // Creative drafts — Opus for prose quality.
    contentCreator: { model: gateway('anthropic/claude-opus-4.7') },
    // Cross-family critic for self-preference mitigation. GPT needs the
    // toolChoice knob — see ModelKnobs.noToolChoiceRequired.
    brandCritic: {
      model: gateway('openai/gpt-5.5'),
      knobs: { noToolChoiceRequired: true },
    },
    // Fast multimodal scorer — Gemini 3 Flash for hook strength judging.
    engagementCritic: {
      model: gateway('google/gemini-3-flash-preview'),
      knobs: { strictSchemaOnly: true },
    },
    // Final approval — same family as foreman is OK because review is
    // structured-output, not subjective.
    reviewCouncil: { model: gateway('anthropic/claude-opus-4.7') },
    // Mutation engine — DNA evolution. Opus for nuance; default token cap
    // higher because rationales are long.
    mutationEngine: {
      model: gateway('anthropic/claude-opus-4.7'),
      knobs: { defaultMaxOutputTokens: 4096 },
    },
    // Lightweight synthesis. Sonnet again.
    synthesizer: { model: gateway('anthropic/claude-sonnet-4.6') },
  });
}
