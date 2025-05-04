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

# Import logging setup from config.py
from config import setup_logging

# Call the setup function to configure logging
setup_logging()

# Now you can use logging throughout the script
import logging

# Load SPLIT_DIR from project root
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import SPLIT_DIR as TARGET_DIR

# ----------------------------------------
# Validate one directory of JSON files
# ----------------------------------------
def validate(directory: Path):
    has_error = False

    logging.info(f"Validating chunk structure in: {directory}")

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
            logging.error(f"INVALID {file.name}: {e}")
            has_error = True
        else:
            logging.info(f"VALID {file.name}")

    if has_error:
        logging.error("Validation failed. Some files are malformed.")
        sys.exit(1)
    else:
        logging.info("All files passed schema validation.")

# ----------------------------------------
# CLI entrypoint
# ----------------------------------------
def main():
    logging.info("Script started: validate_json_output.py")
    try:
        validate(TARGET_DIR)
        logging.info("Script finished successfully: validate_json_output.py")
    except Exception as e:
        logging.error(f"Script failed: validate_json_output.py, Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
