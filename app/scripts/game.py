import json
import random

from typing import List, Tuple

from app.types_validation import NestedDictList
from app.models.map_model import Maps
from app.models.user_model import UserState

MAX_LEVEL = 50


def obstacle_col(row: int, start: int, end: int) -> List[List[int]]:
    """Returns col of row, col coordinates of obstacles for provided row.
    Row is populated with obstacles from start to end index.
    """
    return [[row, col] for col in range(start, end)]


def obstacle_row(col: int, start: int, end: int) -> List[List[int]]:
    """Returns row of row, col coordinates of obstacles for provided row.
    Row is populated with obstacles from start to end index.
    """
    return [[row, col] for row in range(start, end)]


def obstacle_cube(
    row_start: int, row_end: int, col_start: int, col_end: int
) -> List[List[int]]:
    """Returns obstacles in cube pattern for provided start
    and end of both row and col.
    """
    return [
        [row, col]
        for row in range(row_start, row_end)
        for col in range(col_start, col_end)
    ]


level_obstacles = [
    {
        "level": 1,
        "name": "name01",
        "start": [0, 0],
        "obstacles": obstacle_col(0, 3, 9) + obstacle_cube(1, 10, 0, 10),
    },
    {
        "level": 2,
        "name": "name02",
        "start": [0, 0],
        "obstacles": obstacle_cube(1, 5, 1, 5) + obstacle_cube(7, 9, 7, 9),
    },
    {
        "level": 3,
        "name": "name03",
        "start": [0, 0],
        "obstacles": obstacle_row(1, 1, 9)
        + obstacle_row(3, 1, 9)
        + obstacle_row(5, 1, 9)
        + obstacle_row(7, 1, 9),
    },
    {
        "level": 4,
        "name": "name04",
        "start": [0, 0],
        "obstacles": obstacle_col(0, 1, 9)
        + obstacle_col(1, 2, 8)
        + obstacle_col(2, 3, 7)
        + obstacle_col(3, 4, 6)
        + obstacle_col(4, 5, 5)
        + obstacle_col(5, 6, 4),
    },
    {
        "level": 5,
        "name": "name05",
        "start": [0, 0],
        "obstacles": obstacle_cube(2, 8, 2, 8),
    },
    {
        "level": 6,
        "name": "name06",
        "start": [0, 0],
        "obstacles": obstacle_cube(4, 6, 4, 6),
    },
]


def user_state_update(
    key: str, user_id: str, max_level: int | None = None
) -> UserState | None:
    """Check if move is valid and then updates game_state"""
    if max_level is None:
        max_level = Maps.get_max_level_of_maps()

    user = UserState.get_user_by_id(user_id)
    if user is None:
        return None

    map = json.loads(user.map)
    level = user.level

    prev_pos_x, prev_pos_y = get_position_from_map(map)

    pos_x, pos_y = validate_move(key, map, prev_pos_x, prev_pos_y)

    if (pos_x, pos_y) != (prev_pos_x, prev_pos_y):
        diff = update_score(map, pos_x, pos_y)
        user.add_score(diff=diff)
        map[pos_x][pos_y]["active"] = True
        map[pos_x][pos_y]["visited"] = True
        map[prev_pos_x][prev_pos_y]["active"] = False
        map[prev_pos_x][prev_pos_y]["visited"] = True
        user.set_map(json.dumps(map))

        if level_completed(map):
            user.set_level_completed(True)
            level_condition = level + 1
            if level_condition > max_level:
                user.set_game_completed(True)
                level_condition = max_level

    return UserState.get_user_by_id(user_id)


def user_get_achieved_levels(user_id: str) -> List[dict]:
    """Returns list of dictionaries containing info:
    - Level value.
    - Data value, which represents map.
    If user does not exist, returns None.
    """
    user_state = UserState.get_user_by_id(user_id)
    if user_state:
        cnt_of_levels = user_state.achieved_level
    else:
        return None

    return [
        {"level": level, "data": Maps.get_map_by_level(level)}
        for level in range(1, cnt_of_levels + 1)
    ]


