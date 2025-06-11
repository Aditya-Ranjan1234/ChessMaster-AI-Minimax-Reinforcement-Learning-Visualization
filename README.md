# ChessMaster AI: Minimax & Reinforcement Learning Visualization

A comprehensive chess program that combines traditional minimax algorithm visualization with modern reinforcement learning techniques. This project provides an interactive way to understand and visualize chess AI decision-making processes.

## Features

### Minimax Visualizer
- Interactive chess board with real-time move validation
- Visual representation of the minimax algorithm's decision tree
- Depth-limited minimax search with alpha-beta pruning
- Material advantage tracking and display
- Move history and captured pieces visualization

### Reinforcement Learning Component
- Multi-Agent Deep Reinforcement Learning (MADRL) implementation
- Self-play training capabilities
- Performance metrics visualization
- Model checkpointing and evaluation

## Project Structure

```
ChessMaster AI/
├── Minmax Visualiser/          # Minimax algorithm implementation
│   ├── game/                   # Core game logic
│   ├── pieces/                 # Chess piece implementations
│   ├── players/                # Player implementations (Human, AI)
│   └── web/                    # Web visualization components
│
└── Reinforcement Learning/     # MADRL implementation
    ├── agents/                 # RL agent implementations
    ├── environment/            # Chess environment for RL
    └── training/              # Training scripts and utilities
```

## Requirements

- Python 3.10+
- Pygame
- Flask
- NumPy
- TensorFlow/PyTorch (for RL component)
- Requests

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chessmaster-ai.git
cd chessmaster-ai
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

## Usage

### Running the Minimax Visualizer
```bash
cd Minmax\ Visualiser
python chess.py
```

### Running the Reinforcement Learning Component
```bash
cd Reinforcement\ Learning
python train.py
```

## Features in Detail

### Minimax Visualizer
- **Interactive Board**: Click and drag pieces to make moves
- **AI Opponent**: Play against a computer opponent using minimax algorithm
- **Visualization**: See the AI's thought process through the minimax tree
- **Move Validation**: Automatic validation of legal moves
- **Game State**: Track captured pieces and material advantage

### Reinforcement Learning
- **Self-Play**: Agents learn through self-play
- **Training**: Configurable training parameters
- **Evaluation**: Performance metrics and model evaluation
- **Visualization**: Training progress visualization

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Chess piece assets from [source]
- Inspired by various chess AI implementations
- Built with Pygame and Flask 