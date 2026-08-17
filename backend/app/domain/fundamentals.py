from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FinancialPeriod(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period_end: datetime
    currency: str = "INR"


class IncomeStatement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: FinancialPeriod

    total_revenue: float | None = None
    net_income: float | None = None
    basic_eps: float | None = None
    diluted_eps: float | None = None
    net_interest_income: float | None = None
    interest_income: float | None = None
    interest_expense: float | None = None


class BalanceSheet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: FinancialPeriod

    total_assets: float | None = None
    total_liabilities: float | None = None
    stockholders_equity: float | None = None
    common_stock_equity: float | None = None
    net_loan: float | None = None
    cash_and_cash_equivalents: float | None = None
    tangible_book_value: float | None = None


class CashFlowStatement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: FinancialPeriod

    operating_cash_flow: float | None = None
    free_cash_flow: float | None = None
    capital_expenditure: float | None = None
    cash_dividends_paid: float | None = None
    changes_in_cash: float | None = None


class ValuationMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    market_capitalization: float | None = None
    enterprise_value: float | None = None
    trailing_pe: float | None = None
    forward_pe: float | None = None
    price_to_book: float | None = None


class ProfitabilityMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    return_on_equity: float | None = None
    return_on_assets: float | None = None
    profit_margin: float | None = None
    operating_margin: float | None = None


class GrowthMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revenue_growth: float | None = None
    earnings_growth: float | None = None


class FundamentalsSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    exchange: str | None = None
    currency: str = "INR"

    income_statement: IncomeStatement | None = None
    balance_sheet: BalanceSheet | None = None
    cash_flow: CashFlowStatement | None = None

    valuation: ValuationMetrics = Field(
        default_factory=ValuationMetrics
    )
    profitability: ProfitabilityMetrics = Field(
        default_factory=ProfitabilityMetrics
    )
    growth: GrowthMetrics = Field(
        default_factory=GrowthMetrics
    )

    dividend_yield: float | None = None

    retrieved_at: datetime
    provider: str
