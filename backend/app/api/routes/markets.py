from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.core.exceptions import MarketDataProviderError
from backend.app.data.providers import YahooFinanceMarketProvider
from backend.app.instruments import InstrumentResolutionError, resolver
from backend.app.schemas import (
    DataFreshness,
    HistoricalPricesResponse,
    Quote,
    Source,
)
from backend.app.services.market_analysis_service import (
    MarketAnalysisService,
)
from backend.app.services.market_service import MarketService

router = APIRouter(prefix="/markets", tags=["markets"])


def get_market_service() -> MarketService:
    return MarketService(
        provider=YahooFinanceMarketProvider(),
        resolver=resolver,
    )


def get_market_analysis_service() -> MarketAnalysisService:
    return MarketAnalysisService()


@router.get("/quote/{symbol}", response_model=Quote)
async def get_quote(
    symbol: str,
    exchange: str = Query(..., min_length=1),
    service: MarketService = Depends(get_market_service),
) -> Quote:
    try:
        return await service.get_quote(
            symbol=symbol,
            exchange=exchange,
        )
    except InstrumentResolutionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail="Market data provider is temporarily unavailable.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/history/{symbol}",
    response_model=HistoricalPricesResponse,
)
async def get_historical_prices(
    symbol: str,
    exchange: str = Query(..., min_length=1),
    start_date: date = Query(...),
    end_date: date = Query(...),
    service: MarketService = Depends(get_market_service),
    analysis_service: MarketAnalysisService = Depends(
        get_market_analysis_service,
    ),
) -> HistoricalPricesResponse:
    try:
        prices = await service.get_historical_prices(
            symbol=symbol,
            exchange=exchange,
            start_date=start_date,
            end_date=end_date,
        )
    except InstrumentResolutionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail="Market data provider is temporarily unavailable.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    analysis = analysis_service.analyse_prices(prices)

    retrieved_at = datetime.now(timezone.utc)

    return HistoricalPricesResponse(
        symbol=symbol.upper(),
        exchange=exchange.upper(),
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        count=len(prices),
        data=prices,
        analysis=analysis,
        source=Source(
            name="Yahoo Finance",
            type="market_data",
            provider="yahoo_finance",
        ),
        freshness=DataFreshness(
            observed_at=None,
            retrieved_at=retrieved_at,
            status="fresh",
        ),
    )
