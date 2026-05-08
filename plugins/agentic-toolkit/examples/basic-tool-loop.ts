/**
 * Example: basic-tool-loop
 *
 * Pattern demonstrated: Pattern #1 from skill A — "Tool-Loop (ReAct)".
 *   Single model, single agent, picks which tool to call next from observations,
 *   terminates when it calls a `finalize` tool. The simplest agentic shape that
 *   still scores ≥4 on the real-agency-vs-workflow rubric (§2.4 of the design
 *   doc) — tool order is unknown at design time, tool count varies per run,
 *   environmental feedback drives the next decision, model controls the stop.
 *
 * Use case: a code-review bot. Given a file path and a complaint
 *   ("function is too slow"), the agent reads the file, suggests a fix, and
 *   finalizes with a structured patch + rationale. Cheap because there is NO
 *   council, NO sub-agent spawning, NO mutation engine — one model, one loop.
 *
 * What this shows:
 * - Toolkit `gateway` + `defineRegistry` give you 1-line model swaps. Each
 *   example builds its OWN minimal registry inline so you can see exactly
 *   which roles this pattern needs (here: just one — `reviewer`).
 * - `stopWhen: [hasToolCall("finalize"), stepCountIs(N)]` is the canonical
 *   termination contract — the model controls the stop, but the cap saves you
 *   from runaway token spend.
 * - Tool descriptions are product copy, not comments — they are the model's
 *   primary signal for which tool to pick next.
 * - Closure-captured `final` payload is how you get structured output OUT of
 *   the loop (the model's last text turn is unreliable; the terminator's
 *   `execute` return is the source of truth).
 *
 * Lessons from Brandling baked in:
 * - Hard step cap with explicit error path on timeout (no silent retry).
 * - No `toolChoice: required` — the design doc warns it can infinite-loop on
 *   GPT-class models. We rely on stopWhen instead.
 * - Provenance is required at the type level (see `Provenanced<T>` below).
 */

import { generateText, tool, stepCountIs, hasToolCall } from "ai";
import { z } from "zod";
import * as fs from "node:fs/promises";

import { createGateway } from "../src/gateway";
import { defineRegistry } from "../src/models-registry";
import { withProvenance, type Provenanced } from "../src/provenance";

// ---------------------------------------------------------------------------
// Inline registry — only the roles THIS pattern needs.
//
// Lesson: don't import a shared `MODELS` constant. The toolkit ships a
// `defaultBrandlingRegistry(gateway)` factory for the full 8-role council, but
// each pattern should declare its own minimal subset so the read order matches
// the role order of the pipeline.
// ---------------------------------------------------------------------------

const gateway = createGateway({
  baseURL: process.env.TOKENROUTER_BASE_URL!,
  apiKey: process.env.TOKENROUTER_API_KEY!,
});

const MODELS = defineRegistry({
  // One role for the one loop. Opus for code-review nuance; swap to Sonnet
  // if you want the cheaper / faster cycle and don't mind less-precise patches.
  reviewer: {
    model: gateway("anthropic/claude-opus-4.7"),
    knobs: { defaultMaxOutputTokens: 1024 },
  },
});

const SYSTEM_PROMPT = [
  "You are a senior engineer doing a focused code review.",
  "",
  "WORKFLOW:",
  "1. Call `read_file` to load the file the user is asking about.",
  "2. Reason about the complaint. Identify the smallest change that resolves it.",
  "3. Call `suggest_fix` with a unified-diff-style patch and a one-paragraph rationale.",
  "4. Call `finalize` with the structured review summary. Stop after this.",
  "",
  "RULES:",
  "- Read the file BEFORE suggesting a fix. Do not invent code that isn't there.",
  "- One fix per review. If multiple issues exist, pick the one the user complained about.",
  "- The `finalize` tool's arguments ARE the published review. Make them production-ready.",
].join("\n");

interface ReviewResult {
  filePath: string;
  patch: string;
  rationale: string;
  severity: "low" | "medium" | "high";
}

