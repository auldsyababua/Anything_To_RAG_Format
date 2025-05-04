#!/bin/bash

echo "🔧 Setting up Python virtual environment for PDF analysis..."

# Step 1: Create venv if not exists
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "✅ Virtual environment created in ./venv"
else
  echo "✅ Existing virtual environment found"
fi

# Step 2: Activate it
source venv/bin/activate

# Step 3: Install required packages
echo "📦 Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎉 Environment is ready. To start working, run:"
echo "source venv/bin/activate"
