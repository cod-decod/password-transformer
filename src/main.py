#!/usr/bin/env python3
"""
Password Transformer - Main Application Entry Point
Author: cod-decod
"""

import tkinter as tk
from gui.main_window import PasswordTransformerApp
import sys

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
