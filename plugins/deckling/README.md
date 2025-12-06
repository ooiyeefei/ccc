# Deckling

A Claude Code plugin that generates professional PowerPoint presentations using Anthropic's Platform Skills API.

**Why Deckling?** Traditional approaches like `python-pptx` produce ugly slides because LLMs guess text box coordinates. Deckling uses Anthropic's server-side rendering engine for high-fidelity, professional results.

## Features

- **Generate** - Create new presentations from a topic description
- **Refine** - Edit existing presentations with natural language instructions
- **Recover** - Download files if generation succeeds but download fails

## Installation

### Prerequisites

- [Claude Code](https://github.com/anthropics/claude-code) installed
- Python 3.8+
- Anthropic API key with access to Platform Skills

### Install the Plugin

```bash
# Clone the repository
git clone https://github.com/ooiyeefei/ccc.git
cd ccc

# Add as a local marketplace and install
/plugin marketplace add .
/plugin install deckling@ccc
```

### Install Dependencies

```bash
pip install anthropic
```

### Set API Key

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'
```

## Usage

### Generate a New Presentation

```
/deckling "Quarterly Business Review - 3 slides"
```

```
/deckling "Introduction to Machine Learning - 5 slides, professional style"
```

### Refine an Existing Presentation

Edit text, add slides, or modify styling:

```
/deckling "Change the title to 'Q4 Results'" --refine quarterly.pptx
```

```
/deckling "Make all backgrounds dark blue" --refine my_deck.pptx
```

```
/deckling "Add a new slide about pricing at the end" --refine product.pptx
```

**Note:** Refine creates a versioned file (e.g., `my_deck_v2.pptx`) and never overwrites the original.

### Recover a Lost File

If generation succeeds but download fails, use the FILE_ID from the output:

```
/deckling "file_abc123" --recover
```

## How It Works

Deckling uses Anthropic's [Platform Skills API](https://docs.anthropic.com/en/docs/build-with-claude/skills) which provides server-side document generation. The workflow:

1. **Generate**: Send topic to API → Claude creates slides in a container → Download PPTX
2. **Refine**: Upload existing file → Send edit instructions → Download new version

The API runs an agentic loop (multi-turn conversation) which this plugin handles automatically.

## Cost

- Generation and refinement use API credits for conversation + code execution
- Simpler prompts (fewer slides) = faster + cheaper
- Typical generation: 20-60 seconds

## Roadmap

- [ ] `--template` flag for branded presentations using a style template

## License

MIT

## Contributing

Issues and PRs welcome!
