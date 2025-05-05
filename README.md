# clean-gpt-json

## Purpose

**Anything_To_RAG_Format** is a format-agnostic document ingestion and chunking pipeline for Retrieval-Augmented Generation (RAG). It processes PDFs, Markdown, JSON crawls, HTML, and EPUBs into clean, semantic chunks with token-aware overlap. Output is ready for embedding into vector stores or downstream LLM consumption.

Repo URL: https://github.com/auldsyababua/Anything_To_RAG_Format

---

## Features

* Unified ingestion from mixed file types: `.pdf`, `.md`, `.json`, `.html`, `.epub`
* Normalization of raw text (HTML stripping, image tag removal, Unicode cleanup)
* Sentence and paragraph-aware chunking with token windowing and overlap
* Metadata injection (`doc_id`, `title`, `source_path`, etc.)
* File-level origin tracking and split output by source
* Validated chunk structure and deterministic filenames
* Fully scriptable via `make run`
* Optional filters, PDF analyzers, chunk-size validation, and multi-step Apify + RAG pipeline automation
* Automatic domain-based grouping for website crawls with 50MB-aware chunk splitting
* `recover_apify_run` shell alias to resume pipeline if Apify crawl was interrupted

---

## Folder Layout

```
clean-gpt-json/
├── config.py                    # Centralized path + chunking config
├── Makefile                     # Command shortcuts
├── install.sh                   # Venv bootstrapper
├── semantic-rag-env/            # Virtualenv for pipeline scripts
├── ingestion_source/            # Drop zone for all input documents
└── scripts/                     # Core and utility scripts

~/Desktop/doc-lib/               # OUTPUT_ROOT (external)
├── full/                        # Merged + cleaned JSONs (single-file)
├── split/                       # Final output: domain.json or domain_partN.json
```

---

## Scripts and Dependencies

| Script                         | Purpose                                                            | Depends On                    | Used By                     |
| ------------------------------ | ------------------------------------------------------------------ | ----------------------------- | --------------------------- |
| `smart_ingest.py`              | Main file-type handler + chunker                                   | `config.py`, `nltk`, `fitz`   | `make run`                  |
| `clean_json_chunks.py`         | Removes markdown/HTML junk, strips SVGs, reassigns better titles   | `FULL_OUTPUT_FILE`            | `make run`                  |
| `split_large_json_files.py`    | Groups chunks by domain, splits if >50MB                           | `CLEAN_FULL_OUTPUT_FILE`      | `make run`                  |
| `inject_titles_from_source.py` | Adds `metadata.title` from `url` or fallback                       | `split/` dir                  | `make run`                  |
| `validate_json_output.py`      | Ensures JSON output conforms to chunk schema                       | `split/` dir                  | `make run`                  |
| `analyze_pdf_folder.py`        | Reports # of pages, text density, content types in PDFs            | `SOURCE_FOLDER`, `fitz`       | optional precheck           |
| `normalize_filenames.py`       | Renames files in ingestion folder to consistent snake_case         | `INGESTION_SOURCE`            | optional preclean           |
| `check_split_file_sizes.py`    | Warns if any file exceeds 50MB, counts characters                  | `SPLIT_DIR`                   | postprocessing sanity check |
| `filter_chunks.py`             | Removes boilerplate and duplicate chunks from unified file         | `FULL_OUTPUT_FILE`            | optional dedup/clean        |
| `ragformatter.py`              | Pulls sitemap → crawls → downloads JSON → runs full pipeline       | `.env`, Apify API, `make run` | end-to-end crawler trigger  |
| `sitemap_strip.py`             | Converts sitemap(s) → JSON crawler configs                         | CLI args or XML folder        | feeds Apify actor or review |

---

## Key Paths (`config.py`)

```python
REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path.home() / "Desktop" / "clean-gpt-json"))
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", Path.home() / "Desktop" / "doc-lib"))
INGESTION_SOURCE = REPO_ROOT / "ingestion_source"

FULL_OUTPUT_FILE = OUTPUT_ROOT / "full/unified.json"
CLEAN_FULL_OUTPUT_FILE = OUTPUT_ROOT / "full/unified-clean.json"
SPLIT_DIR = OUTPUT_ROOT / "split"

TARGET_TOKENS = 1000
OVERLAP_TOKENS = 200
```

---

## Workflow

1. **Drop files** into `/ingestion_source` - unless using Apify via `ragformatter`
2. **Run the full pipeline**:

```bash
make run
```

3. **Outputs**:

* Cleaned full JSON: `doc-lib/full/unified-clean.json`
* Split per-domain chunks: `doc-lib/split/{domain}.json` or `domain_partN.json`

---

## Makefile Targets

```make
make install    # Set up venv and install deps
make run        # Run full pipeline (ingest → clean → split → validate)
make post       # Rerun pipeline steps from cleaned file onward
make recover    # Shortcut for recover_apify_run shell alias
```

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
* Crawler output grouped by domain
* Consistent recovery from long-running Apify jobs

---

## Tips for LLMs and Collaborators

* Read `Makefile` for canonical entrypoints
* All I/O paths are centralized in `config.py`
* Scripts are self-contained, CLI-friendly, and idempotent where possible
* Website crawls output 1 file per domain (unless >50MB)
* To recover a failed or long Apify job:

```bash
recover_apify_run <RUN_ID>
```

---

## TODO

* Add CLI arg-based file filtering
* Add .docx/.odt ingestion support
* Optional embedding step with vector DB plugins
* Language/NER tagging per chunk
