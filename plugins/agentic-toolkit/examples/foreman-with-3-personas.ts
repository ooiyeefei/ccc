/**
 * Example: foreman-with-3-personas
 *
 * Pattern demonstrated: Council shape #3 from skill A — "Foreman-Worker
 *   (Orchestrator-Worker)" with mandatory-start / mandatory-end constraints.
 *   The Foreman is itself a Tool-Loop (Pattern #1) where every tool is "call
 *   another agent". Brandling's chosen shape; encoded in the toolkit's
 *   `runCouncil` helper.
 *
 * Use case: a finance-audit assistant for a small accounting firm. The CFO
 *   foreman orchestrates a debate over a single proposed journal entry:
 *   the Senior Accountant drafts the booking, the Auditor critiques it
 *   against IFRS, and the Compliance Officer flags regulatory risk
 *   (LHDN/IRAS/IRS, related-party). Output: an approved or rejected entry
 *   with a written dissent log. Use case from §5.2 of the design doc.
 *
 * What this shows:
 * - `runCouncil` from the toolkit — generic Foreman with mandatory-start
 *   (foreman MUST call SeniorAccountant first) and mandatory-end (foreman
 *   MUST call `finalize` last). Personas are plain async functions wrapped
 *   into AI SDK tools by the runner.
 * - Revision loop bounded at `maxRevisions: 3` (sweet spot from §2.7:
 *   "3-4 agents, 2-4 rounds; beyond that, accuracy degrades").
 * - Cross-family judge — CFO foreman is on Anthropic, Auditor on OpenAI,
 *   Compliance on Google. Brandling lesson: same-family judging itself
 *   triggers self-preference bias (~10% lift toward own outputs).
 * - Each persona handler is itself a leaf agent: it just runs `generateText`
 *   once with a tight system prompt and returns a structured score. No nested
 *   loops here (those go in `sub-agent-spawning.ts`).
 *
 * Lessons from Brandling baked in:
 * - Mandatory-start / mandatory-end are encoded by the runner in BOTH the
 *   system prompt AND the `stopWhen` invariant. The model is told the rule;
 *   the runtime also enforces it.
 * - The runner injects a `request_revision` tool automatically (we don't
 *   provide one). It surfaces the cap to the model as a tool result, so
 *   the model decides when to stop pushing rather than learning the cap by
 *   silent rejection.
 * - All persona outputs accumulate in `state.results` so the final result
 *   carries an audit trail — non-negotiable for regulated domains.
 */

import { z } from "zod";
import { generateText, tool, hasToolCall, stepCountIs } from "ai";

import { createGateway } from "../src/gateway";
import { defineRegistry } from "../src/models-registry";
import { runCouncil, type PersonaDefinition } from "../src/council-state-machine";
import { withProvenance, type Provenanced } from "../src/provenance";
import type { AgentSseEvent } from "../src/events";

// ---------------------------------------------------------------------------
// Inline registry — three model families on purpose. Cross-family judging
// is the §2.7 lever for council quality.
// ---------------------------------------------------------------------------

const gateway = createGateway({
  baseURL: process.env.TOKENROUTER_BASE_URL!,
  apiKey: process.env.TOKENROUTER_API_KEY!,
});

const MODELS = defineRegistry({
  // CFO Foreman — Opus-class for orchestration nuance.
  foreman: {
    model: gateway("anthropic/claude-opus-4.7"),
    knobs: { defaultMaxOutputTokens: 2048 },
  },
  // Senior Accountant drafter — Sonnet for fast, cheap structured output.
  drafter: { model: gateway("anthropic/claude-sonnet-4.6") },
  // Auditor — cross-family OpenAI critic. GPT-class needs the
  // toolChoice knob (see ModelKnobs.noToolChoiceRequired).
  auditorGpt: {
    model: gateway("openai/gpt-5.5"),
    knobs: { noToolChoiceRequired: true },
  },
  // Compliance Officer — Gemini for regulatory checking. Strict-schema knob
  // because Gemini 3 rejects loose schemas at the boundary.
  complianceGemini: {
    model: gateway("google/gemini-3-flash-preview"),
    knobs: { strictSchemaOnly: true },
  },
});

// ---------------------------------------------------------------------------
// Domain types — what's in / what comes out
// ---------------------------------------------------------------------------

