from fastapi import HTTPException, status

from app.repositories import FavoriteRepository
from app.schemas.favorites import FavoriteCreate, FavoriteStock


class FavoriteService:
    def __init__(self, favorites: FavoriteRepository) -> None:
        self.favorites = favorites

    def list_favorites(self, user_id: int) -> list[FavoriteStock]:
        return [FavoriteStock(**item) for item in self.favorites.list_by_user(user_id)]

    def add_favorite(self, user_id: int, payload: FavoriteCreate) -> FavoriteStock:
        try:
            created = self.favorites.add(
                user_id=user_id,
                symbol=payload.symbol,
                name=payload.name,
                currency=payload.currency,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        return FavoriteStock(**created)

    def delete_favorite(self, user_id: int, symbol: str) -> None:
        deleted = self.favorites.delete(user_id, symbol)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Símbolo no encontrado en preferidas",
            )
