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

# Import logging setup from config.py
from config import setup_logging

# Call the setup function to configure logging
setup_logging()

# Now you can use logging throughout the script
import logging

# Load ingestion folder from config
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import INGESTION_SOURCE

# ----------------------------------------
# Analyze a single PDF for extractability
# ----------------------------------------
def analyze_pdf(path: Path) -> dict:
    # analyzes the PDF
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
        logging.error(f"Error analyzing PDF: {path.name}, Error: {str(e)}")  # Log the error
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
    logging.info("Script started: analyze_pdf_folder.py")  # Log when the script starts

    pdfs = list(INGESTION_SOURCE.rglob("*.pdf"))
    if not pdfs:
        logging.info(f"No PDFs found in {INGESTION_SOURCE}")  # Log if no PDFs are found
        return

    logging.info(f"\n[📄] PDF Pre-Check: {len(pdfs)} file(s) found in {INGESTION_SOURCE}\n")
    header = f"{'File':40} | Pages | Text Pages | % Text"
    logging.info(header)
    logging.info("-" * len(header))

    for pdf in pdfs:
        result = analyze_pdf(pdf)
        logging.info(f"{result['filename'][:40]:40} | "
                     f"{result['pages']:>5}  | "
                     f"{result['text_pages']:>10}  | "
                     f"{result['ratio']:>6}%")

    logging.info("\n[✅] PDF audit complete.\n")
    logging.info("Script finished successfully: analyze_pdf_folder.py")  # Log success when done

# Main entry point of the script
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Script failed: analyze_pdf_folder.py, Error: {str(e)}")  # Log the script failure
