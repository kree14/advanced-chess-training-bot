"""
Chess Puzzle Trainer Module

Advanced puzzle training system with tactical pattern recognition,
difficulty progression, and performance tracking.
"""

import chess
import chess.engine
import random
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class PuzzleTheme(Enum):
    """Chess puzzle themes/motifs."""
    FORK = "fork"
    PIN = "pin"
    SKEWER = "skewer"
    DISCOVERED_ATTACK = "discovered_attack"
    DOUBLE_ATTACK = "double_attack"
    DEFLECTION = "deflection"
    DECOY = "decoy"
    CLEARANCE = "clearance"
    INTERFERENCE = "interference"
    ZUGZWANG = "zugzwang"
    MATE_IN_1 = "mate_in_1"
    MATE_IN_2 = "mate_in_2"
    MATE_IN_3 = "mate_in_3"
    BACK_RANK = "back_rank"
    SMOTHERED_MATE = "smothered_mate"
    SACRIFICE = "sacrifice"

class PuzzleDifficulty(Enum):
    """Puzzle difficulty levels."""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5

@dataclass
class ChessPuzzle:
    """Chess puzzle data structure."""
    id: str
    fen: str
    moves: List[str]  # Solution moves in UCI format
    theme: PuzzleTheme
    difficulty: PuzzleDifficulty
    rating: int
    description: str
    hint: str = ""

