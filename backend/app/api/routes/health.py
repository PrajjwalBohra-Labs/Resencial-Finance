from fastapi import APIRouter

from backend.app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()

    return {
        "status": "ok",
        "service": "resencial-finance-api",
        "version": settings.app_version,
        "environment": settings.app_env,
    }
