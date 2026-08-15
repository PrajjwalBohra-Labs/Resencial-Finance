from datetime import date

import pytest

from backend.app.domain.research import ResearchFocus, ResearchRequest
from backend.app.services.research_data_assembler import ResearchDataAssembler


class FakeMarketService:
    provider_name = "test_provider"

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def get_historical_prices(
        self,
        *,
        symbol: str,
        exchange: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, object]]:
        self.calls.append(
            {
                "symbol": symbol,
                "exchange": exchange,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return [
            {
                "date": "2026-08-10",
                "open": 748.0,
                "high": 752.0,
                "low": 745.0,
                "close": 750.0,
                "volume": 1000000,
            },
            {
                "date": "2026-08-11",
                "open": 750.0,
                "high": 758.0,
                "low": 749.0,
                "close": 755.0,
                "volume": 1200000,
            },
        ]


@pytest.mark.asyncio
async def test_assemble_market_context() -> None:
    market_service = FakeMarketService()
    assembler = ResearchDataAssembler(market_service)

    request = ResearchRequest(
        question="Research HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.MARKET,
    )

    context = await assembler.assemble_market_context(
        request=request,
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    assert context.request == request
    assert len(context.evidence) == 1

    evidence = context.evidence[0]

    assert evidence.symbol == "HDFCBANK"
    assert evidence.exchange == "NSE"
    assert evidence.source.provider == "test_provider"
    assert evidence.evidence_type.value == "market_data"


@pytest.mark.asyncio
async def test_assemble_market_context_supports_multiple_symbols() -> None:
    market_service = FakeMarketService()
    assembler = ResearchDataAssembler(market_service)

    request = ResearchRequest(
        question="Compare HDFC Bank and ICICI Bank.",
        symbols=["HDFCBANK", "ICICIBANK"],
        exchange="NSE",
        focus=ResearchFocus.COMPARISON,
    )

    context = await assembler.assemble_market_context(
        request=request,
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    assert len(context.evidence) == 2
    assert len(market_service.calls) == 2

    assert market_service.calls[0]["symbol"] == "HDFCBANK"
    assert market_service.calls[1]["symbol"] == "ICICIBANK"


@pytest.mark.asyncio
async def test_assemble_market_context_defaults_to_nse() -> None:
    market_service = FakeMarketService()
    assembler = ResearchDataAssembler(market_service)

    request = ResearchRequest(
        question="Research HDFC Bank.",
        symbols=["HDFCBANK"],
    )

    await assembler.assemble_market_context(
        request=request,
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    assert market_service.calls[0]["exchange"] == "NSE"


@pytest.mark.asyncio
async def test_assemble_market_context_skips_missing_market_data() -> None:
    class EmptyMarketService(FakeMarketService):
        async def get_historical_prices(
            self,
            *,
            symbol: str,
            exchange: str,
            start_date: date,
            end_date: date,
        ) -> list[dict[str, object]]:
            return []

    market_service = EmptyMarketService()
    assembler = ResearchDataAssembler(market_service)

    request = ResearchRequest(
        question="Research an instrument.",
        symbols=["UNKNOWN"],
        exchange="NSE",
    )

    context = await assembler.assemble_market_context(
        request=request,
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    assert context.evidence == []


@pytest.mark.asyncio
async def test_assemble_market_context_rejects_invalid_date_range() -> None:
    market_service = FakeMarketService()
    assembler = ResearchDataAssembler(market_service)

    request = ResearchRequest(
        question="Research HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
    )

    with pytest.raises(
        ValueError,
        match="start_date must be before or equal to end_date",
    ):
        await assembler.assemble_market_context(
            request=request,
            start_date=date(2026, 8, 11),
            end_date=date(2026, 8, 10),
        )

    assert market_service.calls == []
