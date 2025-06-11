from groq import Groq
import chess
import os
import re
from dotenv import load_dotenv
from state_tracking.base_llm import BaseLLM
from typing import Dict

class GroqInterface(BaseLLM):
    def __init__(self, model_name: str = "mixtral-8x7b-32768", name: str = "Groq LLM"):
        super().__init__(name)
        load_dotenv()
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        self.model_name = model_name

    def get_move(self, fen_string: str) -> dict:
        board = chess.Board(fen_string)
        legal_moves = [move.uci() for move in board.legal_moves]
        prompt = f"""Given the current chess position in FEN format: {fen_string},
        and the legal moves are: {", ".join(legal_moves)}. What is your next move? Please respond with only the UCI move (e.g., e2e4)."""

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
                    max_tokens=200, # Increased max_tokens to allow for more verbose responses if needed
                )

                response_content = chat_completion.choices[0].message.content
                
                # Extract the move using regex, looking for a UCI pattern
                match = re.search(r'[a-h][1-8][a-h][1-8]([qnrb])?', response_content)
                
                if match:
                    move_uci = match.group(0)
                    if chess.Move.from_uci(move_uci) in board.legal_moves:
                        print(f"Groq LLM chose move: {move_uci}")
                        return {'move': move_uci, 'model': self.name}
                    else:
                        print(f"Groq LLM generated illegal move: {move_uci}. Retrying...")
                else:
                    print(f"Groq LLM failed to generate a valid move format. Output: {response_content}. Retrying...")
            except Exception as e:
                print(f"Error communicating with Groq API: {e}. Retrying...")
            attempts += 1

        print("Groq LLM failed to generate a legal move after multiple attempts. Choosing a random legal move.")
        # Fallback: choose a random legal move if LLM consistently fails
        if legal_moves:
            random_move = legal_moves[0] # Just pick the first for now
            print(f"Choosing random legal move as fallback: {random_move}")
            return {'move': random_move, 'model': self.name}
        else:
            return {'move': None, 'model': self.name} # Should not happen in a valid game 