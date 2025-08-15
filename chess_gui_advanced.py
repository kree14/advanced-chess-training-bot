"""
Advanced Chess GUI Module

Enhanced PyQt5 interface with advanced training features, analysis panels,
personality settings, and comprehensive chess training tools.
"""

import sys
import chess
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QPushButton, QLabel, QSlider, QTextEdit, QMessageBox,
    QFrame, QSizePolicy, QTabWidget, QGroupBox, QCheckBox, QSpinBox,
    QComboBox, QProgressBar, QSplitter, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush
from chess_engine import AdvancedChessEngine, GamePhase, MoveAnalysis

# Unicode chess pieces
PIECE_SYMBOLS = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  # White pieces
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'   # Black pieces
}

# Board colors
LIGHT_SQUARE_COLOR = "#F0D9B5"
DARK_SQUARE_COLOR = "#B58863"
HIGHLIGHT_COLOR = "#FFFF99"
LAST_MOVE_COLOR = "#FFE135"
SUGGESTED_MOVE_COLOR = "#90EE90"

class AnalysisWorker(QThread):
    """Background thread for chess analysis to keep GUI responsive."""
    
    analysis_complete = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, engine, board, elo, analysis_time=1.0):
        super().__init__()
        self.engine = engine
        self.board = board.copy()
        self.elo = elo
        self.analysis_time = analysis_time
    
    def run(self):
        """Run analysis in background thread."""
        try:
            result = self.engine.analyze_position_advanced(self.board, self.elo, self.analysis_time)
            self.analysis_complete.emit(result)
        except Exception as e:
            self.analysis_error.emit(str(e))

