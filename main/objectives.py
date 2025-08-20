from api import MLBStatsAPI


api = MLBStatsAPI()

def ba_unsorted(L):
    L = L['lineup']

    return round(sum(
        api.get_stats(y, 'AVG') - api.get_stats(x, 'AVG')
        for x, y in zip(L, L[1:])
        if api.get_stats(x['name'], 'AVG') < api.get_stats(y['name'], 'AVG')
    ), 3)

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

def proper_leadoff(L):
    lineup = L['lineup']
    leadoff_hitter = lineup[0]
    leadoff_obp = api.get_stats(leadoff_hitter['name'], 'OBP')
    
    if leadoff_obp >= 0.310:
        return 0
    else:
        # Return penalty proportional to how far from ideal
        penalty = (0.310 - leadoff_obp) * 10  # Scale for visibility
        return penalty

def proper_best_hitter_second(L):
    lineup = L['lineup']
    second_hitter = lineup[1]

    woba = api.get_stats(second_hitter['name'], 'wOBA') * 10
    wrc_plus = api.get_stats(second_hitter['name'], 'wRC+')
    score = woba + wrc_plus 
    
    # League average: wRC+ = 100, wOBA = 0.320
    # Let's set the threshold as: (wOBA - 0.320) * 1000 + (wRC+ - 100) * 1
    # This gives equal weight to being above average in both stats.
    THRESHOLD = 140  # This is the league average "score"

    if score >= THRESHOLD:
        return 0
    else:
        diff = (THRESHOLD - score) / 100
        return 1 if diff >= 1 else diff  # Return a penalty based on how far below threshold
    
def proper_third_hitter(L):
    lineup = L['lineup']

    # Ensure the third hitter (index 2) has a balanced OBP and SLG
    third_hitter = lineup[2]
    try:
        obp = api.get_stats(third_hitter['name'], 'OBP')
        slg = api.get_stats(third_hitter['name'], 'SLG')
    except (ValueError, KeyError):
        return 1  # Penalize if stats are missing

    # Define what "balanced" means: both above certain thresholds and not too far apart
    OBP_THRESHOLD = 0.350
    SLG_THRESHOLD = 0.425
    MAX_DIFF = 0.070  # OBP and SLG should not differ by more than this

    if obp >= OBP_THRESHOLD and slg >= SLG_THRESHOLD and abs(obp - slg) <= MAX_DIFF:
        return 0
    else:
        return max(0, abs(obp - slg) - MAX_DIFF) # Return a penalty based on the sum of OBP and SLG
    
def proper_cleanup_hitter(L):
    lineup = L['lineup']

    # Ensure the fourth hitter (index 3) has top 3 SLG on the team or SLG >= .450
    fourth_hitter = lineup[3]
    try:
        fourth_slg = api.get_stats(fourth_hitter['name'], 'SLG')
    except (ValueError, KeyError):
        return 1  # Penalize if stats are missing

    # Get all SLG values for the lineup
    slg_values = []
    for player in lineup:
        try:
            slg = api.get_stats(player['name'], 'SLG')
            slg_values.append(slg)
        except (ValueError, KeyError):
            continue

    # Sort SLG values descending
    top_slg = sorted(slg_values, reverse=True)[:3]

    if fourth_slg >= 0.450 or fourth_slg in top_slg:
        return 0
    else:
        return 0.450 - fourth_slg  # Return a penalty based on how far below .450 it is
    
def proper_fifth_hitter(L):
    lineup = L['lineup']

    # Ensure the fifth hitter (index 4) has a low strikeout percentage and a high contact rate
    fifth_hitter = lineup[4]
    try:
        k_percent = api.get_stats(fifth_hitter['name'], 'K%')
        contact_rate = api.get_stats(fifth_hitter['name'], 'Contact%')
    except (ValueError, KeyError):
        return 1  # Penalize if stats are missing

    # Define thresholds
    MAX_K_PERCENT = 0.20      # 20% strikeout rate or lower is good
    MIN_CONTACT_RATE = 0.78   # 78% contact rate or higher is good

    if k_percent <= MAX_K_PERCENT and contact_rate >= MIN_CONTACT_RATE:
        return 0
    else:
        score = (max(0, k_percent - MAX_K_PERCENT) + max(0, MIN_CONTACT_RATE - contact_rate)) * 10
        return 1 if score >= 1 else score  # Return a penalty based on how far off the thresholds
