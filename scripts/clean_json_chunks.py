# scripts/clean_json_chunks.py

# ----------------------------------------
# Chunk Cleaner
# ----------------------------------------
# Takes unified output JSON (from smart_ingest)
# - Removes markdown image syntax
# - Strips inline HTML tags
# - Drops empty, junky, or short chunks
# - Preserves metadata + markdown if present
# Output: Cleaned version of unified.json → unified-clean.json
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

# Import canonical paths from config
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import FULL_OUTPUT_FILE, CLEAN_FULL_OUTPUT_FILE

# ----------------------------------------
# Utility: Clean raw content text
# ----------------------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)         # remove markdown images
    text = re.sub(r"<[^>]+>", "", text)                      # remove inline HTML tags
    text = re.sub(r"\s+", " ", text)                         # normalize whitespace
    return text.strip()

# ----------------------------------------
# Apply cleaning to a single chunk object
# Drops if empty or under threshold
# ----------------------------------------
def clean_chunk(chunk: dict) -> dict | None:
    content = chunk.get("content", "")
    cleaned = clean_text(content)

    if not cleaned or len(cleaned) < 40:
        return None  # drop if blank or too short

    # Strip everything except desired fields
    base = {
        "source": chunk.get("source", ""),
        "content": cleaned,
        "metadata": {}
    }

    # Extract only needed metadata
    meta = chunk.get("metadata", {})
    base["metadata"] = {
        "url": meta.get("url") or meta.get("canonicalUrl"),
        "title": meta.get("title"),
        "doc_id": meta.get("doc_id")
    }

    return base


# ----------------------------------------
# Entry Point
# ----------------------------------------
def main():
    logging.info("Script started: clean_json_chunks.py")
    try:
        parser = argparse.ArgumentParser(description="Clean and filter raw JSON chunks.")
        parser.add_argument("--input", type=str, default=FULL_OUTPUT_FILE, help="Path to raw unified.json")
        parser.add_argument("--output", type=str, default=CLEAN_FULL_OUTPUT_FILE, help="Path to save cleaned output")
        args = parser.parse_args()

        input_path = Path(args.input)
        output_path = Path(args.output)

        raw_chunks = json.loads(input_path.read_text(encoding="utf-8"))
        cleaned_chunks = []

        for chunk in raw_chunks:
            cleaned = clean_chunk(chunk)
            if cleaned:
                cleaned_chunks.append(cleaned)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_chunks, f, indent=2, ensure_ascii=False)

        logging.info(f"Cleaned {len(cleaned_chunks)} chunks → {output_path}")
    except Exception as e:
        logging.error(f"Script failed: clean_json_chunks.py, Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
