"""
File: check_data.py
Description: Diagnostic script to check if all required data files are available
Run this before starting the dashboard to ensure everything is set up correctly
"""

import os
import pandas as pd
import json
from api import MLBStatsAPI

def check_files():
    """Check if all required files exist"""
    print("=== File Availability Check ===")
    
    required_files = [
        'data/batting_stats.csv',
        'teams.json',
        'api.py',
        'evo.py',
        'main.py'
    ]
    
    all_files_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
        if not exists:
            all_files_exist = False
    
    return all_files_exist

def check_data_content():
    """Check the content of data files"""
    print("\n=== Data Content Check ===")
    
    # Check batting stats CSV
    try:
        if os.path.exists('data/batting_stats.csv'):
            df = pd.read_csv('data/batting_stats.csv')
            print(f"✓ batting_stats.csv: {len(df)} players found")
            print(f"  - Columns: {list(df.columns[:10])}...")  # Show first 10 columns
            print(f"  - Sample players: {df['Name'].head(3).tolist()}")
            
            # Check for required columns
            required_cols = ['Name', 'AVG', 'OBP', 'SLG']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"  ⚠ Missing columns: {missing_cols}")
            else:
                print("  ✓ All required columns present")
        else:
            print("✗ batting_stats.csv not found")
    except Exception as e:
        print(f"✗ Error reading batting_stats.csv: {e}")

def test_api():
    """Test the API functionality"""
    print("\n=== API Functionality Test ===")
    
    try:
        api = MLBStatsAPI(update=False)
        print("✓ MLBStatsAPI initialized")
        
        # Test getting teams
        teams = api.get_mlb_teams()
        print(f"✓ Retrieved {len(teams['teams'])} MLB teams")
        
        # Test getting roster for a team
        mets_roster = api.get_roster('New York Mets')
        print(f"✓ Retrieved roster for New York Mets: {len(mets_roster['roster'])} players")
        
        # Test getting stats for a player
        # Try to get stats for a player from the CSV
        if os.path.exists('data/batting_stats.csv'):
            df = pd.read_csv('data/batting_stats.csv')
            sample_player = df['Name'].iloc[0]
            try:
                avg = api.get_stats(sample_player, 'AVG')
                print(f"✓ Retrieved stats for {sample_player}: AVG = {avg}")
            except Exception as e:
                print(f"⚠ Could not get stats for {sample_player}: {e}")
        
        # Test init_sol
        try:
            solution = api.init_sol('New York Mets', 'Test Pitcher', 'R', 'Test Park', 'Clear')
            print(f"✓ Generated initial solution with {len(solution['lineup'])} players")
            
            # Check if lineup players have required fields
            sample_player = solution['lineup'][0]
            required_fields = ['name', 'defensive_position', 'batting_side']
            missing_fields = [field for field in required_fields if field not in sample_player]
            if missing_fields:
                print(f"  ⚠ Sample player missing fields: {missing_fields}")
            else:
                print("  ✓ Lineup players have all required fields")
                
        except Exception as e:
            print(f"✗ Error generating initial solution: {e}")
            return False
            
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False
    
    return True

def test_objective_functions():
    """Test the objective functions"""
    print("\n=== Objective Functions Test ===")
    
    try:
        from main import proper_leadoff, run_production_cascade
        
        # Generate a test solution
        api = MLBStatsAPI(update=False)
        solution = api.init_sol('New York Mets', 'Test Pitcher', 'R', 'Test Park', 'Clear')
        
        # Test proper_leadoff
        try:
            leadoff_score = proper_leadoff(solution)
            print(f"✓ proper_leadoff function: {leadoff_score}")
        except Exception as e:
            print(f"✗ proper_leadoff failed: {e}")
        
        # Test run_production_cascade
        try:
            cascade_score = run_production_cascade(solution)
            print(f"✓ run_production_cascade function: {cascade_score}")
        except Exception as e:
            print(f"✗ run_production_cascade failed: {e}")
            
    except Exception as e:
        print(f"✗ Objective functions test failed: {e}")

def main():
    """Main diagnostic function"""
    print("MLB Lineup Optimization - Data Diagnostic")
    print("=" * 50)
    
    files_ok = check_files()
    check_data_content()
    api_ok = test_api()
    test_objective_functions()
    
    print("\n=== Summary ===")
    if files_ok and api_ok:
        print("✓ All systems ready! You can start the dashboard with: python app.py")
    else:
        print("✗ Issues found. Please fix the above errors before starting the dashboard.")
        
        if not files_ok:
            print("\nSuggestions:")
            print("- Make sure 'data/batting_stats.csv' exists and contains player statistics")
            print("- Ensure all Python files (api.py, evo.py, main.py) are in the project directory")
        
        if not api_ok:
            print("- Check that the batting_stats.csv has the correct format and columns")
            print("- Verify that the MLB Stats API is accessible")

if __name__ == "__main__":
    main()