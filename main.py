"""
File name: main.py
Description: Contains the scoring functions for the MLB lineup optimization problem and the agents to alter the lineup evolutions.
"""

import copy
from api import MLBStatsAPI
import random as rnd
from evo import Evo

api = MLBStatsAPI()

def ba_unsorted(L):
    return round(sum(
        api.get_stats(y, 'AVG') - api.get_stats(x, 'AVG')
        for x, y in zip(L, L[1:])
        if api.get_stats(x, 'AVG') < api.get_stats(y, 'AVG')
    ), 3)

def proper_leadoff(L):
    # Check if the first player is a leadoff hitter
    leadoff_hitter = L[0]
    leadoff_obp = api.get_stats(leadoff_hitter, 'OBP')
    
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
    if len(L) != 10:
        raise ValueError("Lineup must contain exactly 9 players")
    
    # Calculate the actual cascade score
    actual_cascade_score = 0.0
    
    # Calculate cascade for positions 1-8 → 2-9
    for i in range(8):
        current_hitter_obp = api.get_stats(L[i], 'OBP')
        next_hitter_slg = api.get_stats(L[i + 1], 'SLG')
        actual_cascade_score += current_hitter_obp * next_hitter_slg
    
    # Handle wraparound: 9th hitter sets up 1st hitter for next inning
    ninth_hitter_obp = api.get_stats(L[8], 'OBP')
    first_hitter_slg = api.get_stats(L[0], 'SLG')
    actual_cascade_score += ninth_hitter_obp * first_hitter_slg
    
    # Calculate theoretical maximum possible score for this set of players
    obp_values = [api.get_stats(player, 'OBP') for player in L]
    slg_values = [api.get_stats(player, 'SLG') for player in L]
    
    # Maximum possible cascade would be highest OBPs followed by highest SLGs
    obp_sorted = sorted(obp_values, reverse=True)
    slg_sorted = sorted(slg_values, reverse=True)
    
    max_possible_score = sum(obp_sorted[i] * slg_sorted[i] for i in range(9))
    
    # Return penalty: how far we are from the theoretical maximum
    penalty = max_possible_score - actual_cascade_score
    
    return round(penalty, 3)



def swapper(solutions):
    L = solutions[0]
    i = rnd.randrange(0, len(L))
    j = rnd.randrange(0, len(L))
    L[i], L[j] = L[j], L[i]
    return L

def wasted_obp_agent(solutions):
    """
    Agent: Fix Wasted OBP
    
    Finds high OBP players followed by low SLG players and swaps the low SLG player
    with a better power hitter to improve cascade synergy.
    
    Args:
        solutions: List of lineup solutions from population
        
    Returns:
        Modified lineup with improved OBP→SLG cascade
    """
    if not solutions:
        return []
    
    lineup = copy.deepcopy(solutions[0])
    
    if len(lineup) != 10:
        return lineup
    
    # Find all OBP players in top half (positions 0-3 get higher OBP rankings)
    obp_values = [(i, api.get_stats(lineup[i], 'OBP')) for i in range(9)]
    obp_sorted = sorted(obp_values, key=lambda x: x[1], reverse=True)
    high_obp_positions = {pos for pos, _ in obp_sorted[:4]}  # Top 4 OBP players
    
    # Find wasted OBP situations: high OBP followed by low SLG
    wasted_situations = []
    for pos in high_obp_positions:
        next_pos = (pos + 1) % 9
        next_slg = api.get_stats(lineup[next_pos], 'SLG')
        if next_slg < 0.4:  # Low SLG threshold
            wasted_situations.append((pos, next_pos))
    
    if not wasted_situations:
        return lineup
    
    # Pick a random wasted situation to fix
    obp_pos, weak_slg_pos = rnd.choice(wasted_situations)
    weak_slg = api.get_stats(lineup[weak_slg_pos], 'SLG')
    
    # Find someone with better SLG to swap in
    better_slg_candidates = []
    for i in range(9):
        if i != weak_slg_pos and api.get_stats(lineup[i], 'SLG') > weak_slg + 0.05:
            better_slg_candidates.append(i)
    
    if better_slg_candidates:
        swap_with = rnd.choice(better_slg_candidates)
        lineup[weak_slg_pos], lineup[swap_with] = lineup[swap_with], lineup[weak_slg_pos]
    
    return lineup

def wasted_slg_agent(solutions):
    """
    Agent: Fix Wasted SLG
    
    Finds high SLG players preceded by low OBP players and swaps the low OBP player
    with a better table-setter to improve cascade synergy.
    
    Args:
        solutions: List of lineup solutions from population
        
    Returns:
        Modified lineup with improved OBP→SLG cascade
    """
    if not solutions:
        return []
    
    lineup = copy.deepcopy(solutions[0])
    
    if len(lineup) != 10:
        return lineup
    
    # Find all SLG players in top half
    slg_values = [(i, api.get_stats(lineup[i], 'SLG')) for i in range(9)]
    slg_sorted = sorted(slg_values, key=lambda x: x[1], reverse=True)
    high_slg_positions = {pos for pos, _ in slg_sorted[:4]}  # Top 4 SLG players
    
    # Find wasted SLG situations: low OBP before high SLG
    wasted_situations = []
    for slg_pos in high_slg_positions:
        prev_pos = (slg_pos - 1) % 9
        prev_obp = api.get_stats(lineup[prev_pos], 'OBP')
        if prev_obp < 0.32:  # Low OBP threshold
            wasted_situations.append((prev_pos, slg_pos))
    
    if not wasted_situations:
        return lineup
    
    # Pick a random wasted situation to fix
    weak_obp_pos, slg_pos = rnd.choice(wasted_situations)
    weak_obp = api.get_stats(lineup[weak_obp_pos], 'OBP')
    
    # Find someone with better OBP to swap in
    better_obp_candidates = []
    for i in range(9):
        if i != weak_obp_pos and api.get_stats(lineup[i], 'OBP') > weak_obp + 0.05:
            better_obp_candidates.append(i)
    
    if better_obp_candidates:
        swap_with = rnd.choice(better_obp_candidates)
        lineup[weak_obp_pos], lineup[swap_with] = lineup[swap_with], lineup[weak_obp_pos]
    
    return lineup

def main():
    # Create our Evo instance
    E = Evo()

    # register our objectives
    #E.add_objective("ba_unsorted", ba_unsorted)
    E.add_objective("proper_leadoff", proper_leadoff)
    E.add_objective("run_production_cascade", run_production_cascade)

    # register agents
    E.add_agent("swapper", swapper, k=1)
    E.add_agent("wasted_obp_agent", wasted_obp_agent, k=1)
    E.add_agent("wasted_slg_agent", wasted_slg_agent, k=1)

    # Add an initial solution (1-9: lineup, 10: opposing pitcher)
    sol = ['Brandon Nimmo',
           'Francisco Lindor',
           'Juan Soto',
           'Pete Alonso',
           'Jeff McNeil',
           'Mark Vientos',
           'Brett Baty',
           'Luisangel Acuna',
           'Hayden Senger',
           'Zack Wheeler'] # 10 spot for opposing pitcher
    E.add_solution(sol)
    print(E)

    E.evolve(time_limit=180)
    print(E)
    E.summarize()

main()



