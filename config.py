# config.py

# ------------------------------
# Centralized Configuration File
# ------------------------------
# Controls all paths and parameters for RAG preprocessing pipeline
# Keeps everything reproducible and centralized via pathlib

from pathlib import Path  # safer, cross-platform file path handling



# === Base Paths ===

# Absolute path to the clean-gpt-json repository (code lives here)
REPO_ROOT = Path("/Users/colinaulds/Desktop/clean-gpt-json")

# Absolute path to the data/output repository (all results go here)
OUTPUT_ROOT = Path("/Users/colinaulds/Desktop/doc-lib")

# Absolute path to the ingestion source (raw files - JSON, CSV, HTML, EPUB, PDF, etc.)
INGESTION_SOURCE = REPO_ROOT / "ingestion_source"



# === Tokenization Parameters ===

# Target token count per chunk (semantic unit size for RAG)
TARGET_TOKENS = 1000

# Number of overlapping tokens between chunks (for context continuity)
OVERLAP_TOKENS = 200





# === I/O Directories ===

# Where raw or cleaned merged JSON files are stored
FULL_DIR = OUTPUT_ROOT / "full"

# Where per-document, chunked JSON files are written (post-split)
SPLIT_DIR = OUTPUT_ROOT / "split"





# === Main File Paths ===

# Input: merged raw JSON (e.g. from unified_ingest.py)
FULL_OUTPUT_FILE = FULL_DIR / "unraid-full.json"

# Output: cleaned version of the above (e.g. from clean_json_chunks.py)
CLEAN_FULL_OUTPUT_FILE = FULL_DIR / "unraid-clean-full.json"

# Alias used for filtering; typically same as CLEAN_FULL_OUTPUT_FILE
FILTER_INPUT_FILE = CLEAN_FULL_OUTPUT_FILE





# === Markdown Title Injection (optional) ===

# Folder containing raw markdown files (used with title injection)
MARKDOWN_FOLDER = REPO_ROOT / "markdown" / "raw"

# Folder for output markdown files with injected titles
MARKDOWN_OUTPUT_FOLDER = REPO_ROOT / "markdown" / "with_titles"

# CSV file that maps URLs to markdown source documents
CSV_PATH = REPO_ROOT / "markdown" / "urls.csv"




# === JSON Title Injection ===

# Folder where JSON chunks are read for title injection
JSON_INPUT_DIR = SPLIT_DIR

# Folder where updated JSON chunks (with metadata.title) are written
JSON_OUTPUT_DIR = SPLIT_DIR
