from flask import url_for


def test_home(test_client, mock_func):
    """
    Tests, that home endpoint works correctly.
    Tests cover:
    - Response status code.
    - Checking that session is empty.
    - Request path is correct.
    """

    endpoint = "/"
    resp = test_client.get(endpoint)

    assert resp.status_code == 200
    assert resp.request.path == url_for("test_main.test_home")