interface ProposedEntry {
  date: string;
  debit: { account: string; amount: number };
  credit: { account: string; amount: number };
  memo: string;
  vendor?: string;
}

interface AccountantOutput {
  proposed: ProposedEntry;
  reasoning: string;
}

interface AuditorOutput {
  score: number;
  ifrsFindings: string[];
  feedback: string;
}

interface ComplianceOutput {
  score: number;
  flags: string[];
  feedback: string;
}

interface FinalizeArgs {
  decision: "approved" | "approved_with_caveat" | "rejected";
  finalEntry: ProposedEntry;
  caveats: string[];
}

interface AuditDecision {
  decision: "approved" | "approved_with_caveat" | "rejected";
  finalEntry: ProposedEntry;
  caveats: string[];
  dissent: { from: string; reason: string }[];
}

// ---------------------------------------------------------------------------
// Persona handlers — each is a single generateText call with a tight
// system prompt and a closure-captured terminator. This is the same
// "tool-loop with one terminator" shape as basic-tool-loop, just packaged
// as a `PersonaDefinition` for the runner to wrap.
// ---------------------------------------------------------------------------

interface AccountantArgs {
  request: string;
  chartOfAccounts: string[];
  closedPeriodCutoff: string;
}

async function callSeniorAccountant(args: AccountantArgs): Promise<AccountantOutput> {
  let captured: AccountantOutput | undefined;
  const finalizeDraft = tool({
    description: "Emit the structured journal-entry draft.",
    inputSchema: z
      .object({
        proposed: z.object({
          date: z.string(),
          debit: z.object({ account: z.string(), amount: z.number() }),
          credit: z.object({ account: z.string(), amount: z.number() }),
          memo: z.string(),
          vendor: z.string().optional(),
        }),
        reasoning: z.string().min(20),
      })
      .strict(),
    execute: async (input) => {
      captured = input;
      return { ok: true };
    },
  });

  await generateText({
    model: MODELS.drafter.model,
    system: [
      "You are a Senior Accountant in a 5-person firm. Draft ONE clean journal entry from the request.",
      "RULES:",
      "- Use the chart of accounts the user provides. Never invent account codes.",
      "- Cite IFRS treatment in the `reasoning`.",
      "- Flag if the entry crosses a closed period — the Auditor will catch it, but you should too.",
      `- Chart of accounts (verbatim): ${args.chartOfAccounts.join(", ")}`,
      `- Closed-period cutoff: ${args.closedPeriodCutoff}.`,
    ].join("\n"),
    prompt: args.request,
    tools: { finalize_draft: finalizeDraft },
    stopWhen: [hasToolCall("finalize_draft"), stepCountIs(2)],
    maxOutputTokens: 1024,
  });

  if (!captured) {
    throw new Error("Senior Accountant did not finalize a draft.");
  }
  return captured;
}

async function callAuditor(args: { entry: ProposedEntry }): Promise<AuditorOutput> {
  let captured: AuditorOutput | undefined;
  const finalizeAudit = tool({
    description: "Emit the structured IFRS audit verdict.",
    inputSchema: z
      .object({
        score: z.number().int().min(1).max(10),
        ifrsFindings: z.array(z.string()),
        feedback: z.string().min(20),
      })
      .strict(),
    execute: async (input) => {
      captured = input;
      return { ok: true };
    },
  });

  await generateText({
    model: MODELS.auditorGpt.model,
    system: [
      "You are an external Auditor. Score the proposed journal entry on 1-10 against IFRS / GAAP.",
      "RULES:",
      "- Decompose the rubric: completeness, classification, materiality, segregation-of-duties.",
      "- Show reasoning BEFORE the score (CoT-before-score raises agreement with humans).",
      "- Bounded discrete 1-10 scale. Never floats. Never holistic.",
      "- If you detect a closed-period violation or SoD breach, score ≤3 and put the rule-cite in feedback.",
    ].join("\n"),
    prompt: `Proposed entry:\n${JSON.stringify(args.entry, null, 2)}\n\nCall finalize_audit with your score.`,
    tools: { finalize_audit: finalizeAudit },
    // No `toolChoice: 'required'` — the GPT registry knob warned us about it.
    stopWhen: [hasToolCall("finalize_audit"), stepCountIs(2)],
    maxOutputTokens: 1024,
  });

  if (!captured) {
    throw new Error("Auditor did not finalize a verdict.");
  }
  return captured;
}

