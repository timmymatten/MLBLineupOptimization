# MLB Lineup Optimization Project

A multi-objective evolutionary computing framework for optimizing Major League Baseball starting lineups using real MLB data and advanced sabermetric principles.

## Project Overview

[Daily Development Log](log.md)

This project uses evolutionary algorithms to find optimal MLB starting lineups by balancing multiple competing objectives. Rather than simply sorting players by individual statistics, the system considers strategic lineup construction principles like run production cascades, proper leadoff characteristics, player synergies, and position-specific optimization.

## Key Features

- **Multi-Objective Optimization**: Uses Pareto-optimal solutions to reveal tradeoffs between different lineup objectives
- **Real MLB Data Integration**: Pulls current roster data from MLB's official Stats API and FanGraphs statistics
- **Advanced Sabermetrics**: Incorporates modern baseball analytics including wOBA, wRC+, OPS, and contact rates
- **Evolutionary Framework**: Employs genetic algorithm-inspired agents to evolve lineups over time
- **Bench Integration**: Considers full roster depth with bench substitution optimization
- **Performance Profiling**: Built-in performance monitoring to optimize computation efficiency
- **Progress Tracking**: Real-time evolution progress visualization
- **Results Documentation**: Comprehensive scoring analysis and improvement tracking

### Batting Order Philosophy

Based on sabermetric research and game theory, the optimal lineup construction follows this strategic framework:

**1st Position - High OBP Leadoff**  
- Primary objective: Get on base to create scoring opportunities (OBP ≥ 0.310)
- Key metrics: On-Base Percentage (OBP)
- Strategy: Sets the table for power hitters behind them

**2nd Position - Best Overall Hitter**  
- Primary objective: Maximum offensive production in high plate appearance slot
- Key metrics: Combined score of wOBA + wRC+ ≥ 140
- Strategy: Your best hitter gets the most at-bats here

**3rd Position - Balanced Contact/Power**  
- Primary objective: Solid production with balanced OBP and slugging
- Key metrics: OBP ≥ 0.330, SLG ≥ 0.400, difference ≤ 0.070
- Strategy: Versatile hitter who can drive in runs or set up the cleanup spot

**4th Position - Pure Power (Cleanup)**  
- Primary objective: Maximum run production potential
- Key metrics: Top-3 SLG on team or SLG ≥ 0.450
- Strategy: Traditional cleanup hitter for driving in baserunners

**5th Position - Contact/Low Strikeouts**  
- Primary objective: Put ball in play, avoid rally-killing strikeouts
- Key metrics: K% ≤ 20%, Contact% ≥ 78%
- Strategy: Keep the line moving, protect runners

**6th-9th Positions - Depth and Defense**
- Primary objective: Minimize offensive black holes while maintaining defensive integrity
- Strategy: Utilize bench depth and defensive specialists effectively

## Core Components

### Objective Functions (objectives.py)

The system evaluates lineups using seven distinct objectives:

1. **Proper Leadoff** (`proper_leadoff`): Ensures leadoff hitter has sufficient OBP (≥0.310)
2. **Run Production Cascade** (`run_production_cascade`): Measures OBP×SLG synergies between consecutive hitters
3. **Best Nine** (`best_nine`): Position-aware comparison ensuring strongest players are in lineup
4. **Proper Best Hitter** (`proper_best_hitter_second`): Validates 2nd spot has elite combined metrics
5. **Proper Third Hitter** (`proper_third_hitter`): Ensures balanced contact/power in 3-hole
6. **Proper Cleanup Hitter** (`proper_cleanup_hitter`): Validates power production in 4th spot
7. **Proper Fifth Hitter** (`proper_fifth_hitter`): Ensures contact-oriented approach in 5th spot

### Evolutionary Agents (agents.py)

Six specialized agents modify lineups during evolution:

1. **Swapper** (`swapper`): Randomly exchanges two players in batting order
2. **Better Bench Agent** (`better_bench_agent`): Substitutes lineup players with superior bench options at same position
3. **Wasted OBP Agent** (`wasted_obp_agent`): Fixes high-OBP players followed by low-SLG hitters
4. **Wasted SLG Agent** (`wasted_slg_agent`): Addresses high-SLG players preceded by poor table-setters
5. **Leadoff Agent** (`leadoff_agent`): Optimizes leadoff position for maximum OBP
6. **Best Hitter Agent** (`best_hitter_agent`): Ensures elite offensive production in 2nd spot

### Solution Format

Each lineup solution is represented as a comprehensive dictionary:

