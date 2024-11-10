from flask import session, url_for


# def test_home(app_and_client):
#     app, client = app_and_client
#     resp = client.get("/")
#     assert resp.status_code == 200
#     assert len(session.items()) == 0

#     with app.test_request_context("/"):
#         assert resp.request.path == url_for("main.home")
