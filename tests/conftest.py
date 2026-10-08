import json
import types

import pytest


def good_payload(**overrides):
    payload = {
        "summary": "One medium signal on routing cost.",
        "limitations": "Public web and X only. No private or paywalled data. Events after the scan are not covered.",
        "human_review_required": True,
        "signals": [
            {
                "headline": "Carriers extend Cape routing on Asia-Europe lanes",
                "category": "sector",
                "severity": "medium",
                "confidence": 0.78,
                "exposure_matched": "E1",
                "covenant_relevance": "C1: longer voyages raise fuel cost and may lift net debt / EBITDA",
                "why_it_matters": "Longer transit times raise voyage cost for Europe-bound services.",
                "sources": ["https://example.com/shipping-news/cape-routing"],
                "published_date": "2026-10-05",
                "source_type": "web",
            }
        ],
    }
    payload.update(overrides)
    return payload


class FakeResponses:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return types.SimpleNamespace(output_text=json.dumps(self.payload))


class FakeClient:
    def __init__(self, payload):
        self.responses = FakeResponses(payload)


@pytest.fixture
def make_fake():
    return lambda payload=None: FakeClient(payload if payload is not None else good_payload())


@pytest.fixture
def profile():
    return {
        "client_id": "test-client",
        "legal_name": "Test Co (fictional)",
        "fictional": True,
        "sector": "Logistics",
        "exposures": [{"id": "E1", "description": "Routing", "search_hints": ["Cape routing"]}],
        "covenants": [{"id": "C1", "text": "Net debt / EBITDA at or below 3.5x"}],
    }
