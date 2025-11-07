#!/bin/bash

# Google Chat Viewer - Setup Script
# This script sets up the virtual environment and installs dependencies

set -e

echo "🚀 Setting up Google Chat Viewer..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  ./start.sh"
echo ""
echo "To stop the application:"
echo "  ./stop.sh"
echo ""
echo "To activate the virtual environment manually:"
echo "  source venv/bin/activate"
echo ""