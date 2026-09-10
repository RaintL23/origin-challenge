from fastapi import APIRouter, Depends, Response, status

from app.auth import get_current_user
from app.dependencies import get_favorite_service
from app.schemas.auth import UserPublic
from app.schemas.favorites import FavoriteCreate, FavoriteStock
from app.services import FavoriteService

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteStock])
def list_favorites(
    current_user: UserPublic = Depends(get_current_user),
    service: FavoriteService = Depends(get_favorite_service),
) -> list[FavoriteStock]:
    return service.list_favorites(current_user.id)


@router.post("", response_model=FavoriteStock, status_code=status.HTTP_201_CREATED)
def create_favorite(
    payload: FavoriteCreate,
    current_user: UserPublic = Depends(get_current_user),
    service: FavoriteService = Depends(get_favorite_service),
) -> FavoriteStock:
    return service.add_favorite(current_user.id, payload)


@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(
    symbol: str,
    current_user: UserPublic = Depends(get_current_user),
    service: FavoriteService = Depends(get_favorite_service),
) -> Response:
    service.delete_favorite(current_user.id, symbol)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