async function callComplianceOfficer(args: {
  entry: ProposedEntry;
}): Promise<ComplianceOutput> {
  let captured: ComplianceOutput | undefined;
  const finalizeCompliance = tool({
    description: "Emit the structured regulatory verdict.",
    inputSchema: z
      .object({
        score: z.number().int().min(1).max(10),
        flags: z.array(z.string()),
        feedback: z.string().min(20),
      })
      .strict(),
    execute: async (input) => {
      captured = input;
      return { ok: true };
    },
  });

  await generateText({
    model: MODELS.complianceGemini.model,
    system: [
      "You are a Compliance Officer. Score 1-10 on regulatory exposure (LHDN / IRAS / IRS).",
      "RULES:",
      "- Flag related-party transactions, cross-border classification issues, withholding-tax exposure.",
      "- One flag per finding, in flat strings — no nested objects.",
      "- The Auditor handles GAAP/IFRS; you handle tax + regulatory. Don't double-cover.",
    ].join("\n"),
    prompt: `Proposed entry:\n${JSON.stringify(args.entry, null, 2)}\n\nCall finalize_compliance with your score.`,
    tools: { finalize_compliance: finalizeCompliance },
    stopWhen: [hasToolCall("finalize_compliance"), stepCountIs(2)],
    maxOutputTokens: 1024,
  });

  if (!captured) {
    throw new Error("Compliance Officer did not finalize.");
  }
  return captured;
}

// ---------------------------------------------------------------------------
// Foreman: orchestrates the three personas via `runCouncil`. The runner
// wraps each persona in a tool, injects the constraints into the system
// prompt, and enforces `stopWhen: hasToolCall(mandatoryEndTool)`.
// ---------------------------------------------------------------------------

