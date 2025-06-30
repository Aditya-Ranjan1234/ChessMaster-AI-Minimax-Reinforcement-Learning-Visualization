#!/usr/bin/env python3
"""
Test script to verify terminal logging with specific configuration:
- Small model with state tracking vs large model with move history
- Hallucination detection enabled
- 50 move rule (max_moves=50)
"""

import sys
import os
sys.path.append('state_tracking')

from game_orchestrator import GameOrchestrator, TerminalLogger
from local_llm import LocalLLM
from groq_interface import GroqInterface

def test_configuration():
    """Test the specific configuration with terminal logging"""
    
    print("=== Testing Configuration: Small Model vs Large Model ===")
    print("Configuration:")
    print("- Small model (TinyLlama-1.1B): State tracking + move history")
    print("- Large model (Groq Llama-3.1-8B): Move history only")
    print("- Hallucination detection: ENABLED")
    print("- Max moves: 50 (50-move rule)")
    print("- Terminal logging: ENABLED")
    
    # Create LLMs
    try:
        # Small model with state tracking
        small_model = LocalLLM(name="TinyLlama-1.1B")
        print(f"✓ Small model created: {small_model.name}")
        
        # Large model with move history only
        large_model = GroqInterface(model_name="llama-3.1-8b-instant", name="Groq Llama-3.1-8B-Instant")
        print(f"✓ Large model created: {large_model.name}")
        
    except Exception as e:
        print(f"✗ Error creating models: {e}")
        print("Using dummy models for testing...")
        
        # Fallback to dummy models for testing
        class DummyLLM:
            def __init__(self, name, model_type="dummy"):
                self.name = name
                self.model_type = model_type
            def get_move(self, fen, suggested_opening=None):
                # Simulate some moves and potential hallucinations
                import random
                moves = ['e2e4', 'd2d4', 'c2c4', 'g1f3']
                if random.random() < 0.3:  # 30% chance of hallucination
                    return {'move': 'e7e5', 'model': self.name}  # Invalid move
                return {'move': random.choice(moves), 'model': self.name}
        
        small_model = DummyLLM("TinyLlama-1.1B", "state_tracking")
        large_model = DummyLLM("Groq Llama-3.1-8B-Instant", "move_history")
    
    # Create orchestrator with 50-move limit and hallucination detection
    orchestrator = GameOrchestrator(
        white_player=small_model,
        black_player=large_model,
        max_moves=50,  # 50-move rule
        stop_on_hallucination=True  # Hallucination detection enabled
    )
    
    print(f"✓ Orchestrator created with max_moves={orchestrator.max_moves}")
    print(f"✓ Hallucination detection: {orchestrator.stop_on_hallucination}")
    
    # Test terminal logger directly
    print("\n1. Testing TerminalLogger functionality...")
    logger = TerminalLogger(log_dir="test_logs")
    
    logger.start_logging()
    print("This output should be captured by the terminal logger")
    print("Testing hallucination detection...")
    print("Testing 50-move rule...")
    import warnings
    warnings.warn("This warning should also be captured")
    logger.stop_logging()
    
    # Save test log
    test_log_json, test_log_txt = logger.save_log("test_config_001")
    print(f"✓ Test log saved: {test_log_txt}")
    
    # Set up matchups
    matchups = [
        (small_model, large_model, 2),  # Small vs Large, 2 games
        (large_model, small_model, 2)   # Large vs Small, 2 games
    ]
    orchestrator.set_matchups(matchups)
    
    print(f"\n2. Playing {len(matchups)} matchups with terminal logging...")
    
    try:
        # Play games with logging
        results = orchestrator.play_multiple_games(1)  # Play 1 game per matchup
        
        print(f"\n✓ Games completed successfully!")
        print(f"Games played: {results['games_played']}")
        
        # Check for log files
        import glob
        log_files = glob.glob("results/terminal_log_*.json")
        txt_files = glob.glob("results/terminal_log_*.txt")
        
        print(f"\n3. Terminal log files created:")
        print(f"JSON logs: {len(log_files)}")
        print(f"Text logs: {len(txt_files)}")
        
        if log_files:
            print("\nSample log file content:")
            with open(log_files[0], 'r') as f:
                log_data = f.read()
                print(f"First 500 chars: {log_data[:500]}...")
        
        # Check game results for terminal log references
        if results['results']:
            for i, game_result in enumerate(results['results']):
                print(f"\nGame {i+1} result:")
                print(f"  Result: {game_result.get('result', 'N/A')}")
                print(f"  Moves played: {game_result.get('moves_played', 'N/A')}")
                print(f"  Hallucination detected: {game_result.get('hallucination_detected', 'N/A')}")
                if 'terminal_logs' in game_result:
                    print(f"  Terminal logs: {game_result['terminal_logs']}")
                else:
                    print(f"  Terminal logs: Not found")
        
    except Exception as e:
        print(f"✗ Error during game execution: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Configuration Test Complete ===")
    print("Check the 'results/' directory for:")
    print("- game_*.json files (game results)")
    print("- terminal_log_*.json files (structured logs)")
    print("- terminal_log_*.txt files (readable logs)")

if __name__ == "__main__":
    test_configuration() 