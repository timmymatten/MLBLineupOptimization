# ⚾ MLB Lineup Optimization with Evolutionary Computing

An intelligent system that uses evolutionary computing to optimize Major League Baseball batting lineups by balancing multiple competing sabermetric objectives and strategic positioning principles.

## 🎯 Project Overview

Determining the optimal batting order is one of the most complex strategic decisions in baseball, involving intricate trade-offs between statistical performance, situational matchups, and game theory. This project applies multi-objective evolutionary optimization to find mathematically optimal batting lineups using advanced sabermetrics rather than traditional intuition-based approaches.

## ⚾ The Strategic Foundation

### Batting Order Philosophy
Based on sabermetric research and game theory, the optimal lineup construction follows this strategic framework:

**1st Position - High OBP Leadoff**  
- Primary objective: Get on base to create scoring opportunities
- Key metric: On-Base Percentage (OBP)
- Strategy: Sets the table for power hitters behind them

**2nd Position - Best Overall Hitter**  
- Primary objective: Maximum offensive production in high plate appearance slot
- Key metrics: wOBA (weighted On-Base Average), wRC+ (weighted Runs Created)
- Strategy: Your best hitter gets the most at-bats here

**3rd Position - Secondary Power/Contact**  
- Primary objective: Solid production with good OBP to support cleanup hitter
- Key metrics: Balanced OBP and slugging
- Strategy: Versatile hitter who can drive in runs or set up the cleanup spot

**4th Position - Pure Power**  
- Primary objective: Maximum run production potential
- Key metrics: Slugging percentage, home runs, RBIs
- Strategy: Traditional cleanup hitter for driving in baserunners

**5th Position - Contact/Low Strikeouts**  
- Primary objective: Put ball in play, avoid rally-killing strikeouts
- Key metrics: Low strikeout rate (K%), high contact rate
- Strategy: Keep the line moving, protect runners

**6th Position - Next Best Available**  
- Primary objective: Secondary offensive production
- Strategy: Depth scoring threat

**7th-9th Positions - Least Productive**  
- Primary objective: Minimize offensive black holes
- Strategy: Defensive specialists, pitchers, or weakest offensive players

## 🧬 How the Evolutionary Algorithm Works

The system uses a multi-objective evolutionary approach:

1. **Population Initialization**: Generates random batting lineups as starting solutions
2. **Multi-Objective Evaluation**: Scores each lineup across multiple sabermetric objectives
3. **Evolutionary Operators**: Specialized agents make strategic lineup modifications
4. **Pareto Optimization**: Maintains non-dominated solutions representing different strategic trade-offs
5. **Convergence**: Continues evolution until optimal solutions are found

## 📊 Optimization Objectives

The system optimizes for advanced sabermetric metrics:

### Primary Offensive Metrics
- **RE24 (Run Expectancy)**: Maximizes expected runs based on base-out situations
- **wOBA (weighted On-Base Average)**: Comprehensive offensive value metric
- **wRC (weighted Runs Created)**: Total offensive contribution
- **wRAA (weighted Runs Above Average)**: Performance relative to league average

### Strategic Positioning Metrics
- **OBP Optimization**: Ensures high on-base players are positioned for maximum impact
- **Strikeout Minimization**: Reduces rally-killing strikeouts in key situations
- **Situational Performance**: Optimizes based on specific game scenarios

### Advanced Considerations
- **Platoon Advantages**: Left/right-handed batter vs. pitcher matchups
- **Clutch Performance**: Performance in high-leverage situations
- **Speed Utilization**: Optimal positioning for stolen base opportunities

## 🗂️ Data Integration

The system can operate at multiple levels of sophistication:

### Level 1: Overall Statistics
- Season-long performance metrics
- General offensive capabilities
- Basic lineup optimization

### Level 2: Matchup-Specific Analysis
- Performance vs. left-handed/right-handed pitching
- Team-specific historical performance
- Ballpark factor adjustments

### Level 3: Pitcher-Specific Optimization
- Individual pitcher matchup data
- Pitch type effectiveness
- Historical head-to-head performance

## 🤖 Evolutionary Agents

The system employs specialized agents for lineup modifications:

- **Position Swap Agent**: Exchanges players between lineup spots
- **OBP Optimizer Agent**: Moves high OBP players toward leadoff spots
- **Power Positioning Agent**: Optimizes power hitters in RBI positions
- **Matchup Agent**: Adjusts lineup based on opposing pitcher handedness
- **Situational Agent**: Modifies order based on game situation requirements

## 📈 Solution Types

The evolutionary process produces multiple optimal lineup strategies:

- **Table-Setting Lineups**: Maximize on-base opportunities for power hitters
- **Power-Concentrated Lineups**: Stack best hitters in high-impact positions
- **Balanced Lineups**: Distribute offensive production throughout the order
- **Matchup-Optimized Lineups**: Exploit specific pitcher/team weaknesses
- **Small-Ball Lineups**: Emphasize speed, contact, and manufacturing runs

## 🎲 Implementation Architecture

Built on the evolutionary computing framework (`evo.py`):

```python
# Core optimization engine
E = Evo()

# Sabermetric objectives
E.add_objective("re24_maximize", maximize_run_expectancy)
E.add_objective("woba_optimize", optimize_weighted_obp)
E.add_objective("strikeout_minimize", minimize_strikeouts)

# Strategic agents
E.add_agent("position_optimizer", optimize_batting_positions)
E.add_agent("matchup_agent", exploit_pitcher_matchups)
E.add_agent("obp_leadoff_agent", optimize_leadoff_effectiveness)
```

## 🏆 Results and Analysis

The system generates Pareto-optimal solutions representing different strategic philosophies, allowing managers to:

- Compare traditional vs. sabermetric-optimized lineups
- Analyze trade-offs between different offensive strategies
- Optimize for specific game situations or opponent matchups
- Make data-driven decisions about batting order construction

## 🚀 Future Enhancements

- Real-time lineup optimization during games
- Integration with pitch-by-pitch data
- Defensive positioning optimization
- In-game substitution strategy
- Weather and ballpark factor integration

---

*This project demonstrates the power of evolutionary computing in solving complex multi-objective optimization problems in sports analytics, moving beyond traditional baseball wisdom to mathematically optimal solutions.*