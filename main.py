#!/usr/bin/env python3
"""
MediaPipe Gesture Control Desktop Application
Main entry point for the application - PyQt6 Version
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui.pyqt_main import PyQtMainWindow, QApplication

def main():
    """Main entry point"""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Create main window
    window = PyQtMainWindow()
    window.show()
    
    # Start the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()