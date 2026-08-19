from pydantic import BaseModel, ConfigDict, Field


class FundamentalPeriod(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: str
    revenue: float | None = None
    net_income: float | None = None
    basic_eps: float | None = None
    diluted_eps: float | None = None
    total_assets: float | None = None
    stockholders_equity: float | None = None
    net_loans: float | None = None
    operating_cash_flow: float | None = None
    free_cash_flow: float | None = None


class FundamentalAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latest_period: str | None = None
    previous_period: str | None = None

    revenue_growth: float | None = None
    net_income_growth: float | None = None
    basic_eps_growth: float | None = None
    diluted_eps_growth: float | None = None
    asset_growth: float | None = None
    equity_growth: float | None = None

    trailing_pe: float | None = None
    forward_pe: float | None = None
    price_to_book: float | None = None
    return_on_equity: float | None = None
    return_on_assets: float | None = None
    profit_margin: float | None = None
    operating_margin: float | None = None
    revenue_growth_reported: float | None = None
    earnings_growth_reported: float | None = None
    dividend_yield: float | None = None

    market_cap: float | None = None
    enterprise_value: float | None = None

    currency: str | None = None

    observations: list[FundamentalPeriod] = Field(
        default_factory=list,
    )
