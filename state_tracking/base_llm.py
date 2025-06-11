from abc import ABC, abstractmethod
from typing import Dict

class BaseLLM(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_move(self, fen_string: str) -> Dict:
        """Abstract method to get a move from the LLM based on the current FEN string."""
        pass 