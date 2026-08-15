from backend.app.analytics.returns import (
    calculate_absolute_return,
    calculate_percentage_return,
    calculate_price_summary,
)
from backend.app.schemas.market import (
    HistoricalPrice,
    ReturnAnalysis,
)


class MarketAnalysisService:
    """Deterministic analysis of market price observations."""

    @staticmethod
    def analyse_prices(
        prices: list[HistoricalPrice],
    ) -> ReturnAnalysis:
        return ReturnAnalysis(
            absolute_return=calculate_absolute_return(prices),
            percentage_return=calculate_percentage_return(prices),
            price_summary=calculate_price_summary(prices),
        )
