from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.dependencies import get_auth_service
from app.schemas.auth import LoginRequest, LoginResponse, UserPublic
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    return service.login(payload)


@router.get("/me", response_model=UserPublic)
def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return current_user
