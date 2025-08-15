"""
Chess Opening Trainer Module

Advanced opening training system with repertoire building,
move explanation, and statistical analysis.
"""

import chess
import chess.pgn
import random
import json
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

class OpeningPhase(Enum):
    """Opening learning phases."""
    MAIN_LINE = "main_line"
    VARIATIONS = "variations"
    TRANSPOSITIONS = "transpositions"
    TRAPS = "traps"

@dataclass
class OpeningMove:
    """Opening move with explanation and statistics."""
    move: str  # UCI format
    san: str   # Standard algebraic notation
    explanation: str
    frequency: float  # How often this move is played
    success_rate: float  # Win rate for this move
    is_main_line: bool
    alternatives: List[str]  # Alternative moves
    typical_plans: List[str]  # Typical plans after this move

@dataclass
class OpeningLine:
    """Complete opening line with moves and analysis."""
    name: str
    eco_code: str  # Encyclopedia of Chess Openings code
    moves: List[OpeningMove]
    description: str
    typical_pawn_structures: List[str]
    key_ideas: List[str]
    famous_games: List[str]  # Notable games featuring this opening

class OpeningTrainer:
    """Advanced chess opening training system."""
    
    def __init__(self):
        self.openings_database = {}
        self.user_repertoire = {
            'white': {},  # Openings as White
            'black': {}   # Defenses as Black
        }
        self.training_stats = {
            'positions_studied': 0,
            'moves_practiced': 0,
            'accuracy': 0.0,
            'opening_scores': defaultdict(lambda: {'correct': 0, 'total': 0})
        }
        self.current_line = None
        self.current_position = None
        self._initialize_openings()
    
    def _initialize_openings(self):
        """Initialize the openings database with popular openings."""
        
        # Italian Game
        italian_game = OpeningLine(
            name="Italian Game",
            eco_code="C50-C59",
            moves=[
                OpeningMove(
                    move="e2e4", san="e4",
                    explanation="Control the center and open lines for pieces",
                    frequency=0.85, success_rate=0.52, is_main_line=True,
                    alternatives=["d2d4", "g1f3", "c2c4"],
                    typical_plans=["Quick development", "Central control", "King safety"]
                ),
                OpeningMove(
                    move="e7e5", san="e5",
                    explanation="Mirror White's central control",
                    frequency=0.45, success_rate=0.48, is_main_line=True,
                    alternatives=["c7c5", "e7e6", "c7c6"],
                    typical_plans=["Counter-attack in center", "Piece development"]
                ),
                OpeningMove(
                    move="g1f3", san="Nf3",
                    explanation="Develop knight and attack the e5 pawn",
                    frequency=0.90, success_rate=0.54, is_main_line=True,
                    alternatives=["f2f4", "b1c3", "f1c4"],
                    typical_plans=["Attack e5", "Prepare d3", "Castle kingside"]
                ),
                OpeningMove(
                    move="b8c6", san="Nc6",
                    explanation="Defend the e5 pawn and develop",
                    frequency=0.80, success_rate=0.49, is_main_line=True,
                    alternatives=["f7f5", "d7d6", "b8d7"],
                    typical_plans=["Defend e5", "Prepare ...f5 or ...d6"]
                ),
                OpeningMove(
                    move="f1c4", san="Bc4",
                    explanation="Develop bishop to active square, eye f7",
                    frequency=0.75, success_rate=0.53, is_main_line=True,
                    alternatives=["f1b5", "d2d3", "b1c3"],
                    typical_plans=["Attack f7", "Prepare castling", "Central pressure"]
                ),
                OpeningMove(
                    move="f8e7", san="Be7",
                    explanation="Solid development, prepare castling",
                    frequency=0.35, success_rate=0.47, is_main_line=True,
                    alternatives=["f8c5", "f7f5", "g8f6"],
                    typical_plans=["Castle kingside", "Prepare ...d6", "Solid setup"]
                )
            ],
            description="Classical opening focusing on rapid development and central control",
            typical_pawn_structures=["e4-e5 center", "d3-e4 vs d6-e5"],
            key_ideas=["Rapid development", "Central control", "King safety", "Attack on f7"],
            famous_games=["Morphy vs Duke of Brunswick (1858)", "Kasparov vs Topalov (1999)"]
        )
        
        # Sicilian Defense
        sicilian_defense = OpeningLine(
            name="Sicilian Defense",
            eco_code="B20-B99",
            moves=[
                OpeningMove(
                    move="e2e4", san="e4",
                    explanation="Control the center and open lines",
                    frequency=0.85, success_rate=0.52, is_main_line=True,
                    alternatives=["d2d4", "g1f3", "c2c4"],
                    typical_plans=["Central control", "Quick development"]
                ),
                OpeningMove(
                    move="c7c5", san="c5",
                    explanation="Counter-attack on the queenside, unbalanced position",
                    frequency=0.25, success_rate=0.46, is_main_line=True,
                    alternatives=["e7e5", "e7e6", "c7c6"],
                    typical_plans=["Queenside expansion", "Counter-play", "Unbalanced positions"]
                ),
                OpeningMove(
                    move="g1f3", san="Nf3",
                    explanation="Develop knight and prepare d4",
                    frequency=0.85, success_rate=0.55, is_main_line=True,
                    alternatives=["b1c3", "f2f4", "c2c3"],
                    typical_plans=["Prepare d4", "Control center", "Develop pieces"]
                ),
                OpeningMove(
                    move="d7d6", san="d6",
                    explanation="Support the c5 pawn and prepare development",
                    frequency=0.40, success_rate=0.45, is_main_line=True,
                    alternatives=["b8c6", "g7g6", "a7a6"],
                    typical_plans=["Support c5", "Prepare ...Nf6", "Flexible development"]
                ),
                OpeningMove(
                    move="d2d4", san="d4",
                    explanation="Open the center and gain space",
                    frequency=0.90, success_rate=0.56, is_main_line=True,
                    alternatives=["f1b5", "c2c3", "b1c3"],
                    typical_plans=["Central breakthrough", "Open lines", "Initiative"]
                ),
                OpeningMove(
                    move="c5d4", san="cxd4",
                    explanation="Recapture and open the c-file",
                    frequency=0.95, success_rate=0.44, is_main_line=True,
                    alternatives=["g8f6", "b8c6"],
                    typical_plans=["Open c-file", "Piece activity", "Counter-play"]
                )
            ],
            description="Sharp, unbalanced defense leading to complex middlegames",
            typical_pawn_structures=["Sicilian pawn chains", "Open c-file", "Maroczy bind"],
            key_ideas=["Counter-attack", "Unbalanced positions", "Queenside play", "Sharp tactics"],
            famous_games=["Fischer vs Spassky (1972)", "Kasparov vs Karpov (1984)"]
        )
        
        # Queen's Gambit
        queens_gambit = OpeningLine(
            name="Queen's Gambit",
            eco_code="D06-D69",
            moves=[
                OpeningMove(
                    move="d2d4", san="d4",
                    explanation="Control center and open lines for pieces",
                    frequency=0.40, success_rate=0.54, is_main_line=True,
                    alternatives=["e2e4", "g1f3", "c2c4"],
                    typical_plans=["Central control", "Queenside development"]
                ),
                OpeningMove(
                    move="d7d5", san="d5",
                    explanation="Counter White's central control",
                    frequency=0.50, success_rate=0.46, is_main_line=True,
                    alternatives=["g8f6", "f7f5", "e7e6"],
                    typical_plans=["Central equality", "Piece development"]
                ),
                OpeningMove(
                    move="c2c4", san="c4",
                    explanation="Attack the d5 pawn and gain queenside space",
                    frequency=0.80, success_rate=0.55, is_main_line=True,
                    alternatives=["g1f3", "c1f4", "e2e3"],
                    typical_plans=["Pressure d5", "Queenside expansion", "Central control"]
                ),
                OpeningMove(
                    move="e7e6", san="e6",
                    explanation="Support d5 and prepare piece development",
                    frequency=0.45, success_rate=0.47, is_main_line=True,
                    alternatives=["d5c4", "c7c6", "g8f6"],
                    typical_plans=["Solid center", "Prepare ...Nf6", "French-like structure"]
                ),
                OpeningMove(
                    move="b1c3", san="Nc3",
                    explanation="Develop knight and add pressure to d5",
                    frequency=0.85, success_rate=0.54, is_main_line=True,
                    alternatives=["g1f3", "c4d5", "e2e3"],
                    typical_plans=["Pressure d5", "Prepare e4", "Piece development"]
                ),
                OpeningMove(
                    move="g8f6", san="Nf6",
                    explanation="Develop knight and prepare to recapture on d5",
                    frequency=0.70, success_rate=0.46, is_main_line=True,
                    alternatives=["c7c6", "b8d7", "f8e7"],
                    typical_plans=["Develop pieces", "Prepare ...c6", "Solid setup"]
                )
            ],
            description="Positional opening focusing on central control and piece development",
            typical_pawn_structures=["Isolated queen's pawn", "Hanging pawns", "Carlsbad structure"],
            key_ideas=["Central control", "Piece development", "Positional pressure", "Endgame advantages"],
            famous_games=["Capablanca vs Marshall (1909)", "Botvinnik vs Capablanca (1938)"]
        )
        
        # Store openings in database
        self.openings_database = {
            "Italian Game": italian_game,
            "Sicilian Defense": sicilian_defense,
            "Queen's Gambit": queens_gambit
        }
    
    def get_available_openings(self) -> List[str]:
        """Get list of available opening names."""
        return list(self.openings_database.keys())
    
    def start_opening_training(self, opening_name: str) -> Optional[chess.Board]:
        """Start training a specific opening."""
        if opening_name not in self.openings_database:
            return None
        
        self.current_line = self.openings_database[opening_name]
        self.current_position = chess.Board()
        return self.current_position.copy()
    
    def get_next_move_info(self) -> Optional[Dict]:
        """Get information about the next move in the current opening."""
        if not self.current_line or not self.current_position:
            return None
        
        moves_played = len(self.current_position.move_stack)
        
        if moves_played >= len(self.current_line.moves):
            return {
                'status': 'complete',
                'message': 'Opening line completed!',
                'summary': {
                    'name': self.current_line.name,
                    'eco_code': self.current_line.eco_code,
                    'key_ideas': self.current_line.key_ideas,
                    'typical_structures': self.current_line.typical_pawn_structures
                }
            }
        
        next_move = self.current_line.moves[moves_played]
        
        return {
            'status': 'active',
            'move_info': {
                'expected_move': next_move.move,
                'san': next_move.san,
                'explanation': next_move.explanation,
                'frequency': next_move.frequency,
                'success_rate': next_move.success_rate,
                'is_main_line': next_move.is_main_line,
                'alternatives': next_move.alternatives,
                'typical_plans': next_move.typical_plans
            },
            'position_info': {
                'moves_completed': moves_played,
                'total_moves': len(self.current_line.moves),
                'progress': moves_played / len(self.current_line.moves)
            }
        }
    
    def check_move(self, move: chess.Move) -> Tuple[bool, str, Dict]:
        """
        Check if the played move matches the opening line.
        
        Returns:
            (is_correct, feedback, additional_info)
        """
        if not self.current_line or not self.current_position:
            return False, "No active opening training", {}
        
        move_info = self.get_next_move_info()
        if not move_info or move_info['status'] == 'complete':
            return False, "Opening line already completed", {}
        
        expected_move_uci = move_info['move_info']['expected_move']
        played_move_uci = move.uci()
        
        # Update statistics
        self.training_stats['moves_practiced'] += 1
        opening_name = self.current_line.name
        self.training_stats['opening_scores'][opening_name]['total'] += 1
        
        if played_move_uci == expected_move_uci:
            # Correct move
            self.current_position.push(move)
            self.training_stats['opening_scores'][opening_name]['correct'] += 1
            
            # Update overall accuracy
            total_correct = sum(score['correct'] for score in self.training_stats['opening_scores'].values())
            total_moves = sum(score['total'] for score in self.training_stats['opening_scores'].values())
            self.training_stats['accuracy'] = total_correct / total_moves if total_moves > 0 else 0.0
            
            feedback = f"Correct! {move_info['move_info']['explanation']}"
            
            # Check if opening is complete
            next_info = self.get_next_move_info()
            if next_info and next_info['status'] == 'complete':
                feedback += f"\n\nOpening completed! Key ideas: {', '.join(self.current_line.key_ideas)}"
            
            return True, feedback, move_info['move_info']
        else:
            # Incorrect move
            alternatives = move_info['move_info']['alternatives']
            expected_san = move_info['move_info']['san']
            
            feedback = f"Not the main line move. Expected: {expected_san}\n"
            feedback += f"Explanation: {move_info['move_info']['explanation']}\n"
            
            if played_move_uci in alternatives:
                feedback += "Your move is a reasonable alternative, but not the main line."
                # Still make the move to continue
                self.current_position.push(move)
                return False, feedback, move_info['move_info']
            else:
                feedback += f"Alternative main moves: {', '.join(alternatives[:3])}"
                return False, feedback, move_info['move_info']
    
    def get_opening_hint(self) -> str:
        """Get a hint for the current position."""
        move_info = self.get_next_move_info()
        if not move_info or move_info['status'] == 'complete':
            return "No hint available"
        
        plans = move_info['move_info']['typical_plans']
        if plans:
            return f"Think about: {random.choice(plans)}"
        else:
            return "Look for the most natural developing move"
    
    def skip_move(self) -> bool:
        """Skip the current move and show the solution."""
        move_info = self.get_next_move_info()
        if not move_info or move_info['status'] == 'complete':
            return False
        
        expected_move_uci = move_info['move_info']['expected_move']
        move = chess.Move.from_uci(expected_move_uci)
        
        if move in self.current_position.legal_moves:
            self.current_position.push(move)
            return True
        
        return False
    
    def reset_current_opening(self):
        """Reset the current opening to the beginning."""
        if self.current_line:
            self.current_position = chess.Board()
    
    def get_opening_statistics(self) -> Dict:
        """Get detailed statistics about opening training."""
        stats = {
            'overall': {
                'positions_studied': self.training_stats['positions_studied'],
                'moves_practiced': self.training_stats['moves_practiced'],
                'overall_accuracy': self.training_stats['accuracy']
            },
            'by_opening': {}
        }
        
        for opening_name, scores in self.training_stats['opening_scores'].items():
            if scores['total'] > 0:
                accuracy = scores['correct'] / scores['total']
                stats['by_opening'][opening_name] = {
                    'accuracy': accuracy,
                    'correct_moves': scores['correct'],
                    'total_moves': scores['total'],
                    'mastery_level': self._get_mastery_level(accuracy, scores['total'])
                }
        
        return stats
    
    def _get_mastery_level(self, accuracy: float, total_moves: int) -> str:
        """Determine mastery level based on accuracy and practice."""
        if total_moves < 5:
            return "Beginner"
        elif accuracy >= 0.9 and total_moves >= 20:
            return "Master"
        elif accuracy >= 0.8 and total_moves >= 15:
            return "Advanced"
        elif accuracy >= 0.7 and total_moves >= 10:
            return "Intermediate"
        else:
            return "Learning"
    
    def add_to_repertoire(self, opening_name: str, color: str):
        """Add an opening to the user's repertoire."""
        if opening_name in self.openings_database and color in ['white', 'black']:
            self.user_repertoire[color][opening_name] = {
                'added_date': None,  # Would use datetime in real implementation
                'practice_count': 0,
                'mastery_level': 'Learning'
            }
    
    def get_repertoire_openings(self, color: str) -> List[str]:
        """Get openings in the user's repertoire for a specific color."""
        if color in self.user_repertoire:
            return list(self.user_repertoire[color].keys())
        return []
    
    def practice_random_position(self, opening_name: str) -> Optional[Tuple[chess.Board, Dict]]:
        """Get a random position from an opening for practice."""
        if opening_name not in self.openings_database:
            return None
        
        opening = self.openings_database[opening_name]
        
        # Choose a random position in the opening (not the starting position)
        max_moves = min(len(opening.moves), 8)  # Don't go too deep
        num_moves = random.randint(2, max_moves)
        
        board = chess.Board()
        for i in range(num_moves):
            move = chess.Move.from_uci(opening.moves[i].move)
            if move in board.legal_moves:
                board.push(move)
            else:
                break
        
        # Information about the position
        position_info = {
            'opening_name': opening_name,
            'moves_played': num_moves,
            'key_ideas': opening.key_ideas,
            'typical_plans': opening.moves[min(num_moves, len(opening.moves)-1)].typical_plans if num_moves < len(opening.moves) else []
        }
        
        return board, position_info
    
    def save_progress(self, filename: str = "opening_progress.json"):
        """Save training progress to file."""
        try:
            data = {
                'training_stats': dict(self.training_stats),
                'user_repertoire': self.user_repertoire
            }
            # Convert defaultdict to regular dict for JSON serialization
            data['training_stats']['opening_scores'] = dict(data['training_stats']['opening_scores'])
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving opening progress: {e}")
            return False
    
    def load_progress(self, filename: str = "opening_progress.json"):
        """Load training progress from file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.training_stats = data.get('training_stats', self.training_stats)
            self.user_repertoire = data.get('user_repertoire', self.user_repertoire)
            
            # Convert back to defaultdict
            opening_scores = self.training_stats.get('opening_scores', {})
            self.training_stats['opening_scores'] = defaultdict(lambda: {'correct': 0, 'total': 0})
            self.training_stats['opening_scores'].update(opening_scores)
            
            return True
        except Exception as e:
            print(f"Error loading opening progress: {e}")
            return False
