"""
File: app.py
Description: Flask web server to provide API endpoints for the MLB Lineup Optimization Dashboard
Integrates with existing evo.py, api.py, and main.py modules
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import threading
import time
from datetime import datetime
import os

# Import your existing modules
from api import MLBStatsAPI
from evo import Evo
from main import proper_leadoff, run_production_cascade, swapper, wasted_obp_agent, wasted_slg_agent

app = Flask(__name__)
CORS(app)

# Global variables for evolution tracking
current_evolution = None
evolution_thread = None
evolution_data = {
    'running': False,
    'generation': 0,
    'best_solution': None,
    'scores_history': [],
    'start_time': None,
    'time_limit': 180
}

# Initialize API
api = MLBStatsAPI(update=False)

@app.route('/')
def dashboard():
    """Serve the dashboard HTML"""
    try:
        with open('dashboard.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
        <head><title>Dashboard Not Found</title></head>
        <body>
            <h1>Dashboard HTML file not found</h1>
            <p>Please create dashboard.html in the project directory.</p>
            <p>You can copy the dashboard code from the artifacts provided.</p>
            <p><a href="/api/test-data">Test API Connection</a></p>
        </body>
        </html>
        """

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get list of MLB teams"""
    try:
        teams_data = api.get_mlb_teams()
        return jsonify({
            'success': True,
            'teams': teams_data['teams']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/initialize-lineup', methods=['POST'])
def initialize_lineup():
    """Initialize a lineup for a given team and game context"""
    try:
        data = request.json
        team_name = data.get('team_name')
        pitcher_name = data.get('pitcher_name', 'Unknown')
        pitcher_throws = data.get('pitcher_throws', 'R')
        ballpark = data.get('ballpark', 'Unknown')
        weather = data.get('weather', 'Clear')
        
        if not team_name:
            return jsonify({
                'success': False,
                'error': 'Team name is required'
            }), 400
        
        print(f"Initializing lineup for {team_name}")  # Debug logging
        
        # Generate initial lineup
        solution = api.init_sol(
            team_name=team_name,
            opp_pitcher=pitcher_name,
            p_throws=pitcher_throws,
            ballpark=ballpark,
            weather=weather
        )
        
        print(f"Generated solution with {len(solution['lineup'])} players")  # Debug logging
        
        # Calculate initial scores with error handling
        try:
            cascade_score = run_production_cascade(solution)
        except Exception as e:
            print(f"Cascade score error: {e}")
            cascade_score = 0.0
            
        try:
            leadoff_score = proper_leadoff(solution)
        except Exception as e:
            print(f"Leadoff score error: {e}")
            leadoff_score = 0
            
        total_penalty = cascade_score + (1 - leadoff_score)
        
        return jsonify({
            'success': True,
            'lineup': solution,
            'scores': {
                'cascade_score': cascade_score,
                'leadoff_score': leadoff_score,
                'total_penalty': total_penalty
            }
        })
        
    except Exception as e:
        print(f"Initialize lineup error: {e}")  # Debug logging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/start-evolution', methods=['POST'])
def start_evolution():
    """Start the evolutionary optimization process"""
    global current_evolution, evolution_thread, evolution_data
    
    try:
        data = request.json
        initial_solution = data.get('initial_solution')
        time_limit = data.get('time_limit', 180)
        dominance_check = data.get('dominance_check', 50)
        
        if not initial_solution:
            return jsonify({
                'success': False,
                'error': 'Initial solution is required'
            }), 400
        
        if evolution_data['running']:
            return jsonify({
                'success': False,
                'error': 'Evolution is already running'
            }), 400
        
        # Reset evolution data
        evolution_data = {
            'running': True,
            'generation': 0,
            'best_solution': initial_solution,
            'scores_history': [],
            'start_time': time.time(),
            'time_limit': time_limit
        }
        
        # Start evolution in separate thread
        evolution_thread = threading.Thread(
            target=run_evolution,
            args=(initial_solution, time_limit, dominance_check)
        )
        evolution_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Evolution started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stop-evolution', methods=['POST'])
def stop_evolution():
    """Stop the evolutionary optimization process"""
    global evolution_data
    
    evolution_data['running'] = False
    
    return jsonify({
        'success': True,
        'message': 'Evolution stopped'
    })

@app.route('/api/evolution-status', methods=['GET'])
def evolution_status():
    """Get current evolution status and progress"""
    global evolution_data
    
    status = {
        'running': evolution_data['running'],
        'generation': evolution_data['generation'],
        'progress': 0,
        'elapsed_time': 0,
        'scores_history': evolution_data['scores_history'][-50:],  # Last 50 generations
        'best_solution': evolution_data['best_solution']
    }
    
    if evolution_data['start_time']:
        elapsed = time.time() - evolution_data['start_time']
        status['elapsed_time'] = elapsed
        status['progress'] = min(elapsed / evolution_data['time_limit'], 1.0)
    
    return jsonify({
        'success': True,
        'status': status
    })

@app.route('/api/player-stats/<player_name>', methods=['GET'])
def get_player_stats(player_name):
    """Get statistics for a specific player"""
    try:
        stats = {}
        for stat in ['AVG', 'OBP', 'SLG', 'wOBA', 'wRC+']:
            try:
                stats[stat] = api.get_stats(player_name, stat)
            except Exception as stat_error:
                print(f"Error getting {stat} for {player_name}: {stat_error}")
                stats[stat] = None
        
        return jsonify({
            'success': True,
            'player': player_name,
            'stats': stats
        })
    except Exception as e:
        print(f"Player stats error for {player_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-data', methods=['GET'])
def test_data():
    """Test endpoint to check data availability"""
    try:
        # Test if batting stats are available
        import os
        data_file = "data/batting_stats.csv"
        exists = os.path.exists(data_file)
        
        sample_players = []
        if exists:
            import pandas as pd
            df = pd.read_csv(data_file)
            sample_players = df['Name'].head(5).tolist()
        
        return jsonify({
            'success': True,
            'data_file_exists': exists,
            'sample_players': sample_players,
            'api_initialized': api is not None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def run_evolution(initial_solution, time_limit, dominance_check):
    """Run the evolutionary optimization in a separate thread"""
    global current_evolution, evolution_data
    
    try:
        # Create Evo instance
        E = Evo()
        
        # Add objectives
        E.add_objective("proper_leadoff", proper_leadoff)
        E.add_objective("run_production_cascade", run_production_cascade)
        
        # Add agents
        E.add_agent("swapper", swapper, k=1)
        E.add_agent("wasted_obp_agent", wasted_obp_agent, k=1)
        E.add_agent("wasted_slg_agent", wasted_slg_agent, k=1)
        
        # Add initial solution
        E.add_solution(initial_solution)
        current_evolution = E
        
        # Custom evolution loop with progress tracking
        agent_names = list(E.agents.keys())
        start_time = time.time()
        i = 0
        
        while evolution_data['running'] and time.time() - start_time < time_limit:
            # Run one evolution step
            import random as rnd
            pick = rnd.choice(agent_names)
            E.run_agent(pick)
            
            # Update generation counter
            evolution_data['generation'] = i
            
            # Get best solution and scores
            if E.unreduced_pop:
                best_entry = min(E.unreduced_pop.values(), key=lambda x: x["penalty"])
                evolution_data['best_solution'] = best_entry["solution"]
                
                # Record scores for history
                evolution_data['scores_history'].append({
                    'generation': i,
                    'cascade_score': best_entry["scores"].get("run_production_cascade", 0),
                    'leadoff_score': best_entry["scores"].get("proper_leadoff", 0),
                    'total_penalty': best_entry["penalty"],
                    'timestamp': time.time()
                })
                
                # Log progress every 50 generations
                if i % 50 == 0:
                    print(f"Generation {i}: Best penalty = {best_entry['penalty']:.3f}")
            
            # Remove dominated solutions periodically
            if i % dominance_check == 0:
                E.remove_dominated()
                if E.unreduced_pop:
                    print(f"Population reduced to {len(E.unreduced_pop)} solutions")
            
            i += 1
            time.sleep(0.01)  # Small delay to prevent overwhelming the system
        
        # Final cleanup
        E.remove_dominated()
        evolution_data['running'] = False
        
        # Save best solution to file
        if E.get_best_solution():
            with open("best_solution.json", "w") as f:
                json.dump(E.get_best_solution(), f, indent=2)
        
    except Exception as e:
        print(f"Evolution error: {e}")
        evolution_data['running'] = False

@app.route('/api/save-lineup', methods=['POST'])
def save_lineup():
    """Save current lineup to file"""
    try:
        data = request.json
        lineup = data.get('lineup')
        filename = data.get('filename', 'saved_lineup.json')
        
        if not lineup:
            return jsonify({
                'success': False,
                'error': 'Lineup data is required'
            }), 400
        
        # Ensure the filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Create saves directory if it doesn't exist
        import os
        saves_dir = 'saves'
        os.makedirs(saves_dir, exist_ok=True)
        
        # Full path for the saved file
        file_path = os.path.join(saves_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(lineup, f, indent=2)
        
        # Get absolute path for user feedback
        abs_path = os.path.abspath(file_path)
        
        print(f"✓ Lineup saved to: {abs_path}")  # Debug logging
        
        return jsonify({
            'success': True,
            'message': f'Lineup saved to {filename}',
            'file_path': abs_path,
            'relative_path': file_path
        })
        
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/load-lineup', methods=['POST'])
def load_lineup():
    """Load lineup from file"""
    try:
        data = request.json
        filename = data.get('filename', 'best_solution.json')
        
        # Try multiple possible locations for the file
        possible_paths = [
            filename,  # Current directory
            os.path.join('saves', filename),  # saves directory
            'best_solution.json',  # Default output file
            os.path.join('saves', 'best_solution.json')
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': f'File not found. Tried: {", ".join(possible_paths)}'
            }), 404
        
        with open(file_path, 'r') as f:
            lineup = json.load(f)
        
        abs_path = os.path.abspath(file_path)
        print(f"✓ Lineup loaded from: {abs_path}")  # Debug logging
        
        return jsonify({
            'success': True,
            'lineup': lineup,
            'file_path': abs_path
        })
        
    except Exception as e:
        print(f"Load error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/list-saved-lineups', methods=['GET'])
def list_saved_lineups():
    """List all saved lineup files"""
    try:
        import os
        import glob
        from datetime import datetime
        
        saved_files = []
        
        # Check both current directory and saves directory
        search_patterns = [
            '*.json',
            'saves/*.json'
        ]
        
        for pattern in search_patterns:
            for file_path in glob.glob(pattern):
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    saved_files.append({
                        'filename': os.path.basename(file_path),
                        'full_path': os.path.abspath(file_path),
                        'relative_path': file_path,
                        'size_bytes': size,
                        'size_kb': round(size / 1024, 1),
                        'modified': modified
                    })
        
        # Remove duplicates and sort by modification time
        unique_files = {f['filename']: f for f in saved_files}.values()
        sorted_files = sorted(unique_files, key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': sorted_files,
            'count': len(sorted_files)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate-scores', methods=['POST'])
def calculate_scores():
    """Calculate scores for a given lineup"""
    try:
        data = request.json
        lineup = data.get('lineup')
        
        if not lineup:
            return jsonify({
                'success': False,
                'error': 'Lineup data is required'
            }), 400
        
        # Calculate scores with error handling
        try:
            cascade_score = run_production_cascade(lineup)
        except Exception as e:
            print(f"Cascade score error: {e}")
            cascade_score = 0.0
            
        try:
            leadoff_score = proper_leadoff(lineup)
        except Exception as e:
            print(f"Leadoff score error: {e}")
            leadoff_score = 0
            
        total_penalty = cascade_score + (1 - leadoff_score)
        
        return jsonify({
            'success': True,
            'scores': {
                'cascade_score': cascade_score,
                'leadoff_score': leadoff_score,
                'total_penalty': total_penalty
            }
        })
        
    except Exception as e:
        print(f"Calculate scores error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting MLB Lineup Optimization Dashboard...")
    print("Dashboard will be available at: http://localhost:5001")
    print("Debug mode enabled - check terminal for detailed logging")
    app.run(debug=True, host='0.0.0.0', port=5001)