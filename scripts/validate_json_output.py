# scripts/validate_json_output.py

# ----------------------------------------
# Output JSON Validator
# ----------------------------------------
# Verifies that each .json file in the split/ directory:
# - Is a valid JSON list
# - Contains dicts with both "source" and "content" keys
# - Can be parsed without crashing
# If any file fails validation, process exits with code 1.
# ----------------------------------------

import json
import sys
import os
from pathlib import Path

# Load SPLIT_DIR from project root
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import SPLIT_DIR as TARGET_DIR

# ----------------------------------------
# Validate one directory of JSON files
# ----------------------------------------
def validate(directory: Path):
    has_error = False

    print(f"\n[🔍] Validating chunk structure in: {directory}")

    for file in directory.glob("*.json"):
        try:
            # Read file and load JSON
            data = json.loads(file.read_text(encoding="utf-8"))

            # Top-level object must be a list
            if not isinstance(data, list):
                raise ValueError("Top-level JSON object is not a list.")

            # Each entry must be a dict with required fields
            for i, entry in enumerate(data):
                if not isinstance(entry, dict):
                    raise ValueError(f"Entry {i} is not a dict.")
                if "source" not in entry or "content" not in entry:
                    raise ValueError(f"Missing required keys in entry {i}.")

        except Exception as e:
            print(f"❌ INVALID  {file.name}: {e}")
            has_error = True
        else:
            print(f"✅ VALID    {file.name}")

    if has_error:
        print("\n[❌] Validation failed. Some files are malformed.")
        sys.exit(1)
    else:
        print("\n[✅] All files passed schema validation.")

# ----------------------------------------
# CLI entrypoint
# ----------------------------------------
def main():
    validate(TARGET_DIR)

if __name__ == "__main__":
    main()
