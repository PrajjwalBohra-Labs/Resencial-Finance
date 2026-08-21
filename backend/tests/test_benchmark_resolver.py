import pytest

from backend.app.services.benchmark_resolver import (
    BenchmarkResolutionError,
    BenchmarkResolver,
)


def test_resolves_nse_benchmark() -> None:
    resolver = BenchmarkResolver()

    result = resolver.resolve("NSE")

    assert result.symbol == "^NSEI"
    assert result.exchange == "NSE"
    assert result.name == "NIFTY 50"


def test_resolves_bse_benchmark() -> None:
    resolver = BenchmarkResolver()

    result = resolver.resolve("BSE")

    assert result.symbol == "^BSESN"
    assert result.exchange == "BSE"
    assert result.name == "SENSEX"


def test_exchange_resolution_is_case_insensitive() -> None:
    resolver = BenchmarkResolver()

    assert resolver.resolve("nse").name == "NIFTY 50"
    assert resolver.resolve("bse").name == "SENSEX"


def test_unsupported_exchange_is_rejected() -> None:
    resolver = BenchmarkResolver()

    with pytest.raises(
        BenchmarkResolutionError,
        match="No default benchmark is configured",
    ):
        resolver.resolve("NYSE")
