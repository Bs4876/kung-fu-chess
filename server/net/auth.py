"""Pure login/register message handling: authenticates or creates an
account, updates the connection's Session, and returns the wire response.

No socket I/O here (see net/ws_server.py for where these get called from a
real connection) - message-in, response-out, the same testing philosophy as
GameRoom's handle_request_move/handle_request_jump.
"""

import sqlite3

from net import protocol
from net.session import Session
from persistence.users_repository import UsersRepository


def handle_login(message: dict, session: Session, users: UsersRepository) -> dict:
    username, password = message["username"], message["password"]
    if not users.verify_password(username, password):
        return protocol.login_result(False, "invalid_credentials", None, None)
    user = users.get_by_username(username)
    session.user = user
    return protocol.login_result(True, None, user.username, user.elo)


def handle_register(message: dict, session: Session, users: UsersRepository) -> dict:
    username, password = message["username"], message["password"]
    try:
        user = users.create_user(username, password)
    except sqlite3.IntegrityError:
        return protocol.login_result(False, "username_taken", None, None)
    session.user = user
    return protocol.login_result(True, None, user.username, user.elo)
