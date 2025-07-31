"""
File name: main.py
Description: Contains the scoring functions for the MLB lineup optimization problem and the agents to alter the lineup evolutions.
"""

import copy
from api import MLBStatsAPI
import random as rnd
from evo import Evo
import json
from profiler import Profiler, profile

api = MLBStatsAPI(update=True)

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
    
    return round(penalty, 3)

def best_nine(L):
    """
    Objective function: Best Nine by OPS

    Scores the solution based on whether each lineup player has a higher OPS than any available bench player.
    Penalty is the sum of (bench OPS - lineup OPS) for each lineup spot where a bench player is better.
    Score of 0 means every lineup player is better than all bench players by OPS.
    """

    lineup = L['lineup']
    bench = L.get('available_roster', [])

    if not bench or len(lineup) != 9:
        return 0.0

    penalty = 0.0
    for player in lineup:
        try:
            lineup_ops = api.get_stats(player['name'], 'OPS')
        except (ValueError, KeyError):
            continue
        for bench_player in bench:
            try:
                bench_ops = api.get_stats(bench_player['name'], 'OPS')
                if bench_ops > lineup_ops:
                    penalty += bench_ops - lineup_ops
            except (ValueError, KeyError):
                continue

    return round(penalty, 3)

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

@profile
def main():
    # Create our Evo instance
    E = Evo()

    # register our objectives
    #E.add_objective("ba_unsorted", ba_unsorted)
    E.add_objective("proper_leadoff", proper_leadoff)
    E.add_objective("run_production_cascade", run_production_cascade)
    E.add_objective("best_nine", best_nine)

    # register agents
    E.add_agent("swapper", swapper, k=1)
    E.add_agent("wasted_obp_agent", wasted_obp_agent, k=1)
    E.add_agent("wasted_slg_agent", wasted_slg_agent, k=1)
    E.add_agent("better_bench_agent", better_bench_agent, k=1)

    # Initialize a starting solution
    # Example: New York Mets lineup against Zack Wheeler, right-handed pitcher, at Citi Field
    sol = api.init_sol('New York Mets', opp_pitcher='Zack Wheeler', p_throws='R', ballpark='Citi Field', weather='Clear')
    with open("initial_solution.json", "w") as f:
        json.dump(sol, f, indent=2)

    # Add the initial solution to the population
    E.add_solution(sol)
    print(E)

    # Evolve the population for a specified time limit
    E.evolve(time_limit=180)
    print(E)

    # Summarize the final population and save the best solution
    E.summarize()
    best_solution = E.get_best_solution()
    with open("best_solution.json", "w") as f:
        json.dump(best_solution, f, indent=2)

main()
Profiler.report()  # Report profiling results at the end



