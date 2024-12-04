from app.scripts.game import (
    cell_not_blocked,
    get_position_from_map,
    level_completed,
    obstacle_col,
    obstacle_row,
    obstacle_cube,
    create_empty_map,
    update_score,
    validate_move,
)


def test_obstacle_col():
    """Tests, that column of obstacles for provided col is populated
    from start to end indexes.
    """

    assert obstacle_col(1, 1, 1) == []
    assert obstacle_col(1, 5, 3) == []

    start = 1
    end = 10
    row = 99

    assert obstacle_col(row, start, end) == [[row, i] for i in range(start, end)]


def test_obstacle_row():
    """Tests, that row of obstacles for provided col is
    populated from start to end indexes.
    """
    assert obstacle_row(1, 1, 1) == []
    assert obstacle_row(1, 4, 3) == []

    start = 1
    end = 10
    col = 99

    assert obstacle_row(col, start, end) == [[i, col] for i in range(start, end)]


def test_obstacle_cube():
    """Tests, that that row, col coordinates of obstacles are populated for
    start and end indexes of row and col.
    """
    assert obstacle_cube(1, 1, 1, 1) == []
    assert obstacle_cube(5, 1, 5, 1) == []

    col_start = 1
    col_end = 3
    row_start = 1
    row_end = 3

    assert obstacle_cube(row_start, row_end, col_start, col_end) == [
        [row, col]
        for row in range(row_start, row_end)
        for col in range(col_start, col_end)
    ]


def test_validate_move_invalid_direction_names(test_maps):
    """Tests, that for invalid name of directions, position wont be altered."""
    map = test_maps["empty_map"]
    pos = (3, 3)

    for dir in ["a", "b", "c"]:
        assert validate_move(dir, map, *pos) == pos


def test_validate_move_all_valid_directions(test_maps, dirs):
    """Tests, that for provided key, map, expected output position move will be updated.
    If not  valid move, expected position should not be altered from input position.
    This test case counts on position, from which could be moved to all directions.
    """
    map = test_maps["empty_map"]
    pos_x, pos_y = (3, 3)
    for dir in dirs["list"]:
        assert validate_move(dir, map, pos_x, pos_y) != (pos_x, pos_y)


def test_validate_move_no_valid_direction(test_maps, dirs):
    """Tests, that for provided key, map, expected output position move will be updated.
    If not  valid move, expected position should not be altered from input position.
    This test case counts on position, from which could be moved to all directions.
    """
    map = test_maps["no_valid_move"]
    pos_x, pos_y = (3, 3)
    for dir in dirs["list"]:
        assert validate_move(dir, map, pos_x, pos_y) == (pos_x, pos_y)


def test_cell_not_blocked_all_free(test_maps):
    """Tests, that for map, which all of its cells are not
    blocked, output is True.
    """
    map = test_maps["empty_map"]

    for col in range(len(map)):
        for row in range(len(map[0])):
            assert cell_not_blocked(map, col, row) == True


def test_cell_not_blocked_all_blocked(test_maps):
    """Tests, that for map, which all of its cells are
    blocked, output is False.
    """
    map = test_maps["full_map"]

    for col in range(len(map)):
        for row in range(len(map[0])):
            assert cell_not_blocked(map, col, row) == False


def test_update_score_positive(test_maps):
    """Tests, that for unvisited cells, returned score diff is positive."""
    map = test_maps["none_visited"]
    pos = (3, 3)

    for _ in range(len(map)):
        for _ in range(len(map[0])):
            assert update_score(map, *pos) == 100


def test_update_score_negative(test_maps):
    """Tests, that for visited cells, returned score diff is negative."""
    map = test_maps["all_visited"]
    pos = (3, 3)

    for _ in range(len(map)):
        for _ in range(len(map[0])):
            assert update_score(map, *pos) == -100


def test_level_completed_all_visited(test_maps):
    """Tests, that for map, that has all cells visited, level is completed."""
    map = test_maps["all_visited"]

    assert level_completed(map) == True


def test_level_completed_all_blocker(test_maps):
    """Tests, that for map, that has all cells blockers, level is completed."""
    map = test_maps["full_map"]

    assert level_completed(map) == True


def test_level_completed_all_blocker(test_maps):
    """Tests, that for map, that has all cells nonvisited, level is not completed."""
    map = test_maps["none_visited"]

    assert level_completed(map) == False


def test_get_position_from_map_none_active(test_maps):
    """Tests, that for map, that has no active
    cell, output is Tuple[None, None].
    """
    map = test_maps["empty_map"]
    assert get_position_from_map(map) == (None, None)


def test_get_position_from_map_active(test_maps):
    """Tests, that for map, that has active
    cell, output is row, col that is active.
    """
    map = test_maps["empty_map"]
    pos_x, pos_y = 3, 3
    map[pos_x][pos_y]["active"] = True

    assert get_position_from_map(map) == (pos_x, pos_y)


def test_get_position_from_map_multiple_active(test_maps):
    """Tests, that for map, that has multiple active
    cells, output is first found Tuple of row, col.
    """
    map = test_maps["empty_map"]
    pos_x, pos_y = 3, 3
    map[pos_x][pos_y]["active"] = True
    pos_x2, pos_y2 = 3, 4
    map[pos_x2][pos_y2]["active"] = True
    assert get_position_from_map(map) == (pos_x, pos_y)


def test_create_empty_map(test_maps):
    """Tests creation of an empty map."""
    assert create_empty_map() == test_maps["empty_map"]
