from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User as UserModel, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import get_password_hash


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[UserModel]:
    stmt = (
        select(UserModel)
        .offset(skip)
        .limit(limit)
        .order_by(UserModel.id.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_by_id(db: AsyncSession, user_id: int) -> UserModel | None:
    return await db.get(UserModel, user_id)


async def get_by_email(db: AsyncSession, email: str) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user_in: UserCreate) -> UserModel:
    hashed_password = get_password_hash(user_in.password)

    user = UserModel(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        role=user_in.role or UserRole.USER,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update(
    db: AsyncSession,
    user: UserModel,
    user_in: UserUpdate,
) -> UserModel:
    data = user_in.model_dump(exclude_unset=True)

    # Handle password specially
    if "password" in data:
        user.hashed_password = get_password_hash(data.pop("password"))

    for field, value in data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: UserModel) -> None:
    await db.delete(user)
    await db.flush()


async def count(db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(UserModel)
    result = await db.execute(stmt)
    return result.scalar_one()