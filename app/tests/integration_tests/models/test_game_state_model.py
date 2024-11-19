from app.models.game_state_model import GameState
from app.enums import Status
from app.models.user_model import UserState


def db_obj_is_same(state: GameState) -> bool:
    """
    Checks if GameState object is the same as an object from database with matching room_id.
    """
    return GameState.query.filter_by(room_id=state.room_id).first() == state


def test_get_players(test_db, game_state, p1_test, p2_test):
    """
    Tests, that getting players from GameState works correctly.
    """

    p1, p2 = game_state.get_players()
    assert p1 is None and p2 is None

    game_state.player_1_id = p1_test.user_id
    p1, p2 = game_state.get_players()
    assert p1 and (p2 is None)

    game_state.player_2_id = p2_test.user_id
    p1, p2 = game_state.get_players()
    assert (p1 is not None) and (p2 is not None)


def test_update_status(test_db, game_state, p1_test, p2_test):
    """
    Tests, that status is updating correctly.
    """
    assert game_state.update_status() == Status.INIT.value

    game_state.player_1_id = p1_test.user_id
    assert game_state.update_status() == Status.JOIN_WAIT.value

    game_state.player_2_id = p2_test.user_id
    assert game_state.update_status() == Status.READY.value

    p1_test.game_completed = True
    assert game_state.update_status() == Status.READY.value

    p2_test.game_completed = True
    assert game_state.update_status() == Status.FINISHED.value


def test_add_player(test_db, game_state, p1_test, p2_test):
    """
    Tests, that player addition works correctly.
    """
    assert game_state.add_player(p1_test.user_id) == True
    assert game_state.add_player(p2_test.user_id) == True
    assert game_state.add_player(p1_test.user_id) == False


def test_del_player(test_db, game_state, p1_test, p2_test):
    """
    Tests, that player deletion works correctly.
    After both players are deleted, table GameState should be empty.
    """
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    assert game_state.del_player("not_present") == False
    assert game_state.del_player(p1_test.user_id) == True
    assert game_state.player_1_id is None and game_state.player_2_id is not None

    game_state.add_player(p1_test.user_id)
    assert game_state.del_player(p2_test.user_id) == True
    assert game_state.player_1_id is not None and game_state.player_2_id is None

    assert game_state.del_player(p1_test.user_id) == True
    assert test_db.session.query(GameState).first() == None


def test_set_status(test_db, game_state):
    """
    Tests, that setting GameState status works correctly.
    """
    assert game_state.status == Status.INIT.value

    status = "another_status"
    game_state.set_status(status)
    assert game_state.status == status


def test_both_players_completed_level(test_db, game_state, p1_test, p2_test):
    """
    Tests, that evaluation of level completion for both players works correctly.
    """
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    assert game_state.both_players_completed_level() == False

    p1_test.level_completed = True
    assert game_state.both_players_completed_level() == False

    p2_test.level_completed = True
    assert game_state.both_players_completed_level() == True


def test_both_players_completed_game(test_db, game_state, p1_test, p2_test):
    """
    Tests, that evaluation of level completion for both players works correctly.
    """
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    assert game_state.both_players_completed_game() == False

    p1_test.game_completed = True
    assert game_state.both_players_completed_game() == False

    p2_test.game_completed = True
    assert game_state.both_players_completed_game() == True


def test_advance_next_round(test_db, game_state, p1_test, p2_test, test_map):
    """
    Tests, that GameState round advance works correctly.
    """
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    test_map.level = game_state.rounds * game_state.levels_per_round
    assert test_map.level == 12
    assert game_state.current_round == 1
    assert game_state.level == 1

    game_state.advance_next_round()
    assert game_state.current_round == 2
    assert game_state.level == 5

    game_state.advance_next_round()
    assert game_state.current_round == 3
    assert game_state.level == 9

    game_state.advance_next_round()
    assert game_state.current_round == 3
    assert game_state.level == 9


def test_reset_game_state(test_db, game_state, p1_test, p2_test):
    """
    Tests, that GameState reset works correctly.
    """
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)
    level = 3
    current_round = 6
    p1_rounds_won = 2
    p2_rounds_won = 3
    winner_id = "some_id"
    status = Status.FINISHED.value

    game_state.level = level
    game_state.current_round = current_round
    game_state.p1_rounds_won = p1_rounds_won
    game_state.p2_rounds_won = p2_rounds_won
    game_state.winner_id = winner_id
    game_state.staus = status

    game_state.reset_game_state()

    assert game_state.level != level
    assert game_state.current_round != current_round
    assert game_state.p1_rounds_won != p1_rounds_won
    assert game_state.p2_rounds_won != p2_rounds_won
    assert game_state.winner_id != winner_id
    assert game_state.status != status


