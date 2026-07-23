"""login - the one operation that doesn't need require_authenticated,
since it's what authenticates the connection in the first place."""

from services import auth_service


async def handle_login(connection, message: dict, users) -> None:
    await connection.send(auth_service.handle_login(message, connection.session, users))
