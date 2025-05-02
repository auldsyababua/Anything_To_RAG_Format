# scripts/analyze_pdf_folder.py

import fitz  # PyMuPDF
from pathlib import Path
from config import SOURCE_FOLDER as PDF_DIR

# ----------------------------------------
# PDF Content Analyzer
# ----------------------------------------
# Scans all PDFs in SOURCE_FOLDER and reports:
# - Total pages
# - Pages with extractable text
# - Content type summary (text/image)
# - Flags image-only documents

def analyze_pdf(file_path: Path) -> dict:
    doc = fitz.open(file_path)
    total_pages = len(doc)
    pages_with_text = 0
    element_types = set()

    for page in doc:
        text = page.get_text()
        if text.strip():
            pages_with_text += 1

        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            if "lines" in block:
                element_types.add("text")
            elif "image" in block:
                element_types.add("image")

    return {
        "file": file_path.name,
        "pages": total_pages,
        "text_pages": pages_with_text,
        "image_only": (pages_with_text == 0),
        "elements": sorted(element_types),
    }

def scan_folder(pdf_folder: Path):
    results = []
    for file_path in pdf_folder.glob("*.pdf"):
        try:
            info = analyze_pdf(file_path)
            results.append(info)
        except Exception as e:
            results.append({"file": file_path.name, "error": str(e)})
    return results

if __name__ == "__main__":
    from pprint import pprint

    results = scan_folder(PDF_DIR)
    sorted_results = sorted(results, key=lambda x: x.get("text_pages", 0), reverse=True)

    for r in sorted_results:
        pprint(r)
