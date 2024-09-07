import json, time

from typing import List, Tuple
from flask import session

from app.models import (
    Maps,
    GameState,
    UserState,
    advance_user_state_current_level,
    create_multiplayer_game_state,
    create_user_state,
    get_game_state_by_room,
    get_map_by_level,
    get_map_by_user,
    get_user_by_id,
    reset_user_state_level,
    retrieve_user_state_level,
    set_user_score,
    set_user_state_level,
)
from app.extensions import db
from app.enums import Status

NestedDictList = List[List[dict[str, dict | int]]]

MAX_LEVEL = 3


def game_state_advance_ready(room_id: str) -> bool:
    # time.sleep(2)
    # return True
    game_state = get_game_state_by_room(room_id)
    return game_state.both_players_completed_level()


def game_state_next_round_ready(room_id: str) -> bool:
    game_state = get_game_state_by_room(room_id)
    return game_state.bot_players_completed_game()


def game_state_status(room_id: str) -> any:
    # return Status.READY.value
    return get_game_state_by_room(room_id).status


def game_state_creation(user_id: str) -> dict | None:
    user = get_user_by_id(user_id)
    if user is None:
        return None

    return {
        "map": json.loads(user.map),
        "level": user.level,
        "score": user.score,
        "completed": user.level_completed,
        "levels_completed": user.game_completed,
    }


def game_state_update(key: str, user_id: str, max_level: int) -> dict | None:
    """Check if move is valid and then updates game_state"""
    user = get_user_by_id(user_id)
    map = json.loads(user.map)
    level = user.level

    prev_pos_x, prev_pos_y = get_position_from_map(map)

    pos_x, pos_y = validate_move(key, map, prev_pos_x, prev_pos_y)

    # user.set_game_completed(False)
    # user.set_level_completed(False)

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


def game_state_advance_current_level(user_id: str, max_level: int) -> None:
    advance_user_state_current_level(user_id, max_level)


def game_get_achieved_levels(user_id: str) -> List:
    levels = []
    cnt_of_levels = get_user_by_id(user_id).achieved_level

    for level in range(1, cnt_of_levels + 1):
        level_info = {"level": level, "data": get_map_by_level(level)}
        levels.append(level_info)

    return levels


def validate_move(key: str, map: NestedDictList, pos_x: int, pos_y: int) -> dict | None:
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


def create_map() -> NestedDictList:
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
    map[0][0]["active"] = True
    map[0][0]["blocker"] = False
    map[1][0]["blocker"] = False
    map[2][0]["blocker"] = False
    map[3][0]["blocker"] = False
    map[4][0]["blocker"] = False

    return map


def create_map_2() -> NestedDictList:
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
    map[0][0]["active"] = True
    map[0][0]["blocker"] = False
    map[0][1]["blocker"] = False
    map[0][2]["blocker"] = False
    map[0][3]["blocker"] = False
    map[0][4]["blocker"] = False
    return map


def create_map_3() -> NestedDictList:
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
    map[0][0]["active"] = True
    map[0][0]["blocker"] = False
    map[1][0]["blocker"] = False
    map[1][1]["blocker"] = False
    map[1][2]["blocker"] = False
    map[1][3]["blocker"] = False
    return map


def create_map_4() -> NestedDictList:
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
    map[0][0]["active"] = True
    map[0][0]["blocker"] = False
    map[1][0]["blocker"] = False
    map[1][1]["blocker"] = False
    map[1][2]["blocker"] = False
    map[1][3]["blocker"] = False
    map[1][4]["blocker"] = False
    map[1][5]["blocker"] = False
    map[2][5]["blocker"] = False
    map[3][5]["blocker"] = False
    map[4][5]["blocker"] = False
    map[5][5]["blocker"] = False
    return map


def create_db_game_state_data(room_id: str, player_id: str) -> None:
    create_multiplayer_game_state(room_id, player_id)


def create_db_maps_data() -> None:
    if db.session.query(Maps).first():
        print("already existing table")
        return

    map = create_map()
    map_db = Maps(
        name="Hradec",
        data=json.dumps(map),
        level=1,
        start_position=json.dumps(
            {
                "x": 0,
                "y": 0,
            }
        ),
    )

    db.session.add(map_db)
    db.session.commit()

    map = create_map_2()
    map_db = Maps(
        name="Hradec",
        data=json.dumps(map),
        level=2,
        start_position=json.dumps(
            {
                "x": 0,
                "y": 0,
            }
        ),
    )

    db.session.add(map_db)
    db.session.commit()

    map = create_map_3()
    map_db = Maps(
        name="Hradec",
        data=json.dumps(map),
        level=3,
        start_position=json.dumps(
            {
                "x": 0,
                "y": 0,
            }
        ),
    )

    db.session.add(map_db)
    db.session.commit()

    map = create_map_4()
    map_db = Maps(
        name="Hradec",
        data=json.dumps(map),
        level=4,
        start_position=json.dumps(
            {
                "x": 0,
                "y": 0,
            }
        ),
    )

    db.session.add(map_db)
    db.session.commit()
