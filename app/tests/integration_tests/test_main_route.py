from flask import session, url_for


def test_home(app_and_client, mock_func):
    """
    Tests, that home endpoint works correctly.
    Tests cover:
    - Response status code.
    - Checking that session is empty.
    - Call count of mocked fucntion inside endpoint.
    - Request path is correct.
    """
    mock_create = mock_func("app.routes.main_route.create_maps")
    app, client = app_and_client
    resp = client.get("/")

    assert resp.status_code == 200
    assert len(session.items()) == 0
    assert mock_create.call_count == 1

    with app.test_request_context("/"):
        assert resp.request.path == url_for("main.home")
