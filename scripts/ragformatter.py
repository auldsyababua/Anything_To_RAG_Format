
import os
import sys
import time
import json
import argparse
import urllib.parse
import urllib.request
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import subprocess

# ─────────────────────────────────────────────
# ✅ CONFIGURATION
# ─────────────────────────────────────────────
REPO_ROOT = Path("/Users/colinaulds/Desktop/clean-gpt-json")
INGESTION_SOURCE = REPO_ROOT / "ingestion_source"
ACTOR_TASK_ID = "caulds989/website-crawler-rag"

# Load .env if it exists
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

if not APIFY_TOKEN:
    print("[ERROR] APIFY_TOKEN not set. Add it to your .zshrc or create a .env file.")
    sys.exit(1)

# ─────────────────────────────────────────────
# 🔍 UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def parse_sitemap(sitemap_url):
    print(f"[INFO] Fetching sitemap from {sitemap_url}")
    with urllib.request.urlopen(sitemap_url) as res:
        soup = BeautifulSoup(res.read(), "xml")
    return [loc.text.strip() for loc in soup.find_all("loc")]

def extract_domain(url):
    domain = urllib.parse.urlparse(url).hostname or "unknown"
    return domain.replace("www.", "")

def matches_path_prefix(url, filters):
    path = urllib.parse.urlparse(url).path.strip("/")
    return any(path.startswith(f) for f in filters)

def build_actor_payload(urls):
    return {
        "startUrls": [{"url": url, "method": "GET"} for url in urls],
        "saveMarkdown": True,
        "saveHtml": True,
        "removeElementsCssSelector": "script, style, noscript",
        "removeCookieWarnings": True,
        "crawlerType": "playwright:adaptive"
    }

def trigger_apify_run(input_payload):
    print("[INFO] Triggering Apify task run...")
    res = requests.post(
        f"https://api.apify.com/v2/actor-tasks/{ACTOR_TASK_ID}/runs?token={APIFY_TOKEN}",
        json={"input": input_payload}
    )
    res.raise_for_status()
    return res.json()["data"]["id"]



def poll_apify(run_id):
    print("[INFO] Waiting for Apify actor to finish...")
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
    while True:
        res = requests.get(status_url).json()
        status = res["data"]["status"]
        if status in {"SUCCEEDED", "FAILED", "ABORTED"}:
            print(f"[INFO] Crawl finished with status: {status}")
            if status != "SUCCEEDED":
                sys.exit(1)
            return res["data"]["defaultDatasetId"]
        time.sleep(10)

def download_dataset(dataset_id, output_path):
    print("[INFO] Downloading dataset...")
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
    res = requests.get(url)
    res.raise_for_status()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(res.text)
    print(f"[INFO] Saved crawl results to {output_path}")
    return output_path

def run_clean_pipeline():
    print("[INFO] Running RAG formatting pipeline...")
    subprocess.run(["make", "run"], cwd=str(REPO_ROOT))

# ─────────────────────────────────────────────
# 🧠 MAIN WRAPPER
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch sitemap, crawl docs, and chunk for RAG.")
    parser.add_argument("sitemap_url", help="Sitemap URL")
    parser.add_argument("filters", nargs="*", help="Path prefix filters (e.g., guides, examples/setup)")
    args = parser.parse_args()

    # Step 1: Parse and filter sitemap
    all_urls = parse_sitemap(args.sitemap_url)
    filtered_urls = [
        u for u in all_urls if not args.filters or matches_path_prefix(u, args.filters)
    ]

    if not filtered_urls:
        print("[ERROR] No URLs matched the given filters.")
        sys.exit(1)

    print(f"[INFO] {len(filtered_urls)} URLs matched filters.")

    # Step 2: Build Apify payload
    payload = build_actor_payload(filtered_urls)

    # Step 3: Trigger crawl
    run_id = trigger_apify_run(payload)

    # Step 4: Poll until completion
    dataset_id = poll_apify(run_id)

    # Step 5: Save output to ingestion_source
    domain = extract_domain(filtered_urls[0])
    filename = f"{domain.replace('.', '_')}_crawl.json"
    output_path = INGESTION_SOURCE / filename
    download_dataset(dataset_id, output_path)

    # Step 6: Run local clean-gpt-json pipeline
    run_clean_pipeline()

    print(f"[✅] All done. Data processed and chunked from {filename}.")

if __name__ == "__main__":
    main()
