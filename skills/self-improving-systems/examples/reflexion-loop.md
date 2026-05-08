# Reflexion Loop — The Cheapest First Move

Before you stand up a vector store, before you pick mem0 vs Letta, before you write a memory schema: **try Reflexion first**. It's the cheapest rung on the self-improvement ladder ([Shinn et al., 2023, arXiv 2303.11366](https://arxiv.org/abs/2303.11366)) and on coding tasks like HumanEval it pushed pass@1 from ~80% (GPT-4 raw) to ~91% with no fine-tuning, no persistent store, no infra.

The trick: the agent fails, a verifier scores the failure, an LLM writes a *natural-language critique*, and that critique is prepended to the next attempt's prompt. The reflection lives in a per-task scratchpad. **Nothing crosses the task boundary.** No retrieval. No KV. No vector index.

That last part is the load-bearing one. Reflexion's design discipline is: reflection is in-context only. If a reflection turns out to be durably useful — "this codebase always wants `snake_case` test names" — a *human* reads the scratchpad, decides it's a real rule, and promotes it to a system-prompt block or a skill file. The agent does not promote its own reflections. That's the defense against drift, against memory poisoning, and against the agent talking itself into nonsense over a weekend.

## The shape

```
attempt_n:
  agent runs task → trace + output
  verifier scores output → pass | fail + concrete signal
  if pass → done
  if fail:
    reflection_LLM(task, trace, output, signal) → 1-3 sentence critique
    append critique to scratchpad
attempt_(n+1):
  prompt = base_prompt + scratchpad + task
  (no persistent memory, no retrieval — scratchpad is in-process state)
```

Three actors, one mutable buffer. That's it.

## Reference excerpt

```typescript
// reflexion-loop.ts — drop-in pattern, ~30 lines
type Attempt = { output: string; passed: boolean; signal: string };
type Reflection = string;

async function reflexionLoop(
  task: string,
  agent: (prompt: string) => Promise<string>,
  verify: (output: string) => Promise<{ passed: boolean; signal: string }>,
  reflect: (task: string, attempt: Attempt) => Promise<Reflection>,
  maxAttempts = 3,
): Promise<{ output: string; attempts: number; reflections: Reflection[] }> {
  const reflections: Reflection[] = [];
  for (let i = 0; i < maxAttempts; i++) {
    const reflectionBlock = reflections.length
      ? `\n## Lessons from prior attempts (do not repeat these mistakes)\n${reflections.map((r, j) => `${j + 1}. ${r}`).join("\n")}\n`
      : "";
    const prompt = `${reflectionBlock}\n## Task\n${task}`;
    const output = await agent(prompt);
    const { passed, signal } = await verify(output);
    if (passed) return { output, attempts: i + 1, reflections };
    reflections.push(await reflect(task, { output, passed, signal }));
  }
  // hit cap → return last attempt + the reflection trail (caller decides escalation)
  throw new Error(`reflexion exhausted after ${maxAttempts}; reflections=${JSON.stringify(reflections)}`);
}
```

A few details that matter in practice:

- **Verifier is the load-bearing piece.** Reflexion only works when `verify` is cheap, deterministic, and catches the actual failure. Unit tests, type-checkers, and SQL-runs-without-error are great. "LLM-as-judge says it looks fine" is not — you'll get reflections that hallucinate problems and the agent will chase ghosts.
- **Reflection prompt should demand specificity.** "What went wrong?" produces vapor. "Quote the exact line of the failed test, name the wrong assumption, and state the corrected rule in one sentence" produces something actionable. Cite the signal verbatim in the reflection prompt — make the LLM read its own bug report.
- **Cap attempts hard (3-5).** Past round 4 you hit [degeneration-of-thought](https://arxiv.org/html/2506.00066v1) — the agent re-asserts wrong reflections more confidently. If 3 attempts didn't fix it, the bug is structural and a human needs to look.
- **Keep the scratchpad in-process.** Don't write reflections to disk between tasks. Don't index them. Don't retrieve them later. If you find yourself wanting to, you've hit the escalation point.

## When this is enough

Reflexion alone covers most "my agent keeps making the same mistake within one task" cases. Concrete green-lights:

- **Code-emitting agents** with fast verifiers (tests, type-check, lint). This is the canonical Reflexion win.
- **Single-session reasoning** where the failure mode is "missed an edge case" or "wrong tool call" — visible in the trace, fixable by reading the trace.
- **Within-task self-correction** for tool-loop agents, especially when paired with a critic at the end of the loop ([Evaluator-Optimizer pattern](https://www.anthropic.com/engineering/building-effective-agents)).

## When to escalate

Three signals say you've outgrown the scratchpad:

1. **The same reflection keeps recurring across tasks.** "Use `snake_case`", "The user prefers concise replies", "API X is deprecated, use Y." If you'd manually copy-paste these into a system prompt, you need a real memory store — start at tier 2 (conversation summary) or tier 5 (KV fact store) per the [memory ladder](../references/architectures.md). See [`kv-store-mem0.md`](./kv-store-mem0.md).
2. **Reflections need to outlive a session.** A user comes back tomorrow and the agent should remember why their last attempt was rejected. Scratchpad is per-task; this is per-user. KV store, with a write-time validator.
3. **Cross-task skill accumulation.** "When task type X comes up, here's the playbook that worked." That's [Voyager](https://arxiv.org/abs/2305.16291)-style skill library territory and a different conversation.

The promotion bar from scratchpad to persistent store is **a human read, a human decision**. Never let the agent write its own reflections into core memory — that's the prompt-injection bomb the [MINJA paper](https://arxiv.org/abs/2503.03704) lights up at ≥95% lab success rate. Scratchpad is ephemeral by design. Keep it that way until you have a real reason and a real eval ([`eval-harness.md`](./eval-harness.md)) to spend on the upgrade.
