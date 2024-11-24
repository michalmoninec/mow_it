from flask import jsonify
from app.types_validation import (
    UserID,
    validate_json,
    validate_user_in_db,
    validate_room_in_db,
)

from app.models.user_model import UserState
from app.models.game_state_model import GameState


def func_test(*args):
    return jsonify({"error": "FALSE"}), 200


def test_json_validation_not_instance(apply_validation, test_client):
    """
    Tests json validation decorator with empty payload.
    Response error should be "Invalid JSON payload."
    Resp status should be 400.
    """
    endpoint = "/"
    data = []
    validated_func = apply_validation(validate_json, UserID, func_test)

    test_client.post(endpoint, json=data)

    resp, resp_code = validated_func()
    resp_data = resp.get_json()
    assert resp_data["error"] == "Invalid JSON payload."
    assert resp_code == 400


def test_json_validation_empty_json(apply_validation, test_client):
    """
    Tests json validation decorator with empty payload.
    Response error should be "Missing field"
    Resp status should be 400.
    """
    endpoint = "/"
    data = {}
    validated_func = apply_validation(validate_json, UserID, func_test)

    test_client.post(endpoint, json=data)

    resp, resp_code = validated_func()
    resp_data = resp.get_json()
    assert resp_data["error"] == "Missing field"
    assert resp_code == 400


def test_json_validation_invalid_type(apply_validation, test_client):
    """
    Tests json validation decorator with empty payload.
    Response error should be "Invalid type."
    Resp status should be 400.
    """
    endpoint = "/"
    data = {"user_id": 55}
    validated_func = apply_validation(validate_json, UserID, func_test)

    test_client.post(endpoint, json=data)

    resp, resp_code = validated_func()
    resp_data = resp.get_json()
    assert resp_data["error"] == "Invalid type."
    assert resp_code == 400


def test_json_validation_valid(apply_validation, test_client):
    """
    Tests json validation decorator with empty payload.
    Response error should be "Invalid type."
    Resp status should be 400.
    """
    endpoint = "/"
    data = {"user_id": "55"}
    validated_func = apply_validation(validate_json, UserID, func_test)

    test_client.post(endpoint, json=data)

    resp, resp_code = validated_func()
    resp_data = resp.get_json()
    assert resp_data["error"] == "FALSE"
    assert resp_code == 200


def test_user_validation_in_db_not_found(apply_validation, test_client, test_db):
    """
    Tests, that user validation works correctly.
    Provided user ID is not inside db.
    Response error should be: "User not found in databse".
    Resp status should be 404.
    """
    endpoint = "/"
    data = {"user_id": "55"}
    validated_func = apply_validation(validate_user_in_db, UserState, func_test)

    test_client.post(endpoint, json=data)

    resp, resp_code = validated_func()
    resp_data = resp.get_json()
    assert resp_data["error"] == "User not found in databse"
    assert resp_code == 404


def test_user_validation_in_db_user_none(apply_validation, test_client, test_db):
    """
    Tests, that user validation works correctly.
    Provided user ID is None.
    Response error should be: "FALSE".
    Resp status should be 200.
    """
    endpoint = "/"
    data = {"user_id": None}
    validated_func = apply_validation(validate_user_in_db, UserState, func_test)

    test_client.post(endpoint, json=data)

    resp, resp_code = validated_func()
    resp_data = resp.get_json()
    assert resp_data["error"] == "FALSE"
    assert resp_code == 200


def test_user_validation_in_db_user_found(
    apply_validation, test_client, test_db, test_user
):
    """
    Tests, that user validation works correctly.
    Provided user ID is inside db.
    Response error should be: "FALSE".
    Resp status should be 200.
    """
    endpoint = "/"
    data = {"user_id": test_user.user_id}
    validated_func = apply_validation(validate_user_in_db, UserState, func_test)

    test_client.post(endpoint, json=data)

    resp, resp_code = validated_func()
    resp_data = resp.get_json()
    assert resp_data["error"] == "FALSE"
    assert resp_code == 200


def test_room_validation_in_db_not_found(apply_validation, test_client, test_db):
    """
    Tests, that user validation works correctly.
    Provided user ID is not inside db.
    Response error should be: "User not found in databse".
    Resp status should be 404.
    """

    data = {"room_id": "55"}
    validated_func = apply_validation(validate_room_in_db, GameState, func_test)

    resp, resp_code = validated_func(data)
    resp_data = resp.get_json()
    assert resp_data["error"] == "Room not found in databse"
    assert resp_code == 404


def test_room_validation_in_db_user_none(apply_validation, test_client, test_db):
    """
    Tests, that user validation works correctly.
    Provided user ID is None.
    Response error should be: "FALSE".
    Resp status should be 404.
    """

    data = {"room_id": None}
    validated_func = apply_validation(validate_room_in_db, GameState, func_test)

    resp, resp_code = validated_func(data)
    resp_data = resp.get_json()
    assert resp_data["error"] == "FALSE"
    assert resp_code == 200


def test_room_validation_in_db_user_found(
    apply_validation, test_client, test_db, test_game
):
    """
    Tests, that user validation works correctly.
    Provided user ID is  inside db.
    Response error should be: "FALSE".
    Resp status should be 200.
    """

    data = {"room_id": test_game.room_id}
    validated_func = apply_validation(validate_room_in_db, GameState, func_test)

    resp, resp_code = validated_func(data)
    resp_data = resp.get_json()
    assert resp_data["error"] == "FALSE"
    assert resp_code == 200
