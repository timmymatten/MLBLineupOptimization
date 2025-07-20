# MLB Lineup Optimization Project

A multi-objective evolutionary computing framework for optimizing Major League Baseball starting lineups using real MLB data and advanced sabermetric principles.

## Project Overview

This project uses evolutionary algorithms to find optimal MLB starting lineups by balancing multiple competing objectives. Rather than simply sorting players by individual statistics, the system considers strategic lineup construction principles like run production cascades, proper leadoff characteristics, and player synergies.

## Key Features

- **Multi-Objective Optimization**: Uses Pareto-optimal solutions to reveal tradeoffs between different lineup objectives
- **Real MLB Data Integration**: Pulls current roster data from MLB's official Stats API
- **Advanced Sabermetrics**: Incorporates modern baseball analytics beyond traditional statistics
- **Evolutionary Framework**: Employs genetic algorithm-inspired agents to evolve lineups over time
- **Performance Profiling**: Built-in performance monitoring to optimize computation efficiency

## Project Structure

```
├── main.py                    # Main execution script with objectives and agents
├── evo.py                     # Evolutionary computing framework
├── api.py                     # MLB Stats API integration and data management
├── profiler.py                # Performance monitoring utilities
├── test_api.py                # API testing and validation
├── best_solution.json         # Output: Optimized lineup result
├── data/                      # Statistical data files
├── logs/                      # Development logs and progress notes
└── ref_test_files/            # Reference test solutions and examples
```

## Core Components

### Objectives (Fitness Functions)

1. **Run Production Cascade**: Measures how well each batter "sets up" the next batter by calculating OBP × SLG synergies between consecutive lineup positions
2. **Proper Leadoff**: Evaluates whether the leadoff hitter has sufficient on-base percentage (≥0.350) for optimal table-setting

### Evolutionary Agents

1. **Swapper**: Randomly exchanges two players in the lineup
2. **Wasted OBP Agent**: Identifies high on-base players followed by low slugging players and optimizes the pairing
3. **Wasted SLG Agent**: Finds high power hitters preceded by poor table-setters and improves the sequence

### Solution Format

Each lineup solution is represented as a comprehensive dictionary containing:

```json
{
  "lineup": [
    {
      "name": "Francisco Lindor",
      "lineup_position": 1,
      "position_code": "6",
      "jersey_number": "12",
      "player_id": 32129,
      "batting_side": "S",
      "defensive_position": "Shortstop"
    }
  ],
  "available_roster": [...],
  "opposing_pitcher": {
    "name": "Zack Wheeler",
    "throws": "R"
  },
  "game_context": {
    "ballpark": "Citi Field",
    "weather": "Clear",
    "inning": 1,
    "situation": "standard"
  }
}
```

## Technical Implementation

- **Language**: Python
- **Key Libraries**: 
  - `requests` for MLB API integration
  - `pandas` for statistical data management
  - `numpy` for numerical computations
  - `pybaseball` for additional baseball statistics
- **Optimization Method**: Non-dominated sorting with Pareto frontier analysis
- **Runtime**: Configurable evolution time (default: 180 seconds)

## Usage

```python
# Initialize the evolutionary framework
E = Evo()

# Add objectives
E.add_objective("proper_leadoff", proper_leadoff)
E.add_objective("run_production_cascade", run_production_cascade)

# Register agents
E.add_agent("swapper", swapper, k=1)
E.add_agent("wasted_obp_agent", wasted_obp_agent, k=1)
E.add_agent("wasted_slg_agent", wasted_slg_agent, k=1)

# Generate initial solution and evolve
sol = api.init_sol('New York Mets', 'Zack Wheeler', 'R', 'Citi Field', 'Clear')
E.add_solution(sol)
E.evolve(time_limit=180)
```

## Current Status

The project has evolved through 8 development iterations, with major milestones including:

- ✅ Basic lineup sorting by batting average
- ✅ Multi-objective optimization framework
- ✅ MLB API integration with roster management
- ✅ Advanced sabermetric objectives (run production cascade)
- ✅ Dictionary-based solution format for comprehensive lineup representation
- ✅ Performance profiling and optimization

## Future Enhancements

- **Platoon Advantages**: Incorporate left/right-handed matchup optimization
- **Bench Integration**: Enable substitutions from available roster players
- **Additional Objectives**: Expand to include defensive positioning, base-running, and situational hitting
- **Historical Validation**: Back-test optimized lineups against actual game results
- **Real-time Integration**: Connect to live game data for in-game optimization

## Academic Context

This project demonstrates the application of evolutionary computing to real-world optimization problems, specifically addressing the complexity of multi-objective decision-making in professional sports analytics. The work bridges computer science, statistics, and sports science domains.

---

*This project is part of ongoing research into multi-objective optimization techniques and their applications in sports analytics.*
