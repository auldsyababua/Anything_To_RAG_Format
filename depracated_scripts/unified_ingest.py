# scripts/unified_ingest.py

import json
import fitz  # PyMuPDF
import re
import nltk
import argparse
from pathlib import Path
from nltk.tokenize import sent_tokenize

from config import SOURCE_FOLDER, FULL_OUTPUT_FILE, TARGET_TOKENS, OVERLAP_TOKENS

nltk.download('punkt')


# Normalize filenames to lowercase ASCII with underscores
def normalize_filename(name):
    import unicodedata
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"(_)+", "_", name)
    return name.strip("_")


# Remove unwanted Unicode artifacts from PDF text
def clean_text(text):
    return text.replace('\u00ad', '').replace('\n', ' ').replace('\xa0', ' ').strip()


# Chunk PDF text into sentence groups by token window and overlap
def chunk_sentences(text, target_tokens, overlap_tokens, meta):
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
            # overlap preservation
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


# Chunk markdown by paragraph windows using H1–H6 headings as soft titles
def extract_markdown_chunks(text, window_size, overlap, meta):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []

    if len(paragraphs) < window_size:
        chunks.append({
            "source": meta["source_path"],
            "title": None,
            "content": "\n\n".join(paragraphs),
            "metadata": meta
        })
        return chunks

    for i in range(0, len(paragraphs) - window_size + 1, max(1, window_size - overlap)):
        window = paragraphs[i:i + window_size]
        title = None
        for para in window:
            match = re.match(r'^#{1,6}\s+(.*)', para)
            if match:
                title = match.group(1)
                break
        chunks.append({
            "source": meta["source_path"],
            "title": title,
            "content": "\n\n".join(window),
            "metadata": meta
        })
    return chunks


# Process a single .pdf or .md file
def process_file(path: Path, input_dir: Path, window_size: int, overlap: int):
    chunks = []
    safe_filename = normalize_filename(path.stem)
    source_path = f"{input_dir.name}/{safe_filename}"

    if path.suffix.lower() == ".pdf":
        doc = fitz.open(path)
        for i, page in enumerate(doc):
            text = clean_text(page.get_text())
            meta = {
                "page_number": i + 1,
                "source_file": safe_filename,
                "source_path": source_path
            }
            chunks.extend(chunk_sentences(text, TARGET_TOKENS, OVERLAP_TOKENS, meta))

    elif path.suffix.lower() == ".md":
        with path.open("r", encoding="utf-8") as f:
            content = f.read()
        meta = {
            "source_file": safe_filename,
            "source_path": source_path
        }
        chunks.extend(extract_markdown_chunks(content, window_size, overlap, meta))

    return chunks


# Traverse directory tree and process each supported file
def process_folder(input_dir: Path, window_size: int, overlap: int):
    all_chunks = []
    for path in input_dir.rglob("*"):
        if path.suffix.lower() in [".pdf", ".md"]:
            all_chunks.extend(process_file(path, input_dir, window_size, overlap))
    return all_chunks


# Entrypoint
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=Path, default=SOURCE_FOLDER)
    parser.add_argument("--output_file", type=Path, default=FULL_OUTPUT_FILE)
    parser.add_argument("--window_size", type=int, default=TARGET_TOKENS)
    parser.add_argument("--overlap", type=int, default=OVERLAP_TOKENS)
    args = parser.parse_args()

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    chunks = process_folder(args.input_dir, args.window_size, args.overlap)

    with args.output_file.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"Processed {len(chunks)} chunks into {args.output_file}")
