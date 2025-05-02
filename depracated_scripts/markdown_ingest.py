# scripts/markdown_ingest.py

import os
import json
import re
import argparse
from pathlib import Path

# Extracts chunks from a markdown string using sliding window over paragraphs.
# Optionally detects first heading in window as a title.
def extract_chunks_from_markdown(text, window_size, overlap):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    # Slide over paragraphs using window size and overlap
    for i in range(0, len(paragraphs) - window_size + 1, max(1, window_size - overlap)):
        window = paragraphs[i:i + window_size]
        title = None
        # Check for first Markdown heading in this chunk
        for para in window:
            match = re.match(r'^#{1,6}\s+(.*)', para)
            if match:
                title = match.group(1)
                break
        # Construct chunk
        chunks.append({
            "title": title,
            "content": "\n\n".join(window)
        })
    return chunks

# Ingest all .md files in input_dir, process them into JSON chunks, save to output_path
def ingest_markdown(input_dir: str, output_path: str, window_size: int, overlap: int):
    results = []
    for file in Path(input_dir).rglob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract and normalize chunks
        chunks = extract_chunks_from_markdown(content, window_size, overlap)
        for i, chunk in enumerate(chunks):
            results.append({
                "id": f"{file.stem}_chunk{i}",
                "source": str(file),
                "type": "markdown",
                "title": chunk["title"],
                "content": chunk["content"]
            })
    # Write to output JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

# CLI entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")                    # Folder containing markdown files
    parser.add_argument("output_path")                  # Output JSON file
    parser.add_argument("--window_size", type=int, default=1)  # Number of paragraphs per chunk
    parser.add_argument("--overlap", type=int, default=0)      # Overlap between chunks
    args = parser.parse_args()

    ingest_markdown(args.input_dir, args.output_path, args.window_size, args.overlap)
