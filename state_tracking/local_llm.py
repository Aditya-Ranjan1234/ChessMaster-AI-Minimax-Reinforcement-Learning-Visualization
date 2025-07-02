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
        
        # Get move history for context
        move_history = []
        for i, move in enumerate(board.move_stack):
            move_history.append(f"{i+1}. {move.uci()}")
        move_history_str = ", ".join(move_history) if move_history else "No moves played yet"
        
        if opening_move and len(board.move_stack) == 0:
            prompt = f"""Given the current chess position in FEN format: {fen_string},\n\n- Move history: {move_history_str}\n- Legal moves: {', '.join(legal_moves)}\n- Opening principle: Play {opening_move} as a strong opening move.\n- Evaluate the position for both sides.\n- Choose ONLY from this list of legal moves.\n- Select a move that develops a new piece, controls the center (squares e4, d4, e5, d5), supports other pieces, avoids unnecessary repetition, avoids moving the same piece multiple times in the opening, and considers king safety (castling, not exposing the king).\n- Do NOT just move the same piece back and forth.\n- Respond with ONE move in UCI format (e.g., e2e4), and nothing else.\n"""
        else:
            prompt = f"""Given the current chess position in FEN format: {fen_string},\n\n- Move history: {move_history_str}\n- Legal moves: {', '.join(legal_moves)}\n- Evaluate the position for both sides.\n- Choose ONLY from this list of legal moves.\n- Select a move that develops a new piece, controls the center (squares e4, d4, e5, d5), supports other pieces, avoids unnecessary repetition, avoids moving the same piece multiple times in the opening, and considers king safety (castling, not exposing the king).\n- Do NOT just move the same piece back and forth.\n- Respond with ONE move in UCI format (e.g., e2e4), and nothing else.\n"""
        
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            sequences = self.pipe(
                prompt,
                do_sample=False,
                num_return_sequences=1,
                eos_token_id=self.tokenizer.eos_token_id,
                max_new_tokens=50,
            )
            generated_text = sequences[0]['generated_text']
            match = re.search(r'[a-h][1-8][a-h][1-8]([qnrb])?', generated_text)
            if match:
                move_uci = match.group(0)
                try:
                    parsed_move = chess.Move.from_uci(move_uci)
                    if parsed_move in board.legal_moves:
                        # print(f"Local LLM chose move: {move_uci}")
                        return {'move': move_uci, 'model': self.name}
                    else:
                        print(f"Local LLM generated illegal move: {move_uci}. Retrying...")
                except ValueError:
                    print(f"Local LLM generated invalid UCI format: {move_uci}. Retrying...")
            else:
                print(f"Local LLM failed to generate a valid move format. Output: {generated_text}. Retrying...")
            attempts += 1
        
        print(f"Local LLM failed to generate a legal move after {max_attempts} attempts. Model loses.")
        return {'move': None, 'model': self.name} 