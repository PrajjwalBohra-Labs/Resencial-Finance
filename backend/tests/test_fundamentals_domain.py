from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.app.domain.fundamentals import (
    BalanceSheet,
    CashFlowStatement,
    FinancialPeriod,
    FundamentalsSnapshot,
    GrowthMetrics,
    IncomeStatement,
    ProfitabilityMetrics,
    ValuationMetrics,
)


def test_financial_period_defaults_to_inr() -> None:
    period = FinancialPeriod(
        period_end=datetime(
            2026,
            3,
            31,
            tzinfo=timezone.utc,
        )
    )

    assert period.currency == "INR"


def test_income_statement_preserves_typed_financial_fields() -> None:
    statement = IncomeStatement(
        period=FinancialPeriod(
            period_end=datetime(
                2026,
                3,
                31,
                tzinfo=timezone.utc,
            )
        ),
        total_revenue=1_000_000.0,
        net_income=200_000.0,
        basic_eps=45.89,
        diluted_eps=45.75,
        net_interest_income=750_000.0,
    )

    assert statement.total_revenue == 1_000_000.0
    assert statement.net_income == 200_000.0
    assert statement.basic_eps == 45.89
    assert statement.diluted_eps == 45.75
    assert statement.net_interest_income == 750_000.0


def test_balance_sheet_preserves_typed_financial_fields() -> None:
    statement = BalanceSheet(
        period=FinancialPeriod(
            period_end=datetime(
                2026,
                3,
                31,
                tzinfo=timezone.utc,
            )
        ),
        total_assets=5_000_000.0,
        total_liabilities=4_500_000.0,
        stockholders_equity=500_000.0,
        net_loan=3_000_000.0,
    )

    assert statement.total_assets == 5_000_000.0
    assert statement.total_liabilities == 4_500_000.0
    assert statement.stockholders_equity == 500_000.0
    assert statement.net_loan == 3_000_000.0


def test_cash_flow_statement_preserves_typed_financial_fields() -> None:
    statement = CashFlowStatement(
        period=FinancialPeriod(
            period_end=datetime(
                2026,
                3,
                31,
                tzinfo=timezone.utc,
            )
        ),
        operating_cash_flow=250_000.0,
        free_cash_flow=180_000.0,
        capital_expenditure=-70_000.0,
    )

    assert statement.operating_cash_flow == 250_000.0
    assert statement.free_cash_flow == 180_000.0
    assert statement.capital_expenditure == -70_000.0


def test_fundamentals_snapshot_groups_typed_metrics() -> None:
    snapshot = FundamentalsSnapshot(
        symbol="HDFCBANK",
        exchange="NSE",
        income_statement=IncomeStatement(
            period=FinancialPeriod(
                period_end=datetime(
                    2026,
                    3,
                    31,
                    tzinfo=timezone.utc,
                )
            ),
            total_revenue=1_000_000.0,
        ),
        valuation=ValuationMetrics(
            trailing_pe=15.94,
            price_to_book=1.85,
        ),
        profitability=ProfitabilityMetrics(
            return_on_equity=13.84,
        ),
        growth=GrowthMetrics(
            revenue_growth=16.6,
        ),
        retrieved_at=datetime.now(timezone.utc),
        provider="yahoo_finance",
    )

    assert snapshot.symbol == "HDFCBANK"
    assert snapshot.exchange == "NSE"
    assert snapshot.income_statement is not None
    assert snapshot.income_statement.total_revenue == 1_000_000.0
    assert snapshot.valuation.trailing_pe == 15.94
    assert snapshot.valuation.price_to_book == 1.85
    assert snapshot.profitability.return_on_equity == 13.84
    assert snapshot.growth.revenue_growth == 16.6


def test_fundamentals_snapshot_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        FundamentalsSnapshot(
            symbol="HDFCBANK",
            retrieved_at=datetime.now(timezone.utc),
            provider="yahoo_finance",
            unexpected_field="should_not_be_allowed",
        )


def test_financial_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        IncomeStatement(
            period=FinancialPeriod(
                period_end=datetime(
                    2026,
                    3,
                    31,
                    tzinfo=timezone.utc,
                )
            ),
            yahoo_field="provider_specific",
        )
