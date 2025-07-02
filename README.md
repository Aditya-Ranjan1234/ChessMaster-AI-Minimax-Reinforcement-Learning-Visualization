# Chess AI Research Suite

A comprehensive research and development suite exploring the evolution of chess artificial intelligence—from traditional algorithms to modern deep learning and large language models (LLMs) with state tracking.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features & Structure](#features--structure)
- [Implemented Approaches](#implemented-approaches)
- [How to Use](#how-to-use)
- [Research Highlights](#research-highlights)
- [Real-World Applications](#real-world-applications)
- [Further Reading](#further-reading)

---

## Project Overview

This project investigates the progression of chess AI, from classic rule-based engines to state-of-the-art reinforcement learning and LLM-based systems. It demonstrates that with innovative architectural approaches—such as state tracking—even small language models can outperform much larger models in structured reasoning tasks like chess.

**Key Goals:**
- Compare traditional, RL, and LLM-based chess AIs.
- Analyze the impact of state tracking on LLM performance.
- Provide a modular, extensible codebase for research and experimentation.

---

## Features & Structure

```
/scripts/         # Tournament and orchestration scripts
/tests/           # Automated test scripts
/pdfs/            # Project reports and documentation in PDF
/docs/            # LaTeX sources and markdown documentation
/state_tracking/  # LLM, state tracker, and orchestration code
/Reinforcement Learning/ # RL-based chess agent code
/Minmax Visualiser/      # Classic minimax chess engine with visualizer
/play_llm_vs_human/      # Terminal-based play against LLM
```

- **Minmax Visualiser:** Classic chess engine with real-time move visualization.
- **Reinforcement Learning:** Deep RL agents for chess, including training and evaluation scripts.
- **LLM with State Tracking:** Play chess against a local LLM (e.g., TinyLlama) with robust state tracking and logging.
- **Terminal Play:** Play against the LLM in the terminal, with full move legality and state tracking.
- **Testing:** Automated tests for logging, setup, and terminal play.
- **PDFs & Docs:** Full research report, technical documentation, and configuration guides.

---

## Implemented Approaches

### 1. Minimax-Based Chess AI
- Implements the minimax algorithm with alpha-beta pruning.
- Real-time move visualization and profiling.
- Local multiplayer and AI opponent modes.

### 2. Reinforcement Learning Chess AI
- Deep RL agents trained via self-play.
- PPO and custom architectures.
- Training logs, performance metrics, and analysis tools.

### 3. LLM with State Tracking
- Integrates LLMs (e.g., TinyLlama) for move generation.
- External state tracking ensures legality and context.
- Tournament orchestration and hallucination analysis.

---

## How to Use

### Play Chess Against the LLM (Terminal)
```bash
cd play_llm_vs_human
python play_llm_vs_human.py
```
- Enter moves in algebraic notation (e.g., `e4`, `Nf3`, `Qxd5`).
- The LLM will respond, and the game is logged.

### Run Tournaments or RL Training
```bash
cd scripts
python run_chess_tournament.py
```
- See `/Reinforcement Learning/` for RL agent training and evaluation.

### Run Tests
```bash
cd tests
python test_logging_configuration.py
```

---

## Research Highlights

- **State Tracking:** Enables small LLMs to outperform much larger models in chess by maintaining consistent game state and reducing hallucinations.
- **Hybrid Approaches:** Combining LLMs with external state management bridges the gap between language models and traditional engines.
- **Performance Analysis:** Detailed comparison of minimax, RL, and LLM-based systems, including strengths, weaknesses, and computational complexity.

---

## Real-World Applications

- **Online Chess Platforms:** Move validation, undo/redo, and game analysis.
- **AI Research:** Training and benchmarking new models and hybrid systems.
- **Education:** Visual and interactive tools for learning chess and AI.
- **Game Broadcasting:** Live state tracking and move prediction.

---

## Further Reading

- See `/pdfs/` for the full project report and documentation.
- See `/docs/` for LaTeX sources and additional technical notes.

---

## Acknowledgments

This project builds on the open-source work of the chess, AI, and LLM communities. Special thanks to contributors of `python-chess`, `PyTorch`, and LLM APIs. 