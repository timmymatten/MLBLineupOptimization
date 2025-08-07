"""
File name: main.py
Description: Contains the scoring functions for the MLB lineup optimization problem and the agents to alter the lineup evolutions.
"""

import copy
from api import MLBStatsAPI
from evo import Evo
import json
from profiler import Profiler, profile
from agents import swapper, better_bench_agent, wasted_obp_agent, wasted_slg_agent
from objectives import ba_unsorted, proper_leadoff, run_production_cascade, best_nine
import sys
import time
import threading

api = MLBStatsAPI()

def print_progress_bar(iteration, total, prefix='', suffix='', length=50):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

def show_progress_bar(total_time, interval):
        steps = total_time // interval
        for i in range(steps + 1):
            print_progress_bar(i, steps, prefix='Progress', suffix='Complete', length=40)
            time.sleep(interval)

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
    init_solution = copy.deepcopy(sol)
    E.add_solution(sol)

    print("Evolution progress:")

    total_time = 60  # seconds
    interval = 1      # seconds

    # Start progress bar thread
    progress_thread = threading.Thread(target=show_progress_bar, args=(total_time, interval))
    progress_thread.start()

    # Run evolution
    E.evolve(time_limit=total_time)

    # Wait for progress bar to finish
    progress_thread.join()

    print(E)

    # Summarize the final population and save the best solution
    E.summarize()

    # Get the best solution and save it
    best_solution = E.get_best_solution()
    with open("results/best_solution.json", "w") as f:
        json.dump(best_solution, f, indent=2)

    # Generate charts and document score differences
    E.get_scores_chart()
    E.document_score_differences(init_solution)
    
main()
Profiler.report()  # Report profiling results at the end



