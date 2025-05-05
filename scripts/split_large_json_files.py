# scripts/split_large_json_files.py

# ----------------------------------------
# Large File Splitter for TypingMind/LLM Constraints
# ----------------------------------------
# Splits large output files into smaller parts, each under ~50MB character limit
# Output format: domain.json, or domain_part1.json, etc.
# ----------------------------------------

import json
import os
import argparse
import sys
import re
from urllib.parse import urlparse
from pathlib import Path
from collections import defaultdict

# Import logging setup from config.py
from config import setup_logging

# Call the setup function to configure logging
setup_logging()

# Now you can use logging throughout the script
import logging

# Import config paths
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import CLEAN_FULL_OUTPUT_FILE, SPLIT_DIR

# Max size in characters per JSON file (~50MB for TypingMind etc.)
MAX_CHARS_PER_FILE = 50_000_000

# ----------------------------------------
# Normalize domain into safe slug for filename
# ----------------------------------------
def domain_slug(url):
    hostname = urlparse(url).hostname or "unknown"
    return hostname.replace(".", "-")

# Group all chunks under a single domain
def chunk_by_domain(chunks: list) -> dict:
    grouped = defaultdict(list)
    for chunk in chunks:
        url = chunk.get("metadata", {}).get("url") or chunk.get("url")
        domain = domain_slug(url) if url else "unknown"
        grouped[domain].append(chunk)
    return grouped

# Divide large chunk lists into multiple files under the char limit
def split_large_file(chunks: list, max_chars: int) -> list:
    parts = []
    buffer = []
    total = 0

    for chunk in chunks:
        size = len(json.dumps(chunk))
        if total + size > max_chars and buffer:
            parts.append(buffer)
            buffer = []
            total = 0
        buffer.append(chunk)
        total += size

    if buffer:
        parts.append(buffer)

    return parts

# Write split parts to disk with numbered suffixes if needed
def write_chunks(grouped_chunks: dict, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    for domain, chunks in grouped_chunks.items():
        parts = split_large_file(chunks, MAX_CHARS_PER_FILE)

        for i, part in enumerate(parts, 1):
            suffix = f"_part{i}" if len(parts) > 1 else ""
            filename = f"{domain}{suffix}.json"
            out_path = output_dir / filename

            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(part, f, indent=2, ensure_ascii=False)
                logging.info(f"Successfully wrote {filename} to disk")  # Log successful write
            except Exception as e:
                logging.error(f"Failed to write {filename} to disk, Error: {str(e)}")  # Log failure

# Main CLI entrypoint
def main():
    logging.info("Script started: split_large_json_files.py")  # Log when the script starts

    parser = argparse.ArgumentParser(description="Split large JSONs by domain slug.")
    parser.add_argument("--input", type=str, default=CLEAN_FULL_OUTPUT_FILE, help="Input cleaned file")
    parser.add_argument("--output", type=str, default=SPLIT_DIR, help="Output directory for split files")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    try:
        chunks = json.loads(input_path.read_text(encoding="utf-8"))
        grouped = chunk_by_domain(chunks)
        write_chunks(grouped, output_dir)
        logging.info(f"Script finished successfully: split_large_json_files.py")  # Log success
        print(f"[✅] Split into {len(grouped)} domain file(s) → {output_dir}")
    except Exception as e:
        logging.error(f"Script failed: split_large_json_files.py, Error: {str(e)}")  # Log failure
        print(f"[❌] Error: {str(e)}")  # Print the error to the console

# Main entry point of the script
if __name__ == "__main__":
    main()
