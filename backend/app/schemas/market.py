from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.schemas.common import DataFreshness, Source


class Quote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    exchange: str | None = None
    provider_symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    source: Source
    freshness: DataFreshness


class HistoricalPrice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class PriceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    starting_price: float
    latest_price: float
    highest_close: float
    lowest_close: float


class ReturnAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    absolute_return: float
    percentage_return: float
    cagr: float
    maximum_drawdown: float
    annualised_volatility: float
    price_summary: PriceSummary


class HistoricalPricesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    exchange: str
    start_date: str
    end_date: str
    count: int
    data: list[HistoricalPrice]
    analysis: ReturnAnalysis
    source: Source
    freshness: DataFreshness
