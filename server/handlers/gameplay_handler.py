"""request_move / request_jump - only meaningful once seated in a room;
an unseated connection sending either gets the same bad_message error an
unregistered message type would (see router/message_router.py)."""

import protocol


async def handle_request_move(connection, message: dict) -> None:
    if connection.room is None:
        await connection.send(protocol.error("bad_message", f"unexpected message: {message['type']}"))
        return
    connection.room.handle_request_move(connection.socket, message)


async def handle_request_jump(connection, message: dict) -> None:
    if connection.room is None:
        await connection.send(protocol.error("bad_message", f"unexpected message: {message['type']}"))
        return
    connection.room.handle_request_jump(connection.socket, message)
