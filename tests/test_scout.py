import copy
import sys
import types
from pathlib import Path

import pytest

from conftest import good_payload

ROOT = Path(__file__).resolve().parent.parent


# ---------- scan: Grok API usage ----------
def test_scan_calls_grok_with_live_search_and_structured_output(make_fake, profile):
    from scout.scan import scan_client

    fake = make_fake()
    scan_client(profile, fake)
    assert len(fake.responses.calls) == 1
    call = fake.responses.calls[0]
    assert call["model"] == "grok-4.7"
    tool_types = {t["type"] for t in call["tools"]}
    assert {"web_search", "x_search"} <= tool_types
    fmt = call["text"]["format"]
    assert fmt["type"] == "json_schema" and fmt["strict"] is True
    assert "signals" in fmt["schema"]["properties"]


def test_prompt_contains_exposures_and_injection_warning(make_fake, profile):
    from scout.scan import scan_client

    fake = make_fake()
    scan_client(profile, fake)
    blob = str(fake.responses.calls[0]["input"]).lower()
    assert "cape routing" in blob or "routing" in blob
    assert "ignore" in blob and "instruction" in blob  # tells model to ignore instructions found in pages/posts


def test_scan_returns_report_with_metadata(make_fake, profile):
    from scout.scan import scan_client

    report = scan_client(profile, make_fake())
    assert report.client_id == "test-client"
    assert report.model == "grok-4.7"
    assert report.as_of
    assert report.human_review_required is True
    assert report.signals[0].sources
    assert any("web_search" in line for line in report.scan_log)


# ---------- guardrails ----------
def _bad(profile, make_fake, mutate):
    from scout.guardrails import GuardrailError
    from scout.scan import scan_client

    payload = copy.deepcopy(good_payload())
    mutate(payload)
    with pytest.raises(GuardrailError) as exc:
        scan_client(profile, make_fake(payload))
    return exc.value.violations


def test_uncited_signal_blocked(profile, make_fake):
    v = _bad(profile, make_fake, lambda p: p["signals"][0].update(sources=[]))
    assert "NO_CITATION" in v


def test_non_http_source_blocked(profile, make_fake):
    v = _bad(profile, make_fake, lambda p: p["signals"][0].update(sources=["javascript:alert(1)"]))
    assert "BAD_SOURCE_URL" in v


def test_low_confidence_high_severity_blocked(profile, make_fake):
    v = _bad(profile, make_fake, lambda p: p["signals"][0].update(severity="high", confidence=0.3))
    assert "LOW_CONF_HIGH_SEV" in v


@pytest.mark.parametrize(
    "text,code",
    [
        ("contact jane.doe@example.com for details", "PII_EMAIL"),
        ("call +65 9123 4567 now", "PII_PHONE"),
        ("director S1234567A is linked", "PII_NATIONAL_ID"),
    ],
)
def test_pii_blocked(profile, make_fake, text, code):
    v = _bad(profile, make_fake, lambda p: p["signals"][0].update(why_it_matters=text))
    assert code in v


def test_adverse_action_language_blocked(profile, make_fake):
    v = _bad(profile, make_fake, lambda p: p.update(summary="We should downgrade the client and call the loan."))
    assert "ADVERSE_ACTION_LANGUAGE" in v


def test_human_review_cannot_be_disabled(profile, make_fake):
    v = _bad(profile, make_fake, lambda p: p.update(human_review_required=False))
    assert "HUMAN_REVIEW_FLAG" in v


def test_missing_limitations_blocked(profile, make_fake):
    v = _bad(profile, make_fake, lambda p: p.update(limitations=""))
    assert "MISSING_LIMITATIONS" in v


# ---------- profiles ----------
@pytest.mark.parametrize("name", ["meridian-harbour-logistics", "kestrel-coldchain", "aurelia-data-centres"])
def test_bundled_profiles_load(name):
    from scout.profiles import load_profile

    p = load_profile(ROOT / "profiles" / f"{name}.yaml")
    assert p["fictional"] is True and p["exposures"] and p["covenants"]


def test_non_fictional_profile_rejected(tmp_path):
    from scout.profiles import load_profile

    f = tmp_path / "real.yaml"
    f.write_text("client_id: x\nlegal_name: Real Co\nsector: s\nexposures: [{id: E1, description: d}]\ncovenants: []\n")
    with pytest.raises(ValueError):
        load_profile(f)


# ---------- client ----------
def test_make_client_requires_key(monkeypatch):
    from scout.client import make_client

    monkeypatch.delenv("XAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        make_client()


def test_make_client_uses_env(monkeypatch):
    from scout.client import make_client

    seen = {}

    class FakeOpenAI:
        def __init__(self, **kw):
            seen.update(kw)

    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=FakeOpenAI))
    monkeypatch.setenv("XAI_API_KEY", "test-key-not-real")
    monkeypatch.delenv("XAI_BASE_URL", raising=False)
    make_client()
    assert seen["base_url"] == "https://api.x.ai/v1"
    monkeypatch.setenv("XAI_BASE_URL", "https://us.api.x.ai/v1")
    make_client()
    assert seen["base_url"] == "https://us.api.x.ai/v1"


# ---------- brief ----------
def test_brief_escapes_and_filters_links(make_fake, profile):
    from scout.brief import render_brief
    from scout.scan import scan_client

    payload = good_payload()
    payload["signals"][0]["headline"] = "<script>alert(1)</script>"
    payload["signals"][0]["sources"] = ["https://example.com/a", "javascript:alert(1)"]
    # javascript: URL would be blocked by guardrails in scan, so build the report directly
    from scout.schema import SignalReport

    report = SignalReport(**payload, client_id="c", as_of="2026-10-07T00:00:00+00:00", model="grok-4.7", scan_log=[])
    html = render_brief(report)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
    assert 'href="https://example.com/a"' in html
    assert "javascript:" not in html
    assert "human review" in html.lower()


# ---------- cli ----------
def test_cli_writes_json_and_html(tmp_path, make_fake):
    from scout.cli import main

    rc = main(["scan", str(ROOT / "profiles" / "meridian-harbour-logistics.yaml"), "--out", str(tmp_path)], client=make_fake())
    assert rc == 0
    assert (tmp_path / "meridian-harbour.json").exists()
    assert (tmp_path / "meridian-harbour.html").exists()


def test_cli_returns_nonzero_on_guardrail_failure(tmp_path, make_fake):
    from scout.cli import main

    bad = good_payload(human_review_required=False)
    rc = main(["scan", str(ROOT / "profiles" / "kestrel-coldchain.yaml"), "--out", str(tmp_path)], client=make_fake(bad))
    assert rc != 0
    assert not list(tmp_path.glob("*.html"))


# ---------- live smoke (skipped by default) ----------
@pytest.mark.live
def test_live_scan_smoke():
    import os

    if not os.environ.get("XAI_API_KEY"):
        pytest.skip("XAI_API_KEY not set")
    from scout.client import make_client
    from scout.profiles import load_profile
    from scout.scan import scan_client

    report = scan_client(load_profile(ROOT / "profiles" / "meridian-harbour-logistics.yaml"), make_client())
    assert report.human_review_required is True
