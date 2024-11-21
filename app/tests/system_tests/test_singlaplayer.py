def test_home(test_client, test_user):
    """
    Tests singleplayer gameplay.
    Starts at home page, then folows to level selection.
    Selects first level.
    Play few moves, finishes level, advance to another level.
    """
    endpoint = "/"
    test_client.get(endpoint)

    endpoint = "/single_player/level_selection"
    test_client.get(endpoint)

    endpoint = "/single_player/level_data/"
    payload = {
        "user_id": None,
    }
    resp = test_client.post(endpoint, json=payload)
    resp_data = resp.get_json()
    user_id = resp_data["user_id"]

    endpoint = "/single_player/selected_level/"
    payload = {
        "user_id": user_id,
        "selected_level": 1,
    }
    resp = test_client.post(endpoint, json=payload)
    resp_data = resp.get_json()

    if not resp_data["valid_level_set"]:
        assert False

    endpoint = "/single_player/"
    test_client.get(endpoint)

    endpoint = "/single_player/retrieve_map/"
    payload = {
        "user_id": user_id,
    }
    resp = test_client.post(endpoint, json=payload)
    resp_data = resp.get_json()
    user_state = resp_data["user_state"]

    endpoint = "/single_player/move/"
    payload = {"user_id": user_id, "key": "ArrowDown"}
    resp = test_client.post(endpoint, json=payload)
    resp_data = resp.get_json()
    user_state = resp_data["user_state"]
    print(f"level completed: {user_state['completed']}")

    endpoint = "/single_player/move/"
    payload = {"user_id": user_id, "key": "ArrowDown"}
    resp = test_client.post(endpoint, json=payload)
    resp_data = resp.get_json()
    user_state = resp_data["user_state"]
    print(f"level completed: {user_state['completed']}")

    endpoint = "/single_player/move/"
    payload = {"user_id": user_id, "key": "ArrowDown"}
    resp = test_client.post(endpoint, json=payload)
    resp_data = resp.get_json()
    user_state = resp_data["user_state"]

    print(f"level completed: {user_state['completed']}")
