# scripts/normalize_filenames.py

import re
import unicodedata
from pathlib import Path
import sys
import os

# Enable relative import from project root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import SOURCE_FOLDER as SOURCE_DIR

# ----------------------------------------
# Normalize and Rename PDF Filenames
# ----------------------------------------
# Applies consistent formatting to all PDFs in SOURCE_DIR:
# - Converts names to ASCII
# - Lowercases all text
# - Replaces non-alphanumeric characters with underscores
# - Removes archive-specific suffixes
# - Eliminates redundant underscores

def normalize_filename(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_anna[^a-z0-9]*s[^a-z0-9]*archive(_pdf)?$", "", name)
    name = re.sub(r"(_)+", "_", name)
    return name.strip("_")

def rename_all(folder: Path):
    for path in folder.glob("*.pdf"):
        normalized = normalize_filename(path.stem)
        new_path = path.with_name(normalized + path.suffix)
        if path != new_path:
            path.rename(new_path)
            print(f"{path.name} -> {new_path.name}")

if __name__ == "__main__":
    rename_all(SOURCE_DIR)
