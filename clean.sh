#!/bin/bash

# Google Chat Viewer - Clean Script
# This script removes the virtual environment and temporary files

echo "🧹 Cleaning up project..."

# Remove virtual environment
if [ -d "venv" ]; then
    echo "🗑️  Removing virtual environment (venv)..."
    rm -rf venv
else
    echo "ℹ️  Virtual environment not found (skipped)"
fi

# Remove __pycache__ directories
echo "🗑️  Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove .DS_Store files (macOS)
echo "🗑️  Removing .DS_Store files..."
find . -type f -name ".DS_Store" -delete

echo "✅ Cleanup complete! Run ./setup.sh to set up the environment again."
