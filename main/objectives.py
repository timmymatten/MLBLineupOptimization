from api import MLBStatsAPI


api = MLBStatsAPI()

def ba_unsorted(L):
    L = L['lineup']

    return round(sum(
        api.get_stats(y, 'AVG') - api.get_stats(x, 'AVG')
        for x, y in zip(L, L[1:])
        if api.get_stats(x['name'], 'AVG') < api.get_stats(y['name'], 'AVG')
    ), 3)

def proper_leadoff(L):
    lineup = L['lineup']

    # Check if the first player is a leadoff hitter
    leadoff_hitter = lineup[0]
    leadoff_obp = api.get_stats(leadoff_hitter['name'], 'OBP')
    
    # Check if the leadoff hitter has a high enough batting average
    return 1 if leadoff_obp >= 0.350 else 0  # Example threshold for a good leadoff hitter

def run_production_cascade(L):
    """
    Objective function: Run Production Cascade (Minimization)
    
    Evaluates how well each hitter "sets up" the next hitter by measuring
    the synergy between table-setters and run producers.
    
    Formula: MAX_POSSIBLE_SCORE - Sum of (OBP of current hitter × SLG of next hitter)
    Returns a penalty score where 0 = perfect lineup, higher = worse
    
    Args:
        lineup: List of player dictionaries, each containing 'obp' and 'slg' keys
                Example: [{'name': 'Player1', 'obp': 0.350, 'slg': 0.450}, ...]
    
    Returns:
        float: Penalty score (closer to 0 is better)
    """
    lineup = L['lineup']

    if len(lineup) != 9:
        raise ValueError("Lineup must contain exactly 9 players")
    
    # Calculate the actual cascade score
    actual_cascade_score = 0.0
    
    # Calculate cascade for positions 1-8 → 2-9
    for i in range(8):
        current_hitter_obp = api.get_stats(lineup[i]['name'], 'OBP')
        next_hitter_slg = api.get_stats(lineup[i + 1]['name'], 'SLG')
        actual_cascade_score += current_hitter_obp * next_hitter_slg
    
    # Handle wraparound: 9th hitter sets up 1st hitter for next inning
    ninth_hitter_obp = api.get_stats(lineup[8]['name'], 'OBP')
    first_hitter_slg = api.get_stats(lineup[0]['name'], 'SLG')
    actual_cascade_score += ninth_hitter_obp * first_hitter_slg
    
    # Calculate theoretical maximum possible score for this set of players
    obp_values = [api.get_stats(player['name'], 'OBP') for player in lineup]
    slg_values = [api.get_stats(player['name'], 'SLG') for player in lineup]
    
    # Maximum possible cascade would be highest OBPs followed by highest SLGs
    obp_sorted = sorted(obp_values, reverse=True)
    slg_sorted = sorted(slg_values, reverse=True)
    
    max_possible_score = sum(obp_sorted[i] * slg_sorted[i] for i in range(9))
    
    # Return penalty: how far we are from the theoretical maximum
    penalty = max_possible_score - actual_cascade_score
    
    return round(penalty, 3) * 10

def best_nine(L):
    """
    Objective function: Best Nine by OPS, position-aware.

    For each lineup spot, only compare bench players who play the same position.
    Returns 0 if every lineup player is better than all eligible bench players at their position.
    Otherwise, returns the sum of (bench OPS - lineup OPS) for each position where a bench player is better.
    """

    lineup = L['lineup']
    bench = L.get('available_roster', [])

    if not bench or len(lineup) != 9:
        return 0.0

    penalty = 0.0
    for lineup_player in lineup:
        lineup_pos = lineup_player.get('position')
        try:
            lineup_ops = api.get_stats(lineup_player['name'], 'OPS')
        except (ValueError, KeyError):
            continue

        # Only compare bench players who play the same position
        for bench_player in bench:
            if bench_player.get('position') == lineup_pos:
                try:
                    bench_ops = api.get_stats(bench_player['name'], 'OPS')
                    if bench_ops > lineup_ops:
                        penalty += bench_ops - lineup_ops
                except (ValueError, KeyError):
                    continue

    return round(penalty, 3)