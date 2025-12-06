#!/usr/bin/env python3
"""
Deckling Worker - Calls Anthropic Platform Skills API to generate PPTX files.

Usage:
    python3 deckling_worker.py "Topic for presentation"
    python3 deckling_worker.py "Make slide 2 blue" --refine existing.pptx
    python3 deckling_worker.py "file_id_here" --recover

Environment:
    ANTHROPIC_API_KEY must be set

Note: Platform Skills uses an agentic loop. The API may return tool_use blocks
that require continuation. This script handles that automatically.
"""

import os
import sys
import argparse
import time
import anthropic


def upload_for_refinement(client: anthropic.Anthropic, filepath: str) -> str:
    """
    Upload a local PPTX file to Anthropic's Files API for refinement.
    Returns the file_id that can be attached to messages.
    """
    print(f"Uploading {filepath} for refinement...")
    try:
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            file_obj = client.beta.files.upload(
                file=(filename, f, "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
            )
        print(f"Upload complete. FILE_ID_INPUT: {file_obj.id}")
        return file_obj.id
    except Exception as e:
        print(f"Upload Error: {e}")
        sys.exit(1)


def download_file(client: anthropic.Anthropic, file_id: str, filename: str) -> bool:
    """Download a file from Anthropic's Files API and save to disk."""
    print(f"Downloading File ID: {file_id}...")
    try:
        response = client.beta.files.download(
            file_id=file_id,
            betas=["files-api-2025-04-14"]
        )

        # write_to_file expects a path string, not a file object
        response.write_to_file(filename)

        print(f"Success! Saved to: {os.path.abspath(filename)}")
        return True

    except Exception as e:
        print(f"Download Error: {e}")
        return False


def extract_file_id(obj) -> str | None:
    """
    Recursively search for file_id in any nested structure.
    Platform Skills returns file references in various places.
    """
    if isinstance(obj, dict):
        # Direct file_id key
        if 'file_id' in obj:
            return obj['file_id']
        # Check for file references in content
        if obj.get('type') == 'file' and 'id' in obj:
            return obj['id']
        # Recurse into values
        for value in obj.values():
            result = extract_file_id(value)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = extract_file_id(item)
            if result:
                return result
    return None


def get_next_version_filename(original_path: str) -> str:
    """
    Generate a versioned filename (e.g., file.pptx -> file_v2.pptx -> file_v3.pptx).
    Never overwrites the original file.
    """
    base, ext = os.path.splitext(original_path)

    # Check if already versioned
    if base.endswith('_v2'):
        base = base[:-3]
        version = 3
    elif '_v' in base:
        # Extract existing version number
        parts = base.rsplit('_v', 1)
        if parts[1].isdigit():
            base = parts[0]
            version = int(parts[1]) + 1
        else:
            version = 2
    else:
        version = 2

    # Find next available version
    while os.path.exists(f"{base}_v{version}{ext}"):
        version += 1

    return f"{base}_v{version}{ext}"


def run_agentic_loop(
    client: anthropic.Anthropic,
    messages: list,
    output_filename: str,
    operation_name: str = "Processing"
) -> None:
    """
    Run the agentic conversation loop until a file is produced.
    Shared by both generate and refine operations.
    """
    start_time = time.time()
    max_iterations = 50
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            response = client.beta.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=16000,
                betas=["code-execution-2025-08-25", "skills-2025-10-02"],
                container={
                    "skills": [{"type": "anthropic", "skill_id": "pptx", "version": "latest"}]
                },
                tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
                messages=messages
            )
        except anthropic.APIError as e:
            print(f"API Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            sys.exit(1)

        # Check for file_id in response
        response_dict = response.model_dump()
        file_id = extract_file_id(response_dict)

        if file_id:
            # Found a file! Print immediately for recovery
            elapsed = time.time() - start_time
            print(f"\nFILE_ID: {file_id}")
            print(f"{operation_name} time: {elapsed:.1f} seconds")

            download_file(client, file_id, output_filename)
            return

        # Check stop reason
        stop_reason = response.stop_reason

        if stop_reason == "end_turn":
            # Model finished but no file found
            print(f"\n{operation_name} completed but no file was produced.")
            print("Response content:")
            for block in response.content:
                if hasattr(block, 'text'):
                    print(block.text[:500])
            return

        elif stop_reason == "tool_use":
            # Model wants to use a tool - continue the conversation
            print(f"[Step {iteration}] {operation_name}...", end="\r")

            # Add assistant response to messages
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # For server-side tool execution, add empty tool results
            tool_results = []
            for block in response.content:
                if hasattr(block, 'type') and block.type == 'tool_use':
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": ""
                    })

            if tool_results:
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

            continue

        else:
            print(f"Unexpected stop reason: {stop_reason}")
            print("Response content:")
            for block in response.content:
                if hasattr(block, 'text'):
                    print(block.text[:200])
            return

    print(f"Warning: Reached max iterations ({max_iterations}) without completing.")


