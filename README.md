# Claude Code Custom Plugins

Custom plugins for [Claude Code](https://github.com/anthropics/claude-code).

## Available Plugins

| Plugin | Description | Command |
|--------|-------------|---------|
| [deckling](./plugins/deckling) | Generate professional PPTX presentations using Anthropic Platform Skills API | `/deckling` |

## Installation

### Prerequisites

- [Claude Code](https://github.com/anthropics/claude-code) installed
- Refer to the [official Claude Code documentation](https://github.com/anthropics/claude-code) for setup

### Install a Plugin

```bash
# Clone this repository
git clone https://github.com/anthropics/ccc.git

# Symlink the plugin to your Claude Code plugins directory
ln -s $(pwd)/ccc/plugins/deckling ~/.claude/plugins/deckling
```

### Verify Installation

```bash
/help
```

You should see the plugin commands available.

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

## License

MIT
