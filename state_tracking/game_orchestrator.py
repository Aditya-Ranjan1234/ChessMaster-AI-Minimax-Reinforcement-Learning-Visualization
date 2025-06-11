import chess
from state_tracking.state_tracker import ChessStateTracker
from state_tracking.local_llm import LocalLLM
from state_tracking.groq_interface import GroqInterface
from state_tracking.results_analyzer import ResultsAnalyzer
import time
import os
from typing import Dict, Optional
import json

class GameOrchestrator:
    def __init__(self, white_player: 'BaseLLM', black_player: 'BaseLLM', max_moves: int = 100, stop_on_hallucination: bool = True):
        self.state_tracker = ChessStateTracker()
        self.white_player = white_player
        self.black_player = black_player
        self.results_analyzer = ResultsAnalyzer()
        self.max_moves = max_moves
        self.stop_on_hallucination = stop_on_hallucination
        
    def play_game(self) -> Dict:
        """Play a complete game between the two models"""
        game = chess.pgn.Game()
        game.headers["Event"] = "LLM Chess Match"
        game.headers["White"] = self.white_player.name
        game.headers["Black"] = self.black_player.name
        
        node = game
        move_count = 0
        game_ended = False
        
        while not game_ended and move_count < self.max_moves:
            # Get current position
            current_fen = self.state_tracker.current_fen
            # A temporary board for validation, as the main board is in state_tracker
            current_board = chess.Board(current_fen) 
            
            # Determine whose turn it is
            is_white_turn = current_board.turn == chess.WHITE
            current_model = self.white_player if is_white_turn else self.black_player
            
            # Get move from current model
            move_data = current_model.get_move(current_fen)
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
                if self.stop_on_hallucination:
                    break
                else:
                    print(f"Invalid move format by {current_model.name}, but game continues with random move.")
                    # Fallback to a random legal move if format is invalid
                    move = next(iter(current_board.legal_moves)) 
                    move_data['move'] = move.uci()


            # Validate move
            if not self._validate_move(current_board, move, move_data['model']):
                game_ended = True
                result = "0-1" if is_white_turn else "1-0"  # Current player loses
                # The _validate_move method already records hallucination.
                if self.stop_on_hallucination:
                    print(f"Game stopped due to hallucination by {move_data['model']}")
                    break
                else:
                    print(f"Hallucination detected by {move_data['model']}, but game continues.")
                
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
                if self.stop_on_hallucination:
                    print(f"Game stopped due to unplayable move by {current_model.name}")
                    break
                else:
                    print(f"Unplayable move detected by {current_model.name}, but game continues.")
            
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
                
            move_count += 1
            
        # End the game in results analyzer
        game_result = {
            'result': result if game_ended else "1/2-1/2",  # Draw if max moves reached
            'moves_played': move_count,
            'hallucination_detected': bool(self.results_analyzer.current_game['hallucinations']) # Check if any hallucinations were recorded for this game
        }
        self.results_analyzer.end_game(game_result)
        
        return {
            'result': game_result['result'],
            'moves_played': move_count,
            'hallucination_detected': game_result['hallucination_detected'],
            'pgn': str(game)
        }
        
    def _validate_move(self, board: chess.Board, move: chess.Move, model: str) -> bool:
        """Validate a move and detect hallucinations"""
        if move not in board.legal_moves:
            # Record hallucination
            self.results_analyzer.add_hallucination({
                'move': move.uci(),
                'model': model,
                'move_number': len(board.move_stack) + 1,
                'fen': board.fen(),
                'timestamp': time.time()
            })
            return False
        return True
        
    def _get_game_result(self, board: chess.Board) -> str:
        """Get the game result in standard notation"""
        if board.is_checkmate():
            return "1-0" if board.turn == chess.BLACK else "0-1"
        elif board.is_stalemate():
            return "1/2-1/2"
        elif board.is_insufficient_material():
            return "1/2-1/2"
        elif board.is_fifty_moves():
            return "1/2-1/2"
        elif board.is_repetition():
            return "1/2-1/2"
        return "1/2-1/2"  # Default to draw
        
    def play_multiple_games(self, num_games: int) -> Dict:
        """Play multiple games and aggregate results"""
        results = []
        for i in range(num_games):
            print(f"\n--- Playing game {i+1}/{num_games} for {self.white_player.name} (White) vs {self.black_player.name} (Black) ---")
            game_result = self.play_game()
            results.append(game_result)
            
            # Reset state for next game
            self.state_tracker.reset() # Reset the board in the ChessStateTracker for a fresh game
            
        return {
            'games_played': num_games,
            'results': results,
            'summary': self.results_analyzer.games_data # This will contain all games played by this orchestrator instance
        }

if __name__ == "__main__":
    # Instantiate your LLMs
    local_llm = LocalLLM(name="TinyLlama-1.1B")
    
    # Groq-backed models
    groq_mixtral = GroqInterface(model_name="llama-3.3-70b-versatile", name="Groq Llama-3.3-70B-Versatile")
    # Assuming Groq API offers these models, use their specific identifiers if different
    groq_llama_3_1_8b_instant = GroqInterface(model_name="llama-3.1-8b-instant", name="Groq Llama-3.1-8B-Instant")
    groq_gemma_7b_it = GroqInterface(model_name="gemma2-9b-it", name="Groq Gemma2-9B-IT")
    
    # Define your matchups as a list of (white_player, black_player, num_games) tuples
    matchups = [
        (local_llm, groq_mixtral, 10), # TinyLlama (White) vs. Groq Llama-3.3-70B-Versatile (Black)
        (groq_mixtral, local_llm, 10), # Groq Llama-3.3-70B-Versatile (White) vs. TinyLlama (Black)
        
        (local_llm, groq_llama_3_1_8b_instant, 10), # TinyLlama (White) vs. Groq Llama-3.1-8B-Instant (Black)
        (groq_llama_3_1_8b_instant, local_llm, 10), # Groq Llama-3.1-8B-Instant (White) vs. TinyLlama (Black)
        
        (local_llm, groq_gemma_7b_it, 10), # TinyLlama (White) vs. Groq Gemma2-9B-IT (Black)
        (groq_gemma_7b_it, local_llm, 10), # Groq Gemma2-9B-IT (White) vs. TinyLlama (Black)
    ]
    
    all_results_summary = []
    
    for i, (white_player, black_player, num_games) in enumerate(matchups):
        print(f"\n--- Starting Matchup {i+1}: {white_player.name} (White) vs. {black_player.name} (Black) ---")
        orchestrator = GameOrchestrator(
            white_player=white_player,
            black_player=black_player,
            max_moves=100, # Max moves per game
            stop_on_hallucination=True # Stops the game if a hallucination is detected
        )
        
        current_matchup_results = orchestrator.play_multiple_games(num_games)
        all_results_summary.append(current_matchup_results)
        print(f"--- Matchup {i+1} Finished ---")
    
    # Generate combined visualizations after all matchups are done
    print("\nGenerating combined visualizations...")
    # A new ResultsAnalyzer instance is needed to combine results from all matchups
    combined_analyzer = ResultsAnalyzer()
    for matchup_results in all_results_summary:
        for game_data in matchup_results['results']: # Note: 'results' not 'summary'
            combined_analyzer.games_data.append(game_data)
    combined_analyzer.generate_visualizations()

    print("\nAll matchups completed. Check the 'results' folder for detailed data and visualizations.")
    
    # You can further process all_results_summary if needed
    # For example, to save an overall summary of all matchups
    with open("results/overall_matchups_summary.json", "w") as f:
        json.dump(all_results_summary, f, indent=2) 