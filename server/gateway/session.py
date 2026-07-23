"""Per-connection state: which (if any) authenticated user is on this socket."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from persistence.users_repository import User


class Session:
    def __init__(self):
        self.user: "User | None" = None

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None
