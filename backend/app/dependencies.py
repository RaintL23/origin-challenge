from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
from app.integrations.twelvedata import TwelveDataClient
from app.repositories import (
    FavoriteRepository,
    JsonFavoriteRepository,
    JsonStore,
    JsonUserRepository,
    UserRepository,
)
from app.services import AuthService, FavoriteService, StockService


@lru_cache
def _store_for_path(db_path: str) -> JsonStore:
    from pathlib import Path

    return JsonStore(Path(db_path))


def get_json_store(settings: Settings = Depends(get_settings)) -> JsonStore:
    return _store_for_path(str(settings.db_path.resolve()))


def get_user_repo(store: JsonStore = Depends(get_json_store)) -> UserRepository:
    return JsonUserRepository(store)


def get_favorite_repo(store: JsonStore = Depends(get_json_store)) -> FavoriteRepository:
    return JsonFavoriteRepository(store)


def get_twelve_data_client(settings: Settings = Depends(get_settings)) -> TwelveDataClient:
    return TwelveDataClient(settings)


def get_auth_service(
    users: UserRepository = Depends(get_user_repo),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(users, settings)


def get_favorite_service(
    favorites: FavoriteRepository = Depends(get_favorite_repo),
) -> FavoriteService:
    return FavoriteService(favorites)


def get_stock_service(
    client: TwelveDataClient = Depends(get_twelve_data_client),
) -> StockService:
    return StockService(client)
