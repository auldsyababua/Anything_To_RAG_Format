# scripts/split_large_json_files.py

import json
from pathlib import Path
from config import SPLIT_DIR

# ----------------------------------------
# Large Chunk JSON Splitter
# ----------------------------------------
# If a .json file in /split exceeds CHAR_LIMIT characters in total,
# it is broken into multiple sequential files with suffixes (_part1, _part2, ...).
# Original file is deleted after successful split.

CHAR_LIMIT = 2_000_000  # max characters per output JSON file

def split_large_file(filepath: Path):
    data = json.loads(filepath.read_text(encoding="utf-8"))
    total_chars = sum(len(chunk.get("content", "")) for chunk in data)

    if total_chars <= CHAR_LIMIT:
        return  # No need to split

    # Split into blocks below threshold
    chunks = []
    current = []
    char_sum = 0

    for entry in data:
        entry_len = len(entry.get("content", ""))
        if char_sum + entry_len > CHAR_LIMIT and current:
            chunks.append(current)
            current = []
            char_sum = 0
        current.append(entry)
        char_sum += entry_len

    if current:
        chunks.append(current)

    base_path = filepath.with_suffix("")
    for i, part in enumerate(chunks, 1):
        out_path = base_path.parent / f"{base_path.name}_part{i}.json"
        out_path.write_text(json.dumps(part, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ Wrote {len(part)} chunks to {out_path.name}")

    filepath.unlink()
    print(f"🗑️  Removed original: {filepath.name}")

# Apply to all JSON files in split/
for json_path in SPLIT_DIR.glob("*.json"):
    split_large_file(json_path)
