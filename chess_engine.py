"""
Advanced Chess Engine Integration Module

This module handles the integration with the Stockfish chess engine,
providing advanced move analysis, opening book integration, endgame tablebase support,
and sophisticated ELO-based move selection for comprehensive chess training.
"""

import chess
import chess.engine
import chess.polyglot
import random
import sys
import json
import time
import threading
from typing import Tuple, Optional, Dict, List, Set
from dataclasses import dataclass
from enum import Enum

# Default Stockfish path - modify this if Stockfish is not in your PATH
STOCKFISH_PATH = "stockfish"

class GamePhase(Enum):
    """Chess game phases for different training approaches."""
    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"

@dataclass
class MoveAnalysis:
    """Detailed move analysis data structure."""
    move: chess.Move
    score: chess.engine.PovScore
    depth: int
    nodes: int
    time: float
    pv: List[chess.Move]
    rank: int
    accuracy: float = 0.0
    blunder: bool = False
    mistake: bool = False
    inaccuracy: bool = False

@dataclass
class PositionEvaluation:
    """Complete position evaluation with tactical and strategic elements."""
    score: chess.engine.PovScore
    best_move: chess.Move
    game_phase: GamePhase
    tactical_motifs: List[str]
    strategic_themes: List[str]
    king_safety: Dict[str, float]
    material_balance: Dict[str, int]
    pawn_structure: Dict[str, float]