export async function reviewCode(args: {
  filePath: string;
  complaint: string;
}): Promise<Provenanced<ReviewResult>> {
  const { filePath, complaint } = args;

  // Closure-captured terminator output. The model's text response is
  // unreliable; this is the source of truth for what the loop produced.
  let captured: ReviewResult | undefined;

  const readFile = tool({
    description:
      "Read a source file from disk. Returns the file contents verbatim. Call this FIRST before reasoning about a fix — never invent code.",
    inputSchema: z.object({ path: z.string().min(1) }).strict(),
    execute: async ({ path }) => {
      const contents = await fs.readFile(path, "utf-8");
      return { path, contents, lineCount: contents.split("\n").length };
    },
  });

  const suggestFix = tool({
    description:
      "Propose a unified-diff-style patch for the smallest change that resolves the user's complaint. Returns the patch echoed back so you can refine it before finalizing.",
    inputSchema: z
      .object({
        patch: z.string().min(1).describe("Unified diff. Include 3 lines of context."),
        rationale: z.string().min(20).describe("One paragraph: why this fix, not another."),
      })
      .strict(),
    execute: async ({ patch, rationale }) => {
      return { patch, rationale, accepted: true };
    },
  });

  const finalize = tool({
    description:
      "Emit the final review and end the loop. Call ONCE after suggest_fix. severity is 'high' for correctness/security, 'medium' for perf/clarity, 'low' for style.",
    inputSchema: z
      .object({
        patch: z.string().min(1),
        rationale: z.string().min(20),
        severity: z.enum(["low", "medium", "high"]),
      })
      .strict(),
    execute: async ({ patch, rationale, severity }) => {
      captured = { filePath, patch, rationale, severity };
      return { ok: true };
    },
  });

  // Hard wall-clock cap — Brandling lesson: no `max_turns` cap → runaway.
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), 60_000);

  try {
    await generateText({
      model: MODELS.reviewer.model, // 1-line model swap via the registry.
      system: SYSTEM_PROMPT,
      prompt: `File: ${filePath}\nComplaint: ${complaint}\n\nBegin by calling read_file.`,
      tools: { read_file: readFile, suggest_fix: suggestFix, finalize },
      stopWhen: [hasToolCall("finalize"), stepCountIs(8)],
      maxOutputTokens: MODELS.reviewer.knobs?.defaultMaxOutputTokens ?? 1024,
      abortSignal: ac.signal,
    });
  } finally {
    clearTimeout(timer);
  }

  if (!captured) {
    // Step cap hit before finalize — explicit error path, not silent retry.
    throw new Error(
      `Reviewer did not finalize within step cap. File=${filePath} complaint="${complaint}".`,
    );
  }

  // Provenance is required at type level (toolkit lesson #3): every output
  // carries a `_source` stamp so downstream UI / persistence / mutation
  // engines can distinguish live vs cached vs evolved.
  return withProvenance(captured, "live");
}

// ---------------------------------------------------------------------------
// Look here:
//   - The `tools` map is the model's entire action space. Three tools, one
//     of which is the terminator. That's the minimum shape of a real agent.
//   - `stopWhen: [hasToolCall("finalize"), stepCountIs(8)]` is the contract.
//     `hasToolCall` lets the MODEL stop when it's done; `stepCountIs` is the
//     escape hatch for runaway loops. Both required.
//   - `captured` lives in the closure. The terminator's `execute` writes to
//     it; we read it AFTER `generateText` returns. This is how you get
//     structured output out of an AI SDK tool loop.
//   - The registry has ONE entry. Everything you'd swap (cheaper model,
//     different family) is one line in `defineRegistry({...})` above.
//   - No council. No sub-agents. No memory. This is the cheapest shape that
//     still earns the name "agent" by the §2.4 rubric. Do not add more
//     until you fail this loop.
// ---------------------------------------------------------------------------
