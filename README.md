# ⚾ MLB Lineup Optimization with Evolutionary Computing

An intelligent system that uses evolutionary computing to optimize Major League Baseball batting lineups by balancing multiple competing objectives.

## 🎯 Project Overview

Determining the optimal batting order is one of the most strategic decisions in baseball. This project applies multi-objective evolutionary optimization to find the best possible batting lineups, considering multiple statistical factors simultaneously rather than relying on traditional intuition-based approaches.

## ⚾ The Problem

Building an optimal batting lineup involves complex trade-offs:
- Do you put your best hitter first or fourth?
- How do you balance power vs. contact hitters?
- Where do you place fast runners for stolen base opportunities?
- How do you optimize against left-handed vs. right-handed pitching?

Traditional approaches rely on manager intuition or simple rules of thumb. This system finds mathematically optimal solutions.

## 🧬 How It Works

The evolutionary algorithm:
1. **Starts** with random batting lineups
2. **Evaluates** each lineup across multiple performance objectives
3. **Evolves** lineups using specialized agents that make strategic changes
4. **Keeps** the best solutions (Pareto-optimal) that represent different trade-offs
5. **Continues** improving until the best possible lineups are found

## 📊 Optimization Objectives

The system optimizes for:

**🏃 Expected Runs**: Maximize run scoring potential using advanced sabermetrics  
**⚡ Low Strikeouts**: Minimize lineup's overall strikeout rate  
**👥 On-Base Percentage**: Maximize getting runners on base  
**🚫 Avoid Double Plays**: Minimize rally-killing double plays  
**🤝 Platoon Advantage**: Optimize left/right-handed batter vs. pitcher matchups  
**💨 Speed Placement**: Put fast runners in positions where they can steal bases

## 🗂️ Data Sources

Uses real MLB player statistics:
- Batting averages, on-base percentage, slugging
- Strikeout and walk rates
- Performance splits vs. left/right-handed pitching
- Sprint speed and stolen base success rates
- Advanced metrics like wOBA and wRC+

## 📈 Results

The system finds multiple optimal lineups representing different strategies:
- **Power-focused** lineups that maximize run production
- **Contact-heavy** lineups that minimize strikeouts
- **Speed-optimized** lineups for stolen base opportunities
- **Balanced** lineups with good performance across all areas

