from typing import List, TypedDict
from functools import wraps
from flask import jsonify, request

NestedDictList = List[List[dict[str, dict | int]]]


class UserID(TypedDict):
    user_id: str | None


class LevelAndUserID(TypedDict, UserID):
    selected_level: int


class KeyAndUserID(TypedDict, UserID):
    key: str


class RoomAndUserID(TypedDict, UserID):
    room_id: str


def validate_json(typed_dict):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()

            if not (isinstance(data, dict)):
                return jsonify({"error": "Invalid JSON payload."}), 400

            try:
                for field, field_type in typed_dict.__annotations__.items():
                    if field not in data:
                        raise KeyError("Missing field")
                    if not isinstance(data[field], field_type):
                        raise TypeError("Invalid type.")
                validated_data = typed_dict(**data)
            except (KeyError, TypeError) as e:
                return jsonify({"error": str(e)}), 400

            return func(validated_data, *args, **kwargs)

        return wrapper

    return decorator


def validate_user_in_db(user_model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            user_id = data.get("user_id")
            if user_id and not user_model.get_user_by_id(user_id):
                return jsonify({"error": "User not found in databse"}), 404
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_room_in_db(room_model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            room_id = data.get("room_id")
            if room_id and not room_model.get_game_state_by_room(room_id):
                return jsonify({"error": "Room not found in databse"}), 404
            return func(*args, **kwargs)

        return wrapper

    return decorator
