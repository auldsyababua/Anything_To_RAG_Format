# scripts/inject_titles_from_urls.py

import json
import pandas as pd
from urllib.parse import urlparse
from pathlib import Path
from config import (
    MARKDOWN_FOLDER,
    CSV_PATH,
    MARKDOWN_OUTPUT_FOLDER,
    JSON_INPUT_DIR,
    JSON_OUTPUT_DIR
)

# ----------------------------------------
# Title Injector for Markdown & JSON Chunks
# ----------------------------------------
# Injects H1-style titles into markdown docs and metadata.title into JSON chunks.
# Markdown titles are inferred from URLs in CSV.
# JSON chunk titles are derived from each chunk's metadata.url.

# Ensure output folders exist
MARKDOWN_OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Extract a readable title from the URL path slug
def url_to_title(url: str) -> str:
    if not isinstance(url, str):
        return "Untitled"
    path = urlparse(url).path.strip("/").split("/")[-1]
    return path.replace("-", " ").replace("_", " ").title() or "Home"

# Load title list from CSV
urls_df = pd.read_csv(CSV_PATH)
urls = urls_df.iloc[:, 0].dropna().tolist()
titles = [url_to_title(url) for url in urls]

# === Markdown Title Injection ===
md_files = sorted([f for f in MARKDOWN_FOLDER.glob("*.md")])
pair_count = min(len(md_files), len(titles))

for i in range(pair_count):
    md_path = md_files[i]
    out_path = MARKDOWN_OUTPUT_FOLDER / md_path.name

    content = md_path.read_text(encoding="utf-8")
    if not content.startswith("# "):
        content = f"# {titles[i]}\n\n" + content
    out_path.write_text(content, encoding="utf-8")

print(f"[✓] Injected titles into {pair_count} markdown files.")

# === JSON Metadata Title Injection ===
json_files = sorted([f for f in JSON_INPUT_DIR.glob("*.json")])
injected = 0

for fpath in json_files:
    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
    except Exception:
        continue

    changed = False
    for chunk in data:
        if "metadata" not in chunk:
            continue
        url = chunk["metadata"].get("url")
        if not chunk["metadata"].get("title"):
            chunk["metadata"]["title"] = url_to_title(url)
            changed = True

    if changed:
        (JSON_OUTPUT_DIR / fpath.name).write_text(json.dumps(data, indent=2), encoding="utf-8")
        injected += 1

print(f"[✓] Injected titles into {injected} JSON files.")
