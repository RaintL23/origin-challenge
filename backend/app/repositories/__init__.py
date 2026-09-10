from __future__ import annotations

import json
import threading
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class JsonStore:
    """Thread-safe atomic read/write for the mock JSON database."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._write_unlocked({"users": [], "favorite_stocks": []})

    def read(self) -> dict[str, Any]:
        with self._lock:
            return self._read_unlocked()

    def mutate(self, mutator) -> dict[str, Any]:
        with self._lock:
            data = self._read_unlocked()
            result = mutator(data)
            self._write_unlocked(data)
            return result

    def _read_unlocked(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _write_unlocked(self, data: dict[str, Any]) -> None:
        tmp_path = self.path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        tmp_path.replace(self.path)


class UserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: int) -> dict[str, Any] | None:
        raise NotImplementedError


class FavoriteRepository(ABC):
    @abstractmethod
    def list_by_user(self, user_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def add(self, user_id: int, symbol: str, name: str, currency: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int, symbol: str) -> bool:
        raise NotImplementedError


class JsonUserRepository(UserRepository):
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def get_by_username(self, username: str) -> dict[str, Any] | None:
        data = self.store.read()
        for user in data.get("users", []):
            if user["username"].lower() == username.lower():
                return deepcopy(user)
        return None

    def get_by_id(self, user_id: int) -> dict[str, Any] | None:
        data = self.store.read()
        for user in data.get("users", []):
            if user["id"] == user_id:
                return deepcopy(user)
        return None


class JsonFavoriteRepository(FavoriteRepository):
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def list_by_user(self, user_id: int) -> list[dict[str, Any]]:
        data = self.store.read()
        favorites = [
            deepcopy(item)
            for item in data.get("favorite_stocks", [])
            if item["user_id"] == user_id
        ]
        favorites.sort(key=lambda item: item["symbol"])
        return favorites

    def add(self, user_id: int, symbol: str, name: str, currency: str) -> dict[str, Any]:
        normalized = symbol.upper().strip()

        def mutator(data: dict[str, Any]) -> dict[str, Any]:
            favorites = data.setdefault("favorite_stocks", [])
            for item in favorites:
                if item["user_id"] == user_id and item["symbol"].upper() == normalized:
                    raise ValueError("El símbolo ya está en preferidas")

            next_id = max((item["id"] for item in favorites), default=0) + 1
            created = {
                "id": next_id,
                "user_id": user_id,
                "symbol": normalized,
                "name": name.strip(),
                "currency": currency.strip().upper(),
                "created_at": _utc_now(),
            }
            favorites.append(created)
            return deepcopy(created)

        return self.store.mutate(mutator)

    def delete(self, user_id: int, symbol: str) -> bool:
        normalized = symbol.upper().strip()

        def mutator(data: dict[str, Any]) -> bool:
            favorites = data.setdefault("favorite_stocks", [])
            for index, item in enumerate(favorites):
                if item["user_id"] == user_id and item["symbol"].upper() == normalized:
                    favorites.pop(index)
                    return True
            return False

        return self.store.mutate(mutator)
