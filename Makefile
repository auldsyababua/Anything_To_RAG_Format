# Makefile — clean-gpt-json: End-to-End RAG Pipeline

# --------------------------------------
# Core Paths
# --------------------------------------
REPO_ROOT := $(HOME)/Desktop/clean-gpt-json
SCRIPTS := $(REPO_ROOT)/scripts
INGEST_INPUT := $(REPO_ROOT)/ingestion_source
FULL := $(OUTPUT_ROOT)/full
SPLIT := $(OUTPUT_ROOT)/split

# --------------------------------------
# Default: full pipeline
# --------------------------------------
default: run

# --------------------------------------
# Setup
# --------------------------------------
install:
	@echo "[INSTALL] Bootstrapping virtual environment and dependencies..."
	./install.sh

# --------------------------------------
# Optional Precheck (PDF metadata + filenames)
# --------------------------------------
precheck:
	@echo "[PRECHECK] Auditing PDFs and filenames..."
	python3 $(SCRIPTS)/analyze_pdf_folder.py
	python3 $(SCRIPTS)/normalize_filenames.py --dry-run

# --------------------------------------
# Main Pipeline Stages
# --------------------------------------
ingest:
	@echo "[INGEST] Running smart format-aware ingestion..."
	python3 $(SCRIPTS)/smart_ingest.py

clean:
	@echo "[CLEAN] Cleaning unified chunks..."
	python3 $(SCRIPTS)/clean_json_chunks.py --input $(FULL)/unified.json --output $(FULL)/unified-clean.json

filter:
	@echo "[FILTER] Removing boilerplate and duplicates..."
	python3 $(SCRIPTS)/filter_chunks.py --input $(FULL)/unified-clean.json --output $(FULL)/filtered.json

split:
	@echo "[SPLIT] Splitting into domain files (size-safe)..."
	python3 $(SCRIPTS)/split_large_json_files.py --input $(FULL)/filtered.json --output $(SPLIT)/

inject_titles:
	@echo "[TITLE] Injecting metadata.title fields..."
	python3 $(SCRIPTS)/inject_titles_from_source.py

validate:
	@echo "[VALIDATE] Validating structure of final split files..."
	python3 $(SCRIPTS)/validate_json_output.py

check:
	@echo "[CHECK] Checking file sizes under 50MB..."
	python3 $(SCRIPTS)/check_split_file_sizes.py --input $(SPLIT)/

# --------------------------------------
# Full pipeline
# --------------------------------------
run: ingest clean filter split check inject_titles validate

# Skip ingestion: useful if you've already crawled or dropped files
post: clean filter split check inject_titles validate