def generate_presentation(client: anthropic.Anthropic, topic: str) -> None:
    """Generate a new PPTX presentation."""
    print(f"Deckling: Generating slides for '{topic}'...")
    print("Calling Anthropic Platform Skills API...")
    print("(This may take 1-2 minutes as the AI creates your slides...)\n")

    messages = [{
        "role": "user",
        "content": f"Create a PowerPoint presentation: {topic}. Keep it concise. Save the file and return it."
    }]

    # Generate safe filename
    safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
    safe_topic = safe_topic.replace(' ', '_')[:50]
    filename = f"{safe_topic}.pptx"

    run_agentic_loop(client, messages, filename, "Generation")


def refine_presentation(client: anthropic.Anthropic, instruction: str, filepath: str) -> None:
    """
    Refine an existing PPTX presentation.
    Uploads the file, applies changes, and downloads as a new version.
    """
    # Validate file exists
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    if not filepath.lower().endswith('.pptx'):
        print(f"Error: File must be a .pptx file: {filepath}")
        sys.exit(1)

    print(f"Deckling: Refining '{os.path.basename(filepath)}'...")
    print(f"Instruction: {instruction}")
    print("(Uploading file and applying changes...)\n")

    # Step 1: Upload the file
    input_file_id = upload_for_refinement(client, filepath)

    # Step 2: Build message with file attachment
    # Use container_upload for files that will be processed by code execution
    messages = [{
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"Open the attached PowerPoint presentation. {instruction}. Save the modified file and return it."
            },
            {
                "type": "container_upload",
                "file_id": input_file_id
            }
        ]
    }]

    # Step 3: Generate versioned output filename (never overwrite)
    output_filename = get_next_version_filename(filepath)

    # Step 4: Run the agentic loop
    run_agentic_loop(client, messages, output_filename, "Refinement")


def main():
    parser = argparse.ArgumentParser(
        description="Generate or refine PPTX using Anthropic Platform Skills"
    )
    parser.add_argument(
        "input",
        help="Topic string (for new) OR instruction (with --refine) OR file_id (with --recover)"
    )
    parser.add_argument(
        "--refine",
        metavar="FILE",
        help="Refine an existing PPTX file with the given instruction"
    )
    parser.add_argument(
        "--recover",
        action="store_true",
        help="Download an existing file by ID (skip generation)"
    )
    args = parser.parse_args()

    # Check for API key - fail fast with helpful message
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("\nTo fix this, run:")
        print("  export ANTHROPIC_API_KEY='sk-ant-api03-...'")
        print("\nThen run /deckling again.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if args.recover:
        # Recovery mode - just download existing file
        print("Recovery Mode: Downloading existing file...")
        download_file(client, args.input, "recovered_presentation.pptx")
    elif args.refine:
        # Refine mode - upload existing file, apply changes, download new version
        refine_presentation(client, args.input, args.refine)
    else:
        # Normal mode - generate new presentation
        generate_presentation(client, args.input)


if __name__ == "__main__":
    main()
