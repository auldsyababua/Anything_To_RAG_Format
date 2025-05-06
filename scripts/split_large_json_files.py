
import json
import os
import sys
from urllib.parse import urlparse
from collections import defaultdict
from tqdm import tqdm
from pathlib import Path

MAX_MB = 50
MAX_BYTES = MAX_MB * 1024 * 1024

def load_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_split_file(domain, part_idx, chunks, output_dir):
    filename = f"{domain}_part{part_idx}.json" if part_idx > 1 else f"{domain}.json"
    path = Path(output_dir) / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    return path

def domain_from_url(url):
    try:
        return urlparse(url).netloc.replace('.', '_')
    except Exception:
        return "unknown"

def group_chunks_by_domain(chunks):
    groups = defaultdict(list)
    for chunk in chunks:
        url = chunk.get("metadata", {}).get("url", "")
        doc_id = chunk.get("metadata", {}).get("doc_id")
        domain = domain_from_url(url) if url else doc_id or "unknown"
        groups[domain].append(chunk)
    return groups

def split_large_files(input_path, output_dir):
    chunks = load_chunks(input_path)
    domain_groups = group_chunks_by_domain(chunks)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for domain, group in tqdm(domain_groups.items(), desc="Splitting by domain"):
        part_chunks = []
        current_bytes = 0
        part_idx = 1

        for chunk in group:
            chunk_bytes = len(json.dumps(chunk, ensure_ascii=False).encode("utf-8"))
            if current_bytes + chunk_bytes > MAX_BYTES and part_chunks:
                write_split_file(domain, part_idx, part_chunks, output_dir)
                part_chunks = []
                current_bytes = 0
                part_idx += 1

            part_chunks.append(chunk)
            current_bytes += chunk_bytes

        if part_chunks:
            write_split_file(domain, part_idx, part_chunks, output_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_large_json_files.py <cleaned_input> <output_dir>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    split_large_files(input_path, output_dir)
