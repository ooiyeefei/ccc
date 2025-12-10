# Claude Code Custom Plugins & Skills

Custom plugins and skills for [Claude Code](https://github.com/anthropics/claude-code).

## What's the Difference?

| Type | Format | Use Case |
|------|--------|----------|
| **Plugin** | Folder with `plugin.json`, scripts, skills | Complex workflows with `/commands` and tool execution |
| **Skill** | Single markdown file | Teaching Claude patterns, formats, and knowledge |

---

## Available Plugins

| Plugin | Description | Command |
|--------|-------------|---------|
| [deckling](./plugins/deckling) | Generate professional PPTX presentations using Anthropic Platform Skills API | `/deckling` |

## Available Skills

| Skill | Description |
|-------|-------------|
| [excalidraw-generator](./skills/excalidraw-generator.md) | Generate architecture diagrams as .excalidraw files from codebase analysis |

---

## Installation

### Prerequisites

- [Claude Code](https://github.com/anthropics/claude-code) installed

### Quick Install (Recommended)

```bash
# Add this repo as a marketplace (no git clone needed!)
/plugin marketplace add ooiyeefei/ccc

# Install a plugin
/plugin install deckling@ccc

# Skills are automatically available after marketplace add
```

### Alternative: Local Install

```bash
# Clone this repository
git clone https://github.com/ooiyeefei/ccc.git
cd ccc

# Add as a local marketplace
/plugin marketplace add .

# Install a plugin
/plugin install deckling@ccc
```

### Install a Skill Manually

If you only want skills (without plugins):

```bash
# Create skills directory
mkdir -p ~/.claude/skills

# Download skill file directly
curl -o ~/.claude/skills/excalidraw-generator.md \
  https://raw.githubusercontent.com/ooiyeefei/ccc/main/skills/excalidraw-generator.md
```

---

## Plugin Details

### Deckling

Generate and refine PowerPoint presentations using Anthropic's Platform Skills API.

```bash
# Generate new slides
/deckling "Quarterly Review - 3 slides"

# Refine existing slides
/deckling "Change title to 'Q4 Results'" --refine quarterly.pptx
```

See [plugins/deckling/README.md](./plugins/deckling/README.md) for full documentation.

---

## Skill Details

### Excalidraw Generator

Generate architecture diagrams from any codebase as `.excalidraw` files.

**Usage** (just ask Claude Code):
```
"Generate an architecture diagram for this project"
"Create an excalidraw diagram of the system"
"Visualize this codebase as an excalidraw file"
```

**Features:**
- Analyzes any codebase (Node.js, Python, Java, Go, etc.)
- No prerequisites - works without existing diagrams or Terraform
- Proper 90-degree elbow arrows (not curved)
- Color-coded components by type (database, API, storage, etc.)
- Dynamic IDs and labels based on discovered components

See [skills/excalidraw-generator.md](./skills/excalidraw-generator.md) for full documentation.

---

## License

MIT
