#!/bin/bash

# -----------------------------------------
# RAG Chunking Pipeline Executor
# -----------------------------------------
# Executes full pipeline:
# 1. Activates CLI virtualenv
# 2. Archives previous full.json if exists
# 3. Runs PDF/.md ingestion
# 4. Splits into per-document chunks
# 5. Validates final chunk output

set -e

echo "🔵 Activating Python environment..."
source ../semantic-rag-env/bin/activate

# Resolve full output file from config.py
FULL_OUTPUT_FILE=$(python3 -c 'from config import FULL_OUTPUT_FILE; print(str(FULL_OUTPUT_FILE))')

# Archive previous output
if [ -f "$FULL_OUTPUT_FILE" ]; then
    ts=$(date +%Y%m%d-%H%M%S)
    mv "$FULL_OUTPUT_FILE" "${FULL_OUTPUT_FILE%.json}-$ts.json.bak"
    echo "📦 Archived previous output as ${FULL_OUTPUT_FILE%.json}-$ts.json.bak"
fi

# Run ingestion (PDF/markdown merge)
echo "🔵 Running ingestion and chunking..."
python3 unified_ingest.py

# Optionally enable cleanup:
# echo "🟡 Cleaning low-value or redundant chunks..."
# python3 filter_chunks.py

# Split full.json into per-file chunked JSONs
echo "🔵 Splitting full JSON into per-doc files..."
python3 split_ready_for_customgpt.py

# Validate structural correctness of outputs
echo "🔵 Validating output structure..."
python3 validate_json_output.py

echo "✅ Pipeline complete!"
