# scripts/smart_ingest.py

import json
import fitz  # PyMuPDF
import re
import html
import nltk
from pathlib import Path
from nltk.tokenize import sent_tokenize
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import INGESTION_SOURCE, FULL_OUTPUT_FILE, TARGET_TOKENS, OVERLAP_TOKENS

nltk.download('punkt', quiet=True)

def normalize_filename(name: str) -> str:
    import unicodedata
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")

def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace('\u00ad', '').replace('\xa0', ' ').replace('\n', ' ')
    return re.sub(r'\s+', ' ', text).strip()

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

def normalize_json_entry(entry: dict, i: int, doc_id: str) -> dict:
    content = clean_text(entry.get("text") or entry.get("content", ""))
    metadata = entry.get("metadata", {})
    metadata["doc_id"] = doc_id
    if "url" in entry:
        metadata["url"] = entry["url"]
    return {
        "source": f"{doc_id}_{i}",
        "content": content,
        "metadata": metadata
    }

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
        text = clean_text(re.sub(r"<[^>]+>", "", raw))
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
        doc_id = normalize_filename(path.stem)
        meta = {
            "doc_id": doc_id,
            "source_file": doc_id,
            "source_path": f"{INGESTION_SOURCE.name}/{doc_id}"
        }
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = clean_text(soup.get_text())
            chunks.extend(chunk_sentences(text, TARGET_TOKENS, OVERLAP_TOKENS, meta))

    return chunks

def main():
    all_chunks = []
    for path in INGESTION_SOURCE.rglob("*"):
        if path.suffix.lower() in [".pdf", ".md", ".json", ".html", ".epub"]:
            all_chunks.extend(process_file(path))

    FULL_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    FULL_OUTPUT_FILE.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    print(f"Processed {len(all_chunks)} chunks from {INGESTION_SOURCE} → {FULL_OUTPUT_FILE}")

if __name__ == "__main__":
    main()
