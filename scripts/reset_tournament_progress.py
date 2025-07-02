#!/usr/bin/env python3
"""
Reset Tournament Progress
This script resets the tournament progress to skip problematic matchups.
"""

import json
import os
from datetime import datetime

def reset_tournament_progress():
    """Reset tournament progress to skip problematic matchups"""
    
    # Find the latest progress file
    save_dir = "game_progress"
    if not os.path.exists(save_dir):
        print("❌ No game_progress directory found")
        return
    
    progress_files = sorted([f for f in os.listdir(save_dir) if f.startswith("progress_")])
    if not progress_files:
        print("❌ No progress files found")
        return
    
    latest_progress = os.path.join(save_dir, progress_files[-1])
    print(f"📁 Found latest progress file: {latest_progress}")
    
    # Load the current progress
    try:
        with open(latest_progress, 'r') as f:
            progress_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading progress file: {e}")
        return
    
    print("\n📋 Current Progress:")
    for i, matchup in enumerate(progress_data.get('matchups', [])):
        completed = matchup.get('completed_games', 0)
        total = matchup.get('total_games', 10)
        status = "✅" if completed >= total else "⏳"
        print(f"   {i+1}. {status} {matchup['white']} vs {matchup['black']}: {completed}/{total} games")
    
    # Ask user which matchup to skip to
    print("\n🎯 Tournament Reset Options:")
    print("1. Skip to Matchup 3 (TinyLlama vs Groq Gemma2-9B-IT)")
    print("2. Skip to Matchup 4 (Groq Llama-3.3-70B vs TinyLlama)")
    print("3. Skip to Matchup 5 (Groq Llama-3.1-8B vs TinyLlama)")
    print("4. Skip to Matchup 6 (Groq Gemma2-9B-IT vs TinyLlama)")
    print("5. Start fresh tournament")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    if choice == "1":
        # Skip to Matchup 3
        progress_data['current_matchup_index'] = 2  # 0-indexed, so 2 = matchup 3
        progress_data['current_game_index'] = 0
        print("✅ Reset to Matchup 3")
    elif choice == "2":
        # Skip to Matchup 4
        progress_data['current_matchup_index'] = 3
        progress_data['current_game_index'] = 0
        print("✅ Reset to Matchup 4")
    elif choice == "3":
        # Skip to Matchup 5
        progress_data['current_matchup_index'] = 4
        progress_data['current_game_index'] = 0
        print("✅ Reset to Matchup 5")
    elif choice == "4":
        # Skip to Matchup 6
        progress_data['current_matchup_index'] = 5
        progress_data['current_game_index'] = 0
        print("✅ Reset to Matchup 6")
    elif choice == "5":
        # Start fresh
        progress_data['current_matchup_index'] = 0
        progress_data['current_game_index'] = 0
        # Clear all completed games
        for matchup in progress_data.get('matchups', []):
            matchup['completed_games'] = 0
        progress_data['results'] = {}
        print("✅ Reset to fresh tournament")
    else:
        print("❌ Invalid choice")
        return
    
    # Create backup of original file
    backup_name = latest_progress.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    try:
        with open(backup_name, 'w') as f:
            json.dump(progress_data, f, indent=2)
        print(f"💾 Original progress backed up to: {backup_name}")
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
    
    # Save the reset progress
    try:
        with open(latest_progress, 'w') as f:
            json.dump(progress_data, f, indent=2)
        print(f"✅ Progress reset and saved to: {latest_progress}")
    except Exception as e:
        print(f"❌ Error saving reset progress: {e}")
        return
    
    print("\n📋 Updated Progress:")
    for i, matchup in enumerate(progress_data.get('matchups', [])):
        completed = matchup.get('completed_games', 0)
        total = matchup.get('total_games', 10)
        status = "✅" if completed >= total else "⏳"
        if i == progress_data['current_matchup_index']:
            status = "🎯"  # Current matchup
        print(f"   {i+1}. {status} {matchup['white']} vs {matchup['black']}: {completed}/{total} games")
    
    print(f"\n🎮 Next matchup: {progress_data['current_matchup_index'] + 1}")
    print("🚀 You can now run the tournament again with: python run_chess_tournament.py")

if __name__ == "__main__":
    reset_tournament_progress() 