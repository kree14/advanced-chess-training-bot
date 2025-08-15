#!/usr/bin/env python3
"""
Advanced Chess Training Bot - Main Entry Point

A comprehensive Chess Training Bot with advanced features including:
- Multi-threaded analysis
- Opening book integration
- Personality configuration
- Training statistics
- Comprehensive position evaluation
- Tactical pattern recognition

Author: Chess Training Bot Project
Version: 2.0 Advanced
"""

import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

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
    Main application entry point with version selection.
    """
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Chess Training Bot")
    parser.add_argument("--basic", action="store_true", help="Launch basic version")
    parser.add_argument("--advanced", action="store_true", help="Launch advanced version (default)")
    parser.add_argument("--version", action="version", version="Chess Training Bot 2.0")
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Advanced Chess Training Bot")
    app.setApplicationDisplayName("Advanced Chess Training Bot")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Chess Training Bot Project")
    
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        # Determine which version to launch
        if args.basic:
            print("Starting Chess Training Bot (Basic Version)...")
            from chess_gui import ChessTrainingBotGUI
            window = ChessTrainingBotGUI()
            version_name = "Basic"
        else:
            print("Starting Advanced Chess Training Bot...")
            from chess_gui_advanced import AdvancedChessTrainingBotGUI
            window = AdvancedChessTrainingBotGUI()
            version_name = "Advanced"
        
        window.show()
        
        print(f"Chess Training Bot ({version_name}) is now running!")
        print("Features available:")
        
        if args.basic:
            print("- Basic move suggestions")
            print("- ELO-based difficulty")
            print("- Simple analysis")
        else:
            print("- Advanced multi-threaded analysis")
            print("- Opening book integration")
            print("- Personality configuration")
            print("- Training statistics tracking")
            print("- Comprehensive position evaluation")
            print("- Tactical pattern recognition")
            print("- Game phase detection")
            print("- Move accuracy analysis")
        
        print("\nClose the application window to exit.")
        
        # Start the Qt event loop
        exit_code = app.exec_()
        
        print(f"Chess Training Bot ({version_name}) closed successfully.")
        return exit_code
        
    except ImportError as e:
        error_msg = f"Failed to import required modules:\n\n{str(e)}\n\nMake sure all files are in the same directory."
        print(f"Error: {error_msg}")
        
        try:
            QMessageBox.critical(None, "Import Error", error_msg)
        except:
            pass
        
        return 1
    
    except Exception as e:
        error_msg = f"Failed to start Chess Training Bot:\n\n{str(e)}"
        print(f"Error: {error_msg}")
        
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