class AdvancedChessEngine:
    """
    Advanced chess engine wrapper with comprehensive analysis capabilities.
    """
    
    def __init__(self):
        """Initialize the advanced chess engine."""
        self.engine = None
        self.board = chess.Board()
        self.opening_book = None
        self.tablebase = None
        self.move_history = []
        self.position_cache = {}
        self.training_mode = "adaptive"
        self.personality_traits = {
            "aggression": 0.5,
            "positional_play": 0.5,
            "tactical_awareness": 0.5,
            "endgame_skill": 0.5,
            "opening_knowledge": 0.5
        }
        self._initialize_engine()
        self._load_opening_book()
    
    def _initialize_engine(self):
        """Initialize the Stockfish engine with advanced settings."""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            
            # Configure advanced engine options
            self.engine.configure({
                "Hash": 256,  # 256 MB hash table
                "Threads": 4,  # Use 4 threads
                "MultiPV": 5,  # Analyze top 5 moves
                "Contempt": 0,  # Neutral contempt
                "Skill Level": 20,  # Maximum skill
                "Move Overhead": 30,  # 30ms move overhead
                "Minimum Thinking Time": 20,  # Minimum 20ms thinking
                "Slow Mover": 100,  # Time management
            })
            
            print("Advanced Stockfish engine initialized successfully")
        except FileNotFoundError:
            error_msg = (
                f"Stockfish engine not found at '{STOCKFISH_PATH}'.\n"
                "Please install Stockfish and ensure it's in your PATH, "
                "or update the STOCKFISH_PATH variable in chess_engine.py"
            )
            print(f"Error: {error_msg}")
            raise FileNotFoundError(error_msg)
        except Exception as e:
            error_msg = f"Failed to initialize Stockfish engine: {str(e)}"
            print(f"Error: {error_msg}")
            raise Exception(error_msg)
    
    def _load_opening_book(self):
        """Load opening book for opening phase training."""
        try:
            # Try to load a polyglot opening book (optional)
            # You can download books from: https://www.chessprogramming.org/Opening_Book
            book_paths = [
                "books/performance.bin",
                "books/human.bin",
                "books/computer.bin",
                "performance.bin",
                "human.bin"
            ]
            
            for book_path in book_paths:
                try:
                    self.opening_book = chess.polyglot.open_reader(book_path)
                    print(f"Opening book loaded: {book_path}")
                    break
                except:
                    continue
            
            if not self.opening_book:
                print("No opening book found - using engine analysis for openings")
                
        except Exception as e:
            print(f"Opening book loading failed: {e}")
    
    def detect_game_phase(self, board: chess.Board) -> GamePhase:
        """Detect the current game phase based on material and position."""
        # Count material
        total_material = 0
        piece_count = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                piece_count += 1
                if piece.piece_type == chess.QUEEN:
                    total_material += 9
                elif piece.piece_type == chess.ROOK:
                    total_material += 5
                elif piece.piece_type == chess.BISHOP or piece.piece_type == chess.KNIGHT:
                    total_material += 3
                elif piece.piece_type == chess.PAWN:
                    total_material += 1
        
        # Opening phase detection
        if board.fullmove_number <= 12 and total_material >= 60:
            return GamePhase.OPENING
        
        # Endgame phase detection
        if total_material <= 20 or piece_count <= 12:
            return GamePhase.ENDGAME
        
        # Default to middlegame
        return GamePhase.MIDDLEGAME
    
    def analyze_tactical_motifs(self, board: chess.Board) -> List[str]:
        """Analyze position for tactical motifs and patterns."""
        motifs = []
        
        # Check for basic tactical patterns
        if board.is_check():
            motifs.append("Check")
        
        # Look for hanging pieces
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                attackers = board.attackers(not piece.color, square)
                defenders = board.attackers(piece.color, square)
                if len(attackers) > len(defenders):
                    motifs.append("Hanging Piece")
                    break
        
        # Check for pins and skewers (simplified detection)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
                # Check for potential pins/skewers along piece's attack lines
                for target_square in board.attacks(square):
                    target_piece = board.piece_at(target_square)
                    if target_piece and target_piece.color != piece.color:
                        # Simplified pin detection
                        if piece.piece_type == chess.BISHOP and abs(chess.square_file(square) - chess.square_file(target_square)) == abs(chess.square_rank(square) - chess.square_rank(target_square)):
                            motifs.append("Potential Pin/Skewer")
                            break
                        elif piece.piece_type == chess.ROOK and (chess.square_file(square) == chess.square_file(target_square) or chess.square_rank(square) == chess.square_rank(target_square)):
                            motifs.append("Potential Pin/Skewer")
                            break
        
        # Check for fork opportunities
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.KNIGHT and piece.color == board.turn:
                attacks = board.attacks(square)
                valuable_targets = 0
                for attack_square in attacks:
                    target = board.piece_at(attack_square)
                    if target and target.color != piece.color and target.piece_type in [chess.KING, chess.QUEEN, chess.ROOK]:
                        valuable_targets += 1
                if valuable_targets >= 2:
                    motifs.append("Knight Fork Opportunity")
        
        return list(set(motifs))  # Remove duplicates
    
    def evaluate_king_safety(self, board: chess.Board) -> Dict[str, float]:
        """Evaluate king safety for both sides."""
        safety = {"white": 0.0, "black": 0.0}
        
        for color in [chess.WHITE, chess.BLACK]:
            king_square = board.king(color)
            if king_square is None:
                continue
            
            color_name = "white" if color == chess.WHITE else "black"
            
            # Check if king is castled
            if color == chess.WHITE:
                if king_square in [chess.G1, chess.C1]:
                    safety[color_name] += 2.0  # Castled king is safer
            else:
                if king_square in [chess.G8, chess.C8]:
                    safety[color_name] += 2.0
            
            # Count attackers around king
            king_zone = []
            king_file = chess.square_file(king_square)
            king_rank = chess.square_rank(king_square)
            
            for file_offset in [-1, 0, 1]:
                for rank_offset in [-1, 0, 1]:
                    new_file = king_file + file_offset
                    new_rank = king_rank + rank_offset
                    if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                        king_zone.append(chess.square(new_file, new_rank))
            
            # Count enemy attackers in king zone
            enemy_attackers = 0
            for square in king_zone:
                if board.attackers(not color, square):
                    enemy_attackers += 1
            
            safety[color_name] -= enemy_attackers * 0.5
            
            # Pawn shield evaluation
            pawn_shield = 0
            if color == chess.WHITE and king_rank < 3:
                for file_offset in [-1, 0, 1]:
                    shield_file = king_file + file_offset
                    if 0 <= shield_file <= 7:
                        shield_square = chess.square(shield_file, king_rank + 1)
                        if board.piece_at(shield_square) and board.piece_at(shield_square).piece_type == chess.PAWN and board.piece_at(shield_square).color == color:
                            pawn_shield += 1
            elif color == chess.BLACK and king_rank > 4:
                for file_offset in [-1, 0, 1]:
                    shield_file = king_file + file_offset
                    if 0 <= shield_file <= 7:
                        shield_square = chess.square(shield_file, king_rank - 1)
                        if board.piece_at(shield_square) and board.piece_at(shield_square).piece_type == chess.PAWN and board.piece_at(shield_square).color == color:
                            pawn_shield += 1
            
            safety[color_name] += pawn_shield * 0.3
        
        return safety
    
    def analyze_pawn_structure(self, board: chess.Board) -> Dict[str, float]:
        """Analyze pawn structure weaknesses and strengths."""
        structure = {"white_weaknesses": 0.0, "black_weaknesses": 0.0, "white_strengths": 0.0, "black_strengths": 0.0}
        
        white_pawns = []
        black_pawns = []
        
        # Collect pawn positions
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                if piece.color == chess.WHITE:
                    white_pawns.append(square)
                else:
                    black_pawns.append(square)
        
        # Analyze for each color
        for color, pawns, weakness_key, strength_key in [
            (chess.WHITE, white_pawns, "white_weaknesses", "white_strengths"),
            (chess.BLACK, black_pawns, "black_weaknesses", "black_strengths")
        ]:
            pawn_files = [chess.square_file(p) for p in pawns]
            
            # Doubled pawns
            for file in range(8):
                file_count = pawn_files.count(file)
                if file_count > 1:
                    structure[weakness_key] += (file_count - 1) * 0.5
            
            # Isolated pawns
            for pawn in pawns:
                pawn_file = chess.square_file(pawn)
                has_neighbor = False
                for neighbor_file in [pawn_file - 1, pawn_file + 1]:
                    if 0 <= neighbor_file <= 7 and neighbor_file in pawn_files:
                        has_neighbor = True
                        break
                if not has_neighbor:
                    structure[weakness_key] += 0.5
            
            # Passed pawns
            for pawn in pawns:
                pawn_file = chess.square_file(pawn)
                pawn_rank = chess.square_rank(pawn)
                is_passed = True
                
                # Check if any enemy pawns can stop this pawn
                enemy_pawns = black_pawns if color == chess.WHITE else white_pawns
                for enemy_pawn in enemy_pawns:
                    enemy_file = chess.square_file(enemy_pawn)
                    enemy_rank = chess.square_rank(enemy_pawn)
                    
                    if abs(enemy_file - pawn_file) <= 1:
                        if color == chess.WHITE and enemy_rank > pawn_rank:
                            is_passed = False
                            break
                        elif color == chess.BLACK and enemy_rank < pawn_rank:
                            is_passed = False
                            break
                
                if is_passed:
                    structure[strength_key] += 0.8
        
        return structure
    
    def comprehensive_position_analysis(self, board: chess.Board, analysis_time: float = 1.0) -> PositionEvaluation:
        """Perform comprehensive position analysis."""
        if not self.engine:
            raise Exception("Engine not initialized")
        
        # Get engine analysis
        limit = chess.engine.Limit(time=analysis_time)
        analysis = self.engine.analyse(board, limit, multipv=1, info=chess.engine.INFO_ALL)
        
        if not analysis:
            raise Exception("Engine analysis failed")
        
        info = analysis[0]
        best_move = info['pv'][0] if 'pv' in info and info['pv'] else None
        score = info.get('score', chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
        
        # Detect game phase
        game_phase = self.detect_game_phase(board)
        
        # Analyze tactical motifs
        tactical_motifs = self.analyze_tactical_motifs(board)
        
        # Strategic themes based on position
        strategic_themes = []
        if game_phase == GamePhase.OPENING:
            strategic_themes.extend(["Development", "Center Control", "King Safety"])
        elif game_phase == GamePhase.MIDDLEGAME:
            strategic_themes.extend(["Piece Activity", "Pawn Structure", "King Attack"])
        else:  # ENDGAME
            strategic_themes.extend(["King Activity", "Pawn Promotion", "Opposition"])
        
        # Evaluate king safety
        king_safety = self.evaluate_king_safety(board)
        
        # Material balance
        material_balance = {"white": 0, "black": 0}
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
                        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}[piece.piece_type]
                if piece.color == chess.WHITE:
                    material_balance["white"] += value
                else:
                    material_balance["black"] += value
        
        # Pawn structure analysis
        pawn_structure = self.analyze_pawn_structure(board)
        
        return PositionEvaluation(
            score=score,
            best_move=best_move,
            game_phase=game_phase,
            tactical_motifs=tactical_motifs,
            strategic_themes=strategic_themes,
            king_safety=king_safety,
            material_balance=material_balance,
            pawn_structure=pawn_structure
        )
    
    def analyze_position_advanced(self, board: chess.Board, elo: int, analysis_time: float = 1.0) -> Dict:
        """Advanced position analysis with personality-based move selection."""
        if not self.engine:
            raise Exception("Engine not initialized")
        
        if board.is_game_over():
            return {
                'suggested_move': None,
                'best_move': None,
                'evaluation': None,
                'message': 'Game is over',
                'analysis': None
            }
        
        try:
            # Check opening book first
            if self.opening_book and self.detect_game_phase(board) == GamePhase.OPENING:
                try:
                    book_moves = []
                    for entry in self.opening_book.find_all(board):
                        book_moves.append((entry.move, entry.weight))
                    
                    if book_moves:
                        # Select book move based on ELO (higher ELO = better book moves)
                        if elo >= 2000:
                            # Choose high-weight moves
                            best_book_moves = sorted(book_moves, key=lambda x: x[1], reverse=True)[:3]
                            selected_move = random.choice(best_book_moves)[0]
                        else:
                            # More random book selection for lower ELO
                            selected_move = random.choice(book_moves)[0]
                        
                        return {
                            'suggested_move': selected_move,
                            'best_move': selected_move,
                            'evaluation': chess.engine.PovScore(chess.engine.Cp(15), chess.WHITE),
                            'eval_text': "Book move",
                            'message': f'Opening book move (ELO: {elo})',
                            'source': 'opening_book'
                        }
                except:
                    pass  # Fall back to engine analysis
            
            # Engine analysis with multiple PVs
            limit = chess.engine.Limit(time=analysis_time)
            multipv = min(8, len(list(board.legal_moves)))
            
            analysis = self.engine.analyse(
                board, 
                limit, 
                multipv=multipv,
                info=chess.engine.INFO_ALL
            )
            
            if not analysis:
                return {
                    'suggested_move': None,
                    'best_move': None,
                    'evaluation': None,
                    'message': 'No analysis available'
                }
            
            # Process analysis results
            move_analyses = []
            best_move = None
            best_eval = None
            
            for i, info in enumerate(analysis):
                if 'pv' in info and info['pv']:
                    move = info['pv'][0]
                    score = info.get('score', chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
                    depth = info.get('depth', 0)
                    nodes = info.get('nodes', 0)
                    analysis_time_used = info.get('time', 0.0)
                    pv = info.get('pv', [])
                    
                    if i == 0:
                        best_move = move
                        best_eval = score
                    
                    move_analysis = MoveAnalysis(
                        move=move,
                        score=score,
                        depth=depth,
                        nodes=nodes,
                        time=analysis_time_used,
                        pv=pv,
                        rank=i + 1
                    )
                    
                    move_analyses.append(move_analysis)
            
            if not move_analyses:
                legal_moves = list(board.legal_moves)
                if legal_moves:
                    random_move = random.choice(legal_moves)
                    return {
                        'suggested_move': random_move,
                        'best_move': random_move,
                        'evaluation': chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE),
                        'message': 'Fallback to random move'
                    }
            
            # Calculate move accuracies and classify mistakes
            self._classify_moves(move_analyses, best_eval)
            
            # Advanced move selection based on ELO and personality
            suggested_move = self._advanced_move_selection(move_analyses, elo, board)
            
            # Get comprehensive position evaluation
            try:
                position_eval = self.comprehensive_position_analysis(board, 0.5)
            except:
                position_eval = None
            
            # Format evaluation
            eval_text = self._format_evaluation(best_eval, board.turn)
            
            return {
                'suggested_move': suggested_move,
                'best_move': best_move,
                'evaluation': best_eval,
                'eval_text': eval_text,
                'move_analyses': move_analyses,
                'position_evaluation': position_eval,
                'message': f'Advanced analysis complete (ELO: {elo})',
                'source': 'engine_analysis'
            }
            
        except Exception as e:
            error_msg = f"Advanced analysis failed: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                'suggested_move': None,
                'best_move': None,
                'evaluation': None,
                'message': error_msg
            }
    
    def _classify_moves(self, move_analyses: List[MoveAnalysis], best_score: chess.engine.PovScore):
        """Classify moves as blunders, mistakes, or inaccuracies."""
        if not move_analyses or not best_score:
            return
        
        try:
            best_cp = best_score.white().score() if best_score.white().score() is not None else 0
            
            for analysis in move_analyses:
                if analysis.score and analysis.score.white().score() is not None:
                    move_cp = analysis.score.white().score()
                    cp_loss = best_cp - move_cp
                    
                    # Calculate accuracy (0-100%)
                    analysis.accuracy = max(0, 100 - abs(cp_loss) / 10)
                    
                    # Classify move quality
                    if cp_loss >= 300:  # 3+ pawn loss
                        analysis.blunder = True
                    elif cp_loss >= 150:  # 1.5+ pawn loss
                        analysis.mistake = True
                    elif cp_loss >= 50:   # 0.5+ pawn loss
                        analysis.inaccuracy = True
                        
        except Exception as e:
            print(f"Move classification error: {e}")
    
    def _advanced_move_selection(self, move_analyses: List[MoveAnalysis], elo: int, board: chess.Board) -> chess.Move:
        """Advanced move selection considering ELO, personality, and position type."""
        if not move_analyses:
            return None
        
        game_phase = self.detect_game_phase(board)
        
        # Adjust selection based on game phase and personality
        aggression = self.personality_traits["aggression"]
        positional = self.personality_traits["positional_play"]
        tactical = self.personality_traits["tactical_awareness"]
        
        # ELO-based strength factor
        strength_factor = max(0.0, min(1.0, (elo - 800) / (2500 - 800)))
        
        # Phase-specific adjustments
        if game_phase == GamePhase.OPENING:
            # In opening, higher ELO players make fewer mistakes
            mistake_probability = 0.1 * (1 - strength_factor)
        elif game_phase == GamePhase.MIDDLEGAME:
            # Middlegame allows for more personality expression
            mistake_probability = 0.2 * (1 - strength_factor)
        else:  # ENDGAME
            # Endgame requires precision
            mistake_probability = 0.15 * (1 - strength_factor)
        
        # Filter moves based on quality
        excellent_moves = [m for m in move_analyses if m.accuracy >= 95]
        good_moves = [m for m in move_analyses if 80 <= m.accuracy < 95]
        okay_moves = [m for m in move_analyses if 60 <= m.accuracy < 80]
        poor_moves = [m for m in move_analyses if m.accuracy < 60]
        
        # Selection logic
        random_value = random.random()
        
        if random_value > mistake_probability:
            # Play good moves
            if excellent_moves and random_value > 0.3:
                return random.choice(excellent_moves).move
            elif good_moves:
                return random.choice(good_moves).move
            elif okay_moves:
                return random.choice(okay_moves).move
        else:
            # Occasionally play weaker moves
            if okay_moves and random_value > mistake_probability / 2:
                return random.choice(okay_moves).move
            elif poor_moves:
                return random.choice(poor_moves).move
        
        # Fallback to best move
        return move_analyses[0].move
    
    def _format_evaluation(self, score: chess.engine.PovScore, turn: chess.Color) -> str:
        """Format the evaluation score for display."""
        if score is None:
            return "No evaluation"
        
        try:
            if score.is_mate():
                mate_in = score.white().mate()
                if mate_in > 0:
                    return f"Mate in {mate_in}"
                else:
                    return f"Mate in {abs(mate_in)} (for Black)"
            else:
                cp_score = score.white().score()
                if cp_score is None:
                    return "No evaluation"
                
                eval_pawns = cp_score / 100.0
                
                if abs(eval_pawns) < 0.1:
                    return "Equal (0.00)"
                elif eval_pawns > 0:
                    return f"White +{eval_pawns:.2f}"
                else:
                    return f"Black +{abs(eval_pawns):.2f}"
                    
        except Exception as e:
            return f"Evaluation error: {str(e)}"
    
    def set_personality(self, traits: Dict[str, float]):
        """Set bot personality traits (0.0 to 1.0 for each trait)."""
        for trait, value in traits.items():
            if trait in self.personality_traits:
                self.personality_traits[trait] = max(0.0, min(1.0, value))
    
    def get_training_hints(self, board: chess.Board) -> List[str]:
        """Generate training hints based on position analysis."""
        hints = []
        
        try:
            position_eval = self.comprehensive_position_analysis(board, 0.3)
            
            # Tactical hints
            if position_eval.tactical_motifs:
                hints.append(f"Tactical motifs present: {', '.join(position_eval.tactical_motifs)}")
            
            # King safety hints
            if position_eval.king_safety["white"] < -1.0:
                hints.append("White king looks unsafe - consider defensive moves")
            if position_eval.king_safety["black"] < -1.0:
                hints.append("Black king looks unsafe - look for attacking chances")
            
            # Material hints
            material_diff = position_eval.material_balance["white"] - position_eval.material_balance["black"]
            if abs(material_diff) >= 3:
                if material_diff > 0:
                    hints.append("White has material advantage - simplify to endgame")
                else:
                    hints.append("Black has material advantage - avoid trades")
            
            # Phase-specific hints
            if position_eval.game_phase == GamePhase.OPENING:
                hints.append("Opening phase: Focus on development and center control")
            elif position_eval.game_phase == GamePhase.MIDDLEGAME:
                hints.append("Middlegame: Look for tactical opportunities and improve piece positions")
            else:
                hints.append("Endgame: Activate your king and create passed pawns")
            
        except Exception as e:
            hints.append(f"Analysis error: {str(e)}")
        
        return hints
    
    def make_move(self, move: chess.Move) -> bool:
        """Make a move on the internal board."""
        try:
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                return True
            else:
                print(f"Illegal move: {move}")
                return False
        except Exception as e:
            print(f"Error making move: {str(e)}")
            return False
    
    def get_board(self) -> chess.Board:
        """Get the current board state."""
        return self.board.copy()
    
    def set_board(self, board: chess.Board):
        """Set the board to a specific position."""
        self.board = board.copy()
    
    def reset_board(self):
        """Reset the board to the starting position."""
        self.board = chess.Board()
        self.move_history = []
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get all legal moves in the current position."""
        return list(self.board.legal_moves)
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.board.is_game_over()
    
    def get_game_result(self) -> str:
        """Get the game result if the game is over."""
        if not self.board.is_game_over():
            return "Game in progress"
        
        result = self.board.result()
        if result == "1-0":
            return "White wins"
        elif result == "0-1":
            return "Black wins"
        else:
            return "Draw"
    
    def quit(self):
        """Safely close the chess engine."""
        if self.opening_book:
            try:
                self.opening_book.close()
            except:
                pass
        
        if self.engine:
            try:
                self.engine.quit()
                print("Advanced Stockfish engine closed successfully")
            except Exception as e:
                print(f"Error closing engine: {str(e)}")
            finally:
                self.engine = None

# Maintain backward compatibility
ChessEngine = AdvancedChessEngine
