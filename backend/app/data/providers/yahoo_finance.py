import asyncio
from datetime import date, datetime, timedelta, timezone

import yfinance as yf

from backend.app.core.exceptions import MarketDataProviderError
from backend.app.data.providers.market import MarketDataProvider
from backend.app.instruments import Equity
from backend.app.schemas import DataFreshness, HistoricalPrice, Quote, Source


class YahooFinanceMarketProvider(MarketDataProvider):
    """Market-data provider backed by Yahoo Finance via yfinance."""

    @property
    def name(self) -> str:
        return "yahoo_finance"

    @staticmethod
    def _to_yahoo_symbol(
        symbol: str,
        exchange: str | None = None,
    ) -> str:
        normalized_symbol = symbol.strip().upper()

        if "." in normalized_symbol:
            return normalized_symbol

        if exchange:
            normalized_exchange = exchange.strip().upper()

            if normalized_exchange == "NSE":
                return f"{normalized_symbol}.NS"

            if normalized_exchange == "BSE":
                return f"{normalized_symbol}.BO"

        return normalized_symbol

    @staticmethod
    def _source() -> Source:
        return Source(
            name="Yahoo Finance",
            type="market_data",
            provider="yahoo_finance",
        )

    @staticmethod
    def _retrieved_at() -> datetime:
        return datetime.now(timezone.utc)

    async def get_quote(self, symbol: str) -> Quote:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> Quote:
            try:
                ticker = yf.Ticker(yahoo_symbol)

                history = ticker.history(
                    period="1d",
                    interval="1m",
                    auto_adjust=False,
                    prepost=False,
                )

                if history.empty:
                    raise ValueError(
                        f"No market data returned for symbol '{yahoo_symbol}'."
                    )

                latest = history.iloc[-1]
                timestamp = history.index[-1]

                if isinstance(timestamp, datetime):
                    quote_timestamp = timestamp
                else:
                    quote_timestamp = timestamp.to_pydatetime()

                retrieved_at = self._retrieved_at()

                return Quote(
                    symbol=symbol.upper(),
                    provider_symbol=yahoo_symbol,
                    timestamp=quote_timestamp,
                    open=float(latest["Open"]),
                    high=float(latest["High"]),
                    low=float(latest["Low"]),
                    close=float(latest["Close"]),
                    volume=int(latest["Volume"]),
                    source=self._source(),
                    freshness=DataFreshness(
                        observed_at=quote_timestamp,
                        retrieved_at=retrieved_at,
                        status="fresh",
                    ),
                )
            except ValueError:
                raise
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide the requested quote."
                ) from exc

        return await asyncio.to_thread(fetch)

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> list[HistoricalPrice]:
            try:
                ticker = yf.Ticker(yahoo_symbol)

                history = ticker.history(
                    start=start_date,
                    end=end_date + timedelta(days=1),
                    interval="1d",
                    auto_adjust=False,
                    prepost=False,
                )

                if history.empty:
                    return []

                prices: list[HistoricalPrice] = []

                for timestamp, row in history.iterrows():
                    prices.append(
                        HistoricalPrice(
                            date=timestamp.date().isoformat(),
                            open=float(row["Open"]),
                            high=float(row["High"]),
                            low=float(row["Low"]),
                            close=float(row["Close"]),
                            volume=int(row["Volume"]),
                        )
                    )

                return prices
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide historical market data."
                ) from exc

        return await asyncio.to_thread(fetch)

    async def get_equity(
        self,
        symbol: str,
    ) -> Equity | None:
        yahoo_symbol = self._to_yahoo_symbol(symbol)

        def fetch() -> Equity | None:
            try:
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.info

                if not info:
                    return None

                return Equity(
                    symbol=symbol.upper(),
                    name=info.get("longName")
                    or info.get("shortName")
                    or symbol.upper(),
                    exchange=info.get("exchange"),
                    isin=info.get("isin"),
                    sector=info.get("sector"),
                    industry=info.get("industry"),
                )
            except Exception as exc:
                raise MarketDataProviderError(
                    "Yahoo Finance could not provide instrument information."
                ) from exc

        return await asyncio.to_thread(fetch)
