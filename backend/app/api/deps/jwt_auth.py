from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings  # must provide SECRET_KEY, ALGORITHM
from app.db.session import get_db
from app.models.user import User as UserModel, UserRole


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    description="JWT access token",
)

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = await db.get(UserModel, user_id)
    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def require_role(*allowed_roles: UserRole) -> Callable:
    if not allowed_roles:
        raise ValueError("At least one allowed role must be provided")

    async def role_checker(
        current_user: Annotated[UserModel, Depends(get_current_active_user)],
    ) -> UserModel:
        if current_user.role not in allowed_roles:
            allowed = ", ".join(r.value for r in allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions, requires one of: {allowed}",
            )
        return current_user

    return role_checker

AdminDep = Annotated[UserModel, Depends(require_role(UserRole.ADMIN))]
AdminOrUserDep = Annotated[UserModel, Depends(require_role(UserRole.ADMIN, UserRole.USER))]