from datetime import date

import pytest

from backend.app.domain.research import ResearchRequest
from backend.app.ports import (
    BondEvidencePort,
    FilingEvidencePort,
    MacroEvidencePort,
    MarketEvidencePort,
    NewsEvidencePort,
)


@pytest.mark.parametrize(
    "port_type",
    [
        MarketEvidencePort,
        NewsEvidencePort,
        FilingEvidencePort,
        MacroEvidencePort,
        BondEvidencePort,
    ],
)
def test_evidence_ports_are_abstract(port_type: type) -> None:
    with pytest.raises(TypeError):
        port_type()


def test_research_evidence_ports_share_collect_contract() -> None:
    request = ResearchRequest(
        question="Research HDFC Bank.",
        symbols=["HDFCBANK"],
        exchange="NSE",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 11),
    )

    assert request.symbols == ["HDFCBANK"]
    assert request.exchange == "NSE"
