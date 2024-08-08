def game_update(key: str, session) -> None:
    last_visited = session["last_visited"]
    map = session["map"]

    # print(f"pos_x is {pos_x}")
    # print(f'Actual position is: {session['position']}')

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

    # update_game(pos_x, pos_y, session)
    session["position"] = {
        "x": pos_x,
        "y": pos_y,
    }

    session["last_visited"] = {
        "x": pos_x,
        "y": pos_y,
    }

    # pos = session["position"]
    map[pos_x][pos_y]["active"] = True

    if valid:
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
    return map
