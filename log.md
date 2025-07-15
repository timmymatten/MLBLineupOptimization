# LOG

## July 1, 2025 (Day 1)

- RE24
- wOBA
- wRC
- wRAA

1. OBP
2. Best Overall
3. Next Best Hitter (some slugging, solid OBP)
4. Best power hitter
5. Ball in play, low k%
6. Next best hitter
7. Least Productive
8. Least Productive
9. Least Productive

### Potential iterations

1. Overal stats
2. Stats against specific team/handed P
3. More specific like the exact pitcher etc.

## July 2, 2025 (Day 2)

- planned organization
- scraped updated rosters with mlb stats api

## July 3, 2025 (Day 2)

- reset thinking about lineup input
- input each of the 9 players in the lineup
- implement roster generated lineups later

## July 10, 2025 (Day 3)

- comlpeted basic sort by BA lineup optimizer

- after several iterations of stat retrieving functions, settled on batting_stats() from pybaseball
- going to start objective functions for real optimization next day

## July 13, 2025 (Day 4)

- completed two new and helpful objectives
- run production cascade
- proper leadoff hitter (had to alter OBP threshold to .350 from .300)
- best model yet, creating what looks to be a real optimal lineup

## July 14, 2025 (Day 5)

- thinking of changing the solution format to a dictionary to accomodate adding the opposing pitcher

```python
solution = {
    'lineup': [
        {'name': 'Brandon Nimmo', 'position': 'CF', 'batting_side': 'L'},
        {'name': 'Francisco Lindor', 'position': 'SS', 'batting_side': 'S'},
        # ... 7 more players
    ],
    'opposing_pitcher': {
        'name': 'Jacob deGrom',
        'throws': 'R',
        'era': 2.54,
        'whip': 1.08
    },
    'available_roster': [
        {'name': 'Eduardo Escobar', 'position': '3B', 'batting_side': 'S'},
        # ... rest of available players
    ],
    'game_context': {
        'ballpark': 'Citi Field',
        'weather': 'Clear',
        'inning': 1,
        'situation': 'standard'
    }
}
```

- could do the above to accomodate entire roster optimization in the future
- need to make get roster function in api.py
- it will take in the team name and the opposing pitcher and produce a dictionary similar to the one above
