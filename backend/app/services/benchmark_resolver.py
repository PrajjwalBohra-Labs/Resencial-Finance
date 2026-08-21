from __future__ import annotations

from dataclasses import dataclass


class BenchmarkResolutionError(ValueError):
    """Raised when no supported benchmark can be resolved."""


@dataclass(frozen=True)
class ResolvedBenchmark:
    symbol: str
    exchange: str
    name: str
    rationale: str


class BenchmarkResolver:
    """Resolves the default broad-market benchmark for an exchange."""

    _BENCHMARKS: dict[str, ResolvedBenchmark] = {
        "NSE": ResolvedBenchmark(
            symbol="^NSEI",
            exchange="NSE",
            name="NIFTY 50",
            rationale="Broad NSE large-cap market benchmark.",
        ),
        "BSE": ResolvedBenchmark(
            symbol="^BSESN",
            exchange="BSE",
            name="SENSEX",
            rationale="Broad BSE large-cap market benchmark.",
        ),
    }

    def resolve(self, exchange: str) -> ResolvedBenchmark:
        normalized = exchange.strip().upper()

        try:
            return self._BENCHMARKS[normalized]
        except KeyError as exc:
            raise BenchmarkResolutionError(
                f"No default benchmark is configured for exchange "
                f"'{normalized}'."
            ) from exc


benchmark_resolver = BenchmarkResolver()
