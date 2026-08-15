from datetime import date

import pytest

from backend.app.data.providers import (
    BondDataProvider,
    FilingsProvider,
    FundamentalsProvider,
    MacroDataProvider,
    MarketDataProvider,
    NewsProvider,
)


def test_provider_interfaces_are_abstract() -> None:
    provider_types = [
        BondDataProvider,
        FilingsProvider,
        FundamentalsProvider,
        MacroDataProvider,
        MarketDataProvider,
        NewsProvider,
    ]

    for provider_type in provider_types:
        with pytest.raises(TypeError):
            provider_type()
