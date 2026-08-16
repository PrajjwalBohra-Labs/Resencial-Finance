from backend.app.analytics.returns import (
    calculate_absolute_return,
    calculate_daily_price_changes,
    calculate_market_period_summary,
    calculate_percentage_return,
    calculate_price_summary,
)
from backend.app.analytics.risk import (
    calculate_annualised_volatility,
    calculate_cagr,
    calculate_max_drawdown,
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
            cagr=calculate_cagr(prices),
            maximum_drawdown=calculate_max_drawdown(prices),
            annualised_volatility=calculate_annualised_volatility(prices),
            price_summary=calculate_price_summary(prices),
            daily_changes=calculate_daily_price_changes(prices),
            period_summary=calculate_market_period_summary(prices),
        )
