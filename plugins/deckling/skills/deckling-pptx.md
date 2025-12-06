# Deckling PPTX Generator

Use this skill when the user runs `/deckling` to create or refine PowerPoint presentations.

## Critical Rules

1. **DO NOT** use `python-pptx`, `pptx`, or any local Python library to generate slides.
2. **DO NOT** write your own slide generation code.
3. **DO** use the provided `deckling_worker.py` script which calls Anthropic's Platform Skills API.

## Why This Matters

- `python-pptx` produces ugly slides because the LLM guesses text box coordinates
- Anthropic Platform Skills uses a server-side rendering engine that produces professional, high-fidelity PPTX files
- The worker script handles all API complexity (beta headers, file upload/download, agentic loop, error recovery)

## Execution Logic

The worker script is located at `scripts/deckling_worker.py` relative to the plugin root.

**To find the script:**
1. This skill file is in the `skills/` subdirectory of the Deckling plugin
2. The worker script is in the `scripts/` subdirectory of the same plugin
3. Determine the absolute path to the plugin folder, then construct the path to `scripts/deckling_worker.py`

## Usage Modes

### Mode 1: Generate New Presentation

```bash
python3 /path/to/deckling_worker.py "Topic - 3 slides about X"
```

**Example:**
```bash
python3 /path/to/deckling_worker.py "Company overview - 3 slides, professional"
```

### Mode 2: Refine Existing Presentation

```bash
python3 /path/to/deckling_worker.py "Instruction to apply" --refine existing.pptx
```

**Example:**
```bash
python3 /path/to/deckling_worker.py "Change the title to 'Q4 Results'" --refine quarterly_report.pptx
python3 /path/to/deckling_worker.py "Make the background blue on all slides" --refine my_deck.pptx
python3 /path/to/deckling_worker.py "Add a new slide about pricing at the end" --refine product_intro.pptx
```

**Important:** Refine mode creates a new versioned file (e.g., `my_deck_v2.pptx`) and NEVER overwrites the original.

### Mode 3: Recover Lost File

If generation succeeds but download fails, use the FILE_ID printed in the output:

```bash
python3 /path/to/deckling_worker.py "file_abc123" --recover
```

## Example Workflow

**User:** `/deckling "Quarterly Business Review - 3 slides"`

You execute:
```bash
python3 /absolute/path/to/deckling-plugin/scripts/deckling_worker.py "Quarterly Business Review - 3 slides"
```

**User:** `/deckling "Add a slide about next quarter goals" --refine Quarterly_Business_Review.pptx`

You execute:
```bash
python3 /absolute/path/to/deckling-plugin/scripts/deckling_worker.py "Add a slide about next quarter goals" --refine Quarterly_Business_Review.pptx
```

Output: `Quarterly_Business_Review_v2.pptx`

## Expected Output

On success, the script will:
1. Print progress messages and timing
2. Print the FILE_ID (for recovery if needed)
3. Save a `.pptx` file to the current working directory
4. Print the absolute path to the saved file

Report the file location to the user when complete.

## Cost Awareness

- **Generation:** Uses API credits for the conversation + code execution
- **Refinement:** Uses API credits for upload + conversation + code execution (slightly more expensive)
- Simpler prompts (fewer slides) = faster + cheaper
