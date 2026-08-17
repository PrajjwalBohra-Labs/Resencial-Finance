import pytest

from backend.app.core.provider_retry import ProviderRetryPolicy


def test_retry_policy_rejects_negative_retries() -> None:
    with pytest.raises(ValueError, match="max_retries"):
        ProviderRetryPolicy(
            max_retries=-1,
            base_delay_seconds=0.1,
            max_delay_seconds=1.0,
            jitter_seconds=0.0,
        )


def test_retry_policy_rejects_invalid_delay_bounds() -> None:
    with pytest.raises(ValueError, match="max_delay_seconds"):
        ProviderRetryPolicy(
            max_retries=2,
            base_delay_seconds=2.0,
            max_delay_seconds=1.0,
            jitter_seconds=0.0,
        )


def test_retry_policy_allows_configured_attempts() -> None:
    policy = ProviderRetryPolicy(
        max_retries=2,
        base_delay_seconds=0.1,
        max_delay_seconds=1.0,
        jitter_seconds=0.0,
    )

    assert policy.should_retry(0)
    assert policy.should_retry(1)
    assert not policy.should_retry(2)


def test_retry_delay_uses_exponential_backoff() -> None:
    policy = ProviderRetryPolicy(
        max_retries=3,
        base_delay_seconds=0.25,
        max_delay_seconds=2.0,
        jitter_seconds=0.0,
    )

    assert policy.delay_for(0) == 0.25
    assert policy.delay_for(1) == 0.5
    assert policy.delay_for(2) == 1.0


def test_retry_delay_is_capped() -> None:
    policy = ProviderRetryPolicy(
        max_retries=10,
        base_delay_seconds=1.0,
        max_delay_seconds=2.0,
        jitter_seconds=0.0,
    )

    assert policy.delay_for(10) == 2.0


def test_retry_delay_includes_bounded_jitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.app.core.provider_retry.random.uniform",
        lambda _lower, _upper: 0.05,
    )

    policy = ProviderRetryPolicy(
        max_retries=2,
        base_delay_seconds=0.25,
        max_delay_seconds=2.0,
        jitter_seconds=0.1,
    )

    assert policy.delay_for(0) == 0.30
