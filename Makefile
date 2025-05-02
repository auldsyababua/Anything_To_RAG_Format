SHELL := /bin/bash
PROJECT_ROOT := $(shell pwd)
VENV := semantic-rag-env
GUI_VENV := gui-env

# === Main RAG Pipeline (format-aware, smart routing) ===
run:
	. $(VENV)/bin/activate && \
	python3 scripts/smart_ingest.py && \
	python3 scripts/clean_json_chunks.py && \
	python3 scripts/split_ready_for_customgpt.py && \
	python3 scripts/inject_titles_from_source.py && \
	python3 scripts/validate_json_output.py

# === GUI PDF Analyzer (Tkinter) ===
gui:
	. $(GUI_VENV)/bin/activate && python3 pdf_gui.py

# === Setup: Install dependencies and venv ===
install:
	chmod +x install.sh && ./install.sh
