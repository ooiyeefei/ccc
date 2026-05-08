/**
 * Multi-model gateway adapter.
 *
 * One OpenAI-compatible endpoint that fronts Claude / GPT / Gemini via a
 * unified gateway (TokenRouter, OpenRouter, LiteLLM, Vercel AI Gateway, etc.).
 * Every agent in a Brandling-style codebase reaches its model through this
 * provider so swapping families (cost / latency / capability) is a one-line
 * edit in the registry rather than per-call.
 *
 * Why a single provider rather than per-family AI SDK providers?
 *   - One auth surface, one retry policy, one billing line.
 *   - The registry (see `models-registry.ts`) becomes the single seam where
 *     "claude-opus is suddenly expensive" turns into a 1-character edit.
 *   - Cross-family councils (Anthropic + OpenAI + Google) work without three
 *     parallel client setups.
 *
 * Lifted from Brandling `src/lib/agents/provider.ts` (line 15) — original code
 * hardcoded TokenRouter env vars; this version takes them as arguments so the
 * toolkit is gateway-agnostic.
 *
 * Usage:
 * ```ts
 * import { createGateway } from '@agentic-toolkit/gateway';
 *
 * export const gateway = createGateway({
 *   name: 'tokenrouter',
 *   baseURL: process.env.TOKENROUTER_BASE_URL!,
 *   apiKey: process.env.TOKENROUTER_API_KEY!,
 * });
 *
 * // Then bind models in models-registry.ts:
 * //   foreman: gateway('anthropic/claude-opus-4.7')
 * ```
 *
 * The returned provider is callable: `gateway('vendor/model-name')` returns a
 * `LanguageModel` ready to pass to `generateText`. AI SDK v6 syntax.
 */

import {
  createOpenAICompatible,
  type OpenAICompatibleProvider,
} from '@ai-sdk/openai-compatible';

export interface GatewayConfig {
  /**
   * OpenAI-compatible `/v1` URL for the gateway.
   *   - TokenRouter: https://api.tokenrouter.com/v1
   *   - OpenRouter:  https://openrouter.ai/api/v1
   *   - LiteLLM:     http://localhost:4000/v1 (or your deployment)
   */
  baseURL: string;
  /** Bearer token / API key for the gateway. */
  apiKey: string;
  /**
   * Provider name used in AI SDK telemetry and traces. Defaults to
   * `'gateway'`. If you run multiple gateways in one process, give each
   * a distinct name so OTel spans separate cleanly.
   */
  name?: string;
}

/**
 * Create an OpenAI-compatible provider wired to the configured gateway.
 *
 * Returned value is the AI SDK v6 `OpenAICompatibleProvider` — call it with a
 * model string (e.g. `gateway('anthropic/claude-opus-4.7')`) to get a
 * `LanguageModel` you can pass to `generateText`.
 */
export function createGateway(
  config: GatewayConfig,
): OpenAICompatibleProvider {
  return createOpenAICompatible({
    name: config.name ?? 'gateway',
    baseURL: config.baseURL,
    apiKey: config.apiKey,
  });
}
