import asyncio

from app.core.config import settings
from app.db.session import engine
from app.services.auth import get_password_hash
from app.models.user import User, UserRole

async def ensure_admin():
    async with engine.begin() as db:
        result = await db.execute(
            sa.select(User).where(User.email == settings.ADMIN_USER)
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            # Optionally ensure role / is_active are correct
            updated = False
            if admin.role != UserRole.ADMIN:
                admin.role = UserRole.ADMIN
                updated = True
            if not admin.is_active:
                admin.is_active = True
                updated = True
            if updated:
                await db.execute(
                    sa.update(User)
                    .where(User.email == settings.ADMIN_USER)
                    .values(role=admin.role, is_active=admin.is_active)
                )
                print(f"✓ Admin user updated: {settings.ADMIN_USER}")
            else:
                print(f"✓ Admin user already exists: {settings.ADMIN_USER}")
            return
        
        # Create admin - use dictionary instead of model instance
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
        
        await db.execute(
            sa.insert(User).values(
                email=settings.ADMIN_USER,
                full_name="System Administrator",
                hashed_password=hashed_password,
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        print(f"✓ Admin user created: {settings.ADMIN_USER}")

if __name__ == "__main__":
    import sqlalchemy as sa  # or move import to top
    asyncio.run(ensure_admin())