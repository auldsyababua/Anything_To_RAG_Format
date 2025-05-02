# scripts/split_ready_for_customgpt.py

import json
import unicodedata
import re
from pathlib import Path
from collections import defaultdict
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CLEAN_FULL_OUTPUT_FILE as INPUT_FILE, SPLIT_DIR as OUTPUT_DIR

# Normalize to ASCII-safe lowercase filenames
def normalize(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"\.json$", "", name)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_anna[^a-z0-9]*s[^a-z0-9]*archive(_pdf)?$", "", name)
    name = re.sub(r"_pdf$", "", name)
    return re.sub(r"_+", "_", name).strip("_")

# Load cleaned full file
chunks = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

# Group by source field
groups = defaultdict(list)
for chunk in chunks:
    groups[chunk["source"]].append({
        "source": chunk["source"],
        "content": chunk["content"],
        "metadata": chunk.get("metadata", {})
    })

# Write each group to /split/{source}.json
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for source_name, entries in groups.items():
    out_path = OUTPUT_DIR / f"{normalize(source_name)}.json"
    out_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(entries)} chunks to {out_path.name}")
