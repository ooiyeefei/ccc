---
description: Generate a professional slide deck using Anthropic Platform Skills API
---

# Deckling - PPTX Generator

Generate or refine PowerPoint presentations using Anthropic's Platform Skills API.

## Usage

```
/deckling "Topic - number of slides"
/deckling "Instruction" --refine existing.pptx
```

## Examples

```
/deckling "Quarterly Review - 3 slides"
/deckling "Company overview - 5 slides, professional"
/deckling "Change the title to 'Q4 Results'" --refine quarterly_report.pptx
```

## Instructions

Use the `deckling-pptx` skill to execute this command. The skill file is located at `skills/deckling-pptx.md` relative to this plugin.

Run the worker script at `scripts/deckling_worker.py` with the user's topic or instruction.
