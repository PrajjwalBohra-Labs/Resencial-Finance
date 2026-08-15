import httpx
import pytest

from backend.app.core.config import get_settings
from backend.app.main import app


@pytest.mark.asyncio
async def test_health() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/api/health")

    assert response.status_code == 200

    data = response.json()
    settings = get_settings()

    assert data["status"] == "ok"
    assert data["service"] == "resencial-finance-api"
    assert data["version"] == settings.app_version
    assert data["environment"] == settings.app_env
