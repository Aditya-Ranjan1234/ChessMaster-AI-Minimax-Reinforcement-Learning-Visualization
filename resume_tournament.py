#!/usr/bin/env python3
"""
Quick Resume Script
Use this to quickly resume a paused tournament.
"""

import sys
import os
import time

# Add the state_tracking directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'state_tracking'))

from run_chess_tournament import TournamentRunner
from game_orchestrator import GameOrchestrator, LocalLLM, GroqInterface

def main():
    print("🔄 Quick Resume - LLM Chess Tournament")
    print("=" * 50)
    
    runner = TournamentRunner()
    
    # Skip the setup and go straight to resuming
    print("🤖 Loading LLM models...")
    
    local_llm = LocalLLM(name="TinyLlama-1.1B")
    groq_mixtral = GroqInterface(model_name="llama-3.3-70b-versatile", name="Groq Llama-3.3-70B-Versatile")
    groq_llama_3_1_8b_instant = GroqInterface(model_name="llama-3.1-8b-instant", name="Groq Llama-3.1-8B-Instant")
    groq_gemma_7b_it = GroqInterface(model_name="gemma2-9b-it", name="Groq Gemma2-9B-IT")
    
    matchups = [
        (local_llm, groq_mixtral, 10),
        (local_llm, groq_llama_3_1_8b_instant, 10),
        (local_llm, groq_gemma_7b_it, 10),
        (groq_mixtral, local_llm, 10),
        (groq_llama_3_1_8b_instant, local_llm, 10),
        (groq_gemma_7b_it, local_llm, 10)
    ]
    
    runner.orchestrator = GameOrchestrator(local_llm, groq_mixtral)
    runner.orchestrator.set_matchups(matchups)
    
    # Force load the latest progress
    save_dir = "game_progress"
    if os.path.exists(save_dir):
        progress_files = sorted([f for f in os.listdir(save_dir) if f.startswith("progress_")])
        if progress_files:
            latest_progress = os.path.join(save_dir, progress_files[-1])
            print(f"📁 Loading latest progress: {latest_progress}")
            runner.orchestrator.load_progress(latest_progress)
            print("✅ Progress loaded successfully!")
        else:
            print("❌ No saved progress found. Run the full tournament first.")
            return
    else:
        print("❌ No saved progress found. Run the full tournament first.")
        return
    
    runner.start_time = time.time()
    
    # Continue the tournament
    print("🚀 Resuming tournament...")
    print("Press Ctrl+C to pause again")
    print("=" * 50)
    
    try:
        while True:
            # Show current progress
            runner.show_progress()
            
            # Check if tournament is complete
            if runner.orchestrator.current_matchup_index >= len(matchups):
                print("🎉 Tournament completed!")
                break
            
            # Play one game at a time
            print(f"\n🎮 Playing games for matchup {runner.orchestrator.current_matchup_index + 1}...")
            results = runner.orchestrator.play_multiple_games(num_games=1)
            
            # Auto-save after each game
            runner.orchestrator.save_progress()
            print("💾 Progress auto-saved after game.")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupt received. Saving progress...")
        runner.orchestrator.save_progress()
        print("✅ Progress saved. You can resume later with:")
        print("   python resume_tournament.py")
    
    # Final summary
    if runner.orchestrator:
        total_games_played = sum(
            data.get('games_played', 0) 
            for data in runner.orchestrator.results_analyzer.games_data.values()
        )
        print(f"\n📊 Final Summary: {total_games_played} games completed")

if __name__ == "__main__":
    main() 