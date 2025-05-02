# scripts/validate_json_output.py

import json
from pathlib import Path
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import SPLIT_DIR as TARGET_DIR

# Validate structure of all .json files in /split
# Each must be a list of dicts with "source" and "content"

def validate(directory: Path):
    has_error = False

    for file in directory.glob("*.json"):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))

            if not isinstance(data, list):
                raise ValueError("Top-level object is not a list")

            for entry in data:
                if "source" not in entry or "content" not in entry:
                    raise ValueError("Missing 'source' or 'content' key")

        except Exception as e:
            print(f"INVALID  {file.name}: {e}")
            has_error = True
        else:
            print(f"VALID    {file.name}")

    if has_error:
        exit(1)

if __name__ == "__main__":
    validate(TARGET_DIR)
