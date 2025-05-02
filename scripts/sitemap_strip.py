import os
import sys
import json
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

# Hardcoded input/output paths
INPUT_FOLDER = "/Users/colinaulds/Desktop/clean-gpt-json/sitemap_sources"
OUTPUT_FOLDER = "/Users/colinaulds/Desktop/clean-gpt-json/ready_to_crawl"

# Parse all <loc> entries in a sitemap XML into a list of URLs
def parse_sitemap_content(xml_content):
    soup = BeautifulSoup(xml_content, "xml")
    return [loc.text.strip() for loc in soup.find_all("loc")]

# Extract the domain (used for output filename)
def extract_domain(url):
    parsed = urllib.parse.urlparse(url)
    domain = parsed.hostname or "output"
    return domain.replace("www.", "").strip()

# Apply strict path prefix matching based on full slug filters
def url_matches_prefix_path(url, filters):
    path = urllib.parse.urlparse(url).path.strip("/")
    return any(path.startswith(f) for f in filters)

# Build the crawler configuration JSON
def build_config(urls):
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
            "nav, footer, script, style, noscript, svg, img[src^='data:'],\n"
            "[role=\"alert\"],\n[role=\"banner\"],\n[role=\"dialog\"],\n"
            "[role=\"alertdialog\"],\n[role=\"region\"][aria-label*=\"skip\" i],\n"
            "[aria-modal=\"true\"]"
        ),
        "renderingTypeDetectionPercentage": 10,
        "respectRobotsTxtFile": False,
        "saveFiles": True,
        "saveHtml": False,
        "saveHtmlAsFile": True,
        "saveMarkdown": True,
        "saveScreenshots": False,
        "startUrls": [{"url": url, "method": "GET"} for url in urls],
        "useSitemaps": True
    }

# Save the generated JSON to disk
def save_json(config, domain):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    out_path = os.path.join(OUTPUT_FOLDER, f"{domain}_crawler_doc.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    print(f"[OK] {out_path} ({len(config['startUrls'])} URLs)")

# Handle a remote sitemap URL
def process_url(sitemap_url, filters=None):
    print(f"Fetching {sitemap_url}...")
    with urllib.request.urlopen(sitemap_url) as response:
        xml_content = response.read()

    all_urls = parse_sitemap_content(xml_content)
    if not all_urls:
        print("[ERROR] No <loc> tags found.")
        return

    if filters:
        urls = [u for u in all_urls if url_matches_prefix_path(u, filters)]
        print(f"[INFO] Filtered {len(urls)} of {len(all_urls)} URLs with filters: {filters}")
    else:
        urls = all_urls

    if not urls:
        print("[WARNING] No URLs matched filters.")
        return

    domain = extract_domain(urls[0])
    config = build_config(urls)
    save_json(config, domain)

# Handle all .xml files in the input folder
def process_folder(filters=None):
    if not os.path.exists(INPUT_FOLDER):
        print(f"[ERROR] Input folder does not exist: {INPUT_FOLDER}")
        return

    xml_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".xml")]
    if not xml_files:
        print("[INFO] No items in sitemap_sources folder. Either add XML files or specify a URL:")
        print("Example: sitemapper https://example.com/sitemap.xml")
        return

    for name in xml_files:
        path = os.path.join(INPUT_FOLDER, name)
        with open(path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        all_urls = parse_sitemap_content(xml_content)
        if not all_urls:
            print(f"[SKIPPED] No <loc> tags in {name}")
            continue

        if filters:
            urls = [u for u in all_urls if url_matches_prefix_path(u, filters)]
            print(f"[INFO] Filtered {len(urls)} of {len(all_urls)} URLs in {name} using filters: {filters}")
        else:
            urls = all_urls

        if not urls:
            print(f"[SKIPPED] No matching URLs in {name}")
            continue

        domain = extract_domain(urls[0])
        config = build_config(urls)
        save_json(config, domain)

# CLI entrypoint
if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].startswith("http"):
        sitemap_url = sys.argv[1]
        filters = sys.argv[2:] if len(sys.argv) > 2 else []
        process_url(sitemap_url, filters)
    else:
        filters = sys.argv[1:] if len(sys.argv) > 1 else []
        process_folder(filters)
