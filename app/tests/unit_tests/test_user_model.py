from app.models.user_model import UserState


def test_user_state_init(test_user_data):
    """
    Tests, that init method works correctly.
    """
    user_state = UserState(**test_user_data)

    for key in test_user_data:
        assert user_state.__getattribute__(key) == test_user_data[key]