class PersonalityDialog(QDialog):
    """Dialog for configuring bot personality traits."""
    
    def __init__(self, current_traits, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bot Personality Settings")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Personality sliders
        self.trait_sliders = {}
        form_layout = QFormLayout()
        
        traits = {
            "aggression": "Aggression (0=Passive, 1=Aggressive)",
            "positional_play": "Positional Play (0=Tactical, 1=Positional)",
            "tactical_awareness": "Tactical Awareness (0=Blind, 1=Sharp)",
            "endgame_skill": "Endgame Skill (0=Weak, 1=Strong)",
            "opening_knowledge": "Opening Knowledge (0=Limited, 1=Extensive)"
        }
        
        for trait, description in traits.items():
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(int(current_traits.get(trait, 0.5) * 100))
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(25)
            
            value_label = QLabel(f"{slider.value()}%")
            slider.valueChanged.connect(lambda v, lbl=value_label: lbl.setText(f"{v}%"))
            
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.addWidget(slider)
            container_layout.addWidget(value_label)
            
            form_layout.addRow(description, container)
            self.trait_sliders[trait] = slider
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_traits(self):
        """Get the configured personality traits."""
        return {trait: slider.value() / 100.0 for trait, slider in self.trait_sliders.items()}

class AdvancedChessBoard(QWidget):
    """Advanced chess board with move highlighting and annotations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.board_buttons = {}
        self.highlighted_squares = set()
        self.last_move_squares = set()
        self.suggested_move_squares = set()
        self.setup_board()
    
    def setup_board(self):
        """Create the 8x8 chess board grid with coordinates."""
        main_layout = QVBoxLayout()
        
        # Board with coordinates
        board_container = QWidget()
        board_layout = QGridLayout(board_container)
        board_layout.setSpacing(1)
        
        # Add file labels (a-h) at top
        for col in range(8):
            file_label = QLabel(chr(ord('a') + col))
            file_label.setAlignment(Qt.AlignCenter)
            file_label.setFont(QFont("Arial", 10, QFont.Bold))
            board_layout.addWidget(file_label, 0, col + 1)
        
        # Add rank labels (8-1) on left and board squares
        for row in range(8):
            # Rank label
            rank_label = QLabel(str(8 - row))
            rank_label.setAlignment(Qt.AlignCenter)
            rank_label.setFont(QFont("Arial", 10, QFont.Bold))
            board_layout.addWidget(rank_label, row + 1, 0)
            
            # Board squares
            for col in range(8):
                button = QPushButton()
                button.setFixedSize(60, 60)
                button.setFont(QFont("Arial", 24))
                
                # Set square color
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
                
                board_layout.addWidget(button, row + 1, col + 1)
        
        main_layout.addWidget(board_container)
        self.setLayout(main_layout)
    
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
            base_color = LIGHT_SQUARE_COLOR if is_light_square else DARK_SQUARE_COLOR
            
            # Apply special highlighting
            color = base_color
            if square_name in self.suggested_move_squares:
                color = SUGGESTED_MOVE_COLOR
            elif square_name in self.last_move_squares:
                color = LAST_MOVE_COLOR
            elif square_name in self.highlighted_squares:
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
    
    def highlight_squares(self, squares, highlight_type="normal"):
        """Highlight specific squares on the board."""
        if highlight_type == "suggested":
            self.suggested_move_squares = set(squares)
        elif highlight_type == "last_move":
            self.last_move_squares = set(squares)
        else:
            self.highlighted_squares = set(squares)
    
    def clear_highlights(self, highlight_type="all"):
        """Clear square highlights."""
        if highlight_type == "all" or highlight_type == "normal":
            self.highlighted_squares.clear()
        if highlight_type == "all" or highlight_type == "suggested":
            self.suggested_move_squares.clear()
        if highlight_type == "all" or highlight_type == "last_move":
            self.last_move_squares.clear()

class MoveAnalysisWidget(QWidget):
    """Widget for displaying detailed move analysis."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the move analysis interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Move Analysis")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Analysis table
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(5)
        self.analysis_table.setHorizontalHeaderLabels(["Move", "Evaluation", "Depth", "Accuracy", "Quality"])
        
        # Resize columns
        header = self.analysis_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.analysis_table)
        
        # Position evaluation
        eval_group = QGroupBox("Position Evaluation")
        eval_layout = QVBoxLayout(eval_group)
        
        self.position_eval_text = QTextEdit()
        self.position_eval_text.setMaximumHeight(150)
        self.position_eval_text.setReadOnly(True)
        eval_layout.addWidget(self.position_eval_text)
        
        layout.addWidget(eval_group)
    
    def update_analysis(self, analysis_data):
        """Update the analysis display with new data."""
        if not analysis_data:
            return
        
        # Update move analysis table
        move_analyses = analysis_data.get('move_analyses', [])
        self.analysis_table.setRowCount(len(move_analyses))
        
        for row, analysis in enumerate(move_analyses):
            # Move
            move_item = QTableWidgetItem(str(analysis.move))
            self.analysis_table.setItem(row, 0, move_item)
            
            # Evaluation
            if analysis.score:
                if analysis.score.is_mate():
                    eval_text = f"M{analysis.score.white().mate()}"
                else:
                    cp = analysis.score.white().score()
                    eval_text = f"{cp/100:.2f}" if cp is not None else "0.00"
            else:
                eval_text = "N/A"
            eval_item = QTableWidgetItem(eval_text)
            self.analysis_table.setItem(row, 1, eval_item)
            
            # Depth
            depth_item = QTableWidgetItem(str(analysis.depth))
            self.analysis_table.setItem(row, 2, depth_item)
            
            # Accuracy
            accuracy_item = QTableWidgetItem(f"{analysis.accuracy:.1f}%")
            self.analysis_table.setItem(row, 3, accuracy_item)
            
            # Quality
            if analysis.blunder:
                quality = "Blunder"
                accuracy_item.setBackground(QColor("#FF6B6B"))
            elif analysis.mistake:
                quality = "Mistake"
                accuracy_item.setBackground(QColor("#FFB347"))
            elif analysis.inaccuracy:
                quality = "Inaccuracy"
                accuracy_item.setBackground(QColor("#FFFF99"))
            else:
                quality = "Good"
                accuracy_item.setBackground(QColor("#90EE90"))
            
            quality_item = QTableWidgetItem(quality)
            self.analysis_table.setItem(row, 4, quality_item)
        
        # Update position evaluation
        position_eval = analysis_data.get('position_evaluation')
        if position_eval:
            eval_text = f"Game Phase: {position_eval.game_phase.value.title()}\n"
            eval_text += f"Material: White {position_eval.material_balance['white']} - Black {position_eval.material_balance['black']}\n"
            eval_text += f"King Safety: White {position_eval.king_safety['white']:.1f} - Black {position_eval.king_safety['black']:.1f}\n"
            
            if position_eval.tactical_motifs:
                eval_text += f"Tactical Motifs: {', '.join(position_eval.tactical_motifs)}\n"
            
            if position_eval.strategic_themes:
                eval_text += f"Strategic Themes: {', '.join(position_eval.strategic_themes)}\n"
            
            self.position_eval_text.setPlainText(eval_text)

