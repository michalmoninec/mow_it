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

level_obstacles = [
    {
        "level": 1,
        "name": "Hradec",
        "start": [0, 0],
        "obstacles": [[col, 0] for col in range(0, 2)],
    },
    {
        "level": 2,
        "name": "Opava",
        "start": [0, 0],
        "obstacles": [[0, row] for row in range(0, 2)],
    },
    {
        "level": 3,
        "name": "Branka",
        "start": [0, 0],
        "obstacles": [[col, 0] for col in range(0, 3)],
    },
    {
        "level": 4,
        "name": "Otice",
        "start": [0, 0],
        "obstacles": [[0, row] for row in range(0, 3)],
    },
    {
        "level": 5,
        "name": "Otice",
        "start": [0, 0],
        "obstacles": [[col, 0] for col in range(0, 4)],
    },
    {
        "level": 6,
        "name": "Otice",
        "start": [0, 0],
        "obstacles": [[0, row] for row in range(0, 4)],
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
    for row in map:
        if any(not cell["blocker"] and not cell["visited"] for cell in row):
            return False
    return True


def get_position_from_map(map: NestedDictList) -> Tuple[int | None, int | None]:
    for row in range(len(map)):
        for col in range(len(map[row])):
            if map[row][col]["active"]:
                return row, col
    return None, None


def create_empty_map() -> NestedDictList:
    map = []
    for col in range(10):
        col_cell = []
        for row in range(10):
            cell = {
                "x": col,
                "y": row,
                "active": False,
                "blocker": True,
                "visited": False,
            }
            col_cell.append(cell)
        map.append(col_cell)

    return map


def create_maps() -> None:
    if is_map_table_empty():
        for level in level_obstacles:
            map = create_empty_map()
            start_pos_x, start_pos_y = level["start"]
            map[start_pos_x][start_pos_y]["active"] = True

            for x, y in level["obstacles"]:
                map[x][y]["blocker"] = False

            create_maps_database(level["name"], map, level["level"])
