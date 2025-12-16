from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AsyncSessionDep
from app.schemas.auth import LoginRequest, Token
import app.services.auth as auth_service

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    data: LoginRequest,
    db: AsyncSessionDep,
) -> Token:
    user = await auth_service.authenticate_user(
        db,
        email=data.email,
        password=data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(
        subject=user.id,
        extra_claims={
            "role": user.role.value,
            "full_name": user.full_name,
            "email": user.email,
        },
    )
    return Token(access_token=access_token)