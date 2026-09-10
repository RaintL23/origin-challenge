from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from psycopg import errors
from psycopg_pool import ConnectionPool

from app.repositories import FavoriteRepository, UserRepository


def _fmt_ts(value: Any) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return (
            value.astimezone(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
    return str(value)


def _user_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "password_hash": row["password_hash"],
        "display_name": row["display_name"],
        "created_at": _fmt_ts(row["created_at"]),
    }


def _favorite_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "symbol": row["symbol"],
        "name": row["name"],
        "currency": row["currency"],
        "created_at": _fmt_ts(row["created_at"]),
    }


class PostgresUserRepository(UserRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool = pool

    def get_by_username(self, username: str) -> dict[str, Any] | None:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, password_hash, display_name, created_at
                    FROM users
                    WHERE LOWER(username) = LOWER(%s)
                    """,
                    (username,),
                )
                return _user_row(cur.fetchone())

    def get_by_id(self, user_id: int) -> dict[str, Any] | None:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, password_hash, display_name, created_at
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,),
                )
                return _user_row(cur.fetchone())


class PostgresFavoriteRepository(FavoriteRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool = pool

    def list_by_user(self, user_id: int) -> list[dict[str, Any]]:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_id, symbol, name, currency, created_at
                    FROM favorite_stocks
                    WHERE user_id = %s
                    ORDER BY symbol
                    """,
                    (user_id,),
                )
                return [_favorite_row(row) for row in cur.fetchall()]

    def add(self, user_id: int, symbol: str, name: str, currency: str) -> dict[str, Any]:
        normalized = symbol.upper().strip()
        try:
            with self.pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO favorite_stocks (user_id, symbol, name, currency)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, user_id, symbol, name, currency, created_at
                        """,
                        (
                            user_id,
                            normalized,
                            name.strip(),
                            currency.strip().upper(),
                        ),
                    )
                    row = cur.fetchone()
                    conn.commit()
                    assert row is not None
                    return _favorite_row(row)
        except errors.UniqueViolation as exc:
            raise ValueError("El símbolo ya está en preferidas") from exc

    def delete(self, user_id: int, symbol: str) -> bool:
        normalized = symbol.upper().strip()
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM favorite_stocks
                    WHERE user_id = %s AND UPPER(symbol) = %s
                    """,
                    (user_id, normalized),
                )
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted
