import json

from typing import List

from app.models import Maps, GameState
from app.extensions import db

NestedDictList = List[List[dict[str, dict | int]]]


def game_state_update(
    key: str, map: NestedDictList, position: dict, score: int
) -> dict | None:
    """Check if move is valid and then updates game_state"""

    prev_pos_x, prev_pos_y = position["x"], position["y"]
    pos_x, pos_y = validate_move(key, map, position)

    if all(pos is not None for pos in (pos_x, pos_y)):
        map[pos_x][pos_y]["active"] = True
        map[pos_x][pos_y]["visited"] = True
        map[prev_pos_x][prev_pos_y]["active"] = False
        map[prev_pos_x][prev_pos_y]["visited"] = True
        score = update_score(map, pos_x, pos_y, score)
    else:
        return None

    return {
        "map": map,
        "position": {
            "x": pos_x,
            "y": pos_y,
        },
        "score": score,
        "completed": game_completed(map),
    }


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
    else:
        return None, None

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
                "blocker": False,
                "visited": False,
            }
            col_cell.append(cell)
        map.append(col_cell)
    map[0][0]["active"] = True
    map[0][3]["blocker"] = True
    map[1][3]["blocker"] = True
    map[2][3]["blocker"] = True
    map[3][3]["blocker"] = True
    map[0][5]["blocker"] = True
    map[1][5]["blocker"] = True
    map[2][5]["blocker"] = True
    map[3][5]["blocker"] = True
    map[0][9]["blocker"] = True
    map[1][9]["blocker"] = True
    map[2][9]["blocker"] = True
    map[3][9]["blocker"] = True
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
