# MCP Integration

The `rethink-survey-mcp-server` (bundled with this plugin) exposes the skill's deterministic operations as MCP tools, the canonical content as MCP resources, and three framing prompts as slash-prompts. Prefer them over reasoning manually whenever they fit the task — the tool outputs are typed, the resource content is canonical, and the prompts are tuned.

If the MCP server is not connected (e.g. running this skill standalone), fall back to reasoning from the reference files. Detect this by attempting a tool call and noting if it's unavailable, or just by absence of the `rethink://` resources.

## Tools (call when the user wants a specific deterministic result)

| Tool | When to call | Returns |
|------|--------------|---------|
| `design_survey_session` | User says "design a survey for X" or "help me build a questionnaire". Stateful wizard with stages: `start` → `add_question` (repeat) → `review` → `finalize`. | Stage-specific payload: research-goal scaffold, candidate questions, draft schema, final question set + JSON output schema. |
| `critique_survey` | User pastes a survey and asks for review, OR says "critique this", "lint", "what's wrong with this". | `CritiqueReport` JSON: per-question violations against the 7 principles + 4-part structure check + concrete rewrite suggestions. Deterministic — prefer over manual lint. |
| `get_template` | User names a use case (event / founder / gig) and wants a starting point. | Full template: research goal, hypotheses, question set, branching, output schema. Pulls from `references/use-cases.md` content. |
| `score_response` | User has one response and wants it scored against the rubric (single-row scoring). | Rubric prompts + extraction JSON Schema. The host LLM (Claude) actually executes the extraction; the tool just hands back the structured prompt. |
| `cluster_responses` | User has a batch and wants pain-unit clustering / canonicalization. | Canonicalization + clustering rubrics. Same pattern: tool returns prompts, host LLM executes. |

**Decision rule:** If the user wants a *result* (lint output, template, scored row, cluster map), call the tool. If the user wants to *understand* (debate trade-offs, learn the principles, discuss a design choice), reason from skill content directly — don't reach for tools.

## Resources (fetch for grounding)

Resources are addressable read-only content under `rethink://`. Fetch them mid-task instead of guessing or paraphrasing.

| URI | Content |
|-----|---------|
| `rethink://principles` | All 7 design principles, full text |
| `rethink://principles/{id}` | Single principle by id (e.g. `behavioral-anchors`) |
| `rethink://structure/4-part` | The 4-part hybrid structure with examples + failure modes |
| `rethink://question-library` | Full library across all 4 parts |
| `rethink://question-library/{part}` | Library subset for one part (`discovery`, `diagnostic`, `intent`, `segmentation`) |
| `rethink://use-case/{event\|founder\|gig}` | Full template for one use case |
| `rethink://scoring/rubrics` | Scoring rubrics + composite-score math |
| `rethink://modality/decision-tree` | Form vs voice vs AI-interviewer decision tree |
| `rethink://anti-patterns` | The "always-cut" anti-pattern list |

**Use case:** When critiquing a survey manually (e.g. MCP unavailable for `critique_survey`), fetch `rethink://principles` and `rethink://anti-patterns` instead of paraphrasing from memory. When proposing questions for a specific part, fetch `rethink://question-library/{part}`.

## Prompts (user-invokable framing templates)

These are slash-prompts the user can invoke directly. If the user types one, follow its framing; otherwise mention them when relevant.

| Prompt | Framing |
|--------|---------|
| `/jarrett-review` | Roleplays Caroline Jarrett reviewing the user's survey. Strict, plain-English, focused on the seven principles and the length-honesty rule. |
| `/design-coaching` | Socratic mode: instead of writing the survey, ask the user the 5–8 design-decision questions one at a time and let them think. Output is the user's reasoning made explicit, not a finished questionnaire. |
| `/mom-test-check` | Founder-discovery–specific lint: applies Rob Fitzpatrick's Mom Test rules (avoid pitching, ask about past behavior, dig for commitment). Use for customer-discovery surveys specifically. |

## Workflow integration

For the existing workflows (in SKILL.md's "Workflow patterns" section), the MCP-augmented flow looks like:

- **"Design a survey for X"** — invoke `design_survey_session` with `stage: start`. Iterate through `add_question` calls. Finish with `finalize`. Fall back to manual walk-through if the tool isn't available.
- **"Critique this survey"** — invoke `critique_survey` with the pasted survey. Surface the `CritiqueReport`. If clarification is needed for a flagged item, fetch `rethink://principles/{id}`. Fall back to manual lint against the 7 principles otherwise.
- **"I have responses, score them"** — single response → `score_response`. Batch → `cluster_responses`. Both return prompts/schemas the host LLM then executes.
- **"Turn into app"** — no MCP tool for this (intentional: scaffolding is a host-side codegen task). Continue using `references/multimodal-ux.md`.
