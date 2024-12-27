from app.enums import Status


def test_multiplayer(two_clients, two_socket_clients, test_map):
    """Tests multiplayer game.
    One player creates game, other joins it.
    Test cover one level completion.
    """
    client1, client2 = two_clients
    socket1, socket2 = two_socket_clients

    client1.get("/")
    client1.get("/multiplayer/create/")

    endpoint = "/multiplayer/create/"
    payload = {"user_id": None}
    resp = client1.post(endpoint, json=payload)
    resp_data = resp.get_json()
    user1_id = resp_data["user_id"]
    room_id = resp_data["room_id"]

    endpoint = f"/multiplayer/join/{room_id}/"
    payload = {
        "user_id": user1_id,
        "room_id": room_id,
    }
    resp = client1.post(endpoint, json=payload)
    resp_data = resp.get_json()

    endpoint = "/multiplayer/play/"
    client1.get(endpoint)

    endpoint = "/multiplayer/play/"
    payload = {
        "user_id": user1_id,
        "room_id": room_id,
    }
    resp = client1.post(endpoint, json=payload)

    event = "join_room"
    payload = {
        "user_id": user1_id,
        "room_id": room_id,
    }
    socket1.emit(event, payload)
    received_events = socket1.get_received()
    rec_event = received_events[0]["args"][0]
    assert rec_event["game_status"] == Status.JOIN_WAIT.value

    endpoint = f"/multiplayer/join/{room_id}/"
    client2.get(endpoint)

    endpoint = f"/multiplayer/join/{room_id}/"
    payload = {
        "user_id": None,
        "room_id": room_id,
    }
    resp = client2.post(endpoint, json=payload)
    resp_data = resp.get_json()
    user2_id = resp_data["user_id"]

    endpoint = "/multiplayer/play/"
    client2.get(endpoint)

    payload = {
        "user_id": user2_id,
        "room_id": room_id,
    }
    resp = client2.post(endpoint, json=payload)

    event = "join_room"
    socket2.emit(event, payload)
    received_events = socket2.get_received()
    rec_event = received_events[0]["args"][0]
    assert rec_event["game_status"] == Status.READY.value

    event = "request_maps_from_server"
    payload = {"room_id": room_id}
    socket2.emit(event, payload)

    s1_events = socket1.get_received()
    s2_events = socket2.get_received()

    event = "request_initial_maps"
    payload = {"user_id": user1_id, "room_id": room_id}
    socket1.emit(event, payload)
    payload["user_id"] = user2_id
    socket2.emit(event, payload)
    s1_events = socket1.get_received()
    s2_events = socket2.get_received()

    event = "request_update_data"
    payload = {
        "user_id": user1_id,
        "room_id": room_id,
        "key": "ArrowDown",
    }
    socket1.emit(event, payload)
    payload["user_id"] = user2_id
    socket2.emit(event, payload)

    socket1.get_received()
    socket2.get_received()

    event = "request_update_data"
    payload = {
        "user_id": user1_id,
        "room_id": room_id,
        "key": "ArrowDown",
    }
    socket1.emit(event, payload)
    payload["user_id"] = user2_id
    socket2.emit(event, payload)

    s1_events = socket1.get_received()
    s2_events = socket2.get_received()

    s1_event_data = s1_events[0]["args"][0]
    s2_event_data = s2_events[2]["args"][0]

    assert s1_event_data["level_completed"] == True
    assert s2_event_data["level_completed"] == True
