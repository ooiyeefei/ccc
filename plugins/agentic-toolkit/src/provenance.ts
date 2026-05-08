/**
 * Provenance tagging for agentic outputs.
 *
 * Every output of an agent / tool / persona should know how it was produced:
 * a real LLM call, a cache hit, a fallback default, a demo placeholder, or a
 * human override. Without this, a UI can't say "this was the model thinking"
 * vs "this was the demo path because your API key bounced", and a debugger
 * can't tell stale data from fresh.
 *
 * Lifted from Brandling `src/lib/types.ts:8`. Brandling Appendix A item 3
 * lesson: **make provenance required, not optional.** Brandling's
 * `_source?: GenerationSource` defaulted to `undefined`, which let codepaths
 * silently produce un-tagged values; downstream UI then guessed and got it
 * wrong. The toolkit makes `_source` a required field via `Provenanced<T>`
 * and a runtime guard.
 *
 * ## Usage
 *
 * ```ts
 * import { withProvenance, assertProvenance, type Provenanced } from
 *   '@agentic-toolkit/provenance';
 *
 * type Brief = { summary: string; angles: string[] };
 *
 * // Generated brief — tag at every callsite, no exceptions.
 * const brief: Provenanced<Brief> = withProvenance(
 *   { summary: '...', angles: [...] },
 *   'live',
 * );
 *
 * // Defensive read at a downstream boundary.
 * function consume(b: Provenanced<Brief>) {
 *   assertProvenance(b);
 *   if (b._source === 'demo') warnUserBanner();
 * }
 * ```
 */

/**
 * The provenance taxonomy. Lifted verbatim from Brandling
 * (`src/lib/types.ts:8`):
 *
 *   - `live`    — real LLM call succeeded and output parsed cleanly.
 *   - `cached`  — loaded from a committed evidence cache or research-cache.
 *   - `partial` — LLM call succeeded but some fields used fallback defaults.
 *   - `demo`    — no API key OR LLM call / parse failed entirely.
 *   - `user`    — user-supplied (e.g. brand name, persona override).
 *
 * Add domain-specific sources by extending the union in your project; do not
 * remove these five.
 */
export type GenerationSource =
  | 'live'
  | 'cached'
  | 'partial'
  | 'demo'
  | 'user';

/**
 * Wrapper type. `Provenanced<T>` requires `_source` on `T`. Use this in
 * function signatures and storage types so the type system rejects un-tagged
 * values at the callsite, not at runtime.
 */
export type Provenanced<T> = T & { _source: GenerationSource };

/**
 * Tag a value with provenance. Pure helper — primarily exists so callsites
 * read as `withProvenance(payload, 'live')` rather than spread syntax with
 * a magic key.
 */
export function withProvenance<T extends object>(
  value: T,
  source: GenerationSource,
): Provenanced<T> {
  return { ...value, _source: source };
}

/**
 * Runtime guard for the cases where TypeScript can't help you (e.g. JSON
 * parsed off the wire, untyped API responses). Throws on missing `_source`
 * with a clear message so the failure points at the boundary that didn't
 * tag.
 *
 * Useful as the first line of any handler that consumes agent output — it
 * pushes the "missed a tag" failure to fail loud rather than letting demo
 * data masquerade as live.
 */
export function assertProvenance<T extends object>(
  value: T,
): asserts value is Provenanced<T> {
  if (
    !value ||
    typeof value !== 'object' ||
    !('_source' in value) ||
    typeof (value as { _source?: unknown })._source !== 'string'
  ) {
    throw new Error(
      'Provenance missing: every agent output must carry _source. ' +
        'Tag with withProvenance(value, "live" | "cached" | "partial" | "demo" | "user").',
    );
  }
}
