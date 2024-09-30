# MOW_IT - lawn mowing web browser game

### Dependencies

```bash
pip install -r requirements.txt
```

### Run script

```bash
python manage.py
```

## Progress:

Project is in active development.
Current state functionality:

-   6 very simple maps.
-   Single player with level selection based on completed levels.
-   Multiplayer for two players, three rounds by two levels each.
-   User id is currently stored in local storage with no authorization.

## Simple web browser game, that aims to:

-   Singleplayer mode.
-   Multiplayer mode.
-   Mode against AI (not implemented - will use refactored "coverage-optimization" project).
-   Map creation followed by finding optimal cover path.

## Stack

-   Python + Flask.
-   Database: sqlite3.
-   Singleplayer uses http requests.
-   Multiplayer uses socket.

## Game

-   Movement with arrows.
-   After level completion, advancing is possible either by clicking next level button or pressing enter.
-   Each unvisited cell adds score, when moving through visited cell, score is decreased.
-   Multiplayer score has bonus for finishing level before your oponent.
