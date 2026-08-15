from datetime import date

from backend.app.data.providers.market import MarketDataProvider
from backend.app.instruments import Equity, InstrumentResolver
from backend.app.schemas.market import HistoricalPrice, Quote


class MarketService:
    """Application service for market-data retrieval."""

    def __init__(
        self,
        provider: MarketDataProvider,
        resolver: InstrumentResolver,
    ) -> None:
        self._provider = provider
        self._resolver = resolver

    @property
    def provider_name(self) -> str:
        return self._provider.name

    async def get_quote(
        self,
        symbol: str,
        exchange: str,
    ) -> Quote:
        resolved = self._resolver.resolve_equity(
            symbol=symbol,
            exchange=exchange,
        )

        quote = await self._provider.get_quote(
            resolved.provider_symbol,
        )

        return quote.model_copy(
            update={
                "symbol": resolved.symbol,
                "exchange": resolved.exchange,
                "provider_symbol": resolved.provider_symbol,
            }
        )

    async def get_historical_prices(
        self,
        symbol: str,
        exchange: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        if start_date > end_date:
            raise ValueError(
                "start_date must be before or equal to end_date."
            )

        resolved = self._resolver.resolve_equity(
            symbol=symbol,
            exchange=exchange,
        )

        return await self._provider.get_historical_prices(
            symbol=resolved.provider_symbol,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_equity(
        self,
        symbol: str,
        exchange: str,
    ) -> Equity | None:
        resolved = self._resolver.resolve_equity(
            symbol=symbol,
            exchange=exchange,
        )

        equity = await self._provider.get_equity(
            resolved.provider_symbol,
        )

        if equity is None:
            return None

        return equity.model_copy(
            update={
                "symbol": resolved.symbol,
                "exchange": resolved.exchange,
            }
        )
