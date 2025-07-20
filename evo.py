"""
File: evo.py
Description: An evolutionary computing framework for solving
multi-objective optimization problems

Used in this project to evolve Major League Baseball lineups.

Finds pareto-optimal solutions revealing tradeoffs between different
objectives

"""
import copy
import random as rnd
import time
from functools import reduce

import numpy as np
import pandas as pd
from profiler import Profiler, profile


class Evo:
    def __init__(self):
        """ Constructor """
        self.pop = {} # scores (tuple) --> solution
        self.unreduced_pop = {}
        self.objectives = {} # name --> obj function (goals)
        self.agents = {} # agents: name --> (operator, num_solutions_input)

    def add_objective(self, name, f):
        """ Add an objective (fitness function) to the framework """
        self.objectives[name] = f

    def add_agent(self, name, op, k=1):
        """ Register a named agent to the framework
        the operator (op) defines what the agent does - how it changes the solution
        the k value is the number of INPUT solutions from the current population """
        self.agents[name] = (op, k)

    def get_random_solutions(self, k=1):
        if len(self.pop) == 0:
            return []
        else:
            all_solutions = list(self.pop.values())
            return [copy.deepcopy(rnd.choice(all_solutions)) for _ in range(k)]

    def add_solution(self, sol):
        """ ((obj1, score1), (obj2, score2), ... (objn, scoren)) """
        scores = tuple((name, f(sol)) for name, f in self.objectives.items())
        penalty = sum(score for _, score in scores)
        entry = {"scores": dict(scores), "solution": sol, "penalty": penalty}

        self.pop[scores] = sol
        self.unreduced_pop[scores] = entry

    def run_agent(self, name):
        """ Execute a named agent """
        op, k = self.agents[name]
        picks = self.get_random_solutions(k)
        new_solution = op(picks)
        self.add_solution(new_solution)

    @staticmethod
    def dominates(q, p):
        pscores = np.array([score for name, score in p])
        qscores = np.array([score for name, score in q])
        score_diffs = qscores - pscores
        return min(score_diffs) >= 0 and max(score_diffs) > 0

    @staticmethod
    def reduce_nds(S, p):
        return S - {q for q in S if Evo.dominates(q, p)}

    def remove_dominated(self):
        nds = reduce(Evo.reduce_nds, self.pop.keys(), self.pop.keys())
        self.pop = {k: self.pop[k] for k in nds}

    def summarize(self):
        """
            Summarizes the final population into a DataFrame.
            Each row contains the score values and the total penalty.
            """
        data = []
        for entry in self.unreduced_pop.values():
            row = entry["scores"].copy()
            row["penalty"] = entry["penalty"]
            data.append(row)

        df = pd.DataFrame(data)
        df.sort_values("penalty", inplace=True)
        df.to_csv('timmatten_summary.csv', index=False)

    def get_best_solution(self):
        if not self.unreduced_pop:
            return None
        best_entry = min(self.unreduced_pop.values(), key=lambda x: x["penalty"])
        return best_entry["solution"]

    @profile
    def evolve(self, n=1, dom=50, time_limit=300):
        """ Run n implications of agents """
        agent_names = list(self.agents.keys())

        start = time.time()
        i = 0

        while time.time() - start < time_limit:
            pick = rnd.choice(agent_names)
            self.run_agent(pick)

            if i % dom == 0:
                self.remove_dominated()
            i += 1

        print(self)
        self.remove_dominated()

    def __str__(self):
        """ Displaying the contents of the population """
        rslt = ""
        for scores, sol in self.pop.items():
            rslt += str(dict(scores)) + ":\t"+str(sol)+"\n"
        return rslt