class TrainingStatsWidget(QWidget):
    """Widget for tracking training statistics."""
    
    def __init__(self):
        super().__init__()
        self.stats = {
            'games_played': 0,
            'moves_played': 0,
            'accuracy_sum': 0.0,
            'blunders': 0,
            'mistakes': 0,
            'inaccuracies': 0,
            'excellent_moves': 0
        }
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the training statistics interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Training Statistics")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Stats display
        stats_group = QGroupBox("Session Stats")
        stats_layout = QFormLayout(stats_group)
        
        self.games_label = QLabel("0")
        self.moves_label = QLabel("0")
        self.accuracy_label = QLabel("0.0%")
        self.blunders_label = QLabel("0")
        self.mistakes_label = QLabel("0")
        self.inaccuracies_label = QLabel("0")
        self.excellent_label = QLabel("0")
        
        stats_layout.addRow("Games Played:", self.games_label)
        stats_layout.addRow("Moves Played:", self.moves_label)
        stats_layout.addRow("Average Accuracy:", self.accuracy_label)
        stats_layout.addRow("Blunders:", self.blunders_label)
        stats_layout.addRow("Mistakes:", self.mistakes_label)
        stats_layout.addRow("Inaccuracies:", self.inaccuracies_label)
        stats_layout.addRow("Excellent Moves:", self.excellent_label)
        
        layout.addWidget(stats_group)
        
        # Reset button
        reset_btn = QPushButton("Reset Statistics")
        reset_btn.clicked.connect(self.reset_stats)
        layout.addWidget(reset_btn)
    
    def update_move_stats(self, analysis: MoveAnalysis):
        """Update statistics with a new move analysis."""
        self.stats['moves_played'] += 1
        self.stats['accuracy_sum'] += analysis.accuracy
        
        if analysis.blunder:
            self.stats['blunders'] += 1
        elif analysis.mistake:
            self.stats['mistakes'] += 1
        elif analysis.inaccuracy:
            self.stats['inaccuracies'] += 1
        elif analysis.accuracy >= 95:
            self.stats['excellent_moves'] += 1
        
        self.update_display()
    
    def game_completed(self):
        """Mark a game as completed."""
        self.stats['games_played'] += 1
        self.update_display()
    
    def update_display(self):
        """Update the statistics display."""
        self.games_label.setText(str(self.stats['games_played']))
        self.moves_label.setText(str(self.stats['moves_played']))
        
        if self.stats['moves_played'] > 0:
            avg_accuracy = self.stats['accuracy_sum'] / self.stats['moves_played']
            self.accuracy_label.setText(f"{avg_accuracy:.1f}%")
        
        self.blunders_label.setText(str(self.stats['blunders']))
        self.mistakes_label.setText(str(self.stats['mistakes']))
        self.inaccuracies_label.setText(str(self.stats['inaccuracies']))
        self.excellent_label.setText(str(self.stats['excellent_moves']))
    
    def reset_stats(self):
        """Reset all statistics."""
        for key in self.stats:
            self.stats[key] = 0 if key != 'accuracy_sum' else 0.0
        self.update_display()

