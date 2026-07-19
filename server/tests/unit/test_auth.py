from config import DEFAULT_ELO
from net import protocol
from net.auth import handle_login, handle_register
from net.session import Session
from persistence.db import connect
from persistence.users_repository import UsersRepository


def users_for(tmp_path) -> UsersRepository:
    return UsersRepository(connect(tmp_path / "test.db"))


def test_register_creates_a_user_and_authenticates_the_session(tmp_path):
    users = users_for(tmp_path)
    session = Session()
    response = handle_register({"username": "alice", "password": "hunter2"}, session, users)

    assert response == {
        "type": protocol.LOGIN_RESULT, "success": True, "reason": None,
        "username": "alice", "elo": DEFAULT_ELO,
    }
    assert session.is_authenticated
    assert session.user.username == "alice"


def test_register_with_a_taken_username_fails_and_does_not_authenticate(tmp_path):
    users = users_for(tmp_path)
    handle_register({"username": "alice", "password": "hunter2"}, Session(), users)

    session = Session()
    response = handle_register({"username": "alice", "password": "different"}, session, users)

    assert response == {
        "type": protocol.LOGIN_RESULT, "success": False, "reason": "username_taken",
        "username": None, "elo": None,
    }
    assert not session.is_authenticated


def test_login_with_correct_credentials_authenticates_the_session(tmp_path):
    users = users_for(tmp_path)
    handle_register({"username": "alice", "password": "hunter2"}, Session(), users)

    session = Session()
    response = handle_login({"username": "alice", "password": "hunter2"}, session, users)

    assert response["success"] is True
    assert response["username"] == "alice"
    assert session.user.username == "alice"


def test_login_with_wrong_password_fails_and_does_not_authenticate(tmp_path):
    users = users_for(tmp_path)
    handle_register({"username": "alice", "password": "hunter2"}, Session(), users)

    session = Session()
    response = handle_login({"username": "alice", "password": "wrong"}, session, users)

    assert response == {
        "type": protocol.LOGIN_RESULT, "success": False, "reason": "invalid_credentials",
        "username": None, "elo": None,
    }
    assert not session.is_authenticated


def test_login_with_unknown_username_fails(tmp_path):
    users = users_for(tmp_path)
    session = Session()
    response = handle_login({"username": "nobody", "password": "anything"}, session, users)
    assert response["success"] is False
    assert not session.is_authenticated
