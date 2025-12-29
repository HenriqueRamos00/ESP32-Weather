"""Seed default settings

Revision ID: 77dbd20ff606
Revises: 149860f5b46d
Create Date: 2025-12-29 15:08:25.137114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77dbd20ff606'
down_revision: Union[str, Sequence[str], None] = '149860f5b46d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_SETTINGS = {
    "offline_threshold_seconds": {
        "value": "300",
        "description": "Number of seconds before a device is considered offline",
    },
    # "max_devices_per_user": {
    #     "value": "10",
    #     "description": "Maximum number of devices a user can register",
    # },
    # "data_retention_days": {
    #     "value": "90",
    #     "description": "Number of days to retain device data",
    # },
}

def upgrade() -> None:
    conn = op.get_bind()

    settings = sa.table(
        "settings",
        sa.column("key", sa.String()),
        sa.column("value", sa.String()),
        sa.column("description", sa.String()),
    )

    for key, data in DEFAULT_SETTINGS.items():
        value = data["value"]
        description = data.get("description")

        # Check if row exists
        row = conn.execute(
            sa.select(settings.c.key, settings.c.value, settings.c.description)
            .where(settings.c.key == key)
        ).fetchone()

        if row is None:
            # Insert new default
            conn.execute(
                sa.insert(settings).values(key=key, value=value, description=description)
            )
        else:
            # Only update description if changed (matching your script behavior)
            if row.description != description:
                conn.execute(
                    sa.update(settings)
                    .where(settings.c.key == key)
                    .values(description=description)
                )


def downgrade() -> None:
    conn = op.get_bind()

    settings = sa.table(
        "settings",
        sa.column("key", sa.String()),
    )

    # Be careful: deleting by key will remove user-customized values too.
    # If you prefer, you can make downgrade a no-op instead.
    conn.execute(
        sa.delete(settings).where(settings.c.key.in_(list(DEFAULT_SETTINGS.keys())))
    )