# Credit Watch bot team (Grok Bot Team Bots, channel: #credit-watch-demo)

| Bot | Role | Skills / tools | Human gate |
|---|---|---|---|
| **Desk Lead** (lead) | Takes the RM request, owns the plan, routes work, assembles the final answer | routine "weekly watchlist"; team memory; Slack | RM confirms scope before build |
| **Spec Analyst** | Turns the RM request + policy into SPEC-001 and a context pack | skill `write-spec`; reads policy docs | RM/Risk approves the spec |
| **Builder** | Launches the Cursor cloud agent via `scripts/launch_cursor_agent.sh`, tracks the PR | skill `launch-cursor-agent`; GitHub/Origin connector | Engineer approves PR (never auto-merge) |
| **Control Gate** | Runs PURE review: pure_check, test results, PR diff vs rules | skill `pure-review`; reads CI | Risk/Compliance signs off |
| **Signal Analyst** | Runs the built scout on the watchlist, summarises signals for RMs | skill `run-scout`; Grok API | RM reviews every signal; nothing leaves the bank without human action |

Channel choice: **chat (Slack)** for approvals and audit trail; **page** (HTML brief) for the artifact RMs read; **voice** optional stretch via Grok TTS for a morning audio brief.

## Handoff template (context pack)
```
Goal: <one sentence>
Client profile: profiles/<id>.yaml (fictional)
Spec: docs/specs/SPEC-001-signal-scout.md @ <commit>
Constraints: PURE rules, no adverse-action advice, human review always
Definition of done: pytest + pure_check green, PR opened, not merged
Owner of next step: <bot or human>
```

## Paste-ready skill texts
**write-spec**: Given an RM request and the policy notes, update SPEC-001 only where the request changes behaviour. List assumptions. Never weaken guardrail codes. Post the diff to the channel and wait for approval.

**launch-cursor-agent**: After spec approval, run `scripts/launch_cursor_agent.sh <repo-url>`. Post the agent link. Poll until finished. Post the PR URL. Do not merge.

**pure-review**: Checkout the PR branch, run `pytest -m "not live"` and `python scripts/pure_check.py`. Check the diff against `.cursor/rules/pure-governance.mdc`. Post PASS/FAIL with reasons and request Risk sign-off.

**run-scout**: With an approved, merged scout, run `scout scan profiles/<id>.yaml --out out/`. Summarise signals by severity, always quote sources, remind the RM that human review is required.

## Admin settings to check before the demo (verified against vendor docs, Oct 2026)
Where: cursor.com/dashboard/bot. Cloud Agents ON (Builder needs it). Execution on Local Computer: Never allow. Enterprise only: Enable Grok Bot, Enforce Auto-review, Action Recording, Network Controls (allow api.cursor.com, api.x.ai, github.com). Team must not be on legacy Privacy Mode.
Create each bot: New chat -> Create new Team Bot -> describe job -> Setup cards (Secrets, Files, Skills) -> Publish to team. Slack: bot details -> Bring to your team's Slack -> Connect Slack workspace -> /invite @BotName in the channel. Files must be .txt/.md/.csv/.json/.yaml/.yml (rename .mdc to .md). Routines are personal to the creator.
Secrets: CURSOR_API_KEY on Builder, XAI_API_KEY on Signal Analyst. Do not give XAI_API_KEY to the Cursor build agent; tests use a fake client.
Open question to test in rehearsal: whether one Team Bot can hand off directly to another in a thread. If not, mention each bot yourself (human-routed handoff).
