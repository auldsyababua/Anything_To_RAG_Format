# scripts/check_split_file_sizes.py

import json
from pathlib import Path
from config import SPLIT_DIR

# ----------------------------------------
# File Size and Character Counter
# ----------------------------------------
# Prints file size (MB) and total character count for each .json in /split
# Flags files exceeding 50MB for downstream embedding constraints.

MAX_MB = 50
BYTES_LIMIT = MAX_MB * 1024 * 1024

for fpath in SPLIT_DIR.glob("*.json"):
    size = fpath.stat().st_size
    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
        chars = sum(len(entry["content"]) for entry in data if "content" in entry)
    except Exception as e:
        print(f"❌ {fpath.name} — parse error: {e}")
        continue

    print(f"{fpath.name} → {size / 1024 / 1024:.1f}MB, {chars:,} chars")
    if size > BYTES_LIMIT:
        print(f"❌ EXCEEDS LIMIT")
