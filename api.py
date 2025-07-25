import requests
import json
import pybaseball as pyb
import pandas as pd

from profiler import Profiler, profile

class MLBStatsAPI:
    def __init__(self, update=False):
        self.base_url = "https://statsapi.mlb.com/api/v1"
        self._teams_cache = None
        self._roster_cache = {}
        self.update = update
    
    def get_mlb_teams(self):
        if self._teams_cache is not None and not self.update:
            # Return cached teams if available and update is not requested
            return self._teams_cache
        response = requests.get(f"{self.base_url}/teams")
        result = response.json()
        result['teams'] = [team for team in result['teams'] if team.get('sport', {}).get('name') == "Major League Baseball"]
        self._teams_cache = result
        return result
    
    def get_college_teams(self):
        response = requests.get(f"{self.base_url}/teams")
        result = response.json()
        result['teams'] = [team for team in result['teams'] if team.get('sport', {}).get('name') == "College Baseball"]
        return result
    
    def get_team_id(self, team_name):
        teams = self.get_mlb_teams()['teams']
        for team in teams:
            if team['name'].lower() == team_name.lower():
                return team['id']
        raise ValueError(f"Team '{team_name}' not found")
    
    def get_player_id(self, player_name):
        parts = player_name.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:])
        return pyb.playerid_lookup(last_name, first_name)['key_mlbam'].iloc[0] if not pyb.playerid_lookup(last_name, first_name).empty else self._get_player_id_from_roster(player_name)

    def _get_player_id_from_roster(self, player_name):
        for team in self.get_mlb_teams()['teams']:
            roster_data = self.get_roster(team['name'])
            for player in roster_data['roster']:
                if player['person']['fullName'].lower() == player_name.lower():
                    return player['person']['id']
        raise ValueError(f"Player '{player_name}' not found in any MLB team roster")

    @profile
    def get_roster(self, team):
        if team in self._roster_cache and not self.update:
            # Return cached roster if available and update is not requested
            return self._roster_cache[team]
        team_id = self.get_team_id(team)
        response = requests.get(f"{self.base_url}/teams/{team_id}/roster")
        roster = response.json()
        self._roster_cache[team] = roster
        return roster
    
    def get_player_stats_url(self, player_id, season=2025):
        url = f"{self.base_url}/people/{player_id}/stats"
        params = {
            'stats': 'season',
            'season': season
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def normalize_name(self, player_name):
        # Convert "Last, First" -> "First Last"
        if "," in player_name:
            last, first = [part.strip() for part in player_name.split(",")]
            return f"{first} {last}"
        return player_name
    
    def unnormalize_name(self, player_name):
        # Convert "First Last" -> "Last, First"
        parts = player_name.split()
        if len(parts) < 2:
            return player_name
        first = parts[0]
        last = " ".join(parts[1:])
        return f"{last}, {first}"
    
    def get_stats(self, player_name, stat, season=2025):
        data = pd.read_csv("data/batting_stats.csv")
        player_row = data[data['Name'] == player_name]
        if player_row.empty:
            raise ValueError(f"Player '{player_name}' not found in stats for {season}")
        return player_row.iloc[0][stat].item()
    
    def get_handedness(self, player_name, player_type):
        data = pd.read_csv("data/batting_stats_2025.csv")
        player_id = self.get_player_id(player_name)
        if player_type == 'batter':
            player_row = data[data['batter'] == player_id]
            return player_row['stand'].iloc[0]
        elif player_type == 'pitcher':
            player_row = data[data['pitcher'] == player_id]
            return player_row['p_throws'].iloc[0]
    
    @profile
    def init_sol(self, team_name, opp_pitcher='Unknown', p_throws='R', ballpark='Unknown', weather='Unknown'):
        """
        Initialize a base solution with the starting lineup and roster for a given team.
        Also includes the opposing pitcher if provided.
        Also includes game context like conditions and venue.
        
        Args:
            team_name (str): Name of the MLB team.
            opp_pitcher (str, optional): Name of the opposing pitcher. Defaults to 'Unknown'.
            p_throws (str): Pitcher's throwing hand ('R' or 'L'). Defaults to 'R'.
            ballpark (str): Name of the ballpark. Defaults to 'Unknown'.
            weather (str): Weather conditions. Defaults to 'Unknown'.
        
        Returns:
            dict: A dictionary containing the starting lineup, roster, opposing pitcher, and game context.
        """
        # Get the team roster
        roster_data = self.get_roster(team_name)
        
        # Extract roster information
        # Only include non-pitchers in the roster
        roster = []
        for player in roster_data['roster']:
            # Skip pitchers (position code "1" = Pitcher)
            if player['position']['code'] != '1':
                player_info = {
                    'name': player['person']['fullName'],
                    'position_code': player['position']['code'],
                    'jersey_number': player['jerseyNumber'],
                    'player_id': player['person']['id'],
                    'status': player['status']['description'],
                    'batting_side': self.get_handedness(player['person']['fullName'], 'batter'),
                    'defensive_position': 'Bench'  # Default position, will be updated later
                }
                roster.append(player_info)
        
        # Create initial lineup ensuring all defensive positions are filled
        import random

        # Define required defensive positions (position codes from MLB API)
        required_positions = {
            '2': 'Catcher',
            '3': 'First Base', 
            '4': 'Second Base',
            '5': 'Third Base',
            '6': 'Shortstop',
            '7': 'Left Field',
            '8': 'Center Field',
            '9': 'Right Field'
        }

        lineup = []
        used_players = set()

        # Helper to copy all keys from roster player and add/override lineup-specific keys
        def make_lineup_entry(roster_player, lineup_position, defensive_position):
            entry = dict(roster_player)  # copy all keys
            entry['defensive_position'] = defensive_position
            return entry

        # Fill defensive positions
        for pos_code, pos_name in required_positions.items():
            available_for_position = [p for p in roster 
                                      if p['position_code'] == pos_code and p['name'] not in used_players]
            if available_for_position:
                selected_player = random.choice(available_for_position)
                lineup.append(make_lineup_entry(selected_player, len(lineup) + 1, pos_name))
                used_players.add(selected_player['name'])
            else:
                available_players = [p for p in roster if p['name'] not in used_players]
                if available_players:
                    selected_player = random.choice(available_players)
                    lineup.append(make_lineup_entry(selected_player, len(lineup) + 1, pos_name))
                    used_players.add(selected_player['name'])
                else:
                    # Fill with empty if no players left
                    empty_player = {
                        'name': '',
                        'position': 'Unknown',
                        'position_code': '',
                        'jersey_number': '',
                        'player_id': '',
                        'status': '',
                        'batting_side': 'R',
                        'defensive_position': pos_name
                    }
                    lineup.append(make_lineup_entry(empty_player, len(lineup) + 1, pos_name))


        # Add DH (9th player)
        remaining_players = [p for p in roster if p['name'] not in used_players]
        if remaining_players:
            dh_player = random.choice(remaining_players)
            lineup.append(make_lineup_entry(dh_player, 9, 'Designated Hitter'))
        else:
            empty_player = {
                'name': '',
                'position': 'Unknown',
                'position_code': '',
                'jersey_number': '',
                'player_id': '',
                'status': '',
                'batting_side': 'R',
                'defensive_position': 'Designated Hitter'
            }
            lineup.append(make_lineup_entry(empty_player, 9, 'Designated Hitter'))

        # Shuffle the batting order while keeping defensive positions assigned
        random.shuffle(lineup)

        # Remove players in the starting lineup from the roster group
        roster = [player for player in roster if player['name'] not in {p['name'] for p in lineup if p['name']}]

        solution = {
            'lineup': lineup,
            'available_roster': roster,
            'opposing_pitcher': {
                'name': opp_pitcher if opp_pitcher else 'Unknown',
                'throws': p_throws,
            },
            'game_context': {
                'ballpark': ballpark,
                'weather': weather,
                'inning': 1,
                'situation': 'standard'
            },
            'team_info': {
                'name': team_name,
                'team_id': roster_data['teamId']
            }
        }

        return solution
 