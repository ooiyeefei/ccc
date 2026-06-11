# Self-Improving Systems - Memory & Learning, Only When Justified

Decide whether your agent actually needs persistent memory, feedback loops, or closed-loop learning — then design the smallest thing that pays for itself.

---

## What It Does

This skill turns Claude Code into a skeptical design partner for agent memory and learning. Its headline message: **most agents shouldn't have persistent memory.** Memory is a liability surface (drift, poisoning, debugging difficulty, GDPR/HIPAA exposure), so the first two stages exist to stop over-engineering:

1. **Cache-vs-learning frame** — "remember state" and "get better over time" share zero infrastructure; most users want the first and are about to build the second
2. **6-question need-memory rubric** — score <4 yes and the skill exits, recommending stateless + RAG
3. **7-tier architecture ladder** — starts at scratchpad-only; each tier-up must be justified by a concrete failure of the tier below on a real eval task
4. **Feedback signal design** — no observable ground-truth signal = state cache, not learning, full stop
5. **Closed-loop wiring with human gates** — autonomy for low-risk appends; human review for anything that mutates policy, voice, or identity
6. **Eval harness** — golden set, memory side-effect regression, drift alarms before going live
7. **8-risk checklist** — poisoning (MINJA-class injection), drift, privacy, reward hacking
8. **Design output** — memory schema + closed-loop spec + eval harness plan

~60% of users discover by the end of Stage 2 that they want a **state cache** (or stateless RAG), not memory + learning. That's the win — the skill is designed to end early.

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Usage

Trigger the skill naturally:

```
"Add memory to my agent"
"My agent keeps forgetting things — give it context management"
"Make my marketing agent learn from past campaigns"
"Should I use mem0 or Letta?"
"How do I set up closed-loop learning for my finance agent?"
```

The skill asks one question at a time and exits as soon as a cheaper answer fits your problem.

## How It Works

### The 7-Tier Memory Ladder

Ordered cheapest → most expensive. Default recommendation is tier 1; "we're using Letta" out of the gate is the most expensive mistake in this design space:

1. Scratchpad-only (Reflexion-style, discarded after the run) ← **ship this first**
2. Conversation summary
3. Episodic event log
4. Vector retrieval over episodes
5. KV fact store
6. Graph memory (needs >3 entities × >50 relationships)
7. Hierarchical OS-style (Letta/MemGPT-class) — real long-horizon agents only

### Hard Rules the Skill Enforces

- **No signal = no learning.** If you can't observe whether the last action was good or bad within hours-to-weeks, you have a state cache — naming it "learning" sets the team up to A/B test against a metric that doesn't exist.
- **Human gates are non-negotiable in production** for core-memory promotion, schema changes, shared skill libraries, and reward-model updates.
- **Memory is untrusted input.** Every retrieval is treated like a web search result — its own context block, never auto-promoted to the system prompt.

## Skill Structure

```
self-improving-systems/
├── SKILL.md                      # The 8-stage Q&A flow + rubrics
├── README.md                     # This file
├── references/
│   ├── architectures.md          # 7-tier ladder deep-dive
│   ├── feedback-signals.md       # Per-domain signal design
│   ├── eval-harness.md           # Golden sets, drift alarms, judge calibration
│   ├── playbook-ladder.md        # Skill/playbook accumulation patterns
│   ├── risks.md                  # 8-risk checklist (poisoning, drift, privacy…)
│   └── case-studies.md           # Worked examples
└── examples/
    ├── reflexion-loop.md         # Tier-1 scratchpad self-correction
    ├── kv-store-mem0.md          # Tier-5 KV fact store
    └── eval-harness.md           # Minimal harness to ship before going live
```

See [SKILL.md](./SKILL.md) for the full 8-stage flow and decision rubrics.
