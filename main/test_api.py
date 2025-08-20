import pytest
from api import MLBStatsAPI
from profiler import profile

api = MLBStatsAPI(update=True)

print(api.get_pitcher_vs_hitter_stats("Pete Alonso", "Zack Wheeler", "OPS"))