def validate_move(key: str, map: NestedDictList, pos_x: int, pos_y: int) -> Tuple:
    """Validates players move, return updated position or not altered position."""

    if (
        key == "ArrowRight"
        and (pos_x + 1 < len(map))
        and cell_not_blocked(map, pos_x + 1, pos_y)
    ):
        pos_x += 1
    elif (
        key == "ArrowLeft"
        and (pos_x - 1 >= 0)
        and cell_not_blocked(map, pos_x - 1, pos_y)
    ):
        pos_x -= 1
    elif (
        key == "ArrowUp"
        and (pos_y - 1 >= 0)
        and cell_not_blocked(map, pos_x, pos_y - 1)
    ):
        pos_y -= 1
    elif (
        key == "ArrowDown"
        and (pos_y + 1 < len(map))
        and cell_not_blocked(map, pos_x, pos_y + 1)
    ):
        pos_y += 1

    return pos_x, pos_y


def cell_not_blocked(map: NestedDictList, x: int, y: int) -> bool:
    """Check if cell is blocker and returns this information."""
    return not map[x][y]["blocker"]


def update_score(map: NestedDictList, pos_x: int, pos_y: int) -> int:
    """Updates score for cell at provided coordinates and return this value.
    If cell was already visited, score is negative, otherwise it is positive.
    """
    if map[pos_x][pos_y]["visited"]:
        return -100
    else:
        return 100


def level_completed(map: NestedDictList) -> bool:
    """Checks map for any unvisited cells."""
    for row in map:
        if any(not cell["blocker"] and not cell["visited"] for cell in row):
            return False
    return True


def get_position_from_map(map: NestedDictList) -> Tuple[int | None, int | None]:
    """Iterates over map and returns cell that is active"""
    for row in range(len(map)):
        for col in range(len(map[row])):
            if map[row][col]["active"]:
                return row, col
    return None, None


def create_empty_map(inverted: bool = False) -> NestedDictList:
    """Creates empty nested list of dict."""
    map = []
    for col in range(10):
        col_cell = []
        for row in range(10):
            cell = {
                "x": col,
                "y": row,
                "active": False,
                "blocker": inverted,
                "visited": False,
            }
            col_cell.append(cell)
        map.append(col_cell)

    return map


def create_maps() -> None:
    """If database table of maps is empty, it creates maps by levels.
    If table updated, returns True, otherwise returns False.
    """
    if Maps.is_map_table_empty():
        for level in range(1, MAX_LEVEL + 1):
            map = generative_map_creation(level)
            invert_non_visited(map)
            name = f"name{level:02}"
            Maps.create_maps_database(name, map, level)
        return True
    return False


def generative_map_creation(level: int) -> NestedDictList:
    """Generatively creates maps.
    Each map is created in way, that is valid to play and complete.
    Starting position is choosed randomly.
    Then direction and depth in that direction is also choosed randomly
    and then those cells are visited.
    Coverage determinates how many cells are to be populated with visited tag.
    """
    start_pos_x = random.randint(0, 9)
    start_pos_y = random.randint(0, 9)
    number_of_cells = random.randint(20, 80)
    directions = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]
    map = create_empty_map()
    map[start_pos_x][start_pos_y]["active"] = True

    curr = 1
    while curr < number_of_cells:
        dir = directions[random.randint(0, 3)]
        depth = random.randint(1, 7)
        for _ in range(1, depth):
            curr_pos_x, curr_pos_y = get_position_from_map(map)
            next_pos_x, next_post_y = validate_move(dir, map, curr_pos_x, curr_pos_y)
            if (curr_pos_x, curr_pos_y) != (next_pos_x, next_post_y):
                if not map[next_pos_x][next_post_y]["visited"]:
                    curr += 1
                map[next_pos_x][next_post_y]["active"] = True
                map[next_pos_x][next_post_y]["visited"] = True
                map[curr_pos_x][curr_pos_y]["active"] = False
                map[curr_pos_x][curr_pos_y]["visited"] = True
            else:
                break

    return map


def invert_non_visited(map: NestedDictList) -> None:
    """Non visited cells are changed to blockers."""
    for row in range(len(map)):
        for col in range(len(map[row])):
            if not map[row][col]["visited"]:
                map[row][col]["blocker"] = True
            else:
                map[row][col]["visited"] = False
