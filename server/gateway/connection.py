"""One websocket connection's mutable state: which user (if any) is
logged in, and which room (if any) it's currently seated in or spectating.
"""

import protocol
from gateway.session import Session


class Connection:
    def __init__(self, websocket):
        self.socket = websocket
        self.session = Session()
        self.room = None          # currently seated GameRoom, or None
        self.viewing_room = None  # currently spectating GameRoom, or None

    async def send(self, message: dict) -> None:
        await self.socket.send(protocol.encode(message))
