# scripts/check_split_file_sizes.py

# ----------------------------------------
# Split File Size Checker
# ----------------------------------------
# - Walks all .json files in the split/ directory
# - Warns if any file exceeds 50MB (e.g. for TypingMind)
# - Prints size in MB + character count
# - Acts as a sanity check after file splitting
# ----------------------------------------

import os
import sys
import json
import argparse
from pathlib import Path
# Import logging setup from config.py
from config import setup_logging

# Call the setup function to configure logging
setup_logging()

# Now you can use logging throughout the script
import logging

# Import configured SPLIT_DIR from project root
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import SPLIT_DIR as DEFAULT_DIR

# Max safe size in bytes (50MB threshold)
MAX_BYTES = 50 * 1024 * 1024

# ----------------------------------------
# Check each file in the split output directory
# ----------------------------------------
def check_file_sizes(directory: Path):
    too_large = []

    logging.info(f"Checking files in: {directory}")

    for file in directory.glob("*.json"):
        size_bytes = os.path.getsize(file)
        size_mb = round(size_bytes / (1024 * 1024), 2)

        data = json.loads(file.read_text(encoding="utf-8"))
        char_count = sum(len(c.get("content", "")) for c in data)

        tag = "⚠️ OVER 50MB" if size_bytes > MAX_BYTES else "OK"
        logging.info(f"{file.name:40}  | {size_mb:6} MB  | {char_count:>7} chars  | {tag}")

        if size_bytes > MAX_BYTES:
            too_large.append(file.name)

    if too_large:
        logging.error("Warning: Some files exceed 50MB and may break LLM tools.")
        sys.exit(1)
    else:
        logging.info("All files are under 50MB.")

# ----------------------------------------
# CLI entrypoint
# ----------------------------------------
def main():
    logging.info("Script started: check_split_file_sizes.py")
    try:
        parser = argparse.ArgumentParser(description="Warn if any output .json files are over 50MB.")
        parser.add_argument("--input", type=str, default=DEFAULT_DIR, help="Directory with split .json files")
        args = parser.parse_args()

        target_dir = Path(args.input)
        check_file_sizes(target_dir)
        logging.info("Script finished successfully: check_split_file_sizes.py")
    except Exception as e:
        logging.error(f"Script failed: check_split_file_sizes.py, Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
