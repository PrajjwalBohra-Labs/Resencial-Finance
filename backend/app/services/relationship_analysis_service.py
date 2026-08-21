from __future__ import annotations

from backend.app.analytics.relationships import (
    calculate_benchmark_comparison,
    calculate_beta,
    calculate_correlation,
    calculate_covariance,
    calculate_rolling_correlation,
)
from backend.app.schemas.market import HistoricalPrice


class RelationshipAnalysisService:
    """Calculates relationships between an asset and a benchmark."""

    @staticmethod
    def _returns(
        prices: list[HistoricalPrice],
    ) -> list[float]:
        if len(prices) < 2:
            return []

        return [
            (
                (current.close / previous.close) - 1
            ) * 100
            for previous, current in zip(
                prices,
                prices[1:],
            )
            if previous.close != 0
        ]

    @staticmethod
    def _align(
        asset_prices: list[HistoricalPrice],
        benchmark_prices: list[HistoricalPrice],
    ) -> tuple[list[HistoricalPrice], list[HistoricalPrice]]:
        benchmark_by_date = {
            price.date: price
            for price in benchmark_prices
        }

        asset_aligned: list[HistoricalPrice] = []
        benchmark_aligned: list[HistoricalPrice] = []

        for asset_price in asset_prices:
            benchmark_price = benchmark_by_date.get(
                asset_price.date
            )

            if benchmark_price is None:
                continue

            asset_aligned.append(asset_price)
            benchmark_aligned.append(benchmark_price)

        if len(asset_aligned) < 2:
            raise ValueError(
                "At least two common price observations are required."
            )

        return asset_aligned, benchmark_aligned

    @classmethod
    def analyse(
        cls,
        asset_prices: list[HistoricalPrice],
        benchmark_prices: list[HistoricalPrice],
        *,
        rolling_window: int = 20,
    ) -> dict[str, object]:
        asset, benchmark = cls._align(
            asset_prices,
            benchmark_prices,
        )

        asset_returns = cls._returns(asset)
        benchmark_returns = cls._returns(benchmark)

        result: dict[str, object] = {
            "observations": len(asset),
            "return_observations": min(
                len(asset_returns),
                len(benchmark_returns),
            ),
            "correlation": None,
            "covariance": None,
            "beta": None,
            "rolling_correlation": [],
            "benchmark_comparison": calculate_benchmark_comparison(
                asset_start=asset[0].close,
                asset_end=asset[-1].close,
                benchmark_start=benchmark[0].close,
                benchmark_end=benchmark[-1].close,
            ),
        }

        if len(asset_returns) >= 2:
            try:
                result["correlation"] = calculate_correlation(
                    asset_returns,
                    benchmark_returns,
                )
            except ValueError:
                result["correlation"] = None

            try:
                result["covariance"] = calculate_covariance(
                    asset_returns,
                    benchmark_returns,
                )
            except ValueError:
                result["covariance"] = None

            try:
                result["beta"] = calculate_beta(
                    asset_returns,
                    benchmark_returns,
                )
            except ValueError:
                result["beta"] = None

        if len(asset_returns) >= rolling_window:
            result["rolling_correlation"] = (
                calculate_rolling_correlation(
                    asset_returns,
                    benchmark_returns,
                    rolling_window,
                )
            )

        return result
