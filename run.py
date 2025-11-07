#!/usr/bin/env python3
"""
Google Chat Viewer - Simple Setup Script
"""

import subprocess
import sys
import os
from pathlib import Path

def setup_and_run():
    """Setup virtual environment and run the application."""
    
    print("🚀 Google Chat Viewer")
    print("=" * 30)
    
    venv_path = Path("venv")
    
    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created!")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False
    
    # Determine pip path
    if os.name == "nt":  # Windows
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:  # macOS/Linux
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Install requirements
    print("📚 Installing requirements...")
    try:
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False
    
    # Launch the app
    print("🌐 Launching Google Chat Viewer...")
    print("   Press Ctrl+C to stop")
    try:
        subprocess.run([str(python_path), "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    setup_and_run()