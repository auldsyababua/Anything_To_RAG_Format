import sys
import time
import json
import argparse
import requests
import subprocess
from pathlib import Path

# Add the project root to sys.path to access config.py
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import logging setup from config.py
from config import setup_logging, REPO_ROOT, INGESTION_SOURCE, APIFY_TOKEN

# Call the setup function to configure logging
setup_logging()

# Now you can use logging throughout the script
import logging

def build_actor_payload(domain, filters):
    include_globs = [{"glob": f"{domain.rstrip('/')}/{f.strip('/')}**"} for f in filters]
    return {
        "startUrls": [{"url": domain, "method": "GET"}],
        "useSitemaps": True,
        "respectRobotsTxtFile": False,
        "crawlerType": "playwright:adaptive",
        "includeUrlGlobs": include_globs,
        "excludeUrlGlobs": [],
        "keepUrlFragments": False,
        "ignoreCanonicalUrl": False,
        "maxCrawlDepth": 20,
        "maxCrawlPages": 9999999,
        "initialConcurrency": 0,
        "maxConcurrency": 200,
        "initialCookies": [],
        "proxyConfiguration": {"useApifyProxy": True},
        "maxSessionRotations": 10,
        "maxRequestRetries": 5,
        "requestTimeoutSecs": 60,
        "minFileDownloadSpeedKBps": 128,
        "dynamicContentWaitSecs": 10,
        "waitForSelector": "",
        "softWaitForSelector": "",
        "maxScrollHeightPixels": 5000,
        "keepElementsCssSelector": "",
        "removeElementsCssSelector": (
            "nav, footer, script, style, noscript, svg, img[src^='data:'],"
            "[role='alert'],[role='banner'],[role='dialog'],[role='alertdialog'],"
            "[role='region'][aria-label*='skip' i],[aria-modal='true']"
        ),
        "removeCookieWarnings": True,
        "expandIframes": True,
        "clickElementsCssSelector": "[aria-expanded='false']",
        "htmlTransformer": "readableText",
        "readableTextCharThreshold": 100,
        "aggressivePrune": False,
        "debugMode": False,
        "debugLog": False,
        "saveHtml": False,
        "saveHtmlAsFile": False,
        "saveMarkdown": True,
        "saveFiles": False,
        "saveScreenshots": False,
        "maxResults": 9999999,
        "clientSideMinChangePercentage": 15,
        "renderingTypeDetectionPercentage": 10
    }

def trigger_apify_run(input_payload):
    logging.info("[INFO] Triggering Apify actor run (async)...")
    url = "https://api.apify.com/v2/acts/apify~website-content-crawler/runs"
    headers = {
        "Authorization": f"Bearer {APIFY_TOKEN}",
        "Content-Type": "application/json"
    }
    logging.debug(f"DEBUG - Apify Payload: {json.dumps(input_payload, indent=2)}")
    res = requests.post(url, json=input_payload, headers=headers)

    if not res.ok:
        logging.error(f"[ERROR] Apify response: {res.text}")

    res.raise_for_status()
    run_id = res.json()["data"]["id"]
    logging.info(f"[INFO] Apify run ID: {run_id}")
    return run_id

def poll_apify(run_id):
    logging.info("[INFO] Waiting for Apify actor to finish...")
    url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {APIFY_TOKEN}"
    }
    while True:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()["data"]
        status = data["status"]
        logging.debug(f"[DEBUG] Status: {status}")
        if status in {"SUCCEEDED", "FAILED", "ABORTED"}:
            if status != "SUCCEEDED":
                logging.error(f"[ERROR] Crawl finished with status: {status}")
                sys.exit(1)
            logging.info("[INFO] Crawl finished successfully.")
            return data["defaultDatasetId"]
        time.sleep(10)

def download_dataset(dataset_id, output_path):
    logging.info("[INFO] Downloading dataset...")
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
    res = requests.get(url)
    res.raise_for_status()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(res.text)
    logging.info(f"[INFO] Saved crawl results to {output_path}")
    return output_path

def run_clean_pipeline():
    logging.info("[INFO] Running RAG formatting pipeline...")
    subprocess.run(["make", "run"], cwd=str(REPO_ROOT))

def main():
    logging.info("Script started: ragformatter.py")
    try:
        parser = argparse.ArgumentParser(
            description="Crawl a domain and restrict by path filters"
        )
        parser.add_argument("domain", help="Root domain (e.g., https://docs.pinecone.io/)")
        parser.add_argument("filters", nargs="*", help="Optional subpaths (e.g., guides, setup)")
        args = parser.parse_args()

        payload = build_actor_payload(args.domain, args.filters)
        run_id = trigger_apify_run(payload)
        dataset_id = poll_apify(run_id)

        domain_clean = args.domain.split("//")[-1].strip("/").replace(".", "_")
        filename = f"{domain_clean}_crawl.json"
        output_path = INGESTION_SOURCE / filename
        download_dataset(dataset_id, output_path)

        run_clean_pipeline()
        logging.info("Script finished successfully: ragformatter.py")
        print(f"[✅] All done. Data processed and chunked from {filename}.")
    except Exception as e:
        logging.error(f"Script failed: ragformatter.py, Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
