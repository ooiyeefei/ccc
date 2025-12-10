# Skills

Skills are markdown files that teach Claude Code how to perform specific tasks. Unlike plugins (which have commands and scripts), skills are pure knowledge/instruction files.

## Available Skills

| Skill | Description |
|-------|-------------|
| [excalidraw-generator](./excalidraw-generator.md) | Generate architecture diagrams as .excalidraw files from codebase analysis |

## Installation

Skills are installed at the **user level** in Claude Code:

```bash
# Option 1: Copy skill file to your Claude Code settings
# Skills go in ~/.claude/skills/ (create if doesn't exist)
mkdir -p ~/.claude/skills
cp skills/excalidraw-generator.md ~/.claude/skills/

# Option 2: Reference the skill directly when prompting
# Just ask Claude Code to use the skill by describing what you want
```

## Usage

Once installed, Claude Code will automatically use the skill when you ask related questions:

```
"Generate an architecture diagram for this project"
"Create an excalidraw diagram of the system"
"Visualize this codebase as an excalidraw file"
```

## Skill vs Plugin

| Aspect | Skill | Plugin |
|--------|-------|--------|
| Format | Single markdown file | Folder with plugin.json, scripts, skills |
| Commands | No slash commands | Has `/command` support |
| Scripts | No code execution | Can have Python/Node scripts |
| Use case | Teaching Claude patterns/formats | Complex workflows with tools |

## Adding New Skills

1. Create a markdown file in this folder
2. Follow the pattern: clear instructions, examples, critical rules
3. Update this README with the new skill
