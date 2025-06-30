#!/usr/bin/env python3
"""
Test script to demonstrate terminal logging functionality
"""

import sys
import os
sys.path.append('state_tracking')

from game_orchestrator import GameOrchestrator, TerminalLogger
from local_llm import LocalLLM
from groq_interface import GroqInterface

def test_terminal_logging():
    """Test the terminal logging functionality"""
    
    print("=== Testing Terminal Logging Functionality ===")
    
    # Create a simple test with dummy LLMs
    class DummyLLM:
        def __init__(self, name):
            self.name = name
        def get_move(self, fen, suggested_opening=None):
            return {'move': 'e2e4', 'model': self.name}
    
    # Create test LLMs
    white_player = DummyLLM("Test-White")
    black_player = DummyLLM("Test-Black")
    
    # Create orchestrator
    orchestrator = GameOrchestrator(white_player, black_player)
    
    # Test terminal logger directly
    print("\n1. Testing TerminalLogger class directly...")
    logger = TerminalLogger(log_dir="test_logs")
    
    # Start logging
    logger.start_logging()
    
    # Generate some test output
    print("This is test stdout output")
    print("Another line of output")
    import warnings
    warnings.warn("This is a test warning")
    
    # Stop logging
    logger.stop_logging()
    
    # Save the log
    log_json, log_txt = logger.save_log("test_game_001")
    
    print(f"Terminal log saved to:")
    print(f"  JSON: {log_json}")
    print(f"  Text: {log_txt}")
    
    # Read and display the log content
    print("\n2. Log content:")
    with open(log_txt, 'r') as f:
        print(f.read())
    
    print("\n3. Testing with actual game simulation...")
    
    # Set up a simple matchup
    matchups = [(white_player, black_player, 1)]
    orchestrator.set_matchups(matchups)
    
    # Play one game (this will trigger the logging)
    try:
        results = orchestrator.play_multiple_games(1)
        print(f"\nGame completed! Results: {results}")
    except Exception as e:
        print(f"Game simulation failed (expected with dummy LLMs): {e}")
    
    print("\n=== Terminal Logging Test Complete ===")
    print("Check the 'test_logs' directory for generated log files.")

if __name__ == "__main__":
    test_terminal_logging() 