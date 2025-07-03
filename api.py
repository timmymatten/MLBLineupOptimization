import requests
import json

class MLBStatsAPI:
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
    
    def get_mlb_teams(self):
        """Get all MLB teams"""
        response = requests.get(f"{self.base_url}/teams")
        result = response.json()
        result['teams'] = [team for team in result['teams'] if team.get('sport', {}).get('name') == "Major League Baseball"]
        return result
    
    def get_college_teams(self):
        """Get all College teams"""
        response = requests.get(f"{self.base_url}/teams")
        result = response.json()
        result['teams'] = [team for team in result['teams'] if team.get('sport', {}).get('name') == "College Baseball"]
        return result
    
    def get_roster(self, team_id):
        """Get current roster for a team"""
        response = requests.get(f"{self.base_url}/teams/{team_id}/roster")
        return response.json()
    
    def get_player_stats(self, player_id, season=2025):
        """Get player stats for a season"""
        url = f"{self.base_url}/people/{player_id}/stats"
        params = {
            'stats': 'season',
            'season': season
        }
        response = requests.get(url, params=params)
        return response.json()
    
# Usage example
api = MLBStatsAPI()

# Get all teams
teams = api.get_mlb_teams()
with open("teams.json", "w") as f:
    json.dump(teams, f, indent=4)
print(f"Found {len(teams['teams'])} teams")
print("Teams:")
for team in teams['teams']:
    print(f"{team['name']} ({team['id']}) - {team['venue']['name']}")

print("\n")

# Get Yankees roster (team ID 147)
yankees_roster = api.get_roster(121)
print(f"Yankees Roster ({len(yankees_roster['roster'])} players):")

for player in yankees_roster['roster']:
    print(f"{player['person']['fullName']} - {player['position']['name']}")