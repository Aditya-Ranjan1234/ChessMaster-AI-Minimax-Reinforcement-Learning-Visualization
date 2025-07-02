#!/usr/bin/env python3
"""
Test script to verify the chess tournament setup works correctly.
"""

import sys
import os

# Add the state_tracking directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'state_tracking'))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from game_orchestrator import GameOrchestrator, LocalLLM, GroqInterface
        from state_tracker import ChessStateTracker
        from results_analyzer import ResultsAnalyzer
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_state_tracker():
    """Test the state tracker functionality"""
    try:
        from state_tracker import ChessStateTracker
        tracker = ChessStateTracker()
        
        # Test initial state
        initial_fen = tracker.board.fen()
        expected_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        print(f"   Initial FEN: {initial_fen}")
        print(f"   Expected FEN: {expected_fen}")
        assert initial_fen == expected_fen, f"FEN mismatch: {initial_fen} != {expected_fen}"
        
        # Test making a move
        print("   Testing move: e2e4")
        success, message = tracker.make_move("e2e4")
        print(f"   Move result: success={success}, message='{message}'")
        assert success == True, f"Move failed: {message}"
        
        # Check if the move was actually made
        new_fen = tracker.board.fen()
        print(f"   New FEN after move: {new_fen}")
        
        # In FEN notation, e4 move should show:
        # - Pawn moved from e2 to e4
        # - e2 becomes empty (1 in FEN)
        # - e4 has a white pawn (P in FEN)
        # - The 4th rank should show "4P3" (empty squares, then pawn, then empty squares)
        expected_fen_after_e4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        assert new_fen == expected_fen_after_e4, f"FEN after e4 move incorrect: {new_fen}"
        
        # Test that current_fen is updated
        assert tracker.current_fen == new_fen, f"current_fen not updated: {tracker.current_fen} != {new_fen}"
        
        print("✅ State tracker working correctly")
        return True
    except Exception as e:
        print(f"❌ State tracker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_creation():
    """Test that LLM instances can be created"""
    try:
        from local_llm import LocalLLM
        from groq_interface import GroqInterface
        
        # Test local LLM creation (this will load the model)
        print("Loading TinyLlama model... (this may take a moment)")
        local_llm = LocalLLM(name="TinyLlama-1.1B")
        print("✅ Local LLM created successfully")
        
        # Test Groq interface creation (this won't make API calls yet)
        groq_llm = GroqInterface(model_name="llama-3.3-70b-versatile", name="Groq Llama-3.3-70B-Versatile")
        print("✅ Groq interface created successfully")
        
        return True
    except Exception as e:
        print(f"❌ LLM creation test failed: {e}")
        return False

def main():
    print("Testing Chess Tournament Setup")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("State Tracker Test", test_state_tracker),
        ("LLM Creation Test", test_llm_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n{'='*40}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! You can now run the tournament with:")
        print("   python run_chess_tournament.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running the tournament.")
    
    return passed == total

if __name__ == "__main__":
    main() 