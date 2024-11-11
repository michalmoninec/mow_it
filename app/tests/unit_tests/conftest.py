import pytest

from app.models.game_state_model import GameState


def empty_map() -> None:
    map = [
        [
            {
                "x": col,
                "y": row,
                "active": False,
                "blocker": False,
                "visited": False,
            }
            for row in range(10)
        ]
        for col in range(10)
    ]
    return map


def full_obstacles_map() -> None:
    map = [
        [
            {
                "x": col,
                "y": row,
                "active": False,
                "blocker": True,
                "visited": False,
            }
            for row in range(10)
        ]
        for col in range(10)
    ]
    return map


def full_visited_map() -> None:
    map = [
        [
            {
                "x": col,
                "y": row,
                "active": False,
                "blocker": False,
                "visited": True,
            }
            for row in range(10)
        ]
        for col in range(10)
    ]
    return map


@pytest.fixture
def test_maps():
    map_with_start = empty_map()
    map_with_start[0][0]["active"] = True

    full_map = full_obstacles_map()

    return {
        "empty_map": empty_map(),
        "map_wit_start": map_with_start,
        "no_valid_move": full_map,
        "full_map": full_map,
        "all_visited": full_visited_map(),
        "none_visited": empty_map(),
    }


@pytest.fixture
def game_state():
    return GameState()
