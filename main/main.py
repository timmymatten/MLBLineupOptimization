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
from agents import swapper, better_bench_agent, wasted_obp_agent, wasted_slg_agent
from objectives import ba_unsorted, proper_leadoff, run_production_cascade, best_nine

api = MLBStatsAPI()

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
    with open("results/initial_solution.json", "w") as f:
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
    with open("results/best_solution.json", "w") as f:
        json.dump(best_solution, f, indent=2)
    E.get_scores_chart()

main()
Profiler.report()  # Report profiling results at the end



