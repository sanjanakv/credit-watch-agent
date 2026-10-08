# SPEC-001: Credit Signal Scout

Status: approved for build. Author: Spec Analyst bot, reviewed by the Desk Lead bot and the requesting RM.
(Pre-written fallback copy: if the live Spec Analyst output is weak, paste this one.)

## Problem
A credit memo is a snapshot. Between reviews, events tied to a client's real exposures (routes, fuel, FX,
regulation, power, export rules) surface on the web and on X before they reach a credit file. RMs need a
sourced, explainable shortlist each morning, not another dashboard.

## Users
Relationship manager (reads the brief), credit risk manager (reviews flagged signals), tech risk (approves the code).

## Scope
A Python package `scout` with a CLI:

    scout scan profiles/<client>.yaml --out out/

For each profile it calls the Grok API with live web search and X search, returns a structured
`SignalReport`, runs guardrails, writes `out/<client_id>.json` and `out/<client_id>.html`.

## Modules (all required)
| Module | Responsibility |
|---|---|
| `scout/schema.py` | `Severity`, `Category`, `Signal`, `SignalReportDraft` (LLM-facing), `SignalReport` (adds client_id, as_of, model, scan_log) |
| `scout/guardrails.py` | `GuardrailError(violations)` and `validate_report(report) -> list[str]` |
| `scout/profiles.py` | `load_profile(path) -> dict`, rejects profiles not marked `fictional: true` |
| `scout/client.py` | `make_client()` from env `XAI_API_KEY`, `XAI_BASE_URL` |
| `scout/scan.py` | `scan_client(profile, client, model="grok-4.7", now=None) -> SignalReport` |
| `scout/brief.py` | `render_brief(report) -> str` (HTML) |
| `scout/cli.py` | `main(argv=None, client=None) -> int`, `python -m scout` entry |

## Guardrail codes (returned by `validate_report`)
`NO_CITATION`, `BAD_SOURCE_URL`, `LOW_CONF_HIGH_SEV`, `PII_EMAIL`, `PII_PHONE`, `PII_NATIONAL_ID`,
`ADVERSE_ACTION_LANGUAGE`, `HUMAN_REVIEW_FLAG`, `MISSING_LIMITATIONS`.
`scan_client` raises `GuardrailError` if the list is non-empty.

## Grok API usage
See skill `grok-api-integration`. Responses API, model `grok-4.7`, tools `web_search` and `x_search`,
strict JSON schema from `SignalReportDraft`.

## Acceptance
1. `pytest -q` passes (no network needed, tests inject a fake client).
2. `python scripts/pure_check.py` prints PASS.
3. `scout scan profiles/meridian-harbour-logistics.yaml --out out/` works with a real key (live smoke test, run by a human or the Control Gate bot).

## Stretch (only if time)
`--voice` flag: produce a 45-second spoken morning brief using the Grok text-to-speech API
(https://docs.x.ai/developers/model-capabilities/audio/text-to-speech). Read the docs first.

## Out of scope
Writing to any credit system, emailing clients, scoring creditworthiness, using real client data.
