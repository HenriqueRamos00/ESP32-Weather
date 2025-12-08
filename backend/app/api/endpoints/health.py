from fastapi import APIRouter
from sqlalchemy import text
from app.api.deps import AsyncSessionDep

router = APIRouter()


@router.get("/")
async def health_check(db: AsyncSessionDep) -> dict[str, str]:
    """Health check endpoint."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy",
        "database": db_status,
    }