# scripts/smart_ingest.py

# ----------------------------------------
# Format-Aware Ingestion Pipeline
# ----------------------------------------
# Ingests mixed file types (.pdf, .md, .json, .html, .epub)
# Normalizes, chunks, and standardizes output structure
# Final result written to FULL_OUTPUT_FILE (e.g. full/unified.json)
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

# Ensure sentence tokenizer is downloaded
nltk.download('punkt', quiet=True)

# ----------------------------------------
# Load config from project root
# ----------------------------------------
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import (
    INGESTION_SOURCE,
    FULL_OUTPUT_FILE,
    TARGET_TOKENS,
    OVERLAP_TOKENS
)

# ----------------------------------------
# Utility: Normalize filenames into safe doc_ids
# ----------------------------------------
def normalize_filename(name: str) -> str:
    import unicodedata
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    return re.sub(r"[^a-z0-9]+", "_", name).strip("_")

# ----------------------------------------
# Utility: Normalize and clean text
# ----------------------------------------
def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace('\u00ad', '').replace('\xa0', ' ').replace('\n', ' ')
    return re.sub(r'\s+', ' ', text).strip()

# ----------------------------------------
# Sentence window chunking with token overlap
# ----------------------------------------
def chunk_sentences(text: str, target_tokens: int, overlap_tokens: int, meta: dict) -> list:
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        tokens = len(sentence.split())
        if current_tokens + tokens > target_tokens:
            chunks.append({
                "source": meta["source_path"],
                "content": ' '.join(current_chunk),
                "metadata": meta
            })
            # Backtrack for overlap
            overlap = []
            total = 0
            for sent in reversed(current_chunk):
                stokens = len(sent.split())
                if total + stokens <= overlap_tokens:
                    overlap.insert(0, sent)
                    total += stokens
                else:
                    break
            current_chunk = overlap.copy()
            current_tokens = total
        current_chunk.append(sentence)
        current_tokens += tokens

    if current_chunk:
        chunks.append({
            "source": meta["source_path"],
            "content": ' '.join(current_chunk),
            "metadata": meta
        })

    return chunks

# ----------------------------------------
# Paragraph window chunking for Markdown files
# ----------------------------------------
def chunk_markdown(text: str, window_size: int, overlap: int, meta: dict) -> list:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []

    if len(paragraphs) < window_size:
        chunks.append({
            "source": meta["source_path"],
            "content": "\n\n".join(paragraphs),
            "metadata": meta
        })
        return chunks

    for i in range(0, len(paragraphs) - window_size + 1, max(1, window_size - overlap)):
        window = paragraphs[i:i + window_size]
        chunks.append({
            "source": meta["source_path"],
            "content": "\n\n".join(window),
            "metadata": meta
        })

    return chunks

# ----------------------------------------
# Normalize an entry from an Apify crawl .json
# ----------------------------------------
def normalize_json_entry(entry: dict, i: int, doc_id: str) -> dict:
    # DEBUG: Show what's in each entry
    if i < 3:  # Only print first few for sanity
        print(f"[DEBUG] Entry {i}: keys = {list(entry.keys())}")
        print(f"[DEBUG] Text preview: {entry.get('text', '')[:100]}")

    raw_text = entry.get("text") or entry.get("content", "")
    markdown = entry.get("markdown")
    url = entry.get("url")

    metadata = entry.get("metadata", {})
    metadata["doc_id"] = doc_id
    if url:
        metadata["url"] = url

    return {
        "source": f"{doc_id}_{i}",
        "content": clean_text(raw_text),
        "markdown": markdown,
        "metadata": metadata
    }


# ----------------------------------------
# Format-aware dispatch per file type
# ----------------------------------------
def process_file(path: Path) -> list:
    ext = path.suffix.lower()
    doc_id = normalize_filename(path.stem)
    source_path = f"{INGESTION_SOURCE.name}/{doc_id}"
    chunks = []

    if ext == ".pdf":
        doc = fitz.open(path)
        for i, page in enumerate(doc):
            text = clean_text(page.get_text())
            meta = {
                "doc_id": doc_id,
                "page_number": i + 1,
                "source_file": doc_id,
                "source_path": source_path
            }
            chunks.extend(chunk_sentences(text, TARGET_TOKENS, OVERLAP_TOKENS, meta))

    elif ext == ".md":
        text = path.read_text(encoding="utf-8")
        meta = {
            "doc_id": doc_id,
            "source_file": doc_id,
            "source_path": source_path
        }
        chunks.extend(chunk_markdown(text, TARGET_TOKENS, OVERLAP_TOKENS, meta))

    elif ext == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, entry in enumerate(data):
            chunk = normalize_json_entry(entry, i, doc_id)
            if chunk["content"]:
                chunks.append(chunk)

    elif ext == ".html":
        raw = path.read_text(encoding="utf-8")
        text = clean_text(re.sub(r"<[^>]+>", "", raw))  # simple tag strip
        meta = {
            "doc_id": doc_id,
            "source_file": doc_id,
            "source_path": source_path
        }
        chunks.extend(chunk_sentences(text, TARGET_TOKENS, OVERLAP_TOKENS, meta))

    elif ext == ".epub":
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup

        book = epub.read_epub(str(path))
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = clean_text(soup.get_text())
            meta = {
                "doc_id": doc_id,
                "source_file": doc_id,
                "source_path": source_path
            }
            chunks.extend(chunk_sentences(text, TARGET_TOKENS, OVERLAP_TOKENS, meta))

    return chunks

# ----------------------------------------
# Entry Point: Walk folder → process → save output
# ----------------------------------------
def main():
    all_chunks = []

    for path in INGESTION_SOURCE.rglob("*"):
        if path.suffix.lower() in [".pdf", ".md", ".json", ".html", ".epub"]:
            all_chunks.extend(process_file(path))

    with open(FULL_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"[✅] Ingestion complete. {len(all_chunks)} chunks → {FULL_OUTPUT_FILE}")

if __name__ == "__main__":
    main()
