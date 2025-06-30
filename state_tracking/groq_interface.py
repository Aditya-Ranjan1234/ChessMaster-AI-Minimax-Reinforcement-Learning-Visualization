from groq import Groq
import chess
import os
import re
from dotenv import load_dotenv
from state_tracking.base_llm import BaseLLM
from typing import Dict, Optional
import random

class GroqInterface(BaseLLM):
    def __init__(self, model_name: str = "llama-3.3-70b-versatile", name: str = "Groq LLM"):
        super().__init__(name)
        load_dotenv()
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        self.model_name = model_name

    def get_move(self, fen_string: str, opening_move: Optional[str] = None) -> dict:
        board = chess.Board(fen_string)
        legal_moves = [move.uci() for move in board.legal_moves]
        
        # Format move history as PGN
        pgn_game = chess.pgn.Game()
        node = pgn_game
        for move in board.move_stack:
            node = node.add_variation(move)
        pgn_str = str(pgn_game.mainline()) if board.move_stack else "No moves played yet"
        
        if opening_move and len(board.move_stack) == 0:
            prompt = f"""Given the current chess position in FEN format: {fen_string},\n\n- Move history (PGN): {pgn_str}\n- Legal moves: {', '.join(legal_moves)}\n- Opening principle: Play {opening_move} as a strong opening move.\n- Evaluate the position for both sides.\n- Suggest a move that develops a piece, controls the center, and avoids repetition.\n- Do NOT repeat any move from the move history above.\n- Respond ONLY with the UCI move (e.g., e2e4).\n"""
        else:
            prompt = f"""Given the current chess position in FEN format: {fen_string},\n\n- Move history (PGN): {pgn_str}\n- Legal moves: {', '.join(legal_moves)}\n- Evaluate the position for both sides.\n- Suggest a move that develops a piece, controls the center, and avoids repetition.\n- Do NOT repeat any move from the move history above.\n- Respond ONLY with the UCI move (e.g., e2e4).\n"""
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model_name,
                    temperature=0.7,
                    max_tokens=200,
                )
                response_content = chat_completion.choices[0].message.content
                match = re.search(r'[a-h][1-8][a-h][1-8]([qnrb])?', response_content)
                if match:
                    move_uci = match.group(0)
                    try:
                        parsed_move = chess.Move.from_uci(move_uci)
                        if parsed_move in board.legal_moves:
                            print(f"Groq LLM chose move: {move_uci}")
                            return {'move': move_uci, 'model': self.name}
                        else:
                            print(f"Groq LLM generated illegal move: {move_uci}. Retrying...")
                    except ValueError:
                        print(f"Groq LLM generated invalid UCI format: {move_uci}. Retrying...")
                else:
                    print(f"Groq LLM failed to generate a valid move format. Output: {response_content}. Retrying...")
            except Exception as e:
                print(f"Error communicating with Groq API: {e}. Retrying...")
            attempts += 1
        print(f"Groq LLM failed to generate a legal move after {max_attempts} attempts. Model loses.")
        return {'move': None, 'model': self.name} 