class AdvancedChessTrainingBotGUI(QMainWindow):
    """Advanced main application window with comprehensive training features."""
    
    def __init__(self):
        super().__init__()
        self.engine = None
        self.current_board = chess.Board()
        self.selected_square = None
        self.last_analysis = None
        self.analysis_worker = None
        self.settings = QSettings("ChessTrainingBot", "Advanced")
        
        self.init_ui()
        self.init_engine()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the advanced user interface."""
        self.setWindowTitle("Advanced Chess Training Bot")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 11px;
            }
            QPushButton {
                background-color: #4A4A4A;
                color: #FFFFFF;
                border: 1px solid #666666;
                padding: 6px;
                font-size: 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QPushButton:pressed {
                background-color: #3A3A3A;
            }
            QTabWidget::pane {
                border: 1px solid #666666;
                background-color: #3A3A3A;
            }
            QTabBar::tab {
                background-color: #4A4A4A;
                color: #FFFFFF;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #5A5A5A;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666666;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTableWidget {
                background-color: #3A3A3A;
                alternate-background-color: #4A4A4A;
                selection-background-color: #5A5A5A;
                gridline-color: #666666;
            }
            QTextEdit {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #666666;
                font-family: 'Courier New', monospace;
                font-size: 9px;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        central_widget_layout = QHBoxLayout(central_widget)
        central_widget_layout.addWidget(main_splitter)
        
        # Left panel - Chess board
        board_frame = QFrame()
        board_frame.setFrameStyle(QFrame.Box)
        board_frame.setStyleSheet("QFrame { border: 2px solid #666666; }")
        board_layout = QVBoxLayout(board_frame)
        
        board_title = QLabel("Chess Board")
        board_title.setAlignment(Qt.AlignCenter)
        board_title.setFont(QFont("Arial", 14, QFont.Bold))
        board_layout.addWidget(board_title)
        
        self.chess_board = AdvancedChessBoard(self)
        board_layout.addWidget(self.chess_board)
        
        # Game info
        game_info_layout = QHBoxLayout()
        self.game_phase_label = QLabel("Phase: Opening")
        self.move_count_label = QLabel("Move: 1")
        self.turn_label = QLabel("Turn: White")
        
        game_info_layout.addWidget(self.game_phase_label)
        game_info_layout.addWidget(self.move_count_label)
        game_info_layout.addWidget(self.turn_label)
        board_layout.addLayout(game_info_layout)
        
        main_splitter.addWidget(board_frame)
        
        # Right panel - Tabbed interface
        right_panel = QTabWidget()
        
        # Training tab
        training_tab = self.create_training_tab()
        right_panel.addTab(training_tab, "Training")
        
        # Analysis tab
        self.analysis_widget = MoveAnalysisWidget()
        right_panel.addTab(self.analysis_widget, "Analysis")
        
        # Statistics tab
        self.stats_widget = TrainingStatsWidget()
        right_panel.addTab(self.stats_widget, "Statistics")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        right_panel.addTab(settings_tab, "Settings")
        
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([600, 800])
        
        # Update board display
        self.update_board_display()
        self.update_game_info()
    
    def create_training_tab(self):
        """Create the main training control tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # ELO Rating Control
        elo_group = QGroupBox("Bot Strength")
        elo_layout = QVBoxLayout(elo_group)
        
        elo_label = QLabel("Bot ELO Rating:")
        elo_label.setFont(QFont("Arial", 12))
        elo_layout.addWidget(elo_label)
        
        self.elo_slider = QSlider(Qt.Horizontal)
        self.elo_slider.setMinimum(800)
        self.elo_slider.setMaximum(2500)
        self.elo_slider.setValue(1500)
        self.elo_slider.setTickPosition(QSlider.TicksBelow)
        self.elo_slider.setTickInterval(200)
        self.elo_slider.valueChanged.connect(self.on_elo_changed)
        elo_layout.addWidget(self.elo_slider)
        
        self.elo_value_label = QLabel("Current ELO: 1500")
        self.elo_value_label.setAlignment(Qt.AlignCenter)
        self.elo_value_label.setFont(QFont("Arial", 11, QFont.Bold))
        elo_layout.addWidget(self.elo_value_label)
        
        layout.addWidget(elo_group)
        
        # Analysis Controls
        analysis_group = QGroupBox("Analysis Controls")
        analysis_layout = QVBoxLayout(analysis_group)
        
        # Analysis time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Analysis Time:"))
        self.analysis_time_spin = QSpinBox()
        self.analysis_time_spin.setMinimum(1)
        self.analysis_time_spin.setMaximum(30)
        self.analysis_time_spin.setValue(3)
        self.analysis_time_spin.setSuffix(" sec")
        time_layout.addWidget(self.analysis_time_spin)
        analysis_layout.addLayout(time_layout)
        
        # Analysis buttons
        self.suggest_move_btn = QPushButton("Suggest Move")
        self.suggest_move_btn.clicked.connect(self.suggest_move)
        analysis_layout.addWidget(self.suggest_move_btn)
        
        self.make_bot_move_btn = QPushButton("Make Bot Move")
        self.make_bot_move_btn.clicked.connect(self.make_bot_move)
        analysis_layout.addWidget(self.make_bot_move_btn)
        
        self.get_hints_btn = QPushButton("Get Training Hints")
        self.get_hints_btn.clicked.connect(self.get_training_hints)
        analysis_layout.addWidget(self.get_hints_btn)
        
        layout.addWidget(analysis_group)
        
        # Game Controls
        game_group = QGroupBox("Game Controls")
        game_layout = QVBoxLayout(game_group)
        
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.clicked.connect(self.new_game)
        game_layout.addWidget(self.new_game_btn)
        
        self.reset_position_btn = QPushButton("Reset Position")
        self.reset_position_btn.clicked.connect(self.reset_position)
        game_layout.addWidget(self.reset_position_btn)
        
        self.flip_board_btn = QPushButton("Flip Board")
        self.flip_board_btn.clicked.connect(self.flip_board)
        game_layout.addWidget(self.flip_board_btn)
        
        layout.addWidget(game_group)
        
        # Evaluation display
        eval_group = QGroupBox("Evaluation & Messages")
        eval_layout = QVBoxLayout(eval_group)
        
        self.evaluation_text = QTextEdit()
        self.evaluation_text.setMaximumHeight(200)
        self.evaluation_text.setPlainText("Welcome to Advanced Chess Training Bot!\n\nSet your desired ELO rating and start training.\nClick 'Suggest Move' for move recommendations.")
        eval_layout.addWidget(self.evaluation_text)
        
        layout.addWidget(eval_group)
        
        # Progress bar for analysis
        self.analysis_progress = QProgressBar()
        self.analysis_progress.setVisible(False)
        layout.addWidget(self.analysis_progress)
        
        return tab
    
    def create_settings_tab(self):
        """Create the settings configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Bot Personality
        personality_group = QGroupBox("Bot Personality")
        personality_layout = QVBoxLayout(personality_group)
        
        self.personality_btn = QPushButton("Configure Personality")
        self.personality_btn.clicked.connect(self.configure_personality)
        personality_layout.addWidget(self.personality_btn)
        
        self.personality_display = QLabel("Current: Balanced")
        personality_layout.addWidget(self.personality_display)
        
        layout.addWidget(personality_group)
        
        # Training Mode
        mode_group = QGroupBox("Training Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.training_mode_combo = QComboBox()
        self.training_mode_combo.addItems(["Adaptive", "Tactical", "Positional", "Endgame", "Opening"])
        mode_layout.addWidget(self.training_mode_combo)
        
        layout.addWidget(mode_group)
        
        # Display Options
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout(display_group)
        
        self.show_coordinates_cb = QCheckBox("Show Board Coordinates")
        self.show_coordinates_cb.setChecked(True)
        display_layout.addWidget(self.show_coordinates_cb)
        
        self.highlight_last_move_cb = QCheckBox("Highlight Last Move")
        self.highlight_last_move_cb.setChecked(True)
        display_layout.addWidget(self.highlight_last_move_cb)
        
        self.auto_analysis_cb = QCheckBox("Auto-analyze Moves")
        self.auto_analysis_cb.setChecked(False)
        display_layout.addWidget(self.auto_analysis_cb)
        
        layout.addWidget(display_group)
        
        # Engine Settings
        engine_group = QGroupBox("Engine Settings")
        engine_layout = QFormLayout(engine_group)
        
        self.hash_size_spin = QSpinBox()
        self.hash_size_spin.setMinimum(16)
        self.hash_size_spin.setMaximum(2048)
        self.hash_size_spin.setValue(256)
        self.hash_size_spin.setSuffix(" MB")
        engine_layout.addRow("Hash Size:", self.hash_size_spin)
        
        self.threads_spin = QSpinBox()
        self.threads_spin.setMinimum(1)
        self.threads_spin.setMaximum(16)
        self.threads_spin.setValue(4)
        engine_layout.addRow("Threads:", self.threads_spin)
        
        layout.addWidget(engine_group)
        
        # Save/Load Settings
        settings_buttons = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        load_btn = QPushButton("Load Settings")
        load_btn.clicked.connect(self.load_settings)
        
        settings_buttons.addWidget(save_btn)
        settings_buttons.addWidget(load_btn)
        layout.addLayout(settings_buttons)
        
        layout.addStretch()
        return tab
    
    def init_engine(self):
        """Initialize the advanced chess engine."""
        try:
            self.engine = AdvancedChessEngine()
            self.evaluation_text.append("\n✓ Advanced Stockfish engine initialized successfully!")
        except Exception as e:
            error_msg = f"Failed to initialize chess engine:\n{str(e)}"
            self.evaluation_text.append(f"\n✗ {error_msg}")
            QMessageBox.critical(self, "Engine Error", error_msg)
    
    def configure_personality(self):
        """Open personality configuration dialog."""
        if not self.engine:
            return
        
        current_traits = self.engine.personality_traits
        dialog = PersonalityDialog(current_traits, self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_traits = dialog.get_traits()
            self.engine.set_personality(new_traits)
            
            # Update display
            trait_names = []
            for trait, value in new_traits.items():
                if value > 0.7:
                    trait_names.append(trait.replace('_', ' ').title())
            
            if trait_names:
                self.personality_display.setText(f"Current: {', '.join(trait_names[:2])}")
            else:
                self.personality_display.setText("Current: Balanced")
            
            self.evaluation_text.append(f"\n🎭 Bot personality updated: {trait_names}")
    
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
                    # Highlight last move
                    if self.highlight_last_move_cb.isChecked():
                        self.chess_board.highlight_squares([self.selected_square, square_name], "last_move")
                    
                    self.current_board.push(move)
                    self.update_board_display()
                    self.update_game_info()
                    self.evaluation_text.append(f"Move played: {move}")
                    
                    # Auto-analyze if enabled
                    if self.auto_analysis_cb.isChecked():
                        self.analyze_last_move()
                    
                    if self.current_board.is_game_over():
                        self.handle_game_over()
                        self.stats_widget.game_completed()
                else:
                    self.evaluation_text.append(f"Illegal move: {self.selected_square} to {square_name}")
                    
            except Exception as e:
                self.evaluation_text.append(f"Move error: {str(e)}")
            
            # Clear selection
            self.selected_square = None
            self.chess_board.clear_highlights("normal")
    
    def suggest_move(self):
        """Get move suggestion from the engine."""
        if not self.engine:
            self.evaluation_text.append("\n✗ Engine not available")
            return
        
        if self.current_board.is_game_over():
            self.evaluation_text.append("\n✗ Game is over")
            return
        
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.evaluation_text.append("\n⏳ Analysis already in progress...")
            return
        
        try:
            elo = self.elo_slider.value()
            analysis_time = self.analysis_time_spin.value()
            
            self.evaluation_text.append(f"\n🤔 Analyzing position (ELO: {elo}, Time: {analysis_time}s)...")
            
            # Show progress bar
            self.analysis_progress.setVisible(True)
            self.analysis_progress.setRange(0, 0)  # Indeterminate progress
            
            # Disable buttons during analysis
            self.suggest_move_btn.setEnabled(False)
            self.make_bot_move_btn.setEnabled(False)
            
            # Start background analysis
            self.analysis_worker = AnalysisWorker(self.engine, self.current_board, elo, analysis_time)
            self.analysis_worker.analysis_complete.connect(self.on_analysis_complete)
            self.analysis_worker.analysis_error.connect(self.on_analysis_error)
            self.analysis_worker.start()
            
        except Exception as e:
            error_msg = f"Analysis setup error: {str(e)}"
            self.evaluation_text.append(f"\n✗ {error_msg}")
            self.analysis_progress.setVisible(False)
            self.suggest_move_btn.setEnabled(True)
            self.make_bot_move_btn.setEnabled(True)
    
    def on_analysis_complete(self, analysis):
        """Handle completed analysis."""
        self.last_analysis = analysis
        
        # Hide progress bar and re-enable buttons
        self.analysis_progress.setVisible(False)
        self.suggest_move_btn.setEnabled(True)
        self.make_bot_move_btn.setEnabled(True)
        
        if analysis['suggested_move']:
            suggested = analysis['suggested_move']
            best = analysis['best_move']
            eval_text = analysis.get('eval_text', 'No evaluation')
            source = analysis.get('source', 'engine')
            
            self.evaluation_text.append(f"\n📊 Evaluation: {eval_text}")
            self.evaluation_text.append(f"🎯 Suggested move: {suggested}")
            
            if source == 'opening_book':
                self.evaluation_text.append("📚 Move from opening book")
            elif suggested != best:
                self.evaluation_text.append(f"🏆 Best move: {best}")
                self.evaluation_text.append("💡 Playing sub-optimal move for training")
            else:
                self.evaluation_text.append("✨ Suggested move is the best move!")
            
            # Highlight suggested move squares
            from_square = chess.square_name(suggested.from_square)
            to_square = chess.square_name(suggested.to_square)
            self.chess_board.highlight_squares([from_square, to_square], "suggested")
            
            # Update analysis widget
            self.analysis_widget.update_analysis(analysis)
            
        else:
            self.evaluation_text.append(f"\n✗ {analysis.get('message', 'Analysis failed')}")
    
    def on_analysis_error(self, error_msg):
        """Handle analysis error."""
        self.analysis_progress.setVisible(False)
        self.suggest_move_btn.setEnabled(True)
        self.make_bot_move_btn.setEnabled(True)
        self.evaluation_text.append(f"\n✗ Analysis error: {error_msg}")
    
    def make_bot_move(self):
        """Make the bot's suggested move automatically."""
        if not self.last_analysis or not self.last_analysis.get('suggested_move'):
            self.evaluation_text.append("\n⚠️ No move suggestion available. Click 'Suggest Move' first.")
            return
        
        try:
            move = self.last_analysis['suggested_move']
            
            if move in self.current_board.legal_moves:
                # Highlight last move
                if self.highlight_last_move_cb.isChecked():
                    from_square = chess.square_name(move.from_square)
                    to_square = chess.square_name(move.to_square)
                    self.chess_board.highlight_squares([from_square, to_square], "last_move")
                
                self.current_board.push(move)
                self.update_board_display()
                self.update_game_info()
                self.evaluation_text.append(f"\n🤖 Bot played: {move}")
                
                # Update statistics if we have move analysis
                move_analyses = self.last_analysis.get('move_analyses', [])
                if move_analyses:
                    # Find the analysis for the played move
                    for analysis in move_analyses:
                        if analysis.move == move:
                            self.stats_widget.update_move_stats(analysis)
                            break
                
                # Clear highlights and analysis
                self.chess_board.clear_highlights("suggested")
                self.last_analysis = None
                
                if self.current_board.is_game_over():
                    self.handle_game_over()
                    self.stats_widget.game_completed()
            else:
                self.evaluation_text.append(f"\n✗ Suggested move is no longer legal: {move}")
                
        except Exception as e:
            error_msg = f"Move execution error: {str(e)}"
            self.evaluation_text.append(f"\n✗ {error_msg}")
    
    def get_training_hints(self):
        """Get training hints for the current position."""
        if not self.engine:
            self.evaluation_text.append("\n✗ Engine not available")
            return
        
        try:
            hints = self.engine.get_training_hints(self.current_board)
            
            if hints:
                self.evaluation_text.append("\n💡 Training Hints:")
                for hint in hints:
                    self.evaluation_text.append(f"  • {hint}")
            else:
                self.evaluation_text.append("\n💡 No specific hints for this position")
                
        except Exception as e:
            self.evaluation_text.append(f"\n✗ Hints error: {str(e)}")
    
    def analyze_last_move(self):
        """Analyze the last move played for training feedback."""
        if len(self.current_board.move_stack) == 0:
            return
        
        # This would analyze the last move for accuracy
        # Implementation would involve comparing with engine analysis
        pass
    
    def new_game(self):
        """Start a new game."""
        self.current_board = chess.Board()
        self.selected_square = None
        self.last_analysis = None
        self.chess_board.clear_highlights()
        self.update_board_display()
        self.update_game_info()
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
        self.update_game_info()
        self.evaluation_text.append("\n🔄 Board reset to empty position")
    
    def flip_board(self):
        """Flip the board view (not implemented in this version)."""
        self.evaluation_text.append("\n🔄 Board flip feature coming soon!")
    
    def update_board_display(self):
        """Update the visual chess board."""
        self.chess_board.update_board(self.current_board)
    
    def update_game_info(self):
        """Update game information display."""
        # Update game phase
        if self.engine:
            try:
                phase = self.engine.detect_game_phase(self.current_board)
                self.game_phase_label.setText(f"Phase: {phase.value.title()}")
            except:
                self.game_phase_label.setText("Phase: Unknown")
        
        # Update move count
        self.move_count_label.setText(f"Move: {self.current_board.fullmove_number}")
        
        # Update turn
        turn = "White" if self.current_board.turn == chess.WHITE else "Black"
        self.turn_label.setText(f"Turn: {turn}")
    
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
    
    def save_settings(self):
        """Save current settings."""
        self.settings.setValue("elo", self.elo_slider.value())
        self.settings.setValue("analysis_time", self.analysis_time_spin.value())
        self.settings.setValue("hash_size", self.hash_size_spin.value())
        self.settings.setValue("threads", self.threads_spin.value())
        self.settings.setValue("show_coordinates", self.show_coordinates_cb.isChecked())
        self.settings.setValue("highlight_last_move", self.highlight_last_move_cb.isChecked())
        self.settings.setValue("auto_analysis", self.auto_analysis_cb.isChecked())
        self.settings.setValue("training_mode", self.training_mode_combo.currentText())
        
        self.evaluation_text.append("\n💾 Settings saved successfully!")
    
    def load_settings(self):
        """Load saved settings."""
        self.elo_slider.setValue(self.settings.value("elo", 1500, int))
        self.analysis_time_spin.setValue(self.settings.value("analysis_time", 3, int))
        self.hash_size_spin.setValue(self.settings.value("hash_size", 256, int))
        self.threads_spin.setValue(self.settings.value("threads", 4, int))
        self.show_coordinates_cb.setChecked(self.settings.value("show_coordinates", True, bool))
        self.highlight_last_move_cb.setChecked(self.settings.value("highlight_last_move", True, bool))
        self.auto_analysis_cb.setChecked(self.settings.value("auto_analysis", False, bool))
        
        training_mode = self.settings.value("training_mode", "Adaptive", str)
        index = self.training_mode_combo.findText(training_mode)
        if index >= 0:
            self.training_mode_combo.setCurrentIndex(index)
        
        self.on_elo_changed(self.elo_slider.value())
        self.evaluation_text.append("\n📁 Settings loaded successfully!")
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Save settings on close
        self.save_settings()
        
        # Stop any running analysis
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.terminate()
            self.analysis_worker.wait()
        
        # Close engine
        if self.engine:
            self.engine.quit()
        
        event.accept()

def main():
    """Main application entry point for advanced version."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Advanced Chess Training Bot")
    app.setApplicationVersion("2.0")
    
    # Create and show main window
    window = AdvancedChessTrainingBotGUI()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
