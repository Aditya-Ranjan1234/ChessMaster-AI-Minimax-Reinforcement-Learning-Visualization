# Terminal Logging Feature

## Overview

The terminal logging feature automatically captures all console output (stdout and stderr) during each chess game and saves it alongside the JSON results. This provides a complete audit trail of what happened during each game.

## How It Works

### 1. **Automatic Capture**
- Every game automatically starts terminal logging
- All `print()` statements, warnings, errors, and other console output are captured
- Logging stops when the game ends

### 2. **Dual Format Storage**
Each game generates two log files:

#### **JSON Format** (`terminal_log_YYYYMMDD_HHMMSS.json`)
```json
{
  "game_id": "20250628_143022",
  "timestamp": "2025-06-28T14:30:22.123456",
  "stdout": "All console output here...",
  "stderr": "All error/warning output here...",
  "total_lines": 45
}
```

#### **Text Format** (`terminal_log_YYYYMMDD_HHMMSS.txt`)
```
=== Terminal Log for Game 20250628_143022 ===
Timestamp: 2025-06-28T14:30:22.123456
Total Lines: 45

==================================================
STDOUT:
==================================================
[All console output here]

==================================================
STDERR:
==================================================
[All error/warning output here]
```

### 3. **Integration with Game Results**
Terminal log information is included in the game results:

```json
{
  "result": "1-0",
  "moves_played": 15,
  "hallucination_detected": false,
  "pgn": "...",
  "terminal_logs": {
    "json_file": "results/terminal_log_20250628_143022.json",
    "text_file": "results/terminal_log_20250628_143022.txt"
  }
}
```

## What Gets Logged

### **Captured Output:**
- ✅ All `print()` statements
- ✅ Model move selections
- ✅ Game state information
- ✅ Error messages
- ✅ Warning messages
- ✅ Hallucination detections
- ✅ Game end conditions
- ✅ Progress updates

### **Example Log Content:**
```
--- Playing game 1/10 for TinyLlama-1.1B (White) vs Groq Llama-3.1-8B-Instant (Black) ---
Local LLM chose move: g1h3
Groq LLM chose move: e7e5
Local LLM chose move: h3g5
Groq LLM chose move: e7e5
Hallucination: Groq Llama-3.1-8B-Instant attempted an illegal move: e7e5
Game ended: 0-1
```

## File Structure

After running games, you'll have:

```
results/
├── game_20250628_143022.json          # Game results
├── terminal_log_20250628_143022.json  # Terminal log (JSON)
├── terminal_log_20250628_143022.txt   # Terminal log (Text)
├── game_20250628_143045.json
├── terminal_log_20250628_143045.json
├── terminal_log_20250628_143045.txt
└── ...
```

## Benefits

### **For Research:**
- **Complete Audit Trail**: See exactly what each model did
- **Debugging**: Identify why models made certain moves
- **Hallucination Analysis**: Track when and why hallucinations occurred
- **Performance Analysis**: Monitor response times and errors

### **For Reproducibility:**
- **Exact Replay**: See the exact sequence of events
- **Error Tracking**: Identify system issues or model failures
- **Validation**: Verify game integrity and move legality

## Usage

### **Automatic (Default)**
Terminal logging is enabled by default. No additional setup required.

### **Manual Control**
```python
from state_tracking.game_orchestrator import TerminalLogger

# Create logger
logger = TerminalLogger(log_dir="custom_logs")

# Start logging
logger.start_logging()

# Your code here...
print("This will be captured")

# Stop logging
logger.stop_logging()

# Save log
log_json, log_txt = logger.save_log("my_game_001")
```

## Testing

Run the test script to see terminal logging in action:

```bash
python test_terminal_logging.py
```

This will:
1. Test the TerminalLogger class directly
2. Generate sample log files
3. Display the captured content

## File Naming Convention

- **Game Results**: `game_YYYYMMDD_HHMMSS.json`
- **Terminal Logs**: `terminal_log_YYYYMMDD_HHMMSS.json/.txt`

The timestamp ensures unique filenames and chronological ordering.

## Performance Impact

- **Minimal Overhead**: StringIO buffering is very fast
- **Memory Efficient**: Logs are cleared after each game
- **Disk Space**: ~1-5KB per game (depending on output volume)

## Troubleshooting

### **Log Files Not Created**
- Check that the `results/` directory exists
- Verify write permissions
- Ensure games are completing (not crashing)

### **Empty Log Files**
- Games might be ending too quickly
- Check for exceptions in game execution
- Verify that models are generating output

### **Large Log Files**
- Models might be generating excessive output
- Consider filtering or truncating logs
- Monitor for infinite loops or repeated output

## Future Enhancements

Potential improvements:
- **Log Rotation**: Automatic cleanup of old logs
- **Compression**: Gzip compression for large logs
- **Filtering**: Selective capture of specific output types
- **Real-time Streaming**: Live log viewing during games
- **Search/Indexing**: Fast search through log content 