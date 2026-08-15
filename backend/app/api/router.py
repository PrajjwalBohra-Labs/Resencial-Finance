from fastapi import APIRouter

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.markets import router as markets_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(markets_router)
