"""
astranotes.repository.user_repository
JSON-file-backed user store. Consistent with JsonFileRepository pattern (NFR-02).
One file per user: ~/.astranotes/users/{user_id}.json
"""
import json
from pathlib import Path
from typing import Optional

from astranotes.models.user import User, UserNotFoundError, UserAlreadyExistsError


class UserRepository:
    def __init__(self, users_dir: Path) -> None:
        self.users_dir = Path(users_dir)
        self.users_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, user_id: str) -> Path:
        return self.users_dir / f"{user_id}.json"

    def save(self, user: User) -> None:
        with open(self._path(user.id), "w", encoding="utf-8") as f:
            json.dump(user.to_dict(), f, indent=2)

    def get_by_username(self, username: str) -> Optional[User]:
        for path in self.users_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("username") == username:
                    return User.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                continue
        return None

    def get(self, user_id: str) -> User:
        path = self._path(user_id)
        if not path.exists():
            raise UserNotFoundError(user_id)
        with open(path, "r", encoding="utf-8") as f:
            return User.from_dict(json.load(f))

    def list_all(self) -> list:
        users = []
        for path in self.users_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    users.append(User.from_dict(json.load(f)))
            except (json.JSONDecodeError, KeyError):
                continue
        return sorted(users, key=lambda u: u.created_at)

    def username_exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None
