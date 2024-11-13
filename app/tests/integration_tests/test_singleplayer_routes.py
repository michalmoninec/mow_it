from flask import session, url_for


def test_get_single_player_level_selection(app_and_client):
    """
    Tests, that endpoint '/single_player/level_selection/' works correctly.
    """
    app, client = app_and_client

    resp = client.get("/single_player/level_selection/")

    assert resp.status_code == 200

    with app.test_request_context("/"):
        assert resp.request.path == url_for(
            "singleplayer.single_player_level_selection"
        )