class PuzzleTrainer:
    """Advanced chess puzzle training system."""
    
    def __init__(self, engine_path: str = "stockfish"):
        self.engine_path = engine_path
        self.engine = None
        self.puzzles = []
        self.current_puzzle = None
        self.user_stats = {
            'solved': 0,
            'attempted': 0,
            'rating': 1200,
            'theme_performance': {},
            'difficulty_performance': {}
        }
        self._initialize_engine()
        self._load_default_puzzles()
    
    def _initialize_engine(self):
        """Initialize chess engine for puzzle verification."""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        except Exception as e:
            print(f"Warning: Could not initialize engine for puzzle trainer: {e}")
    
    def _load_default_puzzles(self):
        """Load a set of default chess puzzles."""
        # Sample puzzles - in a real implementation, these would be loaded from a database
        default_puzzles = [
            ChessPuzzle(
                id="fork_001",
                fen="rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3",
                moves=["d1h5"],  # Queen to h5, forking king and knight
                theme=PuzzleTheme.FORK,
                difficulty=PuzzleDifficulty.BEGINNER,
                rating=800,
                description="White to play and win material with a fork",
                hint="Look for a move that attacks two pieces at once"
            ),
            ChessPuzzle(
                id="pin_001",
                fen="r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
                moves=["c4f7"],  # Bishop takes f7, pinning the king
                theme=PuzzleTheme.PIN,
                difficulty=PuzzleDifficulty.BEGINNER,
                rating=900,
                description="White to play and create a devastating pin",
                hint="Attack the king through another piece"
            ),
            ChessPuzzle(
                id="mate_in_2_001",
                fen="6k1/5ppp/8/8/8/8/5PPP/R3K2R w K - 0 1",
                moves=["a1a8", "g8h7", "a8h8"],  # Back rank mate in 2
                theme=PuzzleTheme.MATE_IN_2,
                difficulty=PuzzleDifficulty.INTERMEDIATE,
                rating=1400,
                description="White to play and mate in 2 moves",
                hint="The black king has no escape squares on the back rank"
            ),
            ChessPuzzle(
                id="sacrifice_001",
                fen="r2qkb1r/ppp2ppp/2n1bn2/2bpp3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 6",
                moves=["c4f7", "e8f7", "d1h5"],  # Bishop sacrifice followed by queen check
                theme=PuzzleTheme.SACRIFICE,
                difficulty=PuzzleDifficulty.ADVANCED,
                rating=1800,
                description="White sacrifices a piece for a winning attack",
                hint="Sometimes material must be given up for a greater advantage"
            ),
            ChessPuzzle(
                id="smothered_mate_001",
                fen="6rk/6pp/8/8/8/8/8/5RNK w - - 0 1",
                moves=["f1f8", "g8f8", "g1e7"],  # Classic smothered mate pattern
                theme=PuzzleTheme.SMOTHERED_MATE,
                difficulty=PuzzleDifficulty.EXPERT,
                rating=2200,
                description="White delivers a beautiful smothered mate",
                hint="The knight can deliver mate when the king is trapped by its own pieces"
            )
        ]
        
        self.puzzles = default_puzzles
        
        # Initialize theme performance tracking
        for theme in PuzzleTheme:
            self.user_stats['theme_performance'][theme.value] = {'solved': 0, 'attempted': 0}
        
        # Initialize difficulty performance tracking
        for difficulty in PuzzleDifficulty:
            self.user_stats['difficulty_performance'][difficulty.value] = {'solved': 0, 'attempted': 0}
    
    def get_puzzle_by_rating(self, target_rating: int, tolerance: int = 200) -> Optional[ChessPuzzle]:
        """Get a puzzle close to the target rating."""
        suitable_puzzles = [
            p for p in self.puzzles 
            if abs(p.rating - target_rating) <= tolerance
        ]
        
        if suitable_puzzles:
            return random.choice(suitable_puzzles)
        
        # If no suitable puzzles, return closest one
        return min(self.puzzles, key=lambda p: abs(p.rating - target_rating))
    
    def get_puzzle_by_theme(self, theme: PuzzleTheme) -> Optional[ChessPuzzle]:
        """Get a random puzzle of a specific theme."""
        theme_puzzles = [p for p in self.puzzles if p.theme == theme]
        return random.choice(theme_puzzles) if theme_puzzles else None
    
    def get_adaptive_puzzle(self) -> Optional[ChessPuzzle]:
        """Get a puzzle adapted to user's current performance."""
        user_rating = self.user_stats['rating']
        
        # Adjust difficulty based on recent performance
        if self.user_stats['attempted'] > 0:
            success_rate = self.user_stats['solved'] / self.user_stats['attempted']
            
            if success_rate > 0.8:  # Too easy, increase difficulty
                target_rating = user_rating + 100
            elif success_rate < 0.4:  # Too hard, decrease difficulty
                target_rating = user_rating - 100
            else:  # Just right
                target_rating = user_rating
        else:
            target_rating = user_rating
        
        return self.get_puzzle_by_rating(target_rating)
    
    def start_puzzle(self, puzzle: ChessPuzzle) -> chess.Board:
        """Start a new puzzle and return the board position."""
        self.current_puzzle = puzzle
        board = chess.Board(puzzle.fen)
        return board
    
    def check_move(self, board: chess.Board, move: chess.Move) -> Tuple[bool, str, bool]:
        """
        Check if a move is correct for the current puzzle.
        
        Returns:
            (is_correct, feedback_message, is_puzzle_complete)
        """
        if not self.current_puzzle:
            return False, "No active puzzle", False
        
        move_uci = move.uci()
        expected_moves = self.current_puzzle.moves
        
        # Check if this is the next expected move
        moves_played = len(board.move_stack) - len(chess.Board(self.current_puzzle.fen).move_stack)
        
        if moves_played < len(expected_moves):
            expected_move = expected_moves[moves_played]
            
            if move_uci == expected_move:
                # Correct move
                is_complete = (moves_played + 1) >= len(expected_moves)
                
                if is_complete:
                    feedback = "Excellent! Puzzle solved correctly!"
                    self._update_stats(True)
                else:
                    feedback = f"Correct! Continue with the solution..."
                
                return True, feedback, is_complete
            else:
                # Incorrect move
                feedback = f"Not quite right. Expected: {expected_move}"
                return False, feedback, False
        else:
            return False, "Puzzle already completed", True
    
    def get_hint(self) -> str:
        """Get a hint for the current puzzle."""
        if not self.current_puzzle:
            return "No active puzzle"
        
        return self.current_puzzle.hint or "Try to find the most forcing move"
    
    def skip_puzzle(self):
        """Skip the current puzzle and update stats."""
        if self.current_puzzle:
            self._update_stats(False)
            self.current_puzzle = None
    
    def _update_stats(self, solved: bool):
        """Update user statistics."""
        if not self.current_puzzle:
            return
        
        self.user_stats['attempted'] += 1
        
        if solved:
            self.user_stats['solved'] += 1
            # Increase rating for solving puzzle
            rating_gain = max(1, (self.current_puzzle.rating - self.user_stats['rating']) // 50)
            self.user_stats['rating'] += rating_gain
        else:
            # Decrease rating for failing puzzle
            rating_loss = max(1, (self.user_stats['rating'] - self.current_puzzle.rating) // 100)
            self.user_stats['rating'] = max(800, self.user_stats['rating'] - rating_loss)
        
        # Update theme performance
        theme = self.current_puzzle.theme.value
        self.user_stats['theme_performance'][theme]['attempted'] += 1
        if solved:
            self.user_stats['theme_performance'][theme]['solved'] += 1
        
        # Update difficulty performance
        difficulty = self.current_puzzle.difficulty.value
        self.user_stats['difficulty_performance'][difficulty]['attempted'] += 1
        if solved:
            self.user_stats['difficulty_performance'][difficulty]['solved'] += 1
    
    def get_performance_report(self) -> Dict:
        """Get detailed performance statistics."""
        if self.user_stats['attempted'] == 0:
            return {
                'overall_success_rate': 0.0,
                'current_rating': self.user_stats['rating'],
                'puzzles_solved': 0,
                'puzzles_attempted': 0,
                'theme_analysis': {},
                'difficulty_analysis': {}
            }
        
        overall_success_rate = self.user_stats['solved'] / self.user_stats['attempted']
        
        # Analyze theme performance
        theme_analysis = {}
        for theme, stats in self.user_stats['theme_performance'].items():
            if stats['attempted'] > 0:
                success_rate = stats['solved'] / stats['attempted']
                theme_analysis[theme] = {
                    'success_rate': success_rate,
                    'solved': stats['solved'],
                    'attempted': stats['attempted'],
                    'strength': 'Strong' if success_rate > 0.7 else 'Weak' if success_rate < 0.4 else 'Average'
                }
        
        # Analyze difficulty performance
        difficulty_analysis = {}
        for difficulty, stats in self.user_stats['difficulty_performance'].items():
            if stats['attempted'] > 0:
                success_rate = stats['solved'] / stats['attempted']
                difficulty_analysis[difficulty] = {
                    'success_rate': success_rate,
                    'solved': stats['solved'],
                    'attempted': stats['attempted']
                }
        
        return {
            'overall_success_rate': overall_success_rate,
            'current_rating': self.user_stats['rating'],
            'puzzles_solved': self.user_stats['solved'],
            'puzzles_attempted': self.user_stats['attempted'],
            'theme_analysis': theme_analysis,
            'difficulty_analysis': difficulty_analysis
        }
    
    def save_progress(self, filename: str = "puzzle_progress.json"):
        """Save user progress to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.user_stats, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving progress: {e}")
            return False
    
    def load_progress(self, filename: str = "puzzle_progress.json"):
        """Load user progress from file."""
        try:
            with open(filename, 'r') as f:
                self.user_stats = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading progress: {e}")
            return False
    
    def quit(self):
        """Clean up resources."""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
