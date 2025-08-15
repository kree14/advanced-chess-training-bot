#!/usr/bin/env python3
"""
Chess Training Bot - Main Entry Point

A full-fledged Chess Training Bot with adjustable ELO ratings and Stockfish integration.
Built with Python, PyQt5, and the python-chess library.

Author: Chess Training Bot Project
Version: 1.0
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Import our custom modules
try:
    from chess_gui import ChessTrainingBotGUI
except ImportError as e:
    print(f"Error importing chess_gui module: {e}")
    print("Make sure all required files are in the same directory.")
    sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing_deps = []
    
    try:
        import PyQt5
    except ImportError:
        missing_deps.append("PyQt5")
    
    try:
        import chess
    except ImportError:
        missing_deps.append("python-chess")
    
    if missing_deps:
        error_msg = (
            "Missing required dependencies:\n\n" +
            "\n".join(f"- {dep}" for dep in missing_deps) +
            "\n\nPlease install them using:\n" +
            "pip install " + " ".join(missing_deps)
        )
        print(error_msg)
        
        # Try to show GUI error if PyQt5 is available
        if "PyQt5" not in missing_deps:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Missing Dependencies", error_msg)
        
        return False
    
    return True

def main():
    """
    Main application entry point.
    
    This function:
    1. Checks for required dependencies
    2. Creates the QApplication instance
    3. Initializes the main window
    4. Starts the Qt event loop
    5. Handles cleanup on exit
    """
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Chess Training Bot")
    app.setApplicationDisplayName("Chess Training Bot")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Chess Training Bot Project")
    
    # Enable high DPI scaling for better display on high-resolution screens
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        # Create and show the main window
        print("Starting Chess Training Bot...")
        window = ChessTrainingBotGUI()
        window.show()
        
        print("Chess Training Bot is now running!")
        print("Close the application window to exit.")
        
        # Start the Qt event loop
        exit_code = app.exec_()
        
        print("Chess Training Bot closed successfully.")
        return exit_code
        
    except Exception as e:
        error_msg = f"Failed to start Chess Training Bot:\n\n{str(e)}"
        print(f"Error: {error_msg}")
        
        # Show error dialog if possible
        try:
            QMessageBox.critical(None, "Startup Error", error_msg)
        except:
            pass
        
        return 1

if __name__ == "__main__":
    """
    Entry point when script is run directly.
    """
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
