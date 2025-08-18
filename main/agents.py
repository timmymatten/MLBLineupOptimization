import copy
from api import MLBStatsAPI
import random as rnd
from profiler import profile

api = MLBStatsAPI()

@profile
def swapper(solutions):
    if not solutions:
        return {}
    sol = copy.deepcopy(solutions[0])
    L = sol['lineup']
    i = rnd.randrange(0, len(L))
    j = rnd.randrange(0, len(L))
    L[i], L[j] = L[j], L[i]
    sol['lineup'] = L
    return sol

@profile
def better_bench_agent(solutions):
    """
    Agent: Better Bench Substitution

    Identifies lineup players who can be replaced by bench players with higher OPS
    that can play the same defensive position. This agent helps optimize the lineup
    by utilizing the full roster depth.

    Args:
        solutions: List of solution dicts (each with 'lineup' and 'available_roster' keys)

    Returns:
        Modified solution with improved lineup through bench substitution
    """
    if not solutions:
        return {}

    # Deep copy to avoid mutating the original solution
    sol = copy.deepcopy(solutions[0])
    lineup = sol['lineup']
    bench = sol['available_roster']

    if len(lineup) != 9 or not bench:
        return sol

    # Find substitution opportunities
    substitution_opportunities = []
    
    for lineup_idx, lineup_player in enumerate(lineup):
        if not lineup_player.get('name'):  # Skip empty lineup spots
            continue
            
        try:
            lineup_ops = api.get_stats(lineup_player['name'], 'OPS')
        except (ValueError, KeyError):
            continue  # Skip if we can't get stats for this player
        
        # Find bench players who can play this position and have better OPS
        current_position = lineup_player.get('position_code')
        
        for bench_idx, bench_player in enumerate(bench):
            if not bench_player.get('name'):  # Skip empty bench spots
                continue
                
            # Check if bench player can play the required position
            if bench_player.get('position_code') != current_position:
                continue
                
            try:
                bench_ops = api.get_stats(bench_player['name'], 'OPS')
                
                # Check if bench player is significantly better (threshold to avoid marginal swaps)
                if bench_ops > lineup_ops + 0.025:  # 25 point OPS improvement threshold
                    improvement = bench_ops - lineup_ops
                    substitution_opportunities.append({
                        'lineup_idx': lineup_idx,
                        'bench_idx': bench_idx,
                        'improvement': improvement,
                        'lineup_player': lineup_player,
                        'bench_player': bench_player
                    })
            except (ValueError, KeyError):
                continue  # Skip if we can't get stats for bench player

    # If no good substitutions found, return original solution
    if not substitution_opportunities:
        return sol

    # Sort by improvement and pick the best substitution
    # This ensures we make the most impactful swap
    best_substitution = max(substitution_opportunities, key=lambda x: x['improvement'])
    
    lineup_idx = best_substitution['lineup_idx']
    bench_idx = best_substitution['bench_idx']
    
    # Create the new bench player entry (formerly in lineup)
    demoted_player = dict(lineup[lineup_idx])
    demoted_player['defensive_position'] = 'Bench'
    
    # Create the new lineup player entry (formerly on bench)
    promoted_player = dict(bench[bench_idx])
    promoted_player['defensive_position'] = lineup[lineup_idx]['defensive_position']
    
    # Make the swap
    lineup[lineup_idx] = promoted_player
    bench[bench_idx] = demoted_player
    
    # Update the solution
    sol['lineup'] = lineup
    sol['available_roster'] = bench
    
    return sol

@profile
def wasted_obp_agent(solutions):
    """
    Agent: Fix Wasted OBP

    Finds high OBP players followed by low SLG players and swaps the low SLG player
    with a better power hitter from the lineup to improve cascade synergy.

    Args:
        solutions: List of solution dicts (each with a 'lineup' key)

    Returns:
        Modified lineup with improved OBP→SLG cascade
    """
    if not solutions:
        return {}

    # Deep copy to avoid mutating the original solution
    sol = copy.deepcopy(solutions[0])
    lineup = sol['lineup']

    if len(lineup) != 9:
        return sol

    # Find all OBP players in top half (positions 0-3 get higher OBP rankings)
    obp_values = [(i, api.get_stats(lineup[i]['name'], 'OBP')) for i in range(9)]
    obp_sorted = sorted(obp_values, key=lambda x: x[1], reverse=True)
    high_obp_positions = {pos for pos, _ in obp_sorted[:4]}  # Top 4 OBP players

    # Find wasted OBP situations: high OBP followed by low SLG
    wasted_situations = []
    for pos in high_obp_positions:
        next_pos = (pos + 1) % 9
        next_slg = api.get_stats(lineup[next_pos]['name'], 'SLG')
        if next_slg < 0.4:  # Low SLG threshold
            wasted_situations.append((pos, next_pos))

    if not wasted_situations:
        return sol

    # Pick a random wasted situation to fix
    obp_pos, weak_slg_pos = rnd.choice(wasted_situations)
    weak_slg = api.get_stats(lineup[weak_slg_pos]['name'], 'SLG')

    # Find someone else in the lineup with better SLG to swap in
    better_slg_candidates = []
    for i in range(9):
        if i != weak_slg_pos and api.get_stats(lineup[i]['name'], 'SLG') > weak_slg + 0.05:
            better_slg_candidates.append(i)

    if better_slg_candidates:
        swap_with = rnd.choice(better_slg_candidates)
        lineup[weak_slg_pos], lineup[swap_with] = lineup[swap_with], lineup[weak_slg_pos]

    # Return the modified lineup (as a list of player dicts)
    sol['lineup'] = lineup
    return sol

