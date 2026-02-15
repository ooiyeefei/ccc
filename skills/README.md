# Skills

Skills are markdown files that teach Claude Code how to perform specific tasks.

## Available Skills

| Skill | Description |
|-------|-------------|
| [excalidraw](./excalidraw/SKILL.md) | Generate architecture diagrams as .excalidraw files from codebase analysis |
| [streak](./streak/SKILL.md) | Universal challenge tracker with flexible cadence, intelligent insights, and cross-challenge learning detection. Includes optional [Telegram bot](./streak/README.md#telegram-bot-optional) for mobile notifications and interactive check-ins |
| [uat-testing](./uat-testing/SKILL.md) | End-to-end User Acceptance Testing for web applications. Analyzes branch changes and specs, generates test cases, executes via Playwright browser automation, and produces pass/fail reports with screenshots. See [README](./uat-testing/README.md) for details |

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
"Run UAT on this branch"
"Test this feature against the spec"
```

## Skill Structure

Each skill folder contains:
- `SKILL.md` - Main skill file with YAML frontmatter (name, description)
- Optional reference files for additional context

## See Also

For more complex functionality with agents, commands, and hooks, see [plugins](../plugins/).
