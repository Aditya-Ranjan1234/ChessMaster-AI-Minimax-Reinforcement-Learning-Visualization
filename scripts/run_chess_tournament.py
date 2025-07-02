#!/usr/bin/env python3
"""
Chess Tournament Runner
Run this script from the project root to start the LLM chess tournament.
"""

import sys
import os
import signal
import time
from datetime import datetime

# Add the state_tracking directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'state_tracking'))

# Now import and run the orchestrator
from game_orchestrator import GameOrchestrator, LocalLLM, GroqInterface

class TournamentRunner:
    def __init__(self):
        self.orchestrator = None
        self.paused = False
        self.start_time = None
        self.failure_count = 0  # Track consecutive failures
        self.max_failures = 5   # Maximum consecutive failures before skipping matchup
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Interrupt received. Saving progress...")
        if self.orchestrator:
            self.orchestrator.save_progress()
        print("✅ Progress saved. You can resume later with the same command.")
        sys.exit(0)
    
    def show_progress(self):
        """Display current tournament progress"""
        if not self.orchestrator:
            return
            
        print("\n" + "="*60)
        print("📊 TOURNAMENT PROGRESS")
        print("="*60)
        
        total_matchups = len(self.orchestrator.matchups)
        current_matchup = self.orchestrator.current_matchup_index + 1
        
        # Handle case where current_matchup_index is out of bounds
        if self.orchestrator.current_matchup_index >= total_matchups:
            print(f"Current Matchup: {total_matchups}/{total_matchups} (Completed)")
            print("🎉 Tournament completed!")
        else:
            print(f"Current Matchup: {current_matchup}/{total_matchups}")
            
            white, black, total_games = self.orchestrator.matchups[self.orchestrator.current_matchup_index]
            matchup_key = f"{white.name}_vs_{black.name}"
            completed_games = self.orchestrator.results_analyzer.games_data.get(matchup_key, {}).get('games_played', 0)
            print(f"Current Game: {completed_games + 1}/{total_games}")
            print(f"Players: {white.name} (White) vs {black.name} (Black)")
        
        # Show overall progress
        total_games_played = sum(
            data.get('games_played', 0) 
            for data in self.orchestrator.results_analyzer.games_data.values()
        )
        total_games = total_matchups * 10
        print(f"Overall Progress: {total_games_played}/{total_games} games completed")
        
        if self.start_time:
            elapsed = time.time() - self.start_time
            print(f"Time Elapsed: {elapsed/3600:.1f} hours")
        
        print("="*60)
    
    def show_menu(self):
        """Show interactive menu"""
        print("\n🎮 TOURNAMENT CONTROLS")
        print("1. Continue tournament")
        print("2. Show progress")
        print("3. Pause and save")
        print("4. Exit")
        return input("Choose option (1-4): ").strip()
    
    def load_saved_progress(self):
        """Load saved progress if available"""
        save_dir = "game_progress"
        if os.path.exists(save_dir):
            progress_files = sorted([f for f in os.listdir(save_dir) if f.startswith("progress_")])
            if progress_files:
                latest_progress = os.path.join(save_dir, progress_files[-1])
                print(f"📁 Found saved progress: {latest_progress}")
                
                # Show what's in the saved progress
                try:
                    import json
                    with open(latest_progress, 'r') as f:
                        save_data = json.load(f)
                    
                    print("📋 Saved Progress Summary:")
                    for matchup in save_data.get('matchups', []):
                        completed = matchup.get('completed_games', 0)
                        total = matchup.get('total_games', 10)
                        print(f"   {matchup['white']} vs {matchup['black']}: {completed}/{total} games")
                    
                    load = input("\n🔄 Load saved progress? (y/n): ").lower() == 'y'
                    if load:
                        self.orchestrator.load_progress(latest_progress)
                        print("✅ Progress loaded successfully!")
                        return True
                except Exception as e:
                    print(f"❌ Error reading progress file: {e}")
        
        return False
    
    def run_tournament(self):
        """Main tournament execution"""
        print("🏆 Starting LLM Chess Tournament...")
        print("=" * 60)
        
        # Set up signal handler for graceful interruption
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Instantiate your LLMs
        print("🤖 Loading LLM models...")
        local_llm = LocalLLM(name="TinyLlama-1.1B")
        
        # Groq-backed models
        groq_mixtral = GroqInterface(model_name="llama-3.3-70b-versatile", name="Groq Llama-3.3-70B-Versatile")
        groq_llama_3_1_8b_instant = GroqInterface(model_name="llama-3.1-8b-instant", name="Groq Llama-3.1-8B-Instant")
        groq_gemma_7b_it = GroqInterface(model_name="gemma2-9b-it", name="Groq Gemma2-9B-IT")
        
        # Define your matchups
        matchups = [
            (local_llm, groq_mixtral, 10),
            (local_llm, groq_llama_3_1_8b_instant, 10),
            (local_llm, groq_gemma_7b_it, 10),
            (groq_mixtral, local_llm, 10),
            (groq_llama_3_1_8b_instant, local_llm, 10),
            (groq_gemma_7b_it, local_llm, 10)
        ]
        
        print("📋 Tournament Setup:")
        print(f"   • Total matchups: {len(matchups)}")
        print(f"   • Games per matchup: 10")
        print(f"   • Total games: {len(matchups) * 10}")
        print()
        print("🎯 Matchups:")
        for i, (white, black, games) in enumerate(matchups, 1):
            print(f"   {i}. {white.name} (White) vs {black.name} (Black) - {games} games")
        print()
        
        # Create orchestrator and set matchups
        self.orchestrator = GameOrchestrator(local_llm, groq_mixtral)
        self.orchestrator.set_matchups(matchups)
        
        # Load saved progress if available
        progress_loaded = self.load_saved_progress()
        
        if not progress_loaded:
            print("🚀 Starting fresh tournament...")
        else:
            print("🔄 Resuming tournament...")
        
        self.start_time = time.time()
        
        # Main tournament loop
        while True:
            try:
                # Show current progress
                self.show_progress()
                
                # Check if tournament is complete
                if self.orchestrator.current_matchup_index >= len(matchups):
                    print("🎉 Tournament completed!")
                    break
                
                # Show menu if not in auto-mode
                if not progress_loaded:
                    choice = self.show_menu()
                    if choice == "2":
                        continue
                    elif choice == "3":
                        print("💾 Saving progress...")
                        self.orchestrator.save_progress()
                        print("✅ Progress saved. You can resume later.")
                        return
                    elif choice == "4":
                        print("👋 Exiting tournament.")
                        return
                    elif choice != "1":
                        print("❌ Invalid choice. Continuing...")
                
                # Get current matchup info
                white_player, black_player, total_games = self.orchestrator.matchups[self.orchestrator.current_matchup_index]
                matchup_key = f"{white_player.name}_vs_{black_player.name}"
                completed_games = self.orchestrator.results_analyzer.games_data.get(matchup_key, {}).get('games_played', 0)
                
                # Check if current matchup is completed
                if completed_games >= total_games:
                    print(f"\n✅ Matchup {self.orchestrator.current_matchup_index + 1} completed!")
                    self.orchestrator.current_matchup_index += 1
                    self.orchestrator.current_game_index = 0
                    continue
                
                # Play one game for current matchup
                print(f"\n🎮 Playing game {completed_games + 1}/{total_games} for matchup {self.orchestrator.current_matchup_index + 1}...")
                print(f"Players: {white_player.name} (White) vs {black_player.name} (Black)")
                
                # Start terminal logging for this game
                self.orchestrator.terminal_logger.start_logging()
                
                try:
                    # Play the game
                    game_result = self.orchestrator.play_game()
                    
                    # Game completed successfully, reset failure counter
                    self.failure_count = 0
                    
                    # Stop logging and save terminal output
                    self.orchestrator.terminal_logger.stop_logging()
                    game_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                    log_json, log_txt = self.orchestrator.terminal_logger.save_log(game_id)
                    
                    # Add terminal log info to game result
                    game_result['terminal_logs'] = {
                        'json_file': log_json,
                        'text_file': log_txt
                    }
                    
                    # Auto-save after each game
                    self.orchestrator.save_progress()
                    print("💾 Progress auto-saved after game.")
                    
                    # Reset state for next game
                    self.orchestrator.state_tracker.reset()
                    
                except Exception as e:
                    # Game failed, increment failure counter
                    self.failure_count += 1
                    print(f"\n❌ Game failed (failure #{self.failure_count}): {e}")
                    
                    # Stop logging even if game failed
                    self.orchestrator.terminal_logger.stop_logging()
                    
                    # Check if we should skip this matchup
                    if self.failure_count >= self.max_failures:
                        print(f"\n⚠️  Skipping matchup {self.orchestrator.current_matchup_index + 1} after {self.failure_count} consecutive failures")
                        print(f"Players: {white_player.name} vs {black_player.name}")
                        self.orchestrator.current_matchup_index += 1
                        self.orchestrator.current_game_index = 0
                        self.failure_count = 0  # Reset for next matchup
                        continue
                    
                    # Save progress even after failure
                    self.orchestrator.save_progress()
                    print("💾 Progress saved after failure.")
                    
                    # Reset state for next attempt
                    self.orchestrator.state_tracker.reset()
                    continue
                
                # Reset progress_loaded flag after first game
                progress_loaded = False
                
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupt received. Saving progress...")
                self.orchestrator.save_progress()
                print("✅ Progress saved. You can resume later with the same command.")
                break
            except Exception as e:
                print(f"\n❌ Error during tournament: {e}")
                print("💾 Saving progress before exiting...")
                self.orchestrator.save_progress()
                break
        
        # Final summary
        if self.orchestrator:
            total_games_played = sum(
                data.get('games_played', 0) 
                for data in self.orchestrator.results_analyzer.games_data.values()
            )
            print(f"\n📊 Final Summary: {total_games_played} games completed")

def main():
    runner = TournamentRunner()
    runner.run_tournament()

if __name__ == "__main__":
    main() 