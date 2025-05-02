# scripts/filter_chunks.py

import json
import sys
import os
from pathlib import Path

# Enable relative import from repo root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import FILTER_INPUT_FILE

# ----------------------------------------
# Chunk Filter and Deduplicator
# ----------------------------------------
# Removes boilerplate/disclaimer chunks and redundant text chunks
# from a merged full JSON file. Output is saved with -cleaned suffix.

# Keywords to filter out typical boilerplate/legal noise
KEYWORDS_TO_EXCLUDE = [
    "copyright", "all rights reserved", "isbn", "no part of this publication",
    "printed in the united states", "cengage learning", "reproduction prohibited"
]

# Test if a chunk is boilerplate based on known phrases
def is_boilerplate(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS_TO_EXCLUDE)

# Remove duplicated chunk content (case/space-insensitive)
def deduplicate_chunks(chunks):
    seen = set()
    deduped = []
    for chunk in chunks:
        sig = hash(chunk["content"].strip().lower())
        if sig not in seen:
            seen.add(sig)
            deduped.append(chunk)
    return deduped

# Orchestrate filter + dedup + save
def filter_chunks(input_path: Path, output_path: Path):
    chunks = json.loads(input_path.read_text(encoding="utf-8"))

    filtered = [chunk for chunk in chunks if not is_boilerplate(chunk["content"])]
    deduped = deduplicate_chunks(filtered)

    output_path.write_text(json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Filtered {len(chunks) - len(filtered)} boilerplate chunks.")
    print(f"Removed {len(filtered) - len(deduped)} duplicate chunks.")
    print(f"Saved {len(deduped)} cleaned chunks to {output_path}.")

if __name__ == "__main__":
    input_path = Path(FILTER_INPUT_FILE)
    output_clean = input_path.with_name(input_path.stem + "-cleaned.json")
    filter_chunks(input_path, output_clean)
