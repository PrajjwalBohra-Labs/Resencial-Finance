from datetime import date

from backend.app.instruments import (
    Bond,
    Equity,
    ETF,
    GovernmentSecurity,
    InstrumentType,
    InvIT,
    REIT,
    TBill,
)


def test_equity_model() -> None:
    equity = Equity(
        symbol="HDFCBANK",
        name="HDFC Bank Limited",
        exchange="NSE",
        isin="INE040A01034",
        sector="Financial Services",
        industry="Banks",
    )

    assert equity.instrument_type == InstrumentType.EQUITY
    assert equity.currency == "INR"
    assert equity.symbol == "HDFCBANK"


def test_bond_model() -> None:
    bond = Bond(
        symbol="TEST-BOND",
        name="Example Corporate Bond",
        issuer="Example Issuer",
        isin="INE000000000",
        coupon_rate=8.5,
        maturity_date=date(2030, 1, 1),
        credit_rating="AAA",
        rating_outlook="Stable",
    )

    assert bond.instrument_type == InstrumentType.BOND
    assert bond.coupon_rate == 8.5
    assert bond.maturity_date == date(2030, 1, 1)


def test_government_security_model() -> None:
    security = GovernmentSecurity(
        symbol="GS-2035",
        name="Government of India 7.25% 2035",
        issuer="Government of India",
        isin="IN0000000000",
        coupon_rate=7.25,
        maturity_date=date(2035, 6, 15),
    )

    assert security.instrument_type == InstrumentType.GOVERNMENT_SECURITY
    assert security.issuer == "Government of India"


def test_t_bill_model() -> None:
    t_bill = TBill(
        symbol="TBILL-364D",
        name="91 Day Treasury Bill",
        issuer="Government of India",
        maturity_date=date(2027, 8, 15),
        face_value=100.0,
    )

    assert t_bill.instrument_type == InstrumentType.T_BILL
    assert t_bill.face_value == 100.0


def test_etf_model() -> None:
    etf = ETF(
        symbol="NIFTYBEES",
        name="Nippon India ETF Nifty BeES",
        exchange="NSE",
        isin="INF204KB14I2",
        underlying_index="NIFTY 50",
    )

    assert etf.instrument_type == InstrumentType.ETF
    assert etf.underlying_index == "NIFTY 50"


def test_reit_model() -> None:
    reit = REIT(
        symbol="EXAMPLE-REIT",
        name="Example REIT",
        exchange="NSE",
        isin="INE000000000",
        sector="Real Estate",
    )

    assert reit.instrument_type == InstrumentType.REIT
    assert reit.sector == "Real Estate"


def test_invit_model() -> None:
    invit = InvIT(
        symbol="EXAMPLE-INVIT",
        name="Example Infrastructure InvIT",
        exchange="NSE",
        isin="INE000000000",
        sector="Infrastructure",
    )

    assert invit.instrument_type == InstrumentType.INVIT
    assert invit.sector == "Infrastructure"
