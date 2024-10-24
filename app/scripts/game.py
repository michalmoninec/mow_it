import json

from typing import List, Tuple, Set

from app.models import (
    advance_user_state_current_level,
    create_maps_database,
    get_map_by_level,
    get_user_by_id,
    get_max_level_of_maps,
    is_map_table_empty,
)
from app.custom_types import NestedDictList


def obstacle_col(row: int, start: int, end: int) -> List[List[int]]:
    return [[row, col] for col in range(start, end)]


def obstacle_row(col: int, start: int, end: int) -> List[List[int]]:
    return [[row, col] for row in range(start, end)]


def obstacle_cube(
    row_start: int, row_end: int, col_start: int, col_end: int
) -> List[List[int]]:
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
        "obstacles": obstacle_col(1, 0, 7)
        + obstacle_col(3, 1, 8)
        + obstacle_cube(5, 8, 5, 8),
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


def user_state_update(key: str, user_id: str, max_level: int | None = None) -> None:
    """Check if move is valid and then updates game_state"""
    if max_level is None:
        max_level = get_max_level_of_maps()

    user = get_user_by_id(user_id)
    map = json.loads(user.map)
    level = user.level

    prev_pos_x, prev_pos_y = get_position_from_map(map)

    pos_x, pos_y = validate_move(key, map, prev_pos_x, prev_pos_y)

    if (pos_x, pos_y) != (prev_pos_x, prev_pos_y):
        diff = update_score(map, pos_x, pos_y)
        user.set_score(diff=diff)
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


def user_get_achieved_levels(user_id: str) -> List[dict]:
    """
    TODO - change with comprehension.
    """
    levels = []
    cnt_of_levels = get_user_by_id(user_id).achieved_level

    for level in range(1, cnt_of_levels + 1):
        level_info = {"level": level, "data": get_map_by_level(level)}
        levels.append(level_info)

    return levels


def validate_move(key: str, map: NestedDictList, pos_x: int, pos_y: int) -> Tuple:
    """Validates players move, return updated position or None"""

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
    return not map[x][y]["blocker"]


def update_score(map: NestedDictList, pos_x: int, pos_y: int) -> int:
    if map[pos_x][pos_y]["visited"]:
        return -100
    else:
        return 100


def level_completed(map: NestedDictList) -> bool:
    """
    Checks map for any unvisited cells.
    """
    for row in map:
        if any(not cell["blocker"] and not cell["visited"] for cell in row):
            return False
    return True


def get_position_from_map(map: NestedDictList) -> Tuple[int | None, int | None]:
    """
    Iterates over map and returns cell that is active
    """
    for row in range(len(map)):
        for col in range(len(map[row])):
            if map[row][col]["active"]:
                return row, col
    return None, None


def create_empty_map() -> NestedDictList:
    """
    Creates empty nested list of dict.
    """
    map = []
    for col in range(10):
        col_cell = []
        for row in range(10):
            cell = {
                "x": col,
                "y": row,
                "active": False,
                "blocker": False,
                "visited": False,
            }
            col_cell.append(cell)
        map.append(col_cell)

    return map


def create_maps() -> None:
    """
    If database table of maps is empty, it creates maps by levels.
    """
    if is_map_table_empty():
        for level in level_obstacles:
            map = create_empty_map()
            start_pos_x, start_pos_y = level["start"]
            map[start_pos_x][start_pos_y]["active"] = True

            for x, y in level["obstacles"]:
                map[x][y]["blocker"] = True

            create_maps_database(level["name"], map, level["level"])
