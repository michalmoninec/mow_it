import json


from app.models import Maps, GameState
from app.extensions import db


def game_update(key: str, session) -> None:

    last_visited = session["last_visited"]
    map = session["map"]
    pos_x = session["position"]["x"]
    pos_y = session["position"]["y"]
    valid = True

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
        valid = False

    session["position"] = {
        "x": pos_x,
        "y": pos_y,
    }

    session["last_visited"] = {
        "x": pos_x,
        "y": pos_y,
    }

    map[pos_x][pos_y]["active"] = True

    if valid:
        if map[pos_x][pos_y]["visited"]:
            session["score"] -= 100
        else:
            session["score"] += 100
        map[last_visited["x"]][last_visited["y"]]["active"] = False
        map[last_visited["x"]][last_visited["y"]]["visited"] = True


def cell_not_blocked(map, x, y) -> bool:
    return not map[x][y]["blocker"]


def create_map():
    print("Somebody initialized map creation.")
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
    return map


def create_db_test_data(room_id: str, player_id: str):

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


def create_db_maps_data():
    map = create_map()
    map_db = Maps(name="Hradec", data=json.dumps(map))

    db.session.add(map_db)
    db.session.commit()
