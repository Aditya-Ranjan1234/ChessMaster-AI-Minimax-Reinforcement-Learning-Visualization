import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import json
import os
from datetime import datetime
import chess.pgn
import numpy as np

class ResultsAnalyzer:
    def __init__(self):
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)
        self.games_data = {}
        self.current_game = {
            'moves': [],
            'evaluations': {'local': [], 'groq': []},
            'hallucinations': []
        }
        
    def add_move(self, move_data: Dict):
        """Add a move to the current game tracking"""
        self.current_game['moves'].append({
            'move': move_data['move'],
            'model': move_data['model'],
            'fen': move_data['fen'],
            'timestamp': move_data['timestamp']
        })
        
    def add_evaluation(self, local_eval: float, groq_eval: float):
        """Add model evaluations for the current position"""
        self.current_game['evaluations']['local'].append(local_eval)
        self.current_game['evaluations']['groq'].append(groq_eval)
        
    def add_hallucination(self, hallucination_data: Dict):
        """Add hallucination data to the current game"""
        self.current_game['hallucinations'].append(hallucination_data)
        
    def end_game(self, game_result: Dict):
        """End the current game and save its data"""
        game_data = {
            'game_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'result': game_result['result'],
            'moves': self.current_game['moves'],
            'evaluations': self.current_game['evaluations'],
            'hallucinations': self.current_game['hallucinations'],
            'game_length': len(self.current_game['moves']),
            'hallucination_detected': bool(self.current_game['hallucinations']),
            'white_player': game_result['white_player'],
            'black_player': game_result['black_player']
        }
        
        # Add terminal log information if available
        if 'terminal_logs' in game_result:
            game_data['terminal_logs'] = game_result['terminal_logs']
        
        matchup_key = f"{game_data['white_player']}_vs_{game_data['black_player']}"
        if matchup_key not in self.games_data:
            self.games_data[matchup_key] = {'games_played': 0, 'games': []}
            
        self.games_data[matchup_key]['games_played'] += 1
        self.games_data[matchup_key]['games'].append(game_data)
        self._save_game_data(game_data)
        self._reset_current_game()
        
    def _reset_current_game(self):
        """Reset the current game tracking"""
        self.current_game = {
            'moves': [],
            'evaluations': {'local': [], 'groq': []},
            'hallucinations': []
        }
        
    def _save_game_data(self, game_data: Dict):
        """Save game data to JSON file"""
        filename = f"{self.results_dir}/game_{game_data['game_id']}.json"
        with open(filename, 'w') as f:
            json.dump(game_data, f, indent=2)
            
    def generate_visualizations(self):
        """Generate various visualizations of the game data"""
        if not self.games_data:
            print("No game data available for visualization")
            return
            
        # 1. Game Length Distribution
        plt.figure(figsize=(10, 6))
        game_lengths = [game['game_length'] for game in self.games_data.values()]
        sns.histplot(game_lengths, bins=20)
        plt.title('Distribution of Game Lengths')
        plt.xlabel('Number of Moves')
        plt.ylabel('Frequency')
        plt.savefig(f"{self.results_dir}/game_lengths.png")
        plt.close()
        
        # 2. Evaluation Comparison
        for game in self.games_data.values():
            plt.figure(figsize=(12, 6))
            moves = range(len(game['games']))
            plt.plot(moves, [game['games'][i]['evaluations']['local'] for i in range(len(game['games']))], label='Local LLM', alpha=0.7)
            plt.plot(moves, [game['games'][i]['evaluations']['groq'] for i in range(len(game['games']))], label='Groq LLM', alpha=0.7)
            plt.title(f'Model Evaluations - Game {game["games"][0]["game_id"]}')
            plt.xlabel('Move Number')
            plt.ylabel('Evaluation')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{self.results_dir}/evaluations_{game['games'][0]['game_id']}.png")
            plt.close()
            
        # 3. Hallucination Analysis
        hallucination_games = [game for game in self.games_data.values() for g in game['games'] if g['hallucination_detected']]
        if hallucination_games:
            plt.figure(figsize=(10, 6))
            move_numbers = [g['hallucinations'][i]['move_number'] for game in hallucination_games for i in range(len(g['games']))]
            models = [g['games'][i]['model'] for game in hallucination_games for i in range(len(g['games']))]
            
            sns.countplot(x=move_numbers, hue=models)
            plt.title('Hallucination Distribution by Move Number and Model')
            plt.xlabel('Move Number')
            plt.ylabel('Number of Hallucinations')
            plt.savefig(f"{self.results_dir}/hallucination_distribution.png")
            plt.close()
            
        # 4. Win/Loss/Draw Statistics
        results = [game['games'][i]['result'] for game in self.games_data.values() for i in range(len(game['games']))]
        result_counts = pd.Series(results).value_counts()
        
        plt.figure(figsize=(8, 8))
        plt.pie(result_counts, labels=result_counts.index, autopct='%1.1f%%')
        plt.title('Game Results Distribution')
        plt.savefig(f"{self.results_dir}/results_distribution.png")
        plt.close()
        
        # 5. Generate Summary Report
        self._generate_summary_report()
        
    def _generate_summary_report(self):
        """Generate a summary report of all games"""
        total_games = sum(data['games_played'] for data in self.games_data.values())
        all_games_flat = [game for matchup_data in self.games_data.values() for game in matchup_data['games']]
        
        hallucination_games = sum(1 for game in all_games_flat if game['hallucination_detected'])
        
        report = {
            'total_games': total_games,
            'games_with_hallucinations': hallucination_games,
            'hallucination_rate': hallucination_games / total_games if total_games > 0 else 0,
            'average_game_length': np.mean([game['game_length'] for game in all_games_flat]),
            'results_distribution': pd.Series([game['result'] for game in all_games_flat]).value_counts().to_dict(),
            'model_performance': {}
        }
        
        all_models = set()
        for matchup_data in self.games_data.values():
            for game in matchup_data['games']:
                all_models.add(game['white_player'])
                all_models.add(game['black_player'])

        for model_name in all_models:
            wins = sum(1 for game in all_games_flat if 
                       (game['white_player'] == model_name and game['result'] == '1-0') or \
                       (game['black_player'] == model_name and game['result'] == '0-1'))
            losses = sum(1 for game in all_games_flat if 
                         (game['white_player'] == model_name and game['result'] == '0-1') or \
                         (game['black_player'] == model_name and game['result'] == '1-0'))
            draws = sum(1 for game in all_games_flat if game['result'] == '1/2-1/2')
            
            report['model_performance'][model_name] = {
                'wins': wins,
                'losses': losses,
                'draws': draws
            }

        with open(f"{self.results_dir}/summary_report.json", 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate HTML report
        html_report = f"""
        <html>
        <head>
            <title>Chess LLM Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
                .metric {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>Chess LLM Analysis Report</h1>
            
            <div class="section">
                <h2>Overall Statistics</h2>
                <div class="metric">Total Games: {report['total_games']}</div>
                <div class="metric">Games with Hallucinations: {report['games_with_hallucinations']}</div>
                <div class="metric">Hallucination Rate: {report['hallucination_rate']:.2%}</div>
                <div class="metric">Average Game Length: {report['average_game_length']:.1f} moves</div>
            </div>
            
            <div class="section">
                <h2>Results Distribution</h2>
                <div class="metric">White Wins: {report['results_distribution'].get('1-0', 0)}</div>
                <div class="metric">Black Wins: {report['results_distribution'].get('0-1', 0)}</div>
                <div class="metric">Draws: {report['results_distribution'].get('1/2-1/2', 0)}</div>
            </div>
            
            <div class="section">
                <h2>Model Performance</h2>
                {''.join(f'''
                <h3>{model_name}</h3>
                <div class="metric">Wins: {data['wins']}</div>
                <div class="metric">Losses: {data['losses']}</div>
                <div class="metric">Draws: {data['draws']}</div>
                ''' for model_name, data in report['model_performance'].items())}
            </div>
            
            <div class="section">
                <h2>Visualizations</h2>
                <img src="game_lengths.png" alt="Game Lengths Distribution">
                <img src="results_distribution.png" alt="Results Distribution">
                <img src="hallucination_distribution.png" alt="Hallucination Distribution">
            </div>
        </body>
        </html>
        """
        
        with open(f"{self.results_dir}/report.html", 'w') as f:
            f.write(html_report) 