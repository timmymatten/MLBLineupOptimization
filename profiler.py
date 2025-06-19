"""
A performance profiler using decorators
When we tage a function with the @profile tage, it will keep track of how often
that function is called and total accumulated run time and average run time per call.
This will help us identify performance bottlenecks in our code

"""
import time
from collections import defaultdict


def profile(f):
    """ Convenience function to make profile tag simpler"""
    return Profiler.profile(f)

class Profiler:
    """ Our profiler class"""
    calls = defaultdict(int) # function name --> number of calls of that function
    time = defaultdict(float) # function name --> total accumulated run time

    @staticmethod
    def profile(f):
        """decorator"""
        def wrapper(*args, **kwargs):

            fname = f.__name__ # there may be a more robust way of getting the name
            start = time.time_ns()

            val = f(*args, **kwargs)

            end = time.time_ns()
            elapsed = (end - start) / 10 ** 9

            # update profiler data
            Profiler.calls[fname] += 1
            Profiler.time[fname] += elapsed

            return val

        return wrapper

    @staticmethod
    def report():
        """ Summarize # calls, total runtime, and time/call for each function """
        print("Function         Calls           TotSec          Sec/Call")
        for name, num in Profiler.calls.items():
            sec = Profiler.time[name]
            print(f'{name:20s} {num:6d} {sec:10.6f} {sec / num:10.6f}')




