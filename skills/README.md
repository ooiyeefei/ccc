# Skills

Skills are markdown files that teach Claude Code how to perform specific tasks.

## Available Skills

| Skill | Description |
|-------|-------------|
| [excalidraw](./excalidraw/SKILL.md) | Generate architecture diagrams as .excalidraw files from codebase analysis, with optional PNG/SVG export via Playwright |
| [streak](./streak/SKILL.md) | Universal challenge tracker with flexible cadence, intelligent insights, and cross-challenge learning detection. Includes optional [Telegram bot](./streak/README.md#telegram-bot-optional) for mobile notifications and interactive check-ins |
| [uat-testing](./uat-testing/SKILL.md) | End-to-end User Acceptance Testing for web applications. Analyzes branch changes and specs, generates test cases, executes via Playwright browser automation, and produces pass/fail reports with screenshots. See [README](./uat-testing/README.md) for details |
| [agentic-system-design](./agentic-system-design/SKILL.md) | Prescriptive 12-stage Q&A workflow for designing agentic pipelines, multi-model councils, and sub-agent hierarchies. Filters agent-washing, wasteful councils, and unnecessary depth before you build. See [README](./agentic-system-design/README.md) for details |
| [self-improving-systems](./self-improving-systems/SKILL.md) | Decide whether your agent actually needs persistent memory, feedback loops, or closed-loop learning — then design the smallest thing that pays for itself. Default position: scratchpad-only, stateless agent first. See [README](./self-improving-systems/README.md) for details |
| [secure-by-design](./secure-by-design/SKILL.md) | Enterprise security review for any system design or codebase: classify assets and trust boundaries FIRST, then recommend only the controls that fit (deny-by-default, anti-IDOR, append-only audit, JIT, four-eyes, read/write scope split), right-sized for team scale. Grounded in shipped patterns. See [README](./secure-by-design/README.md) for details |
| [htmldrop](./htmldrop/SKILL.md) | Publish HTML files as shareable links via Surge.sh, with optional embedded annotation widget for collaborative review and AI-converged feedback synthesis. See [README](./htmldrop/README.md) for details |
| [landing-page-gtm](./landing-page-gtm/SKILL.md) | Build high-converting SaaS landing pages with GTM-aware marketing copy, competitive positioning, and sales psychology. See [README](./landing-page-gtm/README.md) for details |
| [pitch-craft](./pitch-craft/SKILL.md) | The timed-spoken-script engine: demo voiceovers, deck narration, and live pitch speeches with word budgets, storytelling rules (hook, throughline, analogies), trim points, and re-sync after re-records. See [README](./pitch-craft/README.md) for details |
| [demo-video](./demo-video/SKILL.md) | Record crisp hi-res product demo videos by driving the real app with a browser agent: a recording contract (real browser state, whole journey, every claim proven on screen) enforced by three gates, plus Xvfb framebuffer capture (no macroblocking). See [README](./demo-video/README.md) for details |
| [pitch-deck](./pitch-deck/SKILL.md) | Build a pitch deck as one self-contained HTML file (hash nav, entry animations, brand mark, cited numbers), narrate it, and optionally record the walkthrough in parts that stitch around a demo. See [README](./pitch-deck/README.md) for details |
| [pitch-package](./pitch-package/SKILL.md) | The end-to-end pitch orchestrator: interview the audience and slot, budget the time, compose deck + demo + live speech via the other pitch skills, with stitch plan, fallback ladder, and day-of checklist. See [README](./pitch-package/README.md) for details |

## The pitch suite - when to use what

Four skills, one factoring: three workflows plus one shared engine. Start from what you need to hand over:

| You need | Start with | What it contains | It will pull in |
|---|---|---|---|
| The whole pitch for a slot (hackathon, VC, customer demo) | [pitch-package](./pitch-package/SKILL.md) | Audience interview, slot budgeting, composition plan, audience lenses, stitch variants + fallback ladder, day-of checklist | All three below, as gaps demand |
| Words against a clock (demo voiceover, deck narration, live speech) | [pitch-craft](./pitch-craft/SKILL.md) | Beats-before-words workflow, words-per-second budgets, storytelling rules (hook, throughline, analogies), trim points, re-sync after re-records | Nothing - it is the shared engine |
| Crisp footage of the product itself | [demo-video](./demo-video/SKILL.md) | The recording contract and its three gates, storyboard format, the Xvfb framebuffer recipe (fixes macroblocking), CDP driving patterns, the harness script, verified milestone JSON | pitch-craft, for the narration |
| The deck itself, and optionally its recorded walkthrough | [pitch-deck](./pitch-deck/SKILL.md) | Single-file HTML deck skeleton (hash nav, animations, brand mark, cited numbers), walkthrough recording in parts around a demo | pitch-craft for narration; demo-video's harness for recording |

Rules of thumb: preparing for an audience and a time slot -> **pitch-package** first, always. Only one artifact missing -> call that skill directly. Anything that produces spoken words routes through **pitch-craft**; anything that produces video pixels routes through **demo-video**'s harness.

## Installation

Skills are bundled as a plugin for easy installation:

```bash
# Add the marketplace
/plugin marketplace add ooiyeefei/ccc

# Install the skills plugin
/plugin install ccc-skills@ccc
```

## Usage

After installing, just ask Claude Code:

```
"Generate an architecture diagram for this project"
"Create an excalidraw diagram of the system"
"Export this excalidraw diagram to PNG"
"Run UAT on this branch"
"Test this feature against the spec"
"Design an agent that does HAZOP analysis"
"Should I add memory to my agent?"
"Share this HTML report and let people comment on it"
"Build a landing page for this product"
```

## Skill Structure

Each skill folder contains:
- `SKILL.md` - Main skill file with YAML frontmatter (name, description)
- Optional reference files for additional context

## See Also

For more complex functionality with agents, commands, and hooks, see [plugins](../plugins/).