export async function auditEntry(args: {
  request: string;
  chartOfAccounts: string[];
  closedPeriodCutoff: string;
  onEvent?: (event: AgentSseEvent) => void;
}): Promise<Provenanced<AuditDecision>> {
  const { request, chartOfAccounts, closedPeriodCutoff, onEvent } = args;

  // Personas keyed by tool name. The Foreman sees these as call_X tools.
  const personas: Record<string, PersonaDefinition> = {
    call_senior_accountant: {
      description:
        "Invoke the Senior Accountant to draft ONE journal entry. Returns { proposed, reasoning }. Call FIRST.",
      inputSchema: z.object({}).strict(),
      handler: async () =>
        callSeniorAccountant({ request, chartOfAccounts, closedPeriodCutoff }),
      statusMessage: "Drafting entry...",
    },
    call_auditor: {
      description:
        "Invoke the Auditor for an IFRS / GAAP score. Returns { score, ifrsFindings, feedback }. Score ≤5 → request a revision.",
      inputSchema: z
        .object({
          entry: z.object({
            date: z.string(),
            debit: z.object({ account: z.string(), amount: z.number() }),
            credit: z.object({ account: z.string(), amount: z.number() }),
            memo: z.string(),
            vendor: z.string().optional(),
          }),
        })
        .strict(),
      handler: async ({ entry }: { entry: ProposedEntry }) =>
        callAuditor({ entry }),
      statusMessage: "Auditing against IFRS...",
    },
    call_compliance_officer: {
      description:
        "Invoke the Compliance Officer for tax / regulatory exposure. Returns { score, flags, feedback }. Score ≤5 → request a revision.",
      inputSchema: z
        .object({
          entry: z.object({
            date: z.string(),
            debit: z.object({ account: z.string(), amount: z.number() }),
            credit: z.object({ account: z.string(), amount: z.number() }),
            memo: z.string(),
            vendor: z.string().optional(),
          }),
        })
        .strict(),
      handler: async ({ entry }: { entry: ProposedEntry }) =>
        callComplianceOfficer({ entry }),
      statusMessage: "Checking regulatory exposure...",
    },
    finalize: {
      description:
        "Emit the final audit decision and end the loop. Call ONLY after both critic scores AND a final entry exist. Args become the result.",
      inputSchema: z
        .object({
          decision: z.enum(["approved", "approved_with_caveat", "rejected"]),
          finalEntry: z.object({
            date: z.string(),
            debit: z.object({ account: z.string(), amount: z.number() }),
            credit: z.object({ account: z.string(), amount: z.number() }),
            memo: z.string(),
            vendor: z.string().optional(),
          }),
          caveats: z.array(z.string()),
        })
        .strict(),
      handler: async (a) => a as unknown as FinalizeArgs,
    },
  };

  // runCouncil returns whatever assembleResult builds. The runner doesn't
  // expose a transcript object directly — we read accumulated persona
  // results from `state.results` (last-write-wins per tool name).
  return runCouncil<Provenanced<AuditDecision>>({
    foremanModel: MODELS.foreman.model,
    phase: "audit",
    mandatoryStartTool: "call_senior_accountant",
    mandatoryEndTool: "finalize",
    maxRevisions: 3, // empirical sweet spot: 2-4 rounds (§2.7)
    maxToolCalls: 14, // foreman + 3 personas + 3 revision rounds w/ headroom
    timeoutMs: 180_000,
    personas,
    userPrompt: `Audit request: ${request}`,
    systemPromptSuffix: [
      `Chart of accounts (verbatim, do not invent): ${chartOfAccounts.join(", ")}`,
      `Closed-period cutoff: ${closedPeriodCutoff}. Any entry on/before this date → reject.`,
      "If either critic scores ≤5, call request_revision and re-call call_senior_accountant before finalize.",
    ].join("\n"),
    onEvent,
    assembleResult: (state) => {
      // Build the dissent log from any critic that scored <7.
      const dissent: AuditDecision["dissent"] = [];
      const auditor = state.results["call_auditor"] as
        | AuditorOutput
        | undefined;
      const compliance = state.results["call_compliance_officer"] as
        | ComplianceOutput
        | undefined;
      if (auditor && auditor.score < 7) {
        dissent.push({ from: "Auditor", reason: auditor.feedback });
      }
      if (compliance && compliance.score < 7) {
        dissent.push({ from: "Compliance Officer", reason: compliance.feedback });
      }

      const finalArgs = state.finalArgs as FinalizeArgs | undefined;
      const draft = state.results["call_senior_accountant"] as
        | AccountantOutput
        | undefined;

      // Brandling lesson: callers always want a structured result even on a
      // partial run. Fall back to the draft entry if the foreman never called
      // finalize.
      if (state.finalized && finalArgs) {
        return withProvenance(
          {
            decision: finalArgs.decision,
            finalEntry: finalArgs.finalEntry,
            caveats: finalArgs.caveats,
            dissent,
          },
          "live",
        );
      }
      return withProvenance(
        {
          decision: "rejected" as const,
          finalEntry:
            draft?.proposed ?? {
              date: closedPeriodCutoff,
              debit: { account: "?", amount: 0 },
              credit: { account: "?", amount: 0 },
              memo: "(partial run — foreman did not finalize)",
            },
          caveats: ["Foreman did not finalize within tool-call cap."],
          dissent,
        },
        "partial",
      );
    },
  });
}

// ---------------------------------------------------------------------------
// Look here:
//   - The Foreman's CONSTRAINTS (start with call_senior_accountant, end with
//     finalize, max 3 revisions) are passed to `runCouncil`. The runner
//     templates them into the system prompt AND enforces them via
//     `stopWhen: [hasToolCall(mandatoryEndTool), stepCountIs(maxToolCalls)]`.
//     Defense-in-depth: prompt + runtime agree.
//   - Three critics, three different model families. This is THE single
//     biggest lever for council quality (§2.7: "composition > mechanics").
//     Don't run 5 critics on the same family thinking it'll help — it won't.
//   - `assembleResult` is the seam where you go from "accumulated state" to
//     "domain output". The runner returns whatever you build here, including
//     `Provenanced<T>` wrapping. Partial-run fallback lives in this function.
//   - `state.results` is keyed by tool name. The runner does not expose a
//     transcript stream — if you need ordering, listen to `onEvent` for
//     `agent_step` events with `stepIndex`.
//   - For ANY one-shot non-debatable answer (math, retrieval, exact lookup),
//     skip this entirely — see the "Council-for-everything" anti-pattern in
//     §2.11. Run a single agent with retries, not a 3-person council.
// ---------------------------------------------------------------------------
