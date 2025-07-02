# Play LLM vs Human (Terminal)

This module allows you to play chess against a local LLM (e.g., TinyLlama) or Groq LLM in the terminal, with full state tracking and terminal logging. No graphical UI is provided.

## Features
- Play as White or Black against the LLM.
- Enter moves in standard algebraic notation (e.g., e5, Nf3, Qg1).
- LLM responds with its move in the terminal.
- State tracking and move legality checking.
- Terminal log of the entire game (moves, results, timestamps).

## Usage
- Run the main script in this folder.
- Enter your moves when prompted.
- The LLM will respond with its move.
- The game continues until checkmate, stalemate, or resignation.
- A log file will be saved in this folder after each game.

## Requirements
- Python 3.8+
- `transformers`, `torch`, `python-chess`, and any dependencies for your LLM backend.

## Note
- No changes are made to existing code in the main project.
- This is a standalone terminal experience for LLM-vs-human chess. 