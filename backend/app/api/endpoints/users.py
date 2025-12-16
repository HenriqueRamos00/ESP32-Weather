from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AsyncSessionDep
from app.api.deps.jwt_auth import AdminDep, AdminOrUserDep
from app.schemas.user import User, UserCreate, UserUpdate, UserList
import app.services.user as user_service

router = APIRouter()

@router.get("/", response_model=UserList)
async def get_users(
    db: AsyncSessionDep,
    _: AdminDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    users = await user_service.get_all(db, skip=skip, limit=limit)
    total = await user_service.count(db)
    return {"users": users, "total": total}


@router.get("/me", response_model=User)
async def get_me(current_user: AdminOrUserDep) -> Any:
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSessionDep,
    _: AdminDep,
) -> Any:
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSessionDep,
    _: AdminDep,
) -> Any:
    # you can add explicit uniqueness checks here if you want
    user = await user_service.create(db, user_in)
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSessionDep,
    _: AdminDep,  # require admin
) -> Any:
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = await user_service.update(db, user, user_in)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSessionDep,
    _: AdminDep,  # require admin
) -> None:
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await user_service.delete(db, user)