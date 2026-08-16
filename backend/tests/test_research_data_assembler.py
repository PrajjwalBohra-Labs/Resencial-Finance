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


@pytest.mark.asyncio
async def test_assemble_uses_request_date_range() -> None:
    service = FakeMarketService()
    assembler = ResearchDataAssembler(service)

    request = ResearchRequest(
        question="Analyse HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    context = await assembler.assemble(request)

    assert context.request == request
    assert len(context.evidence) == 1


@pytest.mark.asyncio
async def test_assemble_without_dates_returns_empty_context() -> None:
    service = FakeMarketService()
    assembler = ResearchDataAssembler(service)

    request = ResearchRequest(
        question="Explain HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
    )

    context = await assembler.assemble(request)

    assert context.request == request
    assert context.evidence == []


@pytest.mark.asyncio
async def test_assemble_without_symbols_returns_empty_context() -> None:
    service = FakeMarketService()
    assembler = ResearchDataAssembler(service)

    request = ResearchRequest(
        question="Explain the Indian banking sector.",
    )

    context = await assembler.assemble(request)

    assert context.request == request
    assert context.evidence == []


@pytest.mark.asyncio
async def test_assemble_uses_request_date_range() -> None:
    service = FakeMarketService()
    assembler = ResearchDataAssembler(service)

    request = ResearchRequest(
        question="Analyse HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    context = await assembler.assemble(request)

    assert context.request == request
    assert len(context.evidence) == 1


@pytest.mark.asyncio
async def test_assemble_without_dates_returns_empty_context() -> None:
    service = FakeMarketService()
    assembler = ResearchDataAssembler(service)

    request = ResearchRequest(
        question="Explain HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
    )

    context = await assembler.assemble(request)

    assert context.request == request
    assert context.evidence == []


@pytest.mark.asyncio
async def test_assemble_without_symbols_returns_empty_context() -> None:
    service = FakeMarketService()
    assembler = ResearchDataAssembler(service)

    request = ResearchRequest(
        question="Explain the Indian banking sector.",
    )

    context = await assembler.assemble(request)

    assert context.request == request
    assert context.evidence == []

@pytest.mark.asyncio
async def test_assemble_market_context_includes_deterministic_market_metrics() -> None:
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

    assert len(context.evidence) == 1

    content = context.evidence[0].content

    assert "Daily open-to-close changes:" in content
    assert "2026-08-10:" in content
    assert "2026-08-11:" in content
    assert "Period high:" in content
    assert "Period low:" in content
    assert "Total volume:" in content
    assert "Average daily volume:" in content
from backend.app.services.fundamentals_service import FundamentalsService
from backend.app.services.market_service import MarketService
from backend.app.services.research_data_assembler import ResearchDataAssembler


class FakeFundamentalsProvider:
    name = "fake-fundamentals"

    async def get_income_statement(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        return [
            {
                "period": "2026-03-31",
                "Total Revenue": 1000000.0,
                "Net Income": 200000.0,
            }
        ]

    async def get_balance_sheet(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        return [
            {
                "period": "2026-03-31",
                "Total Assets": 5000000.0,
            }
        ]

    async def get_cash_flow(
        self,
        symbol: str,
    ) -> list[dict[str, object]]:
        return [
            {
                "period": "2026-03-31",
                "Operating Cash Flow": 250000.0,
            }
        ]

    async def get_key_ratios(
        self,
        symbol: str,
    ) -> dict[str, object]:
        return {
            "marketCap": 1500000000000,
            "trailingPE": 18.5,
            "priceToBook": 2.4,
        }


@pytest.mark.asyncio
async def test_fundamental_focus_adds_fundamental_evidence() -> None:
    fundamentals_service = FundamentalsService(
        provider=FakeFundamentalsProvider(),
    )

    assembler = ResearchDataAssembler(
        market_service=FakeMarketService(),
        fundamentals_service=fundamentals_service,
    )

    request = ResearchRequest(
        question="Analyse the fundamentals of HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.FUNDAMENTAL,
    )

    context = await assembler.assemble(request)

    assert len(context.evidence) == 1
    assert context.evidence[0].evidence_type.value == "fundamental"
    assert context.evidence[0].symbol == "HDFCBANK"
    assert "Total Revenue" in context.evidence[0].content
    assert "trailingPE" in context.evidence[0].content


@pytest.mark.asyncio
async def test_market_focus_does_not_add_fundamental_evidence() -> None:
    fundamentals_service = FundamentalsService(
        provider=FakeFundamentalsProvider(),
    )

    assembler = ResearchDataAssembler(
        market_service=FakeMarketService(),
        fundamentals_service=fundamentals_service,
    )

    request = ResearchRequest(
        question="Analyse HDFC Bank market performance.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        focus=ResearchFocus.MARKET,
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    context = await assembler.assemble(request)

    assert len(context.evidence) == 1
    assert all(
        item.evidence_type.value != "fundamental"
        for item in context.evidence
    )


