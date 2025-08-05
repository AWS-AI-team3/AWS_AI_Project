#!/usr/bin/env python3
"""
MediaPipe Gesture Control Desktop Application
Main entry point for the application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui.main_window import GestureControlApp

def main():
    """Main entry point"""
    app = GestureControlApp()
    app.run()

if __name__ == "__main__":
    main()