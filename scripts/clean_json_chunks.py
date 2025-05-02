# scripts/clean_json_chunks.py

import json
import re
from pathlib import Path
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import FULL_OUTPUT_FILE, CLEAN_FULL_OUTPUT_FILE

# Strip image tags, HTML, excess spacing
def strip_junk(text: str) -> str:
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"<svg.*?</svg>", "", text, flags=re.DOTALL)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# Normalize bad or missing titles
def extract_title(raw_title: str, content: str) -> str:
    if raw_title and raw_title.strip().lower() != "github":
        return raw_title.strip()
    match = re.search(r"^#+\s+(.*)", content, flags=re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"

# Filter out trivial chunks
def is_valid(chunk: dict) -> bool:
    return bool(chunk.get("content", "").strip()) and len(chunk["content"]) > 20

# Load → clean → write
chunks = json.loads(FULL_OUTPUT_FILE.read_text(encoding="utf-8"))
cleaned = []

for chunk in chunks:
    content = strip_junk(chunk.get("content", ""))
    title = extract_title(chunk.get("title"), content)
    cleaned_chunk = {
        "source": chunk.get("source", "unknown"),
        "title": title,
        "content": content,
        "metadata": chunk.get("metadata", {})
    }
    if is_valid(cleaned_chunk):
        cleaned.append(cleaned_chunk)

CLEAN_FULL_OUTPUT_FILE.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")
print(f"Cleaned {len(cleaned)} valid chunks saved to {CLEAN_FULL_OUTPUT_FILE}")
