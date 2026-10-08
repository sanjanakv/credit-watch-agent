# credit-signal-scout: agent instructions

This repo is a DEMO of an early-warning tool for corporate credit monitoring at a bank.
All client profiles are FICTIONAL. Never add real client names, real people, or real account data.

## What you are building
Implement the `scout` package so that `pytest` passes and `python scripts/pure_check.py` prints PASS.
The contract is `docs/specs/SPEC-001-signal-scout.md`. The tests in `tests/` are the source of truth.

## Ground rules
- Read the spec first, then the tests, then write code. Do not edit tests to make them pass.
  If a test looks wrong, say so in the PR description instead.
- Governance rules live in `.cursor/rules/`. Skills live in `.cursor/skills/`. Use them.
- Keep the package small: schema, guardrails, profiles, client, scan, brief, cli. No extra frameworks.
- Open a PR. Never push to main. Never merge. A human approves the merge.
- PR description must include: what changed, how you verified it (commands + results),
  PURE self-review (see skill `pure-self-review`), and anything you were unsure about.

## Cursor Cloud specific instructions

- Setup is `.cursor/environment.json` only. Python 3.12 is already on the default image. There is no dev server and no `start` process.
- After install, `pytest` and `scout` are on `/usr/local/bin`. From `/workspace`, run `pytest` and `python scripts/pure_check.py`.
- `XAI_API_KEY` is optional. Tests marked `live` skip when it is unset. Do not add a key for the default test run.
