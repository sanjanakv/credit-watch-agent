---
name: pure-self-review
description: Checklist the agent completes and pastes into the PR description before finishing. Use at the end of every task in this repo.
---

# PURE self-review (paste into the PR)

Run `pytest -q` and `python scripts/pure_check.py` first, then answer each line with evidence (file:line or command output).

- [ ] Purposeful: no code path recommends or performs adverse action. Where is this enforced?
- [ ] Unsurprising: `human_review_required` is always true. Where is this enforced and tested?
- [ ] Respectful: PII patterns are rejected. Which test proves it?
- [ ] Explainable: each signal has sources, confidence, exposure, model name, timestamp, tools used. Which test proves it?
- [ ] Secrets: none in code, logs or tests. Output of `pure_check.py` pasted below.
- [ ] Untrusted input: HTML output escapes model text and only links http(s) URLs. Which test proves it?
- [ ] Open questions or assumptions a reviewer should challenge:
