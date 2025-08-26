#!/usr/bin/env python3
"""
Password Transformer - Main Application Entry Point
Author: cod-decod
"""

import tkinter as tk
import sys
import os

# Add the parent directory to sys.path so we can import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.gui.main_window import PasswordTransformerApp

def main():
    """Main application entry point"""
    try:
        app = PasswordTransformerApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
