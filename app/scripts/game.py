import json

from typing import List
from flask import session

from app.models import (
    Maps,
    GameState,
    UserState,
    advance_user_state_current_level,
    create_user_state,
    reset_user_state_level,
    retrieve_user_state_level,
    get_map_by_level,
    set_user_state_level,
)
from app.extensions import db

NestedDictList = List[List[dict[str, dict | int]]]

MAX_LEVEL = 3


def game_state_creation(user_id: str) -> dict | None:
    level = retrieve_user_state_level(user_id)
    if level is None:
        return None

    map = get_map_by_level(level=level)
    if map is None:
        return None

    return {
        "map": json.loads(map.data),
        "pos": json.loads(map.start_position),
        "level": level,
        "score": 0,
        "completed": False,
        "levels_completed": False,
    }


def game_state_update(
    key: str, map: NestedDictList, position: dict, score: int, user_id: str
) -> dict | None:
    """Check if move is valid and then updates game_state"""
    pos_x, pos_y = validate_move(key, map, position)

    prev_pos_x, prev_pos_y = position["x"], position["y"]

    completed = False
    levels_completed = False
    level = retrieve_user_state_level(user_id)

    if (pos_x, pos_y) != (prev_pos_x, prev_pos_y):
        score = update_score(map, pos_x, pos_y, score)
        map[pos_x][pos_y]["active"] = True
        map[pos_x][pos_y]["visited"] = True
        map[prev_pos_x][prev_pos_y]["active"] = False
        map[prev_pos_x][prev_pos_y]["visited"] = True

        if game_completed(map):
            completed = True
            level_condition = level + 1
            if level_condition > MAX_LEVEL:
                levels_completed = True
                level_condition = MAX_LEVEL

            # set_user_state_level(user_id, level)
            db.session.commit()
    else:
        pass
        # maybe some message flashing of invalid move

    return {
        "map": map,
        "pos": {
            "x": pos_x,
            "y": pos_y,
        },
        "score": score,
        "completed": completed,
        "levels_completed": levels_completed,
        "level": level,
    }


def game_state_advance_current_level(user_id: str) -> None:
    advance_user_state_current_level(user_id)


def game_get_achieved_levels(user_id: str) -> List:
    levels = []
    cnt_of_levels = UserState.query.filter_by(user_id=user_id).first().achieved_level

    for i in range(1, cnt_of_levels + 1):
        level_info = {"level": i, "data": Maps.query.filter_by(level=i).first().data}
        levels.append(level_info)

    return levels


def validate_move(
    key: str, map: NestedDictList, position: dict[str, int]
) -> dict | None:
    """Validates players move, return updated position or None"""

    pos_x = position["x"]
    pos_y = position["y"]

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


def update_score(map: NestedDictList, pos_x: int, pos_y: int, score: int) -> int:
    if map[pos_x][pos_y]["visited"]:
        score -= 100
    else:
        score += 100
    return score


def game_completed(map: NestedDictList) -> bool:
    for row in map:
        if any(not cell["blocker"] and not cell["visited"] for cell in row):
            return False
    return True


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


def create_db_game_state_data(room_id: str, player_id: str) -> None:

    # map = Maps(name="Hradec", data=json.dumps(create_map()))
    # db.session.add(map)
    start_position = {
        "x": 0,
        "y": 0,
    }

    game_state = GameState(
        room_id=room_id,
        player_1_id=player_id,
        status="init",
        level=1,
        map=json.dumps(create_map()),
        player_1_map=json.dumps(create_map()),
        player_1_pos=json.dumps(start_position),
        player_2_map=json.dumps(create_map()),
        player_2_pos=json.dumps(start_position),
        player_1_score=0,
        player_2_score=0,
    )

    db.session.add(game_state)
    db.session.commit()


def create_db_maps_data() -> None:
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
