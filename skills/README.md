# Skills

Skills are markdown files that teach Claude Code how to perform specific tasks.

## Available Skills

| Skill | Description |
|-------|-------------|
| [excalidraw](./excalidraw/SKILL.md) | Generate architecture diagrams as .excalidraw files from codebase analysis |
| [streak](./streak/SKILL.md) | Universal challenge tracker with flexible cadence, intelligent insights, and cross-challenge learning detection. Includes optional [Telegram bot](./streak/README.md#telegram-bot-optional) for mobile notifications and interactive check-ins |

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
"Visualize this codebase as an excalidraw file"
```

## Skill Structure

Each skill folder contains:
- `SKILL.md` - Main skill file with YAML frontmatter (name, description)
- Optional reference files for additional context

## See Also

For more complex functionality with agents, commands, and hooks, see [plugins](../plugins/).