@profile
def wasted_slg_agent(solutions):
    """
    Agent: Fix Wasted SLG

    Finds high SLG players preceded by low OBP players and swaps the low OBP player
    with a better table-setter from the lineup to improve cascade synergy.

    Args:
        solutions: List of solution dicts (each with a 'lineup' key)

    Returns:
        Modified lineup with improved OBP→SLG cascade
    """
    if not solutions:
        return {}

    # Deep copy to avoid mutating the original solution
    sol = copy.deepcopy(solutions[0])
    lineup = sol['lineup']

    if len(lineup) != 9:
        return sol

    # Find all SLG players in top half
    slg_values = [(i, api.get_stats(lineup[i]['name'], 'SLG')) for i in range(9)]
    slg_sorted = sorted(slg_values, key=lambda x: x[1], reverse=True)
    high_slg_positions = {pos for pos, _ in slg_sorted[:4]}  # Top 4 SLG players

    # Find wasted SLG situations: low OBP before high SLG
    wasted_situations = []
    for slg_pos in high_slg_positions:
        prev_pos = (slg_pos - 1) % 9
        prev_obp = api.get_stats(lineup[prev_pos]['name'], 'OBP')
        if prev_obp < 0.32:  # Low OBP threshold
            wasted_situations.append((prev_pos, slg_pos))

    if not wasted_situations:
        return sol

    # Pick a random wasted situation to fix
    weak_obp_pos, slg_pos = rnd.choice(wasted_situations)
    weak_obp = api.get_stats(lineup[weak_obp_pos]['name'], 'OBP')

    # Find someone else in the lineup with better OBP to swap in
    better_obp_candidates = []
    for i in range(9):
        if i != weak_obp_pos and api.get_stats(lineup[i]['name'], 'OBP') > weak_obp + 0.05:
            better_obp_candidates.append(i)

    if better_obp_candidates:
        swap_with = rnd.choice(better_obp_candidates)
        lineup[weak_obp_pos], lineup[swap_with] = lineup[swap_with], lineup[weak_obp_pos]

    # Return the modified lineup (as a list of player dicts)
    sol['lineup'] = lineup
    return sol

def leadoff_agent(solutions):
    """
    Agent: Leadoff Hitter Optimization

    Ensures the leadoff hitter has a high enough OBP to set the tone for the lineup.
    If not, it replaces the leadoff hitter with a better candidate from the roster.

    Args:
        solutions: List of solution dicts (each with a 'lineup' key)

    Returns:
        Modified solution with optimized leadoff hitter
    """
    if not solutions:
        return {}

    sol = copy.deepcopy(solutions[0])
    lineup = sol['lineup']

    if len(lineup) != 9:
        return sol

    leadoff_hitter = lineup[0]
    leadoff_obp = api.get_stats(leadoff_hitter['name'], 'OBP')

    # Check if the leadoff hitter has a high enough OBP
    if leadoff_obp >= 0.350:  # Example threshold for a good leadoff hitter
        return sol  # No change needed

    # Find a better candidate from the roster
    best_candidate = None
    best_obp = 0.0

    for player in sol.get('available_roster', []):
        if player['name'] == leadoff_hitter['name']:
            continue  # Skip current leadoff hitter
        try:
            player_obp = api.get_stats(player['name'], 'OBP')
            if player_obp > best_obp:
                best_obp = player_obp
                best_candidate = player
        except (ValueError, KeyError):
            continue  # Skip players with missing stats

    if best_candidate and best_obp > leadoff_obp:
        # Replace the leadoff hitter with the better candidate
        lineup[0] = best_candidate

    sol['lineup'] = lineup
    return sol

def best_hitter_agent(solutions):
    """
    Agent: Best Hitter Optimization

    Ensures the 2nd spot in the lineup is occupied by a hitter whose sum of wOBA, wRC+, and OPS exceeds 180.
    If not, it swaps in the best available hitter meeting this criterion.

    Args:
        solutions: List of solution dicts (each with a 'lineup' key)

    Returns:
        Modified solution with qualified hitter in the 2nd spot
    """
    if not solutions:
        return {}

    sol = copy.deepcopy(solutions[0])
    lineup = sol['lineup']

    if len(lineup) != 9:
        return sol

    # Compute score for each player: wOBA + wRC+ + OPS
    player_scores = []
    for idx, player in enumerate(lineup):
        try:
            woba = api.get_stats(player['name'], 'WOBA') * 100
            wrc_plus = api.get_stats(player['name'], 'WRC')
            ops = api.get_stats(player['name'], 'OPS') * 100
            score = woba + wrc_plus + ops
            player_scores.append((idx, player, score))
        except (ValueError, KeyError):
            continue

    # Check if the 2nd spot meets the threshold
    second_idx = 1
    second_score = None
    for idx, player, score in player_scores:
        if idx == second_idx:
            second_score = score
            break

    if second_score is not None and second_score > 180:
        return sol  # No change needed

    # Find the best available hitter with score > 180
    qualified = [(idx, player, score) for idx, player, score in player_scores if score > 180 and idx != second_idx]
    if not qualified:
        return sol  # No qualified hitter to swap in

    # Pick the best qualified hitter
    best_idx, best_player, best_score = max(qualified, key=lambda x: x[2])

    # Swap into the 2nd spot
    lineup[second_idx], lineup[best_idx] = lineup[best_idx], lineup[second_idx]

    sol['lineup'] = lineup
    return sol
