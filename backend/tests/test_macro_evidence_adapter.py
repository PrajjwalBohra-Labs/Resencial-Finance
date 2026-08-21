from datetime import date, datetime, timezone

import pytest

from backend.app.data.evidence.macro_evidence_adapter import (
    MacroEvidenceAdapter,
)
from backend.app.domain.research import ResearchRequest
from backend.app.domain.research_sources import MacroObservation


class FakeMacroProvider:
    name = "fake-macro"

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def get_series(
        self,
        series_name: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MacroObservation]:
        self.calls.append(
            {
                "series_name": series_name,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        return [
            MacroObservation(
                series_name=series_name,
                observation_date=date(2026, 8, 11),
                value=6.25,
                unit="%",
                source_name="fake-rbi",
                url="https://example.test/macro",
                retrieved_at=datetime.now(timezone.utc),
                provider=self.name,
            )
        ]


@pytest.mark.asyncio
async def test_macro_adapter_returns_empty_for_blank_question() -> None:
    provider = FakeMacroProvider()
    adapter = MacroEvidenceAdapter(provider)

    request = ResearchRequest(
        question="   ",
    )

    evidence = await adapter.collect(request)

    assert evidence == []
    assert provider.calls == []


@pytest.mark.asyncio
async def test_macro_adapter_converts_observations_to_evidence() -> None:
    provider = FakeMacroProvider()
    adapter = MacroEvidenceAdapter(provider)

    request = ResearchRequest(
        question="India CPI inflation",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 11),
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 1

    item = evidence[0]

    assert item.evidence_type.value == "macro"
    assert item.title == "India CPI inflation"
    assert "Series: India CPI inflation" in item.content
    assert "Observation date: 2026-08-11" in item.content
    assert "Value: 6.25" in item.content
    assert "Unit: %" in item.content
    assert item.source.name == "fake-rbi"
    assert item.source.url == "https://example.test/macro"


@pytest.mark.asyncio
async def test_macro_adapter_passes_question_and_date_range_to_provider() -> None:
    provider = FakeMacroProvider()
    adapter = MacroEvidenceAdapter(provider)

    request = ResearchRequest(
        question="  India repo rate  ",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 11),
    )

    await adapter.collect(request)

    assert provider.calls == [
        {
            "series_name": "India repo rate",
            "start_date": date(2026, 8, 1),
            "end_date": date(2026, 8, 11),
        }
    ]


@pytest.mark.asyncio
async def test_macro_adapter_returns_all_observations() -> None:
    provider = FakeMacroProvider()

    original_get_series = provider.get_series

    async def get_multiple(
        series_name: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MacroObservation]:
        records = await original_get_series(
            series_name,
            start_date,
            end_date,
        )

        records.append(
            MacroObservation(
                series_name=series_name,
                observation_date=date(2026, 8, 10),
                value=6.10,
                unit="%",
                source_name="fake-rbi",
                url="https://example.test/macro",
                retrieved_at=datetime.now(timezone.utc),
                provider="fake-macro",
            )
        )

        return records

    provider.get_series = get_multiple

    adapter = MacroEvidenceAdapter(provider)

    request = ResearchRequest(
        question="India CPI inflation",
    )

    evidence = await adapter.collect(request)

    assert len(evidence) == 2
    assert [item.evidence_type.value for item in evidence] == [
        "macro",
        "macro",
    ]