def test_update_round_winner(test_db, game_state, p1_test, p2_test):
    """
    Tests, that round winner evaluation is correct.
    """
    p1_test.rounds_won = 0
    p2_test.rounds_won = 0
    p1_test.score = 100
    p2_test.score = 0
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    game_state.update_round_winner()
    assert p1_test.rounds_won == 1
    assert p2_test.rounds_won == 0

    p2_test.score = 300
    game_state.update_round_winner()
    assert p1_test.rounds_won == 1
    assert p2_test.rounds_won == 1


def test_update_game_winner(test_db, game_state, p1_test, p2_test):
    """
    Tests, that update of game winner is correct.
    """
    p1_test.rounds_won = 3
    p2_test.rounds_won = 2
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    assert game_state.winner_id == None

    game_state.update_game_winner()
    assert game_state.winner_id == p1_test.user_id

    p2_test.rounds_won = 4
    game_state.update_game_winner()
    assert game_state.winner_id == p2_test.user_id


def test_get_game_state_max_level_by_room(test_db, game_state):
    """
    Tests, that GameState with matching room_id gets its max level correctly.
    """
    level = 1
    levels_per_round = 5
    game_state.level = level
    game_state.levels_per_round = levels_per_round

    assert (
        GameState.get_game_state_max_level_by_room(game_state.room_id)
        == level + levels_per_round - 1
    )


def test_game_state_advance_ready(test_db, game_state, p1_test, p2_test):
    """
    Tests, that GameState with matching room_id evaluates level advance correctly.
    """
    p1_test.level_completed = True
    p2_test.level_completed = True
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    assert GameState.game_state_advance_ready(game_state.room_id) == True
    p1_test.level_completed = False
    assert GameState.game_state_advance_ready(game_state.room_id) == False


def test_game_state_next_round_ready(test_db, game_state, p1_test, p2_test):
    """
    Tests, that GameState with matching room_id evaluates round advance correctly.
    """
    p1_test.game_completed = True
    p2_test.game_completed = True
    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)

    assert GameState.game_state_next_round_ready(game_state.room_id) == True
    p1_test.game_completed = False
    assert GameState.game_state_next_round_ready(game_state.room_id) == False


def test_get_game_state_status(test_db, game_state, game_data):
    """
    Tests, that GameState with matching room_id gets its status correctly.
    """
    assert GameState.get_game_state_status(game_state.room_id) == game_data["status"]
    status = Status.READY.value
    game_state.status = status
    assert GameState.get_game_state_status(game_state.room_id) == status


def test_get_game_state_by_room(test_db, game_state, p1_test, p2_test):
    """
    Tests, that GameState with matching room_id is returned correctly.
    """
    assert GameState.get_game_state_by_room(game_state.room_id) == game_state

    game_state.add_player(p1_test.user_id)
    game_state.add_player(p2_test.user_id)
    assert GameState.get_game_state_by_room(game_state.room_id) == game_state


def test_create_multiplayer_game_state(test_db, test_map, game_method_create):
    """
    Tests, that GameState with matching room_id is created correctly.
    """
    test_map.level = 1
    room_id = "some_room_id"
    GameState.create_multiplayer_game_state(room_id)

    game_state = GameState.get_game_state_by_room(room_id)

    for key in game_method_create:
        assert game_state.__getattribute__(key) == game_method_create[key]


def test_create_user_after_room_join(test_db, game_state, p1_test, test_map):
    """
    Tests, that GameState with matching room_id gets user by provided ID.
    Then it checks if user exist.
    If user does not exists, it is created with GameState properties.
    If user exists, its properties is set by GameState properties.
    This test covers non existing user.
    """
    test_map.level = 1
    test_map.data = game_state.map
    non_exist_user_id = "non_exist_user_id"
    GameState.create_user_after_room_join(game_state.room_id, non_exist_user_id)
    user = UserState.get_user_by_id(non_exist_user_id)

    assert user.level == game_state.level
    assert user.map == game_state.map


def test_create_user_after_room_join(test_db, game_state, p1_test, test_map):
    """
    Tests, that GameState with matching room_id gets user by provided ID.
    Then it checks if user exist.
    If user does not exists, it is created with GameState properties.
    If user exists, its properties is set by GameState properties.
    This test covers existing user.
    """
    test_map.level = 1
    test_map.data = game_state.map
    p1_test.level = 99

    GameState.create_user_after_room_join(game_state.room_id, p1_test.user_id)
    user = UserState.get_user_by_id(p1_test.user_id)

    assert user.level == game_state.level
    assert user.map == game_state.map
