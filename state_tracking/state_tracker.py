import chess
import chess.pgn
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime

class ChessStateTracker:
    def __init__(self):
        self.board = chess.Board()
        self.move_history: List[str] = []
        self.state_history: List[Dict] = []
        self.game_start_time = datetime.now()
        self._update_state()  # Initialize the current_fen and state_history
        
    def make_move(self, move: str) -> Tuple[bool, str]:
        """
        Attempts to make a move and returns (success, message)
        """
        try:
            move_obj = chess.Move.from_uci(move)
            if move_obj in self.board.legal_moves:
                self.board.push(move_obj)
                self.move_history.append(move)
                self._update_state()
                return True, "Move successful"
            return False, "Illegal move"
        except Exception as e:
            return False, f"Invalid move format: {str(e)}"
    
    def _update_state(self):
        """Updates the current state information"""
        state = {
            'fen': self.board.fen(),
            'legal_moves': [move.uci() for move in self.board.legal_moves],
            'is_check': self.board.is_check(),
            'is_checkmate': self.board.is_checkmate(),
            'is_stalemate': self.board.is_stalemate(),
            'halfmove_clock': self.board.halfmove_clock,
            'fullmove_number': self.board.fullmove_number,
            'turn': 'white' if self.board.turn else 'black',
            'castling_rights': {
                'K': self.board.has_castling_rights(chess.WHITE) & chess.BB_H1,
                'Q': self.board.has_castling_rights(chess.WHITE) & chess.BB_A1,
                'k': self.board.has_castling_rights(chess.BLACK) & chess.BB_H8,
                'q': self.board.has_castling_rights(chess.BLACK) & chess.BB_A8
            }
        }
        self.state_history.append(state)
        self.current_fen = state['fen']
    
    def get_current_state(self) -> Dict:
        """Returns the current state of the board"""
        return self.state_history[-1] if self.state_history else self._get_initial_state()
    
    def _get_initial_state(self) -> Dict:
        """Returns the initial state of the board"""
        return {
            'fen': self.board.fen(),
            'legal_moves': [move.uci() for move in self.board.legal_moves],
            'is_check': False,
            'is_checkmate': False,
            'is_stalemate': False,
            'halfmove_clock': 0,
            'fullmove_number': 1,
            'turn': 'white',
            'castling_rights': {
                'K': True, 'Q': True, 'k': True, 'q': True
            }
        }
    
    def get_game_summary(self) -> Dict:
        """Returns a summary of the game"""
        return {
            'moves': self.move_history,
            'final_fen': self.current_fen,
            'game_length': len(self.move_history),
            'duration': (datetime.now() - self.game_start_time).total_seconds(),
            'result': self.board.outcome().result() if self.board.is_game_over() else '*'
        }
    
    def export_pgn(self, filename: str):
        """Exports the game to a PGN file"""
        game = chess.pgn.Game()
        game.headers["Event"] = "State Tracking Test Game"
        game.headers["Date"] = self.game_start_time.strftime("%Y.%m.%d")
        game.headers["Result"] = self.board.outcome().result() if self.board.is_game_over() else '*'
        
        node = game
        for move in self.move_history:
            node = node.add_variation(chess.Move.from_uci(move))
        
        with open(filename, 'w') as f:
            f.write(str(game))
    
    def reset(self):
        """Resets the board to initial state"""
        self.board = chess.Board()
        self.move_history = []
        self.state_history = []
        self.current_fen = self.board.fen()
        self.game_start_time = datetime.now()
        self._update_state() 