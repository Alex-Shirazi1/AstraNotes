"""
astranotes.models.user
User entity for multi-user web UI.
Traces to: web authentication layer (FR extension for web UI)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


class UserNotFoundError(Exception):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"User not found: {username}")


class UserAlreadyExistsError(Exception):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Username already taken: {username}")


@dataclass
class User:
    """
    Registered user. Password is stored as a pbkdf2 hash — never plaintext.
    Each user gets an isolated notes directory: ~/.astranotes/data/{user_id}/
    Roles: "admin" can access the /admin dashboard; "user" cannot.
    """
    username: str
    password_hash: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    role: str = "user"  # "admin" | "user"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "created_at": self.created_at.isoformat(),
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            created_at=datetime.fromisoformat(data["created_at"]),
            role=data.get("role", "user"),  # backwards-compat: old users default to "user"
        )
