from fastapi import Depends
from psycopg_pool import ConnectionPool

from app.config import Settings, get_settings
from app.db import get_connection_pool
from app.integrations.twelvedata import TwelveDataClient
from app.repositories import FavoriteRepository, UserRepository
from app.repositories.postgres import PostgresFavoriteRepository, PostgresUserRepository
from app.services import AuthService, FavoriteService, StockService


def get_db_pool(settings: Settings = Depends(get_settings)) -> ConnectionPool:
    return get_connection_pool(settings)


def get_user_repo(pool: ConnectionPool = Depends(get_db_pool)) -> UserRepository:
    return PostgresUserRepository(pool)


def get_favorite_repo(pool: ConnectionPool = Depends(get_db_pool)) -> FavoriteRepository:
    return PostgresFavoriteRepository(pool)


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
