# LLM Chess Tournament System

This system allows you to run chess tournaments between different LLM models, with the ability to pause and resume at any time.

## 🚀 Quick Start

### 1. Test the Setup
```bash
python test_setup.py
```

### 2. Run the Tournament
```bash
python run_chess_tournament.py
```

### 3. Resume a Paused Tournament
```bash
python resume_tournament.py
```

## 🎮 Tournament Controls

### During Tournament:
- **Ctrl+C**: Pause and save progress immediately
- **Menu Options**:
  - `1`: Continue tournament
  - `2`: Show current progress
  - `3`: Pause and save manually
  - `4`: Exit tournament

### Progress Tracking:
- Progress is automatically saved after each game
- Progress files are stored in `game_progress/` directory
- Tournament can be resumed from exactly where it left off

## 📊 Tournament Structure

**Total Games**: 60 games across 6 matchups

### Matchups:
1. **TinyLlama-1.1B** (White) vs **Groq Llama-3.3-70B-Versatile** (Black) - 10 games
2. **TinyLlama-1.1B** (White) vs **Groq Llama-3.1-8B-Instant** (Black) - 10 games
3. **TinyLlama-1.1B** (White) vs **Groq Gemma2-9B-IT** (Black) - 10 games
4. **Groq Llama-3.3-70B-Versatile** (White) vs **TinyLlama-1.1B** (Black) - 10 games
5. **Groq Llama-3.1-8B-Instant** (White) vs **TinyLlama-1.1B** (Black) - 10 games
6. **Groq Gemma2-9B-IT** (White) vs **TinyLlama-1.1B** (Black) - 10 games

## 🔧 Features

### State Tracking:
- Accurate board state validation
- Move legality checking
- Game state persistence

### Hallucination Detection:
- Invalid move format detection
- Illegal move validation
- Automatic loss for hallucinating models

### Enhanced LLM Performance:
- Strategic prompting
- Position evaluation
- Opening book suggestions
- Repetition avoidance
- Fallback evaluation when LLMs fail

## 📁 File Structure

```
├── run_chess_tournament.py      # Main tournament runner
├── resume_tournament.py         # Quick resume script
├── test_setup.py               # Setup verification
├── problems.md                 # Problems and solutions
├── game_progress/              # Progress files
├── results/                    # Game results
└── state_tracking/             # Core tournament logic
```

## 🛠️ Requirements

- Python 3.8+
- Required packages (see `requirements.txt`)
- Groq API key (for Groq models)
- Sufficient RAM for TinyLlama model

## 📈 Results Analysis

Game results are saved in:
- `results/` - Individual game JSON files
- `game_progress/` - Tournament progress files

Each game includes:
- Complete move history
- Model evaluations
- Hallucination detection
- Game outcome analysis

## 🎯 Usage Examples

### Start Fresh Tournament:
```bash
python run_chess_tournament.py
# Choose option 1 to continue
```

### Pause Tournament:
```bash
# Press Ctrl+C during execution
# Or choose option 3 from menu
```

### Resume Tournament:
```bash
python resume_tournament.py
# Automatically loads latest progress
```

### Check Progress:
```bash
python run_chess_tournament.py
# Choose option 2 to see progress
```

## 🔍 Monitoring

The system provides real-time feedback:
- Current matchup and game progress
- Time elapsed
- Games completed vs total
- Model performance statistics

## 🚨 Troubleshooting

1. **Import Errors**: Run `python test_setup.py` first
2. **API Errors**: Check your Groq API key in `.env`
3. **Memory Issues**: Ensure sufficient RAM for TinyLlama
4. **Progress Issues**: Check `game_progress/` directory for saved files

## 📞 Support

If you encounter issues:
1. Check the `problems.md` file for known issues
2. Run the test script to verify setup
3. Check the console output for error messages 