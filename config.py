# config.py

# ------------------------------
# Centralized Configuration File
# ------------------------------
# Controls all paths and parameters for the RAG preprocessing pipeline.
# Keeps everything reproducible and centralized via pathlib + .env.
# ------------------------------

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# === Base Project Paths ===

REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path.home() / "Desktop" / "clean-gpt-json"))
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", Path.home() / "Desktop" / "doc-lib"))
INGESTION_SOURCE = REPO_ROOT / "ingestion_source"

# Sanity checks for the directory paths
if not REPO_ROOT.exists():
    raise FileNotFoundError(f"REPO_ROOT does not exist: {REPO_ROOT}")
if not OUTPUT_ROOT.exists():
    OUTPUT_ROOT.mkdir(parents=True)

# === Chunking Parameters ===

TARGET_TOKENS = 1000
OVERLAP_TOKENS = 200

# === Output File Paths ===

FULL_OUTPUT_FILE = OUTPUT_ROOT / "full/unified.json"
CLEAN_FULL_OUTPUT_FILE = OUTPUT_ROOT / "full/unified-clean.json"
SPLIT_DIR = OUTPUT_ROOT / "split"
FILTER_INPUT_FILE = CLEAN_FULL_OUTPUT_FILE

# === Markdown Injection Paths ===

MARKDOWN_FOLDER = REPO_ROOT / "markdown" / "raw"
MARKDOWN_OUTPUT_FOLDER = REPO_ROOT / "markdown" / "with_titles"
CSV_PATH = REPO_ROOT / "markdown" / "urls.csv"

# === JSON Title Injection ===

JSON_INPUT_DIR = SPLIT_DIR
JSON_OUTPUT_DIR = SPLIT_DIR

# === Apify Credentials ===

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

if not APIFY_TOKEN:
    raise ValueError("Missing APIFY_TOKEN in environment")

# === Logging Configuration ===

# Log directory and file inside the repo
LOGS_DIR = REPO_ROOT / "logs"
LOG_FILE = LOGS_DIR / "pipeline_log.txt"

# Ensure the logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Function to setup logging
def setup_logging():
    import logging

    logging.basicConfig(
        filename=LOG_FILE,  # Log file inside the repo
        level=logging.INFO,  # Log everything at INFO level and above
        format='%(asctime)s - %(message)s'  # Log format with timestamp
    )
