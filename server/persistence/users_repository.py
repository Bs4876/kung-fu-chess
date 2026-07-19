"""SQLite-backed user accounts: username/password + ELO rating."""

import sqlite3
from dataclasses import dataclass

from config import DEFAULT_ELO
from persistence.passwords import hash_password, verify_password


@dataclass
class User:
    id: int
    username: str
    elo: int


class UsersRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def create_user(self, username: str, password: str) -> User:
        """Raises sqlite3.IntegrityError if username is already taken."""
        password_hash, salt = hash_password(password)
        cursor = self._connection.execute(
            "INSERT INTO users (username, password_hash, password_salt, elo, created_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (username, password_hash, salt, DEFAULT_ELO),
        )
        self._connection.commit()
        return User(id=cursor.lastrowid, username=username, elo=DEFAULT_ELO)

    def get_by_username(self, username: str) -> User | None:
        row = self._connection.execute(
            "SELECT id, username, elo FROM users WHERE username = ?", (username,)
        ).fetchone()
        return User(*row) if row is not None else None

    def verify_password(self, username: str, password: str) -> bool:
        row = self._connection.execute(
            "SELECT password_hash, password_salt FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row is None:
            return False
        password_hash, salt = row
        return verify_password(password, password_hash, salt)

    def update_elo(self, username: str, new_elo: int) -> None:
        self._connection.execute("UPDATE users SET elo = ? WHERE username = ?", (new_elo, username))
        self._connection.commit()
