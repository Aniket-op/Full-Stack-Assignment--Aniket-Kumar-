#!/bin/bash

# 1. Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# 2. Activate venv
# Try Windows path first, then Linux/Mac path
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Could not find activate script for virtual environment."
    exit 1
fi

# 3. Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 4. Install Playwright browsers (chromium only to save time/space if desired, but default installs all)
echo "Installing Playwright browsers..."
playwright install chromium

# 5. Start server
echo "Starting server on http://localhost:8000"
# Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
