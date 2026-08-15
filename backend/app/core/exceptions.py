class MarketDataProviderError(Exception):
    """Raised when the market-data provider cannot fulfill a request."""


class LLMProviderError(Exception):
    """Raised when the language-model provider cannot fulfill a request."""
