# Excalidraw - Architecture Diagram Generator

Generate architecture diagrams as `.excalidraw` files from codebase analysis, with optional PNG and SVG export.

---

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Quick Start

After installing, just ask Claude Code:

```
"Generate an architecture diagram for this project"
"Create an excalidraw diagram of the system"
"Visualize this codebase as an excalidraw file"
```

Claude Code will analyze any codebase (Node.js, Python, Java, Go, etc.), identify components, map relationships, and generate a valid `.excalidraw` JSON file.

## Features

- **Any codebase**: Discovers services, databases, APIs, and infrastructure from source code
- **No prerequisites**: Works without existing diagrams, Terraform, or specific file types
- **Proper arrows**: 90-degree elbow arrows with correct edge binding (not curved)
- **Color-coded**: Components styled by type (database, API, storage, AI/ML, etc.)
- **Cloud palettes**: AWS, Azure, GCP, and Kubernetes color schemes
- **Multiple layouts**: Vertical flow, horizontal pipeline, hub-and-spoke patterns
- **PNG/SVG export**: Optionally export to PNG and/or SVG via Playwright

## PNG/SVG Export

After generating a diagram, Claude Code will ask if you want to export to PNG, SVG, or both.

The export uses `@excalidraw/utils` loaded in a Playwright browser — fully programmatic, no manual upload to excalidraw.com needed.

**Requirements:** Playwright MCP tools must be available.

**Output:** Exported files are saved alongside the `.excalidraw` file:
```
docs/architecture/
├── system-architecture.excalidraw    # Editable diagram
├── system-architecture.svg           # Vector export
└── system-architecture.png           # Raster export
```

## Output

- **Location**: `docs/architecture/` or user-specified path
- **Format**: `.excalidraw` JSON (editable in [excalidraw.com](https://excalidraw.com) or VS Code extension)
- **Exports**: `.svg` and `.png` viewable directly or embeddable in documentation

## Reference Files

The skill includes detailed reference documentation:

| File | Contents |
|------|----------|
| `references/json-format.md` | Element types, required properties, text bindings |
| `references/arrows.md` | Routing algorithm, patterns, bindings, staggering |
| `references/colors.md` | Default, AWS, Azure, GCP, K8s palettes |
| `references/examples.md` | Complete JSON examples, layout patterns |
| `references/validation.md` | Checklists, validation algorithm, bug fixes |
| `references/export.md` | PNG/SVG export procedure via Playwright |

## License

MIT
