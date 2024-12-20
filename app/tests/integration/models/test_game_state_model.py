import json
from app.models.game_state_model import GameState
from app.enums import Status
from app.models.user_model import UserState


def db_obj_is_same(state: GameState) -> bool:
    """Checks if GameState object is the same as an object from
    database with matching room_id.
    """
    return GameState.query.filter_by(room_id=state.room_id).first() == state


def test_get_players(test_db, test_game, p1_test, p2_test):
    """Tests, that getting players from GameState works correctly."""

    p1, p2 = test_game.get_players()
    assert p1 is None and p2 is None

    test_game.player_1_id = p1_test.user_id
    p1, p2 = test_game.get_players()
    assert p1 and (p2 is None)

    test_game.player_2_id = p2_test.user_id
    p1, p2 = test_game.get_players()
    assert (p1 is not None) and (p2 is not None)


def test_update_status(test_db, test_game, p1_test, p2_test):
    """Tests, that status is updating correctly."""
    assert test_game.update_status() == Status.INIT.value

    test_game.player_1_id = p1_test.user_id
    assert test_game.update_status() == Status.JOIN_WAIT.value

    test_game.player_2_id = p2_test.user_id
    assert test_game.update_status() == Status.READY.value

    p1_test.game_completed = True
    assert test_game.update_status() == Status.READY.value

    p2_test.game_completed = True
    assert test_game.update_status() == Status.FINISHED.value


def test_add_player(test_db, test_game, p1_test, p2_test):
    """Tests, that player addition works correctly."""
    assert test_game.add_player(p1_test.user_id) == True
    assert test_game.add_player(p2_test.user_id) == True
    assert test_game.add_player(p1_test.user_id) == False


def test_del_player(test_db, test_game, p1_test, p2_test):
    """Tests, that player deletion works correctly.
    After both players are deleted, table GameState should be empty.
    """
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)

    assert test_game.del_player("not_present") == False
    assert test_game.del_player(p1_test.user_id) == True
    assert test_game.player_1_id is None and test_game.player_2_id is not None

    test_game.add_player(p1_test.user_id)
    assert test_game.del_player(p2_test.user_id) == True
    assert test_game.player_1_id is not None and test_game.player_2_id is None

    assert test_game.del_player(p1_test.user_id) == True
    assert test_db.session.query(GameState).first() == None


def test_set_status(test_db, test_game):
    """Tests, that setting GameState status works correctly."""
    assert test_game.status == Status.INIT.value

    status = "another_status"
    test_game.set_status(status)
    assert test_game.status == status


def test_both_players_completed_level(test_db, test_game, p1_test, p2_test):
    """Tests, that evaluation of level completion for
    both players works correctly.
    """
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)

    assert test_game.both_players_completed_level() == False

    p1_test.level_completed = True
    assert test_game.both_players_completed_level() == False

    p2_test.level_completed = True
    assert test_game.both_players_completed_level() == True


def test_both_players_completed_game(test_db, test_game, p1_test, p2_test):
    """Tests, that evaluation of level completion
    for both players works correctly.
    """
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)

    assert test_game.both_players_completed_game() == False

    p1_test.game_completed = True
    assert test_game.both_players_completed_game() == False

    p2_test.game_completed = True
    assert test_game.both_players_completed_game() == True


def test_advance_next_round(test_db, test_game, p1_test, p2_test, test_map):
    """Tests, that GameState round advance works correctly."""
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)

    test_map.level = test_game.rounds * test_game.levels_per_round
    assert test_map.level == 12
    assert test_game.current_round == 1
    assert test_game.level == 1

    test_game.advance_next_round()
    assert test_game.current_round == 2
    assert test_game.level == 5

    test_game.advance_next_round()
    assert test_game.current_round == 3
    assert test_game.level == 9

    test_game.advance_next_round()
    assert test_game.current_round == 3
    assert test_game.level == 9


def test_reset_game_state(test_db, test_game, p1_test, p2_test):
    """Tests, that GameState reset works correctly."""
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)
    level = 3
    current_round = 6
    p1_rounds_won = 2
    p2_rounds_won = 3
    winner_id = "some_id"
    status = Status.FINISHED.value

    test_game.level = level
    test_game.current_round = current_round
    test_game.p1_rounds_won = p1_rounds_won
    test_game.p2_rounds_won = p2_rounds_won
    test_game.winner_id = winner_id
    test_game.staus = status

    test_game.reset_game_state()

    assert test_game.level != level
    assert test_game.current_round != current_round
    assert test_game.p1_rounds_won != p1_rounds_won
    assert test_game.p2_rounds_won != p2_rounds_won
    assert test_game.winner_id != winner_id
    assert test_game.status != status


