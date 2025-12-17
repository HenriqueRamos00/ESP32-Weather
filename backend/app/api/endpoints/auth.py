from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AsyncSessionDep
from app.schemas.auth import Token
import app.services.auth as auth_service

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSessionDep,
) -> Token:
    # Swagger will send "username", you can treat it as email
    user = await auth_service.authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password,
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
    return Token(access_token=access_token, token_type="bearer")