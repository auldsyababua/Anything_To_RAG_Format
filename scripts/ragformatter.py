
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from subprocess import run
from dotenv import load_dotenv

from config import RAW_OUTPUT_TEMPLATE, CLEANED_OUTPUT_TEMPLATE, SPLIT_DIR, FAILED_DIR

load_dotenv()

def get_timestamp_run_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def run_apify_crawl(domain, output_path):
    os.environ["APIFY_DOMAIN"] = domain
    os.environ["APIFY_OUTPUT_PATH"] = str(output_path)
    try:
        print(f"Running Apify crawl for domain: {domain}")
        result = run(["bash", "apify_crawl.sh"], check=True)
        return True
    except Exception as e:
        print(f"Apify crawl failed for {domain}: {e}")
        return False

def process_domain(domain, run_id):
    raw_output_path = RAW_OUTPUT_TEMPLATE.with_name(f"{domain}__{run_id}.json")
    cleaned_output_path = CLEANED_OUTPUT_TEMPLATE.with_name(f"{domain}__{run_id}.json")

    success = run_apify_crawl(domain, raw_output_path)
    if not success:
        FAILED_DIR.mkdir(parents=True, exist_ok=True)
        (FAILED_DIR / f"{domain}__{run_id}.fail").write_text("Apify crawl failed")
        return

    run([
        "python", "scripts/clean_json_chunks.py",
        str(raw_output_path),
        str(cleaned_output_path)
    ])

    run([
        "python", "scripts/split_large_json_files.py",
        str(cleaned_output_path),
        str(SPLIT_DIR)
    ])

def main(domains):
    run_id = get_timestamp_run_id()
    for domain in domains:
        process_domain(domain, run_id)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ragformatter.py domain1 [domain2 ...]")
        sys.exit(1)

    domains = sys.argv[1:]
    main(domains)
