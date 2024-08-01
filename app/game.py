def game_update(key, session) -> None:
    last_visited = session["last_visited"]
    map = session["map"]
    
    # print(f"pos_x is {pos_x}")
    print(f'Actual position is: {session['position']}')

    pos_x = session["position"]["x"]
    pos_y = session["position"]["y"]

    valid = True

    if key == "ArrowRight" and (pos_x + 1 < len(map)):
        pos_x += 1
    elif key == "ArrowLeft" and (pos_x - 1 >= 0):
        pos_x -= 1
    elif key == "ArrowUp" and (pos_y - 1 >= 0):
        pos_y -= 1
    elif key == "ArrowDown" and (pos_y + 1 < len(map)):
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

