import fitz  # PyMuPDF for PDF reading
import os
import json
import nltk
import re
import unicodedata
from nltk.tokenize import sent_tokenize
import sys

# Allow imports from project root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import SOURCE_FOLDER, FULL_OUTPUT_FILE

# Download NLTK tokenizer if not already present
nltk.download('punkt')

# Chunk size configuration
TARGET_TOKENS = 900        # Max tokens per chunk
OVERLAP_TOKENS = 100       # Overlap between chunks to preserve context


def extract_text_by_page(pdf_path):
    """Extract text from a PDF, returning a list of strings (one per page)."""
    doc = fitz.open(pdf_path)
    return [page.get_text() for page in doc]


def clean_text(text):
    """Basic cleanup for extracted text."""
    return text.replace('\u00ad', '').replace('\n', ' ').replace('\xa0', ' ').strip()


def normalize_filename(name):
    """
    Normalize filename:
    - Lowercase
    - Remove non-ASCII characters
    - Remove 'Anna’s Archive' suffixes
    - Replace spaces and slashes
    - Remove special characters
    """
    import unicodedata, re, os
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = os.path.splitext(name)[0]
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_anna[^a-z0-9]*s[^a-z0-9]*archive(_pdf)?$", "", name)
    name = re.sub(r"(_)+", "_", name)
    name = name.strip("_")
    return name


def tokenize_into_chunks_with_metadata(text, target_tokens, overlap_tokens, page_number, source_file, parent_dir):
    """
    Split cleaned text into semantically coherent chunks using sentence tokenization.
    Adds overlap for context preservation.
    Attaches page-level metadata to each chunk.
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())

        if current_tokens + sentence_tokens > target_tokens:
            chunks.append({
                "source": f"{parent_dir}/{source_file}",
                "content": ' '.join(current_chunk),
                "metadata": {
                    "page_number": page_number,
                    "source_file": source_file
                }
            })

            overlap = []
            total = 0
            for sent in reversed(current_chunk):
                sent_tokens = len(sent.split())
                if total + sent_tokens <= overlap_tokens:
                    overlap.insert(0, sent)
                    total += sent_tokens
                else:
                    break
            current_chunk = overlap.copy()
            current_tokens = total

        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    if current_chunk:
        chunks.append({
            "source": f"{parent_dir}/{source_file}",
            "content": ' '.join(current_chunk),
            "metadata": {
                "page_number": page_number,
                "source_file": source_file
            }
        })

    return chunks


def process_pdfs(input_folder):
    """Process all PDF files in the given folder into cleaned, chunked, and normalized output."""
    all_chunks = []
    parent_dir = os.path.basename(os.path.normpath(input_folder))

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(input_folder, filename)
            pages = extract_text_by_page(filepath)
            file_chunks = []

            safe_filename = normalize_filename(filename)

            for i, page_text in enumerate(pages):
                clean = clean_text(page_text)
                page_chunks = tokenize_into_chunks_with_metadata(
                    clean,
                    TARGET_TOKENS,
                    OVERLAP_TOKENS,
                    i + 1,
                    safe_filename,
                    parent_dir
                )
                file_chunks.extend(page_chunks)

            all_chunks.extend(file_chunks)
            print(f"✅ Processed {filename} into {len(file_chunks)} chunks.")

    return all_chunks


if __name__ == "__main__":
    os.makedirs(os.path.dirname(FULL_OUTPUT_FILE), exist_ok=True)
    chunks = process_pdfs(SOURCE_FOLDER)
    with open(FULL_OUTPUT_FILE, "w") as f:
        json.dump(chunks, f, indent=2)
    print(f"✨ Saved {len(chunks)} chunks to {FULL_OUTPUT_FILE}")
