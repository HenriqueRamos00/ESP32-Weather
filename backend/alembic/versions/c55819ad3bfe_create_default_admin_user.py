"""create default admin user

Revision ID: c55819ad3bfe
Revises: c1a0a7a6639e
Create Date: 2025-12-16 14:34:19.374777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c55819ad3bfe'
down_revision: Union[str, Sequence[str], None] = 'c1a0a7a6639e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create default admin user."""
    from app.core.config import settings
    from app.services.auth import get_password_hash
    from app.models.user import UserRole
    
    conn = op.get_bind()
    
    # Check if admin user already exists
    result = conn.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE email = :email"),
        {"email": settings.ADMIN_USER}
    ).scalar()
    
    if result == 0:
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
        
        # Insert admin user (created_at will use server_default=func.now())
        conn.execute(
            sa.text("""
                INSERT INTO users (email, full_name, hashed_password, role, is_active)
                VALUES (:email, :full_name, :hashed_password, :role, :is_active)
            """),
            {
                "email": settings.ADMIN_USER,
                "full_name": "System Administrator",
                "hashed_password": hashed_password,
                "role": "ADMIN",
                "is_active": True,
            }
        )
        print(f"✓ Admin user created: {settings.ADMIN_USER}")
    else:
        print(f"✓ Admin user already exists: {settings.ADMIN_USER}")


def downgrade() -> None:
    """Remove default admin user."""
    from app.core.config import settings
    
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM users WHERE email = :email"),
        {"email": settings.ADMIN_USER}
    )
    print(f"✓ Admin user removed: {settings.ADMIN_USER}")
