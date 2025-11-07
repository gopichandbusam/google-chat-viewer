#!/bin/bash

# Google Chat Viewer - Start Script
# This script starts the Streamlit application in the virtual environment

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in the current directory."
    exit 1
fi

echo "🚀 Starting Google Chat Viewer..."

# Activate virtual environment
source venv/bin/activate

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Please run ./setup.sh to install dependencies."
    exit 1
fi

echo "✅ Virtual environment activated"
echo "🌐 Starting Streamlit application..."
echo ""
echo "📱 The application will open in your default web browser"
echo "🔗 If it doesn't open automatically, visit: http://localhost:8501"
echo ""
echo "To stop the application, press Ctrl+C in this terminal"
echo ""

# Start Streamlit with custom configuration
streamlit run app.py \
    --server.port=8501 \
    --server.address=localhost \
    --server.headless=false \
    --browser.gatherUsageStats=false \
    --theme.base=light