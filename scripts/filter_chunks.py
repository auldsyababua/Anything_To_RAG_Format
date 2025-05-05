# scripts/filter_chunks.py

# ----------------------------------------
# Chunk Filter: Remove Filler and Repetition
# ----------------------------------------
# - Strips legal boilerplate, disclaimers, navigation junk
# - Drops chunks with known non-informative patterns
# - Preserves useful metadata + markdown
# ----------------------------------------

import json
import re
import argparse
import sys
from pathlib import Path

# Import logging setup from config.py
from config import setup_logging

# Call the setup function to configure logging
setup_logging()

# Now you can use logging throughout the script
import logging

# Import config paths
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import CLEAN_FULL_OUTPUT_FILE, FULL_OUTPUT_FILE

# ----------------------------------------
# Known junk phrases to remove
# Expand this list to refine filtering
# ----------------------------------------
JUNK_PATTERNS = [
    r"(?i)all rights reserved",
    r"(?i)this page was last updated",
    r"(?i)copyright \d{4}",
    r"(?i)terms of service",
    r"(?i)privacy policy",
    r"(?i)enable javascript",
    r"(?i)cookie consent",
    r"(?i)log in to your account",
    r"(?i)subscribe to our newsletter",
    r"(?i)accept cookies"
]

# ----------------------------------------
# Return True if a chunk should be excluded
# ----------------------------------------
def is_junk(text: str) -> bool:
    return any(re.search(pat, text) for pat in JUNK_PATTERNS)

# ----------------------------------------
# Entry point
# ----------------------------------------
def main():
    logging.info("Script started: filter_chunks.py")
    try:
        parser = argparse.ArgumentParser(description="Filter boilerplate from chunks.")
        parser.add_argument("--input", type=str, default=CLEAN_FULL_OUTPUT_FILE, help="Path to cleaned file")
        parser.add_argument("--output", type=str, default=FULL_OUTPUT_FILE.parent / "filtered.json", help="Filtered output path")
        args = parser.parse_args()

        input_path = Path(args.input)
        output_path = Path(args.output)

        # Read cleaned chunks from disk
        chunks = json.loads(input_path.read_text(encoding="utf-8"))
        kept = []

        # Drop empty or junk-matching content
        for chunk in chunks:
            content = chunk.get("content", "")
            if not content or is_junk(content):
                continue
            kept.append(chunk)

        # Write back to disk
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(kept, f, indent=2, ensure_ascii=False)

        logging.info(f"Filtered {len(kept)} chunks → {output_path}")
    except Exception as e:
        logging.error(f"Script failed: filter_chunks.py, Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
