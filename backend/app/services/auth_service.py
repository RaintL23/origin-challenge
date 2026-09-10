from fastapi import HTTPException, status

from app.auth.security import create_access_token, user_to_public, verify_password
from app.config import Settings
from app.repositories import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse


class AuthService:
    def __init__(self, users: UserRepository, settings: Settings) -> None:
        self.users = users
        self.settings = settings

    def login(self, payload: LoginRequest) -> LoginResponse:
        user = self.users.get_by_username(payload.username)
        if user is None or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="usuario o clave invalida",
            )

        token = create_access_token(user["id"], user["username"], self.settings)
        return LoginResponse(access_token=token, user=user_to_public(user))
