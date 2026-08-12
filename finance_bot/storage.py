import json
import os
import threading


class TokenStorage:
    """Простое персистентное хранилище access_token по telegram user_id."""

    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._data: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f)

    def get_token(self, user_id: int) -> str | None:
        return self._data.get(str(user_id))

    def set_token(self, user_id: int, token: str) -> None:
        with self._lock:
            self._data[str(user_id)] = token
            self._save()

    def clear_token(self, user_id: int) -> None:
        with self._lock:
            self._data.pop(str(user_id), None)
            self._save()
