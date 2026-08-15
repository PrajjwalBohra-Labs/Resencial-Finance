from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=f"{settings.app_name} API",
    description="Indian financial research intelligence platform.",
    version=settings.app_version,
)

app.include_router(api_router)
