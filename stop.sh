#!/bin/bash

# Google Chat Viewer - Stop Script
# This script stops the Streamlit application and related processes

echo "🛑 Stopping Google Chat Viewer..."

# Find and kill Streamlit processes
STREAMLIT_PIDS=$(pgrep -f "streamlit run app.py" 2>/dev/null || true)

if [ -n "$STREAMLIT_PIDS" ]; then
    echo "🔍 Found Streamlit processes: $STREAMLIT_PIDS"
    
    # Kill processes gracefully
    for pid in $STREAMLIT_PIDS; do
        echo "⏹️  Stopping process $pid..."
        kill -TERM "$pid" 2>/dev/null || true
    done
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Force kill if still running
    for pid in $STREAMLIT_PIDS; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "💥 Force stopping process $pid..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
    
    echo "✅ Streamlit processes stopped"
else
    echo "ℹ️  No running Streamlit processes found"
fi

# Also check for any Python processes running app.py
PYTHON_PIDS=$(pgrep -f "python.*app.py" 2>/dev/null || true)

if [ -n "$PYTHON_PIDS" ]; then
    echo "🔍 Found Python app processes: $PYTHON_PIDS"
    
    for pid in $PYTHON_PIDS; do
        echo "⏹️  Stopping Python process $pid..."
        kill -TERM "$pid" 2>/dev/null || true
    done
    
    sleep 1
    
    for pid in $PYTHON_PIDS; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "💥 Force stopping Python process $pid..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
    
    echo "✅ Python processes stopped"
fi

echo "🎉 Google Chat Viewer stopped successfully"
echo ""
echo "To start again, run: ./start.sh"