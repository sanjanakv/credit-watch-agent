# Credit Watch demo kit (fictional clients only)

Story: a bank's RM desk asks for an exposure-driven early-warning scanner. A Grok Bot team scopes it, a Cursor cloud agent builds it in a repo under bank rules, the built tool calls the Grok API (live web + X search, strict JSON) to produce cited, human-reviewed briefs.

## Setup (about 60 min, do it 2 days before)
1. Create a repo (GitHub, or Cursor Origin with GitHub sync) and push this folder. Keep `reference_solution/` out of the main branch (move to a `fallback` branch).
2. In Cursor: create a cloud environment for the repo (cursor.com/dashboard/cloud-agents#environments), confirm `.cursor/rules`, `.cursor/skills` and `AGENTS.md` are picked up. Do NOT give the build agent your XAI_API_KEY (tests use a fake client).
3. In Grok Bot: create the team bots from `bots/ROSTER.md`, Slack channel `#credit-watch-demo`, connectors (GitHub, Slack), approvals on.
4. Dry run: `export CURSOR_API_KEY=... && scripts/launch_cursor_agent.sh <repo-url>`. Time it. Agent runtime varies, so pre-run once and keep the PR as backup.
5. Fallback: `cp -r reference_solution/scout ./scout && pytest -m "not live" && python scripts/pure_check.py` (21 tests pass).
6. Live scan: `export XAI_API_KEY=... && python -m scout scan profiles/meridian-harbour-logistics.yaml --out out/` and open the HTML.

## Demo failure plan
Agent slow: show the pre-run PR. Grok API error: show the saved `out/*.html`. Guardrail block: this is a feature, show the violation codes.

## Caveats
The Cursor agent payload and `x_search` syntax were checked against vendor docs in Oct 2026; Grok Bot labels may still change. See the step-by-step setup guide doc for every click. Data is synthetic or public. Grok Bot compute and the regional API endpoint are US-hosted; discuss residency openly.
