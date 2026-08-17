import pytest
from pydantic import ValidationError

from backend.app.core.config import Settings


def test_settings_provider_resilience_defaults() -> None:
    settings = Settings()

    assert settings.provider_timeout_seconds == 15.0
    assert settings.provider_max_retries == 2
    assert settings.provider_retry_base_delay_seconds == 0.25
    assert settings.provider_retry_max_delay_seconds == 2.0
    assert settings.provider_retry_jitter_seconds == 0.1


@pytest.mark.parametrize(
    "field,value",
    [
        ("provider_timeout_seconds", 0),
        ("provider_timeout_seconds", -1),
        ("provider_max_retries", -1),
        ("provider_retry_base_delay_seconds", -1),
        ("provider_retry_max_delay_seconds", -1),
        ("provider_retry_jitter_seconds", -1),
    ],
)
def test_settings_reject_invalid_provider_resilience_values(
    field: str,
    value: float | int,
) -> None:
    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_settings_reject_inverted_retry_delay_bounds() -> None:
    with pytest.raises(
        ValidationError,
        match="provider_retry_max_delay_seconds",
    ):
        Settings(
            provider_retry_base_delay_seconds=2.0,
            provider_retry_max_delay_seconds=1.0,
        )


def test_settings_accept_zero_retry_delay() -> None:
    settings = Settings(
        provider_retry_base_delay_seconds=0.0,
        provider_retry_max_delay_seconds=0.0,
        provider_retry_jitter_seconds=0.0,
    )

    assert settings.provider_retry_base_delay_seconds == 0.0
    assert settings.provider_retry_max_delay_seconds == 0.0
    assert settings.provider_retry_jitter_seconds == 0.0