def test_update_round_winner(test_db, test_game, p1_test, p2_test):
    """Tests, that round winner evaluation is correct."""
    p1_test.rounds_won = 0
    p2_test.rounds_won = 0
    p1_test.score = 100
    p2_test.score = 0
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)

    test_game.update_round_winner()
    assert p1_test.rounds_won == 1
    assert p2_test.rounds_won == 0

    p2_test.score = 300
    test_game.update_round_winner()
    assert p1_test.rounds_won == 1
    assert p2_test.rounds_won == 1


def test_update_game_winner(test_db, test_game, p1_test, p2_test):
    """Tests, that update of game winner is correct."""
    p1_test.rounds_won = 3
    p2_test.rounds_won = 2
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)

    assert test_game.winner_id == None

    test_game.update_game_winner()
    assert test_game.winner_id == p1_test.user_id

    p2_test.rounds_won = 4
    test_game.update_game_winner()
    assert test_game.winner_id == p2_test.user_id


def test_get_game_state_max_level_by_room(test_db, test_game):
    """Tests, that GameState with matching room_id
    ets its max level correctly.
    """
    level = 1
    levels_per_round = 5
    test_game.level = level
    test_game.levels_per_round = levels_per_round

    assert (
        GameState.get_game_state_max_level_by_room(test_game.room_id)
        == level + levels_per_round - 1
    )


def test_game_state_advance_ready(test_db, test_game, p1_test, p2_test):
    """Tests, that GameState with matching room_id
    evaluates level advance correctly.
    """
    p1_test.level_completed = True
    p2_test.level_completed = True
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)

    assert GameState.game_state_advance_ready(test_game.room_id) == True
    p1_test.level_completed = False
    assert GameState.game_state_advance_ready(test_game.room_id) == False


def test_game_state_next_round_ready(test_db, test_game, p1_test, p2_test):
    """Tests, that GameState with matching room_id
    evaluates round advance correctly.
    """
    p1_test.game_completed = True
    p2_test.game_completed = True
    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)

    assert GameState.game_state_next_round_ready(test_game.room_id) == True
    p1_test.game_completed = False
    assert GameState.game_state_next_round_ready(test_game.room_id) == False


def test_get_game_state_status(test_db, test_game, game_data):
    """Tests, that GameState with matching room_id
    gets its status correctly.
    """
    assert GameState.get_game_state_status(test_game.room_id) == game_data["status"]
    status = Status.READY.value
    test_game.status = status
    assert GameState.get_game_state_status(test_game.room_id) == status


def test_get_game_state_by_room(test_db, test_game, p1_test, p2_test):
    """Tests, that GameState with matching room_id
    is returned correctly.
    """
    assert GameState.get_game_state_by_room(test_game.room_id) == test_game

    test_game.add_player(p1_test.user_id)
    test_game.add_player(p2_test.user_id)
    assert GameState.get_game_state_by_room(test_game.room_id) == test_game


def test_create_multiplayer_game_state(test_db, test_map, game_method_create):
    """Tests, that GameState with matching room_id is created correctly."""
    test_map.level = 1
    room_id = "some_room_id"
    GameState.create_multiplayer_game_state(room_id)

    game_state = GameState.get_game_state_by_room(room_id)
    game_state.map = json.loads(game_state.map)

    for key in game_method_create:
        assert game_state.__getattribute__(key) == game_method_create[key]


def test_create_user_after_room_join(test_db, test_game, p1_test, test_map):
    """Tests, that GameState with matching room_id gets user by provided ID.
    Then it checks if user exist.
    If user does not exists, it is created with GameState properties.
    If user exists, its properties is set by GameState properties.
    This test covers non existing user.
    """
    test_map.level = 1
    test_map.data = test_game.map
    non_exist_user_id = "non_exist_user_id"
    GameState.create_user_after_room_join(test_game.room_id, non_exist_user_id)
    user = UserState.get_user_by_id(non_exist_user_id)

    assert user.level == test_game.level
    assert user.map == test_game.map


def test_create_user_after_room_join(test_db, test_game, p1_test, test_map):
    """Tests, that GameState with matching room_id gets user by provided ID.
    Then it checks if user exist.
    If user does not exists, it is created with GameState properties.
    If user exists, its properties is set by GameState properties.
    This test covers existing user.
    """
    test_map.level = 1
    test_map.data = test_game.map
    p1_test.level = 99

    GameState.create_user_after_room_join(test_game.room_id, p1_test.user_id)
    user = UserState.get_user_by_id(p1_test.user_id)

    assert user.level == test_game.level
    assert user.map == test_game.map
