import pytest

from backend.app.instruments import (
    InstrumentResolutionError,
    InstrumentType,
    InstrumentResolver,
)


def test_resolve_nse_equity() -> None:
    resolver = InstrumentResolver()

    result = resolver.resolve_equity(
        symbol="HDFCBANK",
        exchange="NSE",
    )

    assert result.symbol == "HDFCBANK"
    assert result.exchange == "NSE"
    assert result.instrument_type == InstrumentType.EQUITY
    assert result.provider_symbol == "HDFCBANK.NS"


def test_resolve_bse_equity() -> None:
    resolver = InstrumentResolver()

    result = resolver.resolve_equity(
        symbol="500180",
        exchange="BSE",
    )

    assert result.symbol == "500180"
    assert result.exchange == "BSE"
    assert result.instrument_type == InstrumentType.EQUITY
    assert result.provider_symbol == "500180.BO"


def test_existing_nse_suffix_is_not_duplicated() -> None:
    resolver = InstrumentResolver()

    result = resolver.resolve_equity(
        symbol="HDFCBANK.NS",
        exchange="NSE",
    )

    assert result.provider_symbol == "HDFCBANK.NS"


def test_symbol_and_exchange_are_normalized() -> None:
    resolver = InstrumentResolver()

    result = resolver.resolve_equity(
        symbol=" hdfcBank ",
        exchange=" nse ",
    )

    assert result.symbol == "HDFCBANK"
    assert result.exchange == "NSE"
    assert result.provider_symbol == "HDFCBANK.NS"


def test_empty_symbol_is_rejected() -> None:
    resolver = InstrumentResolver()

    with pytest.raises(
        InstrumentResolutionError,
        match="Instrument symbol cannot be empty",
    ):
        resolver.resolve_equity(
            symbol="   ",
            exchange="NSE",
        )


def test_unsupported_exchange_is_rejected() -> None:
    resolver = InstrumentResolver()

    with pytest.raises(
        InstrumentResolutionError,
        match="Unsupported exchange",
    ):
        resolver.resolve_equity(
            symbol="HDFCBANK",
            exchange="NYSE",
        )
