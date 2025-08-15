"""
Chess GUI Module

This module implements the PyQt5 graphical user interface for the Chess Training Bot.
Features a modern, clean interface with chessboard visualization and control panels.
"""

import sys
import chess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QPushButton, QLabel, QSlider, QTextEdit, QMessageBox,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from chess_engine import ChessEngine

# Unicode chess pieces
PIECE_SYMBOLS = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  # White pieces
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'   # Black pieces
}

# Board colors
LIGHT_SQUARE_COLOR = "#F0D9B5"
DARK_SQUARE_COLOR = "#B58863"
HIGHLIGHT_COLOR = "#FFFF99"

class ChessBoard(QWidget):
    """Custom chess board widget with 8x8 grid of buttons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.board_buttons = {}
        self.highlighted_squares = set()
        self.setup_board()
    
    def setup_board(self):
        """Create the 8x8 chess board grid."""
        layout = QGridLayout()
        layout.setSpacing(1)
        
        # Create board squares (buttons)
        for row in range(8):
            for col in range(8):
                button = QPushButton()
                button.setFixedSize(60, 60)
                button.setFont(QFont("Arial", 24))
                
                # Set square color (alternating pattern)
                is_light_square = (row + col) % 2 == 0
                color = LIGHT_SQUARE_COLOR if is_light_square else DARK_SQUARE_COLOR
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        border: 1px solid #8B4513;
                        font-size: 24px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #FF6B35;
                    }}
                """)
                
                # Store button reference
                square_name = chess.square_name(chess.square(col, 7 - row))
                self.board_buttons[square_name] = button
                
                # Add click handler
                button.clicked.connect(lambda checked, sq=square_name: self.on_square_clicked(sq))
                
                layout.addWidget(button, row, col)
        
        self.setLayout(layout)
    
    def on_square_clicked(self, square_name):
        """Handle square click events."""
        if self.parent_window:
            self.parent_window.on_board_square_clicked(square_name)
    
    def update_board(self, board):
        """Update the visual representation of the chess board."""
        # Clear all squares first
        for square_name, button in self.board_buttons.items():
            button.setText("")
            
            # Reset to original color
            square = chess.parse_square(square_name)
            row, col = divmod(square, 8)
            is_light_square = (row + col) % 2 == 0
            color = LIGHT_SQUARE_COLOR if is_light_square else DARK_SQUARE_COLOR
            
            # Apply highlight if square is highlighted
            if square_name in self.highlighted_squares:
                color = HIGHLIGHT_COLOR
            
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 1px solid #8B4513;
                    font-size: 24px;
                }}
                QPushButton:hover {{
                    border: 2px solid #FF6B35;
                }}
            """)
        
        # Place pieces on the board
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                square_name = chess.square_name(square)
                piece_symbol = PIECE_SYMBOLS.get(piece.symbol(), piece.symbol())
                self.board_buttons[square_name].setText(piece_symbol)
    
    def highlight_squares(self, squares):
        """Highlight specific squares on the board."""
        self.highlighted_squares = set(squares)
    
    def clear_highlights(self):
        """Clear all square highlights."""
        self.highlighted_squares.clear()

class ChessTrainingBotGUI(QMainWindow):
    """Main application window for the Chess Training Bot."""
    
    def __init__(self):
        super().__init__()
        self.engine = None
        self.current_board = chess.Board()
        self.selected_square = None
        self.last_analysis = None
        
        self.init_ui()
        self.init_engine()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Chess Training Bot")
        self.setGeometry(100, 100, 900, 700)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4A4A4A;
                color: #FFFFFF;
                border: 1px solid #666666;
                padding: 8px;
                font-size: 11px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QPushButton:pressed {
                background-color: #3A3A3A;
            }
            QSlider::groove:horizontal {
                border: 1px solid #666666;
                height: 8px;
                background: #4A4A4A;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: 1px solid #666666;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QTextEdit {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #666666;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Chess board
        board_frame = QFrame()
        board_frame.setFrameStyle(QFrame.Box)
        board_frame.setStyleSheet("QFrame { border: 2px solid #666666; }")
        board_layout = QVBoxLayout(board_frame)
        
        board_title = QLabel("Chess Board")
        board_title.setAlignment(Qt.AlignCenter)
        board_title.setFont(QFont("Arial", 14, QFont.Bold))
        board_layout.addWidget(board_title)
        
        self.chess_board = ChessBoard(self)
        board_layout.addWidget(self.chess_board)
        
        # Right panel - Controls
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Box)
        control_frame.setStyleSheet("QFrame { border: 2px solid #666666; }")
        control_frame.setFixedWidth(300)
        control_layout = QVBoxLayout(control_frame)
        
        # Title
        control_title = QLabel("Training Controls")
        control_title.setAlignment(Qt.AlignCenter)
        control_title.setFont(QFont("Arial", 14, QFont.Bold))
        control_layout.addWidget(control_title)
        
        # ELO Rating Slider
        elo_label = QLabel("Bot ELO Rating:")
        elo_label.setFont(QFont("Arial", 12))
        control_layout.addWidget(elo_label)
        
        self.elo_slider = QSlider(Qt.Horizontal)
        self.elo_slider.setMinimum(800)
        self.elo_slider.setMaximum(2500)
        self.elo_slider.setValue(1500)
        self.elo_slider.setTickPosition(QSlider.TicksBelow)
        self.elo_slider.setTickInterval(200)
        self.elo_slider.valueChanged.connect(self.on_elo_changed)
        control_layout.addWidget(self.elo_slider)
        
        self.elo_value_label = QLabel("Current ELO: 1500")
        self.elo_value_label.setAlignment(Qt.AlignCenter)
        self.elo_value_label.setFont(QFont("Arial", 11, QFont.Bold))
        control_layout.addWidget(self.elo_value_label)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.suggest_move_btn = QPushButton("Suggest Move")
        self.suggest_move_btn.clicked.connect(self.suggest_move)
        button_layout.addWidget(self.suggest_move_btn)
        
        self.make_bot_move_btn = QPushButton("Make Bot Move")
        self.make_bot_move_btn.clicked.connect(self.make_bot_move)
        button_layout.addWidget(self.make_bot_move_btn)
        
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.clicked.connect(self.new_game)
        button_layout.addWidget(self.new_game_btn)
        
        self.reset_position_btn = QPushButton("Reset Position")
        self.reset_position_btn.clicked.connect(self.reset_position)
        button_layout.addWidget(self.reset_position_btn)
        
        control_layout.addLayout(button_layout)
        
        # Evaluation display
        eval_label = QLabel("Analysis & Evaluation:")
        eval_label.setFont(QFont("Arial", 12))
        control_layout.addWidget(eval_label)
        
        self.evaluation_text = QTextEdit()
        self.evaluation_text.setMaximumHeight(200)
        self.evaluation_text.setPlainText("Welcome to Chess Training Bot!\n\nSet your desired ELO rating and start training.\nClick 'Suggest Move' for move recommendations.")
        control_layout.addWidget(self.evaluation_text)
        
        # Add panels to main layout
        main_layout.addWidget(board_frame, 2)
        main_layout.addWidget(control_frame, 1)
        
        # Update board display
        self.update_board_display()
    
    def init_engine(self):
        """Initialize the chess engine."""
        try:
            self.engine = ChessEngine()
            self.evaluation_text.append("\n✓ Stockfish engine initialized successfully!")
        except Exception as e:
            error_msg = f"Failed to initialize chess engine:\n{str(e)}"
            self.evaluation_text.append(f"\n✗ {error_msg}")
            QMessageBox.critical(self, "Engine Error", error_msg)
    
    def on_elo_changed(self, value):
        """Handle ELO slider value changes."""
        self.elo_value_label.setText(f"Current ELO: {value}")
    
    def on_board_square_clicked(self, square_name):
        """Handle chess board square clicks."""
        if not self.selected_square:
            # First click - select piece
            square = chess.parse_square(square_name)
            piece = self.current_board.piece_at(square)
            if piece and piece.color == self.current_board.turn:
                self.selected_square = square_name
                self.chess_board.highlight_squares([square_name])
                self.evaluation_text.append(f"\nSelected: {square_name} ({PIECE_SYMBOLS.get(piece.symbol(), piece.symbol())})")
        else:
            # Second click - attempt move
            try:
                from_square = chess.parse_square(self.selected_square)
                to_square = chess.parse_square(square_name)
                move = chess.Move(from_square, to_square)
                
                # Check for promotion (simplified - always promote to queen)
                if (self.current_board.piece_at(from_square) and 
                    self.current_board.piece_at(from_square).piece_type == chess.PAWN and
                    (chess.square_rank(to_square) == 7 or chess.square_rank(to_square) == 0)):
                    move = chess.Move(from_square, to_square, promotion=chess.QUEEN)
                
                if move in self.current_board.legal_moves:
                    self.current_board.push(move)
                    self.update_board_display()
                    self.evaluation_text.append(f"Move played: {move}")
                    
                    if self.current_board.is_game_over():
                        self.handle_game_over()
                else:
                    self.evaluation_text.append(f"Illegal move: {self.selected_square} to {square_name}")
                    
            except Exception as e:
                self.evaluation_text.append(f"Move error: {str(e)}")
            
            # Clear selection
            self.selected_square = None
            self.chess_board.clear_highlights()
    
    def suggest_move(self):
        """Get move suggestion from the engine."""
        if not self.engine:
            self.evaluation_text.append("\n✗ Engine not available")
            return
        
        if self.current_board.is_game_over():
            self.evaluation_text.append("\n✗ Game is over")
            return
        
        try:
            elo = self.elo_slider.value()
            self.evaluation_text.append(f"\n🤔 Analyzing position (ELO: {elo})...")
            
            # Update engine board state
            self.engine.set_board(self.current_board)
            
            # Get analysis
            analysis = self.engine.analyze_position(self.current_board, elo)
            self.last_analysis = analysis
            
            if analysis['suggested_move']:
                suggested = analysis['suggested_move']
                best = analysis['best_move']
                eval_text = analysis.get('eval_text', 'No evaluation')
                
                self.evaluation_text.append(f"\n📊 Evaluation: {eval_text}")
                self.evaluation_text.append(f"🎯 Suggested move: {suggested}")
                
                if suggested != best:
                    self.evaluation_text.append(f"🏆 Best move: {best}")
                    self.evaluation_text.append("💡 Playing sub-optimal move for training")
                else:
                    self.evaluation_text.append("✨ Suggested move is the best move!")
                
                # Highlight suggested move squares
                from_square = chess.square_name(suggested.from_square)
                to_square = chess.square_name(suggested.to_square)
                self.chess_board.highlight_squares([from_square, to_square])
                
            else:
                self.evaluation_text.append(f"\n✗ {analysis.get('message', 'Analysis failed')}")
                
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            self.evaluation_text.append(f"\n✗ {error_msg}")
    
    def make_bot_move(self):
        """Make the bot's suggested move automatically."""
        if not self.last_analysis or not self.last_analysis.get('suggested_move'):
            self.evaluation_text.append("\n⚠️ No move suggestion available. Click 'Suggest Move' first.")
            return
        
        try:
            move = self.last_analysis['suggested_move']
            
            if move in self.current_board.legal_moves:
                self.current_board.push(move)
                self.update_board_display()
                self.evaluation_text.append(f"\n🤖 Bot played: {move}")
                
                # Clear highlights and analysis
                self.chess_board.clear_highlights()
                self.last_analysis = None
                
                if self.current_board.is_game_over():
                    self.handle_game_over()
            else:
                self.evaluation_text.append(f"\n✗ Suggested move is no longer legal: {move}")
                
        except Exception as e:
            error_msg = f"Move execution error: {str(e)}"
            self.evaluation_text.append(f"\n✗ {error_msg}")
    
    def new_game(self):
        """Start a new game."""
        self.current_board = chess.Board()
        self.selected_square = None
        self.last_analysis = None
        self.chess_board.clear_highlights()
        self.update_board_display()
        self.evaluation_text.append("\n🆕 New game started!")
        
        if self.engine:
            self.engine.reset_board()
    
    def reset_position(self):
        """Reset to empty board."""
        self.current_board = chess.Board(None)  # Empty board
        self.selected_square = None
        self.last_analysis = None
        self.chess_board.clear_highlights()
        self.update_board_display()
        self.evaluation_text.append("\n🔄 Board reset to empty position")
    
    def update_board_display(self):
        """Update the visual chess board."""
        self.chess_board.update_board(self.current_board)
    
    def handle_game_over(self):
        """Handle game over scenarios."""
        result = self.current_board.result()
        outcome = self.current_board.outcome()
        
        if result == "1-0":
            message = "🏆 White wins!"
        elif result == "0-1":
            message = "🏆 Black wins!"
        else:
            message = "🤝 Game drawn!"
        
        if outcome:
            if outcome.termination == chess.Termination.CHECKMATE:
                message += " (Checkmate)"
            elif outcome.termination == chess.Termination.STALEMATE:
                message += " (Stalemate)"
            elif outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
                message += " (Insufficient material)"
            elif outcome.termination == chess.Termination.THREEFOLD_REPETITION:
                message += " (Threefold repetition)"
            elif outcome.termination == chess.Termination.FIFTY_MOVES:
                message += " (50-move rule)"
        
        self.evaluation_text.append(f"\n🎮 Game Over: {message}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.engine:
            self.engine.quit()
        event.accept()

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Chess Training Bot")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = ChessTrainingBotGUI()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
