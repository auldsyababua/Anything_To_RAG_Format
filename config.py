# config.py

# -------------------------DO NOT TOUCH UNLESS YOU KNOW WHAT YOU ARE DOING--------------------------------
# Centralized Configuration paths for this RAG Pipeline - if you want to adjust the settings, do it in the .env file
# --------------------------------------------------------------------------------------------------------
# Controls all paths and parameters.
# Ensures standardized naming, logging, chunking, and
# embedding settings across all scripts.
# --------------------------------------------------------------------------------------------------------

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file (if available)
load_dotenv()

# ================================
# === USER-CONFIGURABLE VALUES ===
# ================================

# Chunking behavior: max size of a chunk and overlap
TARGET_TOKENS = int(os.getenv("TARGET_TOKENS", 1000))  # Default: 1000 tokens
OVERLAP_TOKENS = int(os.getenv("OVERLAP_TOKENS", 200))  # Default: 200 tokens

# Embedding model settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 1536))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Telegram bot notifications
TELEGRAM_BOT_ENABLED = os.getenv("TELEGRAM_BOT_ENABLED", "false").lower() == "true"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Apify integration
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise ValueError("Missing APIFY_TOKEN in environment")

# Log file used across the pipeline
LOG_FILE = LOGS_DIR / "pipeline_log.txt"

def setup_logging():
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        filename=LOG_FILE,
        level=level,
        format='%(asctime)s - %(message)s'
    )

# ============================
# === DO NOT TOUCH SECTION ===
# ============================

# Base project paths
REPO_ROOT = Path(__file__).resolve().parent
PIPELINE_OUTPUT = REPO_ROOT / "pipeline_output"

# Numbered pipeline stage folders
INGESTION_SOURCE = PIPELINE_OUTPUT / "0_ingestion_source"
RAW_DIR = PIPELINE_OUTPUT / "1_raw"
CLEANED_DIR = PIPELINE_OUTPUT / "2_cleaned"
SPLIT_DIR = PIPELINE_OUTPUT / "3_split"
EMBEDDED_DIR = PIPELINE_OUTPUT / "4_embedded"
FAILED_DIR = PIPELINE_OUTPUT / "5_failed"
LOGS_DIR = PIPELINE_OUTPUT / "logs"

# Ensure pipeline subdirectories exist
for folder in [INGESTION_SOURCE, RAW_DIR, CLEANED_DIR, SPLIT_DIR, EMBEDDED_DIR, FAILED_DIR, LOGS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Output file templates — use run_id injection at runtime
RAW_OUTPUT_TEMPLATE = RAW_DIR / "unified-clean__{run_id}.json"
CLEANED_OUTPUT_TEMPLATE = CLEANED_DIR / "unified-clean__{run_id}.json"
EMBEDDED_OUTPUT_TEMPLATE = EMBEDDED_DIR / "unified-embedded__{run_id}.json"
MANIFEST_TEMPLATE = LOGS_DIR / "manifest__{run_id}.json"
RETRY_LOG = LOGS_DIR / "failed_chunks_retry.json"

# Markdown-specific paths
MARKDOWN_FOLDER = REPO_ROOT / "markdown" / "raw"
MARKDOWN_OUTPUT_FOLDER = REPO_ROOT / "markdown" / "with_titles"
CSV_PATH = REPO_ROOT / "markdown" / "urls.csv"

# Paths for JSON title injection
JSON_INPUT_DIR = SPLIT_DIR
JSON_OUTPUT_DIR = SPLIT_DIR