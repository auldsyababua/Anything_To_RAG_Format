# scripts/split_ready_for_customgpt.py

import json
import unicodedata
import re
from pathlib import Path
from collections import defaultdict
import sys, os
from urllib.parse import urlparse

# Import logging setup from config.py
from config import setup_logging

# Call the setup function to configure logging
setup_logging()

# Now you can use logging throughout the script
import logging

# ----------------------------------------
# Chunk Splitter for CustomGPT Compatibility
# ----------------------------------------
# Purpose:
# - Split the cleaned full chunk list into one JSON file per source doc group
# - Group by domain of source field
# - Normalize filenames to be ASCII-safe and lowercase
# Output:
# - One file per domain in split/
# ----------------------------------------

# Enable relative import of project config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CLEAN_FULL_OUTPUT_FILE as INPUT_FILE, SPLIT_DIR as OUTPUT_DIR

def normalize(name: str) -> str:
    """
    Normalize file-safe name from source string:
    - Convert Unicode to ASCII
    - Lowercase
    - Remove trailing _pdf or known patterns
    - Replace non-alphanum with underscores
    """
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii").lower()
    name = re.sub(r"\.json$", "", name)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_anna[^a-z0-9]*s[^a-z0-9]*archive(_pdf)?$", "", name)
    name = re.sub(r"_pdf$", "", name)
    return re.sub(r"_+", "_", name).strip("_")

# Load cleaned merged chunk list from full output file
chunks = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

# Group chunks by normalized domain (project root)
def get_group_key(chunk):
    source = chunk.get("source", "")
    parsed = urlparse(source)
    return parsed.netloc or "unknown_source"

groups = defaultdict(list)
for chunk in chunks:
    group_key = get_group_key(chunk)
    groups[group_key].append({
        "source": chunk["source"],
        "content": chunk["content"],
        "metadata": chunk.get("metadata", {})
    })

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Write one .json file per group (by normalized domain name)
for group_key, entries in groups.items():
    out_path = OUTPUT_DIR / f"{normalize(group_key)}.json"
    out_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2))

def main():
    logging.info("Script started: split_ready_for_customgpt.py")
    try:
        # Load cleaned merged chunk list from full output file
        chunks = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

        # Group chunks by normalized domain (project root)
        groups = defaultdict(list)
        for chunk in chunks:
            group_key = get_group_key(chunk)
            groups[group_key].append({
                "source": chunk["source"],
                "content": chunk["content"],
                "metadata": chunk.get("metadata", {})
            })

        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Write one .json file per group (by normalized domain name)
        for group_key, entries in groups.items():
            out_path = OUTPUT_DIR / f"{normalize(group_key)}.json"
            out_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2))

        logging.info("Script finished successfully: split_ready_for_customgpt.py")
    except Exception as e:
        logging.error(f"Script failed: split_ready_for_customgpt.py, Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
