from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import chess
import re
import torch
import os
from dotenv import load_dotenv
from state_tracking.base_llm import BaseLLM
from typing import Dict, Optional
import random

class LocalLLM(BaseLLM):
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", name: str = "Local LLM"):
        super().__init__(name)
        load_dotenv()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )

    def get_move(self, fen_string: str, opening_move: Optional[str] = None) -> dict:
        board = chess.Board(fen_string)
        legal_moves = [move.uci() for move in board.legal_moves]
        
        if opening_move and len(board.move_stack) == 0: # Only suggest opening if it's the very first move
            prompt = f"""Given the current chess position in FEN format: {fen_string},
            and the legal moves are: {", ".join(legal_moves)}. As the first move, consider playing {opening_move}. What is your next move? Please respond with only the UCI move (e.g., e2e4)."""
        else:
            prompt = f"""Given the current chess position in FEN format: {fen_string},
            and the legal moves are: {", ".join(legal_moves)}. What is your next move? Please respond with only the UCI move (e.g., e2e4)."""
        
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            sequences = self.pipe(
                prompt,
                do_sample=True,
                top_k=10,
                num_return_sequences=1,
                eos_token_id=self.tokenizer.eos_token_id,
                max_new_tokens=50,
            )
            
            generated_text = sequences[0]['generated_text']
            # Extract the move using regex, looking for a UCI pattern
            match = re.search(r'[a-h][1-8][a-h][1-8]([qnrb])?', generated_text)
            
            if match:
                move_uci = match.group(0)
                # Validate the move against the actual board's legal moves
                try:
                    parsed_move = chess.Move.from_uci(move_uci)
                    if parsed_move in board.legal_moves:
                        print(f"Local LLM chose move: {move_uci}")
                        return {'move': move_uci, 'model': self.name}
                    else:
                        print(f"Local LLM generated illegal move: {move_uci}. Retrying...")
                except ValueError:
                    print(f"Local LLM generated invalid UCI format: {move_uci}. Retrying...")
            else:
                print(f"Local LLM failed to generate a valid move format. Output: {generated_text}. Retrying...")
            attempts += 1
        
        print("Local LLM failed to generate a legal move after multiple attempts. Choosing a random legal move.")
        # Fallback: choose a random legal move if LLM consistently fails
        if legal_moves:
            random_move = random.choice(legal_moves) # Pick a random legal move
            print(f"Choosing random legal move as fallback: {random_move}")
            return {'move': random_move, 'model': self.name}
        else:
            return {'move': None, 'model': self.name} # Should not happen in a valid game 