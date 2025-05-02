# scripts/inject_titles_from_source.py

import json
from pathlib import Path
from urllib.parse import urlparse
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import JSON_INPUT_DIR, JSON_OUTPUT_DIR

# Infer title from metadata.url path
def title_from_url(url: str) -> str:
    if not isinstance(url, str):
        return "Untitled"
    slug = urlparse(url).path.strip("/").split("/")[-1]
    return slug.replace("-", " ").replace("_", " ").title() or "Home"

# Fallback: infer title from source filename
def title_from_source(source: str) -> str:
    name = Path(source).stem
    return name.replace("-", " ").replace("_", " ").title() or "Untitled"

# Inject metadata.title into each chunk
def inject():
    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = JSON_INPUT_DIR.glob("*.json")
    modified = 0

    for fpath in files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue

        changed = False
        for chunk in data:
            meta = chunk.get("metadata", {})
            if not meta.get("title"):
                url = meta.get("url")
                meta["title"] = title_from_url(url) if url else title_from_source(chunk.get("source", "untitled"))
                changed = True

        if changed:
            (JSON_OUTPUT_DIR / fpath.name).write_text(json.dumps(data, indent=2), encoding="utf-8")
            modified += 1

    print(f"Injected titles into {modified} JSON files.")

if __name__ == "__main__":
    inject()
