# scripts/normalize_filenames.py

# ----------------------------------------
# Filename Normalizer
# ----------------------------------------
# Renames all files in the ingestion_source directory to:
# - Lowercase
# - ASCII-only
# - snake_case (no spaces or punctuation)
# Useful to prevent path issues or naming collisions in downstream scripts.
# ----------------------------------------

import os
import re
import sys
import unicodedata
import argparse
from pathlib import Path

# Load ingestion source directory from config
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import INGESTION_SOURCE

# ----------------------------------------
# Convert filename to snake_case and strip unsafe characters
# ----------------------------------------
def normalize_filename(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s-]+", "_", name)
    return name.strip("_")

# ----------------------------------------
# Walk ingestion directory and rename files
# ----------------------------------------
def normalize_filenames(dry_run=False):
    files = list(INGESTION_SOURCE.glob("*.*"))
    if not files:
        print(f"[INFO] No files found in {INGESTION_SOURCE}")
        return

    print(f"\n[🔁] Normalizing filenames in: {INGESTION_SOURCE}\n")

    for path in files:
        if not path.is_file():
            continue

        new_name = normalize_filename(path.stem) + path.suffix.lower()
        new_path = path.with_name(new_name)

        if new_path != path:
            if dry_run:
                print(f"[DRY RUN] Would rename: {path.name} → {new_name}")
            else:
                path.rename(new_path)
                print(f"[RENAMED ] {path.name} → {new_name}")

    print("\n[✅] Filename normalization complete.\n")

# ----------------------------------------
# CLI entrypoint
# ----------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Standardize filenames to safe snake_case.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without renaming files")
    args = parser.parse_args()

    normalize_filenames(dry_run=args.dry_run)

if __name__ == "__main__":
    main()
