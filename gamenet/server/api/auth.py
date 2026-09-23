from fastapi import APIRouter, Depends, HTTPException

from gamenet.server.db import get_connection
from gamenet.server.models.schemas import CurrentUserResponse, LoginRequest, LoginResponse
from gamenet.server.security.auth import get_current_user, login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login_operator(payload: LoginRequest) -> LoginResponse:
    with get_connection() as conn:
        result = login(conn, payload.username, payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token, expires_at, user = result
    return LoginResponse(
        access_token=token,
        expires_at=expires_at,
        user=CurrentUserResponse(**user),
    )


@router.get("/me", response_model=CurrentUserResponse)
def current_user(user: dict = Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse(**user)