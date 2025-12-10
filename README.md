# Claude Code Custom Plugins & Skills

Custom plugins and skills for [Claude Code](https://github.com/anthropics/claude-code).

## Available

| Name | Type | Description | Install Command |
|------|------|-------------|-----------------|
| [deckling](./plugins/deckling) | Plugin | Generate PPTX presentations using Anthropic Platform Skills API | `/plugin install deckling@ccc` |
| [ccc-skills](./skills) | Skills | Collection including Excalidraw diagram generation | `/plugin install ccc-skills@ccc` |

---

## Installation

```bash
# Add this repo as a marketplace
/plugin marketplace add ooiyeefei/ccc

# Install the deckling plugin (has /deckling command)
/plugin install deckling@ccc

# Install the skills collection (includes excalidraw)
/plugin install ccc-skills@ccc
```

---

## Plugin: Deckling

Generate and refine PowerPoint presentations using Anthropic's Platform Skills API.

```bash
/deckling "Quarterly Review - 3 slides"
/deckling "Change title to 'Q4 Results'" --refine quarterly.pptx
```

See [plugins/deckling/README.md](./plugins/deckling/README.md) for full documentation.

---

## Skill: Excalidraw Generator

Generate architecture diagrams from any codebase as `.excalidraw` files.

**After installing ccc-skills, just ask Claude Code:**
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

See [skills/excalidraw/SKILL.md](./skills/excalidraw/SKILL.md) for full documentation.

---

## License

MIT
