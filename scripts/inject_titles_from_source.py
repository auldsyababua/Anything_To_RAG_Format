# scripts/inject_titles_from_source.py

# ----------------------------------------
# Metadata Title Injector
# ----------------------------------------
# Adds `metadata.title` to each chunk if not already present.
# Title is inferred from:
#   - metadata.url (slugified path)
#   - source filename (fallback)
# Only updates chunks that are missing a title.
# ----------------------------------------

import os
import sys
import json
import logging
from pathlib import Path

# Import logging setup from config.py
from config import setup_logging, REPO_ROOT

# Call the setup function to configure logging
setup_logging()

# Now you can use logging throughout the script
import logging

# Create logs in this step of the pipeline dynamically
logging.basicConfig(
    filename=log_file_path,  # Path to your log file
    level=logging.INFO,  # Log everything at INFO level and above
    format='%(asctime)s - %(message)s'  # Format with a timestamp
)

# Import configured split directory
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import SPLIT_DIR as TARGET_DIR

# ----------------------------------------
# Generate a title slug from a URL or filename
# e.g. "/docs/setup/index.html" → "setup"
# ----------------------------------------
def infer_title_from_url(url: str) -> str:
    path = Path(url).name or Path(url).parent.name
    name = path.lower().replace("-", " ").replace("_", " ")
    return name.strip()

# ----------------------------------------
# Inject `metadata.title` if missing
# ----------------------------------------
def inject_titles(directory: Path):
    modified_count = 0

    logging.info(f"Injecting titles in directory: {directory}")

    for file in directory.glob("*.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        updated = []

        for chunk in data:
            metadata = chunk.get("metadata", {})

            if "title" not in metadata:
                # Priority 1: Infer from metadata.url
                if "url" in metadata:
                    metadata["title"] = infer_title_from_url(metadata["url"])
                else:
                    # Fallback: Use source file stem
                    metadata["title"] = Path(chunk.get("source", "unknown")).stem

                modified_count += 1

            chunk["metadata"] = metadata
            updated.append(chunk)

        file.write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")

    logging.info(f"Injected titles into {modified_count} chunk(s)")

# ----------------------------------------
# CLI entrypoint
# ----------------------------------------
def main():
    logging.info("Script started: inject_titles_from_source.py")
    try:
        inject_titles(TARGET_DIR)
        logging.info("Script finished successfully: inject_titles_from_source.py")
    except Exception as e:
        logging.error(f"Script failed: inject_titles_from_source.py, Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
