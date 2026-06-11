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
| [htmldrop](./htmldrop/SKILL.md) | Publish HTML files as shareable links via Surge.sh, with optional embedded annotation widget for collaborative review and AI-converged feedback synthesis. See [README](./htmldrop/README.md) for details |
| [landing-page-gtm](./landing-page-gtm/SKILL.md) | Build high-converting SaaS landing pages with GTM-aware marketing copy, competitive positioning, and sales psychology. See [README](./landing-page-gtm/README.md) for details |

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