```json
{
  "lineup": [
    {
      "name": "Aaron Judge",
      "position_code": "9",
      "jersey_number": "99",
      "player_id": 592450,
      "batting_side": "R",
      "defensive_position": "Right Field"
    }
    // ... 8 more players
  ],
  "available_roster": [
    {
      "name": "Giancarlo Stanton",
      "position_code": "10", 
      "jersey_number": "27",
      "player_id": 519317,
      "batting_side": "R",
      "defensive_position": "Bench"
    }
    // ... remaining bench players
  ],
  "opposing_pitcher": {
    "name": "Zack Wheeler",
    "throws": "R"
  },
  "game_context": {
    "ballpark": "Citi Field",
    "weather": "Clear",
    "inning": 1,
    "situation": "standard"
  },
  "team_info": {
    "name": "New York Yankees",
    "team_id": 147
  }
}
```

## Technical Implementation

### Core Technologies
- **Language**: Python 3.8+
- **Key Libraries**: 
  - `requests` for MLB API integration
  - `pandas` for statistical data management  
  - `numpy` for numerical computations
  - `pybaseball` for additional baseball statistics
  - `matplotlib` for visualization
- **Optimization Method**: Non-dominated sorting with Pareto frontier analysis
- **Data Sources**: MLB Stats API, FanGraphs CSV exports

### Performance Optimization
- **Caching System**: Intelligent roster and statistics caching to minimize API calls
- **Profiling**: Built-in function-level performance monitoring with `@profile` decorator
- **Efficient Player Lookup**: Uses `pybaseball.playerid_lookup()` for fast player ID resolution

## Usage

### Basic Execution

```python
from main import main
from api import MLBStatsAPI
from evo import Evo

# Run complete optimization workflow
main()
```

### Custom Optimization

```python
# Initialize the evolutionary framework
E = Evo()

# Add objectives (customize as needed)
E.add_objective("proper_leadoff", proper_leadoff)
E.add_objective("run_production_cascade", run_production_cascade)
E.add_objective("best_nine", best_nine)

# Register agents
E.add_agent("swapper", swapper, k=1)
E.add_agent("better_bench_agent", better_bench_agent, k=1)
E.add_agent("wasted_obp_agent", wasted_obp_agent, k=1)

# Generate initial solution and evolve
api = MLBStatsAPI(update=True)
sol = api.init_sol('New York Yankees', 'Zack Wheeler', 'R', 'Citi Field', 'Clear')
E.add_solution(sol)
E.evolve(time_limit=60)  # 60 second evolution

# Get results
best_solution = E.get_best_solution()
E.summarize()
E.get_scores_chart()
```

### Output Analysis

The system generates comprehensive results:

- **best_solution.json**: Optimized lineup with full player details
- **evolution_scores.csv**: Complete scoring history for all generated solutions
- **score_differences.csv**: Detailed improvement analysis comparing initial vs. final lineups  
- **objective_scores_chart.png**: Visualization of objective function performance
- **Console Output**: Real-time progress bar and evolution statistics

## Development Timeline

The project has evolved through 16 major development iterations:

- ✅ **Days 1-3**: Basic framework and batting average optimization
- ✅ **Days 4-5**: Multi-objective framework with run production cascade
- ✅ **Days 6-9**: Dictionary-based solution format and roster integration
- ✅ **Days 10-11**: Bench player integration and results visualization
- ✅ **Days 12-13**: Performance optimization and progress tracking  
- ✅ **Days 14-15**: Modular architecture with separate agent/objective files
- ✅ **Day 16**: Position-specific optimization and advanced sabermetric objectives

## Current Performance

Based on recent optimization runs, the system consistently achieves:
- **Convergence Time**: 60 seconds for stable solutions
- **Solution Quality**: Multiple Pareto-optimal solutions revealing strategic tradeoffs
- **Improvement Metrics**: Measurable enhancement across all objective functions
- **Processing Speed**: ~1000+ solution evaluations per evolution cycle

## Future Enhancements

### Immediate Priorities
- **Platoon Advantages**: Left/right-handed matchup optimization against specific pitchers
- **Situational Context**: Late-inning, high-leverage, and postseason lineup adjustments
- **Advanced Metrics**: Integration of Statcast data (exit velocity, launch angle, barrel rate)

### Long-term Goals
- **Historical Validation**: Back-testing optimized lineups against actual game results
- **Real-time Integration**: Live game data integration for in-game optimization decisions
- **Machine Learning Enhancement**: Neural network-based objective function learning
- **Multi-team Analysis**: Comparative optimization across different team compositions

## Academic Context

This project demonstrates the application of evolutionary computing to real-world optimization problems in sports analytics. The work bridges multiple disciplines:

- **Computer Science**: Multi-objective optimization, genetic algorithms, performance profiling
- **Statistics**: Sabermetric analysis, regression modeling, data validation
- **Operations Research**: Resource allocation, constraint satisfaction, decision optimization  
- **Sports Science**: Athletic performance modeling, strategic decision-making

The evolutionary approach reveals that optimal lineup construction involves complex tradeoffs that cannot be captured by simple statistical ranking, making this a compelling case study for multi-objective optimization techniques.

---

*This project represents ongoing research into evolutionary computing applications in sports analytics and multi-objective decision-making frameworks.*
