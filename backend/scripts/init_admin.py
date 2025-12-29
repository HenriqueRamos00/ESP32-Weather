import argparse
import asyncio
import sys
from getpass import getpass

import sqlalchemy as sa

from app.core.config import settings
from app.db.session import engine
from app.models.user import User, UserRole
from app.services.auth import get_password_hash


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create or fix the initial admin account.")

    p.add_argument(
        "--email",
        default=getattr(settings, "ADMIN_USER", None),
        help="Admin email (defaults to settings.ADMIN_USER if set).",
    )
    p.add_argument(
        "--full-name",
        default="System Administrator",
        help="Admin full name (default: System Administrator).",
    )

    pw = p.add_mutually_exclusive_group()
    pw.add_argument(
        "--password",
        help="Admin password (WARNING: ends up in shell history/process list).",
    )
    pw.add_argument(
        "--password-stdin",
        action="store_true",
        help="Read admin password from stdin (safer).",
    )
    pw.add_argument(
        "--prompt-password",
        action="store_true",
        help="Prompt for admin password interactively (safer).",
    )

    p.add_argument(
        "--force-password-update",
        action="store_true",
        help="If admin exists, also overwrite their password.",
    )

    return p.parse_args()


def read_password(args: argparse.Namespace) -> str:
    if args.password is not None:
        return args.password
    if args.password_stdin:
        return sys.stdin.read().rstrip("\n")
    if args.prompt_password:
        return getpass("Admin password: ")

    # Fallback: use settings.ADMIN_PASSWORD if present, otherwise prompt
    pw = getattr(settings, "ADMIN_PASSWORD", None)
    if pw:
        return pw
    return getpass("Admin password: ")


async def ensure_admin(email: str, password: str, full_name: str, force_pw_update: bool) -> None:
    async with engine.begin() as db:
        result = await db.execute(sa.select(User).where(User.email == email))
        admin = result.scalar_one_or_none()

        if admin:
            values_to_update = {}

            if admin.role != UserRole.ADMIN:
                values_to_update["role"] = UserRole.ADMIN
            if not admin.is_active:
                values_to_update["is_active"] = True
            if force_pw_update:
                values_to_update["hashed_password"] = get_password_hash(password)

            if values_to_update:
                await db.execute(
                    sa.update(User)
                    .where(User.email == email)
                    .values(**values_to_update)
                )
                print(f"✓ Admin updated: {email}")
            else:
                print(f"✓ Admin already exists: {email}")
            return

        await db.execute(
            sa.insert(User).values(
                email=email,
                full_name=full_name,
                hashed_password=get_password_hash(password),
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        print(f"✓ Admin created: {email}")


def main() -> None:
    args = parse_args()

    if not args.email:
        raise SystemExit("ERROR: --email is required (or set ADMIN_USER in settings).")

    password = read_password(args)
    if not password:
        raise SystemExit("ERROR: Empty password not allowed.")

    asyncio.run(
        ensure_admin(
            email=args.email,
            password=password,
            full_name=args.full_name,
            force_pw_update=args.force_password_update,
        )
    )


if __name__ == "__main__":
    main()