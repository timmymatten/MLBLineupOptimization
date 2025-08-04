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
- so far so good with the dictionary format
- api functions are working so far to generate an initial solution
- try and fix main.py to incorporate new solution format tomorrow

## July 15, 2025 (Day 6)

*Tasks*

- fix solution dictionary so lineup players and roster players have the same keys
- fix main.py to incorporate new solution format

- lineup and roster players have same dict keys
- the roster (bench) players have placeholders for lineup_postion and defensive_positio

## July 16, 2025 (Day 7)

*Tasks*

- ??? change lineup dict to be dict numbered 1-9 instead of a list ???
- ^^ might not have to do this, could instead set lineup_position to its index in the list after the switch
- fix main.py to incorporate new solution format

- created get_handedness() function so the roster didn't have all R as default batting side
- required a get_player_id()
- added a simple cache system to help runtime

## July 19, 2025 (Day 8)

*Tasks*

- fix main.py to incorporate new solution format
- make init sol faster

- main now works with new dict structure for solutions
- made main write the best solution to a file
- had to fix some errors like returning dictionaries rather than list and other dict/list issues

*To-Do*

- switch lineup_position in player dict for solutions when swaps occur
- incorporate the bench players into the lineup
- make better objectives and agents
- make init_sol faster

## July 20, 2025 (Day 9)

- eliminated lineup position from the solution dictionary
- made init_sol faster by making get_player_id faster by not calling get_roster
- used pybaseball playerid_lookup instead of scraping and searching through team rosters
- lowered the amount of calls needed to get_roster which was the biggest time waster according to the profiler report

*To-Do*

- incorporate the bench players into the lineup
- make better objectives and agents

## July 31, 2025 (Day 10)

*Tasks*

- first thing to do is to incorporate bench players into the lineups when looking for replacements in the agents
- this should be something to get almost perfect before moving on to better objectives and agents
- make sure each existing agent is able to effectively replace sub-optimal position players with available players off the bench
- this could be done by making an overal function that checks for available players in a given group of players...
- e.g. the function could take in the bench players and check if there is a player worthy of being in the lineup

- realized i cn make an agent whose job it is to find better players on the bench
- easier and more effective than altering the existing agents to do more work than necessary

- created the best_nine objective and better_bench agent
- organized resulting files to be written to a results directory for organization

## August 3, 2025 (Day 11)

*Tasks*

- document score differences from init and final
- add a chart to results

- added chart to results, to fix/improve later

## August __, 2025 (Day 12)

*Tasks*

- document score differences from init and final
- improve chart
- start improving agents and objectives