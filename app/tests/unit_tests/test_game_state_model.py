from app.models.game_state_model import GameState


def test_game_state_init(game_data):
    """Tests, that init method behaves correctly."""

    game_state = GameState(**game_data)

    for key in game_data:
        assert game_state.__getattribute__(key) == game_data[key]


def test_user_not_in_room(game_state, p1_test, p2_test):
    """Test, that checks presence of user in GameState."""

    p1_id = p1_test.user_id
    p2_id = p2_test.user_id

    assert game_state.user_not_in_room(p1_id) == True
    assert game_state.user_not_in_room(p2_id) == True

    game_state.player_1_id = p1_id
    assert game_state.user_not_in_room(p1_id) == False
    assert game_state.user_not_in_room(p2_id) == True

    game_state.player_2_id = p2_id
    assert game_state.user_not_in_room(p1_id) == False
    assert game_state.user_not_in_room(p2_id) == False


def test_room_is_available(game_state):
    """Tests, that availability in room is decided correctly."""
    assert game_state.room_is_available() == True

    game_state.player_1_id = "abcd"
    assert game_state.room_is_available() == True

    game_state.player_2_id = "1234"
    assert game_state.room_is_available() == False

    del game_state.player_1_id
    assert game_state.room_is_available() == True


def test_final_round(game_state):
    """Tests, if evaluation of final round behaves correctly."""
    game_state.rounds = 10
    game_state.current_round = 1

    assert game_state.final_round() == False

    game_state.current_round = 10
    assert game_state.final_round() == True

    game_state.current_round = 12
    assert game_state.final_round() == False


def test_get_max_level(game_state):
    """Tests, that max level for evaluation is the last level for current round."""
    curr = 1
    max = 4
    game_state.level = 1
    game_state.levels_per_round = 4

    assert game_state.get_max_level() == curr + max - 1

    max = 10
    game_state.levels_per_round = max

    assert game_state.get_max_level() == curr + max - 1
