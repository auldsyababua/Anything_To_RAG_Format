# scripts/analyze_pdf_folder.py

# ----------------------------------------
# PDF Analyzer
# ----------------------------------------
# Scans all PDFs in the ingestion_source directory
# - Counts # of pages per file
# - Estimates % of pages with extractable text
# - Flags scanned/image-based or empty PDFs
# Useful for pre-checking OCR needs or ingest quality
# ----------------------------------------

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path

# Load ingestion folder from config
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import INGESTION_SOURCE

# ----------------------------------------
# Analyze a single PDF for extractability
# ----------------------------------------
def analyze_pdf(path: Path) -> dict:
    try:
        doc = fitz.open(path)
        total_pages = len(doc)
        extractable_pages = sum(1 for page in doc if page.get_text().strip())
        return {
            "filename": path.name,
            "pages": total_pages,
            "text_pages": extractable_pages,
            "ratio": round(100 * extractable_pages / max(1, total_pages), 1)
        }
    except Exception as e:
        return {
            "filename": path.name,
            "pages": 0,
            "text_pages": 0,
            "ratio": 0.0,
            "error": str(e)
        }

# ----------------------------------------
# Walk the ingestion folder and analyze all PDFs
# ----------------------------------------
def main():
    pdfs = list(INGESTION_SOURCE.rglob("*.pdf"))
    if not pdfs:
        print(f"[INFO] No PDFs found in {INGESTION_SOURCE}")
        return

    print(f"\n[📄] PDF Pre-Check: {len(pdfs)} file(s) found in {INGESTION_SOURCE}\n")
    header = f"{'File':40} | Pages | Text Pages | % Text"
    print(header)
    print("-" * len(header))

    for pdf in pdfs:
        result = analyze_pdf(pdf)
        print(f"{result['filename'][:40]:40} | "
              f"{result['pages']:>5}  | "
              f"{result['text_pages']:>10}  | "
              f"{result['ratio']:>6}%")

    print("\n[✅] PDF audit complete.\n")

if __name__ == "__main__":
    main()
