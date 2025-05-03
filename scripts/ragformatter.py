# scripts/ragformatter.py

import sys
import time
import json
import argparse
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import requests
import subprocess
from pathlib import Path

# Allow import of config.py from project root
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Load all paths and credentials from config.py
from config import (
    REPO_ROOT,
    INGESTION_SOURCE,
    APIFY_TOKEN
)

# ─────────────────────────────────────────────
# 🔍 UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def parse_sitemap(sitemap_url):
    print(f"[INFO] Fetching sitemap from {sitemap_url}")
    req = urllib.request.Request(
        sitemap_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; clean-gpt-json/1.0)"}
    )
    with urllib.request.urlopen(req) as res:
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
        "aggressivePrune": True,
        "clickElementsCssSelector": "[aria-expanded=\"false\"]",
        "clientSideMinChangePercentage": 15,
        "crawlerType": "playwright:adaptive",
        "debugLog": False,
        "debugMode": False,
        "expandIframes": True,
        "ignoreCanonicalUrl": True,
        "includeUrlGlobs": [{"glob": ""}],
        "keepUrlFragments": False,
        "proxyConfiguration": {"useApifyProxy": True},
        "readableTextCharThreshold": 100,
        "removeCookieWarnings": True,
        "removeElementsCssSelector": (
            "nav, footer, script, style, noscript, svg, img[src^='data:'],"
            "[role=\"alert\"],[role=\"banner\"],[role=\"dialog\"],[role=\"alertdialog\"],"
            "[role=\"region\"][aria-label*=\"skip\" i],[aria-modal=\"true\"]"
        ),
        "renderingTypeDetectionPercentage": 10,
        "respectRobotsTxtFile": False,
        "saveFiles": True,
        "saveHtml": True,
        "saveHtmlAsFile": True,
        "saveMarkdown": True,
        "saveScreenshots": False,
        "useSitemaps": True,
        "startUrls": [{"url": url, "method": "GET"} for url in urls]
    }

def trigger_apify_run(input_payload):
    print("[INFO] Triggering Apify actor run (async)...")
    url = "https://api.apify.com/v2/acts/apify~website-content-crawler/runs"
    headers = {
        "Authorization": f"Bearer {APIFY_TOKEN}",
        "Content-Type": "application/json"
    }
    res = requests.post(url, json={"input": input_payload}, headers=headers)
    res.raise_for_status()
    return res.json()["data"]["id"]  # this is the runId for polling


def poll_apify(run_id):
    print("[INFO] Waiting for Apify actor to finish...")
    url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {APIFY_TOKEN}"
    }

    while True:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()["data"]
        status = data["status"]
        print(f"[DEBUG] Status: {status}")
        if status in {"SUCCEEDED", "FAILED", "ABORTED"}:
            if status != "SUCCEEDED":
                print(f"[ERROR] Crawl finished with status: {status}")
                sys.exit(1)
            print("[INFO] Crawl finished successfully.")
            return data["defaultDatasetId"]
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
    """
    End-to-end runner:
    - Parses sitemap and filters URLs
    - Submits to Apify and waits for crawl
    - Downloads JSON and stores in ingestion_source/
    - Triggers full local pipeline via `make run`

    Final output:
    - full/unified-clean.json
    - split/{doc_id}.json
    """
    parser = argparse.ArgumentParser(
        description="Fetch sitemap, crawl docs, and chunk for RAG."
    )
    parser.add_argument("sitemap_url", help="Sitemap URL")
    parser.add_argument("filters", nargs="*", help="Path prefix filters (e.g., guides, examples/setup)")
    args = parser.parse_args()

    all_urls = parse_sitemap(args.sitemap_url)
    filtered_urls = [
        u for u in all_urls if not args.filters or matches_path_prefix(u, args.filters)
    ]

    if all(u.endswith(".xml") for u in filtered_urls):
        print("[ERROR] Sitemap returned only XML links — are you passing a sitemap index instead of a page sitemap?")
        sys.exit(1)

    if not filtered_urls:
        print("[ERROR] No URLs matched the given filters.")
        sys.exit(1)

    print(f"[INFO] {len(filtered_urls)} URLs matched filters.")

    payload = build_actor_payload(filtered_urls)
    run_id = trigger_apify_run(payload)
    dataset_id = poll_apify(run_id)

    domain = extract_domain(filtered_urls[0])
    filename = f"{domain.replace('.', '_')}_crawl.json"
    output_path = INGESTION_SOURCE / filename
    download_dataset(dataset_id, output_path)

    run_clean_pipeline()
    print(f"[✅] All done. Data processed and chunked from {filename}.")

if __name__ == "__main__":
    main()
