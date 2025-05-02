```markdown
# clean-gpt-json

## Purpose

**clean-gpt-json** is a format-agnostic document ingestion and chunking pipeline for Retrieval-Augmented Generation (RAG). It processes PDFs, Markdown, JSON crawls, HTML, and EPUBs into clean, semantic chunks with token-aware overlap. Output is ready for embedding into vector stores or downstream LLM consumption.

---

## Features

- Unified ingestion from mixed file types: `.pdf`, `.md`, `.json`, `.html`, `.epub`
- Normalization of raw text (HTML stripping, image tag removal, Unicode cleanup)
- Sentence and paragraph-aware chunking with token windowing and overlap
- Metadata injection (`doc_id`, `title`, `source_path`, etc.)
- File-level origin tracking and split output by source
- Validated chunk structure and deterministic filenames
- Fully scriptable via `make run`

---

## Folder Layout


clean-gpt-json/
├── config.py                    # Centralized path + chunking config
├── Makefile                     # Command shortcuts
├── install.sh                   # Venv bootstrapper
├── semantic-rag-env/            # Virtualenv for pipeline scripts
├── gui-env/                     # Optional: tkinter GUI venv
├── ingestion\_source/           # Drop zone for all input documents
├── full/                        # Merged + cleaned JSONs (single-file)
├── split/                       # Final output: one JSON per doc\_id
└── scripts/
├── smart\_ingest.py               # Master format-aware ingestion script
├── clean\_json\_chunks.py         # Strips junk and invalid chunks
├── split\_ready\_for\_customgpt.py # Groups chunks by doc\_id into output files
├── inject\_titles\_from\_source.py # Adds metadata.title per chunk
├── validate\_json\_output.py      # Final format validator
└── \[others]\*                    # Optional: filtering, large-file splitting, analysis

---

## Key Paths (`config.py`)

REPO_ROOT = Path("/Users/colinaulds/Desktop/clean-gpt-json")
OUTPUT_ROOT = Path("/Users/colinaulds/Desktop/doc-lib")

INGESTION_SOURCE = REPO_ROOT / "ingestion_source"
FULL_OUTPUT_FILE = OUTPUT_ROOT / "full/unified.json"
CLEAN_FULL_OUTPUT_FILE = OUTPUT_ROOT / "full/unified-clean.json"
SPLIT_DIR = OUTPUT_ROOT / "split"

TARGET_TOKENS = 1000
OVERLAP_TOKENS = 200

---

## Workflow

1. **Drop files** into `/ingestion_source`

   * Mixed formats supported in same folder
2. **Run the full pipeline**:

   ```bash
   make run
   ```
3. **Outputs**:

   * Cleaned full JSON: `full/unified-clean.json`
   * Split per-source chunks: `split/{doc_id}.json`

---

## Makefile Targets

make install    # Set up venv and install deps
make run        # Run the entire pipeline (smart ingest → validate)
make gui        # Optional: GUI PDF viewer (Tkinter)

---

## Supported File Types

| Type  | Parsed As         | Handler       |
| ----- | ----------------- | ------------- |
| .pdf  | page text         | PyMuPDF       |
| .md   | paragraph blocks  | regex window  |
| .json | crawler entries   | text+metadata |
| .html | body inner text   | tag-stripped  |
| .epub | content documents | ebooklib+bs4  |

---

## Requirements

* Python 3.10 or 3.11
* `pip install -r requirements.txt` (inside venv)
* macOS/Linux recommended (Tkinter GUI may not run on Windows)

---

## Design Principles

* Single-entry ingestion point
* Stateless, deterministic outputs
* Format detection via file extension
* All metadata stored inline per chunk
* Titles inferred from URL slug or file name

---

## TODO

* Add CLI arg-based file filtering
* Add .docx/.odt ingestion support
* Optional embedding step with vector DB plugins
* Language/NER tagging per chunk


