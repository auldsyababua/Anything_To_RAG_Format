# scripts/smart_ingest.py

# ----------------------------------------
# Format-Aware Ingestion Pipeline
# ----------------------------------------
# Ingests mixed file types (.pdf, .md, .json, .html, .epub)
# Normalizes, chunks, and standardizes output structure
# Final result written to FULL_OUTPUT_FILE (e.g. full/unified.json)
# Also enriches chunks with:
# - chunk_id (unique per doc chunk)
# - chunk_offset (token-level offset)
# - token_count (estimated tokens)
# - headings and section_path (from markdown)
# ----------------------------------------

import json
import fitz  # PyMuPDF for PDF parsing
import re
import html
import nltk
import sys
import os
from pathlib import Path
from nltk.tokenize import sent_tokenize

# Tokenizer (you can swap in tiktoken if available)
def count_tokens(text):
    return len(text.split())

# Config and logging setup
from config import setup_logging, FULL_OUTPUT_FILE
setup_logging()
import logging

nltk.download('punkt', quiet=True)

def clean_text(text):
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)  # remove markdown images
    return text.strip()

# ----------------------------------------
# Chunk plain text using sentence tokenizer
# Adds metadata: chunk_id, offset, token_count
# ----------------------------------------
def chunk_sentences(text, doc_id):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    token_acc = 0
    chunk_index = 0
    word_offset = 0
    for sent in sentences:
        token_len = count_tokens(sent)
        if token_acc + token_len > 1000:
            chunk_text = ' '.join(current_chunk).strip()
            if len(chunk_text) > 40:
                chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        "doc_id": doc_id,
                        "chunk_id": f"{doc_id}_{chunk_index:04d}",
                        "chunk_offset": word_offset,
                        "token_count": count_tokens(chunk_text),
                        "headings": [],
                        "section_path": ""
                    }
                })
                chunk_index += 1
                word_offset += token_acc
            current_chunk = [sent]
            token_acc = token_len
        else:
            current_chunk.append(sent)
            token_acc += token_len

    # last chunk
    chunk_text = ' '.join(current_chunk).strip()
    if len(chunk_text) > 40:
        chunks.append({
            "content": chunk_text,
            "metadata": {
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}_{chunk_index:04d}",
                "chunk_offset": word_offset,
                "token_count": count_tokens(chunk_text),
                "headings": [],
                "section_path": ""
            }
        })

    return chunks

# ----------------------------------------
# Chunk markdown text respecting headings
# Preserves section structure and injects metadata
# ----------------------------------------
def chunk_markdown(text, doc_id):
    lines = text.splitlines()
    chunks = []
    buffer = []
    current_heading = ""
    section_path = []
    chunk_index = 0
    word_offset = 0

    def flush():
        nonlocal chunk_index, word_offset
        if not buffer:
            return
        joined = " ".join(buffer).strip()
        if len(joined) < 40:
            return
        chunks.append({
            "content": joined,
            "metadata": {
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}_{chunk_index:04d}",
                "chunk_offset": word_offset,
                "token_count": count_tokens(joined),
                "headings": [current_heading] if current_heading else [],
                "section_path": " > ".join(section_path)
            }
        })
        chunk_index += 1
        word_offset += count_tokens(joined)
        buffer.clear()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            flush()
            current_heading = re.sub(r'#', '', line).strip()
            section_path.append(current_heading)
        else:
            buffer.append(line)

    flush()
    return chunks

# ----------------------------------------
# Detect file type and dispatch appropriate chunking logic
# ----------------------------------------
def process_file(path: Path):
    ext = path.suffix.lower()
    doc_id = path.stem
    with open(path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    raw_text = clean_text(raw_text)

    if ext == ".md":
        return chunk_markdown(raw_text, doc_id)
    else:
        return chunk_sentences(raw_text, doc_id)

# ----------------------------------------
# Entrypoint: iterate ingestion_source and run chunker
# ----------------------------------------
def main():
    source_dir = Path("ingestion_source")
    all_chunks = []

    for file_path in source_dir.iterdir():
        if file_path.suffix.lower() in [".md", ".txt", ".html"]:
            logging.info(f"Processing {file_path.name}...")
            chunks = process_file(file_path)
            all_chunks.extend(chunks)

    with open(FULL_OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        json.dump(all_chunks, out_f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
