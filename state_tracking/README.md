# Chess State Tracking Module

A novel implementation that combines symbolic state tracking with language reasoning for chess games. This module maintains an authoritative board state while allowing multiple LLMs to interact with it, enabling the detection of hallucinations and inconsistencies in model reasoning.

## Features

- **State Tracking**: Maintains an authoritative FEN string and board state
- **Local LLM Integration**: Uses TinyLlama for lightweight local inference
- **Groq Integration**: Connects with powerful Groq models for comparison
- **Hallucination Detection**: Identifies when models make illegal or inconsistent moves
- **Game Logging**: Detailed logging of moves, states, and model analyses
- **PGN Export**: Exports games in standard PGN format

## Project Structure

```
State Tracking/
├── state_tracker.py      # Core state tracking implementation
├── local_llm.py         # Local LLM interface (TinyLlama)
├── groq_interface.py    # Groq API interface
├── game_orchestrator.py # Game management and hallucination detection
├── requirements.txt     # Project dependencies
└── logs/               # Game logs and PGN files
```

## Requirements

- Python 3.10+
- Groq API key
- CUDA-capable GPU (recommended for local LLM)

## Installation

1. Clone the repository and navigate to the State Tracking directory:
```bash
cd "State Tracking"
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Groq API key:
```bash
# Create .env file
echo "GROQ_API_KEY=your_api_key_here" > .env
```

## Usage

Run a game between the local LLM and Groq model:
```bash
python game_orchestrator.py
```

The orchestrator will:
1. Initialize both models
2. Play moves alternately
3. Track the board state
4. Detect hallucinations
5. Log all moves and analyses
6. Export the game in PGN format

## Hallucination Detection

The module detects hallucinations by:
1. Maintaining an authoritative board state
2. Validating all moves against legal moves
3. Checking for consistency in model analyses
4. Logging any discrepancies

## Logging

The module creates detailed logs in the `logs` directory:
- `game_log.jsonl`: Move-by-move log with state information
- `game_*.pgn`: PGN files of completed games
- Hallucination details when detected

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 