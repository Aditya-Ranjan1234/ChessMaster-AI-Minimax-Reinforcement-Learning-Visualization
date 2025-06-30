import chess
from state_tracker import ChessStateTracker
from local_llm import LocalLLM
from groq_interface import GroqInterface
from results_analyzer import ResultsAnalyzer
import time
import os
from typing import Dict, Optional
import json
from datetime import datetime
import random
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

class TerminalLogger:
    """Captures all terminal output and saves it to files"""
    
    def __init__(self, log_dir="results"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_buffer = []
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
        
    def start_logging(self):
        """Start capturing terminal output"""
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
        
    def stop_logging(self):
        """Stop capturing and restore original stdout/stderr"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
    def get_captured_output(self):
        """Get all captured output"""
        stdout_content = self.stdout_capture.getvalue()
        stderr_content = self.stderr_capture.getvalue()
        return stdout_content, stderr_content
        
    def save_log(self, game_id: str):
        """Save captured output to log file"""
        stdout_content, stderr_content = self.get_captured_output()
        
        log_data = {
            'game_id': game_id,
            'timestamp': datetime.now().isoformat(),
            'stdout': stdout_content,
            'stderr': stderr_content,
            'total_lines': len(stdout_content.split('\n')) + len(stderr_content.split('\n'))
        }
        
        # Save as JSON for structured access
        log_filename = os.path.join(self.log_dir, f"terminal_log_{game_id}.json")
        with open(log_filename, 'w') as f:
            json.dump(log_data, f, indent=2)
            
        # Save as plain text for easy reading
        text_filename = os.path.join(self.log_dir, f"terminal_log_{game_id}.txt")
        with open(text_filename, 'w') as f:
            f.write(f"=== Terminal Log for Game {game_id} ===\n")
            f.write(f"Timestamp: {log_data['timestamp']}\n")
            f.write(f"Total Lines: {log_data['total_lines']}\n")
            f.write("\n" + "="*50 + "\n")
            f.write("STDOUT:\n")
            f.write("="*50 + "\n")
            f.write(stdout_content)
            f.write("\n" + "="*50 + "\n")
            f.write("STDERR:\n")
            f.write("="*50 + "\n")
            f.write(stderr_content)
            
        # Clear buffers for next game
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
        
        return log_filename, text_filename

class GameOrchestrator:
    def __init__(self, white_player: 'BaseLLM', black_player: 'BaseLLM', max_moves: int = 100, stop_on_hallucination: bool = True):
        self.state_tracker = ChessStateTracker()
        self.white_player = white_player
        self.black_player = black_player
        self.results_analyzer = ResultsAnalyzer()
        self.max_moves = max_moves
        self.stop_on_hallucination = stop_on_hallucination
        self.current_matchup_index = 0
        self.current_game_index = 0
        self.matchups = []
        self.save_dir = "game_progress"
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Initialize terminal logger
        self.terminal_logger = TerminalLogger()
        
    def save_progress(self):
        """Save current progress to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_data = {
            'current_matchup_index': self.current_matchup_index,
            'current_game_index': self.current_game_index,
            'matchups': [
                {
                    'white': m[0].name,
                    'black': m[1].name,
                    'total_games': m[2],
                    'completed_games': self.results_analyzer.games_data.get(f"{m[0].name}_vs_{m[1].name}", {}).get('games_played', 0)
                }
                for m in self.matchups
            ],
            'results': self.results_analyzer.games_data
        }
        
        filename = os.path.join(self.save_dir, f"progress_{timestamp}.json")
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nProgress saved to {filename}")
        
    def load_progress(self, filename: str):
        """Load progress from a file"""
        with open(filename, 'r') as f:
            save_data = json.load(f)
            
        self.current_matchup_index = save_data['current_matchup_index']
        self.current_game_index = save_data['current_game_index']
        
        loaded_results = save_data['results']
        # Convert old list format to new dict format if necessary
        if isinstance(loaded_results, list):
            new_results_dict = {}
            for game_data in loaded_results:
                white_player_name = game_data.get('white_player', 'Unknown_White')
                black_player_name = game_data.get('black_player', 'Unknown_Black')
                matchup_key = f"{white_player_name}_vs_{black_player_name}"
                if matchup_key not in new_results_dict:
                    new_results_dict[matchup_key] = {'games_played': 0, 'games': []}
                new_results_dict[matchup_key]['games_played'] += 1
                new_results_dict[matchup_key]['games'].append(game_data)
            self.results_analyzer.games_data = new_results_dict
        else:
            self.results_analyzer.games_data = loaded_results
        
        print(f"\nLoaded progress from {filename}")
        print(f"Resuming from matchup {self.current_matchup_index + 1}, game {self.current_game_index + 1}")
        
    def set_matchups(self, matchups: list):
        """Set the matchups to play"""
        self.matchups = matchups
        
    def play_multiple_games(self, num_games: int = None) -> Dict:
        """Play multiple games and aggregate results"""
        if not self.matchups:
            raise ValueError("No matchups set. Call set_matchups() first.")
            
        results = []
        try:
            while self.current_matchup_index < len(self.matchups):
                white_player, black_player, total_games = self.matchups[self.current_matchup_index]
                
                # Skip completed matchups
                matchup_key = f"{white_player.name}_vs_{black_player.name}"
                completed_games = self.results_analyzer.games_data.get(matchup_key, {}).get('games_played', 0)
                
                if completed_games >= total_games:
                    print(f"\nMatchup {self.current_matchup_index + 1} already completed ({completed_games}/{total_games} games)")
                    self.current_matchup_index += 1
                    self.current_game_index = 0
                    continue
                
                # Calculate remaining games for this matchup
                remaining_games = total_games - completed_games
                games_to_play = min(remaining_games, num_games) if num_games else remaining_games
                
                print(f"\n--- Starting Matchup {self.current_matchup_index + 1}: {white_player.name} (White) vs. {black_player.name} (Black) ---")
                print(f"Playing {games_to_play} games (already completed {completed_games}/{total_games})")
                
                for i in range(games_to_play):
                    print(f"\n--- Playing game {completed_games + i + 1}/{total_games} for {white_player.name} (White) vs {black_player.name} (Black) ---")
                    
                    # Start terminal logging for this game
                    self.terminal_logger.start_logging()
                    
                    game_result = self.play_game()
                    results.append(game_result)
                    
                    # Stop logging and save terminal output
                    self.terminal_logger.stop_logging()
                    game_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                    log_json, log_txt = self.terminal_logger.save_log(game_id)
                    
                    # Add terminal log info to game result
                    game_result['terminal_logs'] = {
                        'json_file': log_json,
                        'text_file': log_txt
                    }
                    
                    # Save progress after each game
                    self.save_progress()
                    
                    # Reset state for next game
                    self.state_tracker.reset()
                
                # Only increment matchup index if this matchup is now completed
                updated_completed_games = self.results_analyzer.games_data.get(matchup_key, {}).get('games_played', 0)
                if updated_completed_games >= total_games:
                    self.current_matchup_index += 1
                    self.current_game_index = 0
                
        except KeyboardInterrupt:
            print("\nGame interrupted by user. Progress has been saved.")
            self.save_progress()
            return {
                'games_played': len(results),
                'results': results,
                'summary': self.results_analyzer.games_data
            }
            
        return {
            'games_played': len(results),
            'results': results,
            'summary': self.results_analyzer.games_data
        }

    def play_game(self) -> Dict:
        """Play a complete game between the two models"""
        game = chess.pgn.Game()
        game.headers["Event"] = "LLM Chess Match"
        game.headers["White"] = self.white_player.name
        game.headers["Black"] = self.black_player.name
        
        node = game
        move_count = 0
        game_ended = False
        
        # Add opening variety by suggesting a random opening move
        opening_moves = [
            "e2e4",  # King's Pawn
            "d2d4",  # Queen's Pawn
            "c2c4",  # English Opening
            "g1f3",  # Reti Opening
            "b1c3",  # Dunst Opening
            "e2e3",  # Van't Kruijs Opening
            "a2a3",  # Anderssen's Opening
            "h2h3",  # Clemenz Opening
            "g2g3",  # Benko Opening
            "b2b3"   # Larsen's Opening
        ]
        suggested_opening = random.choice(opening_moves)
        
        while not game_ended and move_count < self.max_moves:
            # Get current position
            current_fen = self.state_tracker.current_fen
            # Use the state tracker's board for validation
            current_board = self.state_tracker.board
            
            # Determine whose turn it is
            is_white_turn = current_board.turn == chess.WHITE
            current_model = self.white_player if is_white_turn else self.black_player
            
            # Get move from current model
            move_data = current_model.get_move(current_fen, suggested_opening if move_count == 0 else None)
            if move_data['move'] is None:
                print(f"Game ended because {current_model.name} failed to generate a move.")
                game_ended = True
                result = "0-1" if is_white_turn else "1-0" # Current player loses
                break
            
            try:
                move = chess.Move.from_uci(move_data['move'])
            except ValueError:
                print(f"Game ended because {current_model.name} generated an invalid move format: {move_data['move']}")
                game_ended = True
                result = "0-1" if is_white_turn else "1-0"
                self.results_analyzer.add_hallucination({
                    'move': move_data['move'],
                    'model': current_model.name,
                    'move_number': len(current_board.move_stack) + 1,
                    'fen': current_fen,
                    'timestamp': time.time()
                })
                break
            
            # Validate move
            if not self._validate_move(current_board, move, move_data['model']):
                game_ended = True
                result = "0-1" if is_white_turn else "1-0"  # Current player loses
                break
                
            # Make the move via state tracker (this updates the actual board state)
            move_successful, move_message = self.state_tracker.make_move(move.uci())

            if not move_successful:
                # This case should ideally be caught by _validate_move,
                # but as a fallback for robustness.
                print(f"Game ended because {current_model.name} proposed an unplayable move: {move_message}")
                game_ended = True
                result = "0-1" if is_white_turn else "1-0"  # Current player loses
                # Record hallucination if not already recorded by _validate_move
                self.results_analyzer.add_hallucination({
                    'move': move.uci(),
                    'model': current_model.name,
                    'move_number': len(current_board.move_stack) + 1,
                    'fen': current_fen,
                    'timestamp': time.time()
                })
                break
            
            # Record move in game (for PGN generation)
            node = node.add_variation(move)
            
            # Add move to results analyzer
            self.results_analyzer.add_move({
                'move': move.uci(),
                'model': current_model.name,
                'fen': current_fen,
                'timestamp': time.time()
            })
            
            # Add evaluations (if available from the LLM, otherwise 0)
            self.results_analyzer.add_evaluation(
                move_data.get('evaluation', 0),
                move_data.get('opponent_evaluation', 0)
            )
            
            # Check for game end conditions (using the tracker's board)
            if self.state_tracker.board.is_game_over():
                game_ended = True
                result = self._get_game_result(self.state_tracker.board)
                print(f"\nGame ended: {result}")
                
            move_count += 1
            
        # End the game in results analyzer
        game_result = {
            'result': result if game_ended else "1/2-1/2",  # Draw if max moves reached
            'moves_played': move_count,
            'hallucination_detected': bool(self.results_analyzer.current_game['hallucinations']),
            'white_player': self.white_player.name,  # Add white player name
            'black_player': self.black_player.name   # Add black player name
        }
        self.results_analyzer.end_game(game_result)
        
        return {
            'result': game_result['result'],
            'moves_played': move_count,
            'hallucination_detected': game_result['hallucination_detected'],
            'pgn': str(game),
            'terminal_logs': game_result.get('terminal_logs', {})  # Include terminal log info
        }

    def _get_game_result(self, board: chess.Board) -> str:
        """Determine the game result based on the board state"""
        if board.is_checkmate():
            return "1-0" if board.turn == chess.BLACK else "0-1" # Current turn just got checkmated
        elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
            return "1/2-1/2"
        else:
            return "*" # Game still ongoing, or other unknown result

    def _validate_move(self, board: chess.Board, move: chess.Move, model_name: str) -> bool:
        """Validate if the proposed move is legal on the current board."""
        if move not in board.legal_moves:
            print(f"Hallucination: {model_name} attempted an illegal move: {move.uci()}")
            self.results_analyzer.add_hallucination({
                'move': move.uci(),
                'model': model_name,
                'move_number': len(board.move_stack) + 1,
                'fen': board.fen(),
                'timestamp': time.time()
            })
            return False
        return True

if __name__ == "__main__":
    # Instantiate your LLMs
    local_llm = LocalLLM(name="TinyLlama-1.1B")
    
    # Groq-backed models
    groq_mixtral = GroqInterface(model_name="llama-3.3-70b-versatile", name="Groq Llama-3.3-70B-Versatile")
    groq_llama_3_1_8b_instant = GroqInterface(model_name="llama-3.1-8b-instant", name="Groq Llama-3.1-8B-Instant")
    groq_gemma_7b_it = GroqInterface(model_name="gemma2-9b-it", name="Groq Gemma2-9B-IT")
    
    # Define your matchups as a list of (white_player, black_player, num_games) tuples
    matchups = [
        (local_llm, groq_mixtral, 10),
        (local_llm, groq_llama_3_1_8b_instant, 10),
        (local_llm, groq_gemma_7b_it, 10),
        (groq_mixtral, local_llm, 10),
        (groq_llama_3_1_8b_instant, local_llm, 10),
        (groq_gemma_7b_it, local_llm, 10)
    ]
    
    # Create orchestrator and set matchups
    orchestrator = GameOrchestrator(local_llm, groq_mixtral)
    orchestrator.set_matchups(matchups)
    
    # Check if there's a saved progress file
    save_dir = "game_progress"
    if os.path.exists(save_dir):
        progress_files = sorted([f for f in os.listdir(save_dir) if f.startswith("progress_")])
        if progress_files:
            latest_progress = os.path.join(save_dir, progress_files[-1])
            print(f"Found saved progress: {latest_progress}")
            load = input("Load saved progress? (y/n): ").lower() == 'y'
            if load:
                orchestrator.load_progress(latest_progress)
    
    # Play games
    orchestrator.play_multiple_games() 