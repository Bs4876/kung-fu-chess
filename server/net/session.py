"""Per-connection state: which (if any) authenticated user is on this socket."""


class Session:
    def __init__(self):
        self.user = None  # a persistence.users_repository.User once logged in

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None
