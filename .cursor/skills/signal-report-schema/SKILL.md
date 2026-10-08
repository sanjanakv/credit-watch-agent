---
name: signal-report-schema
description: Field definitions and severity semantics for the SignalReport schema. Use when editing schema.py, prompts, or the HTML brief.
---

# SignalReport semantics

- `severity`: `low` = informational; `medium` = plausible effect on a named exposure within 6 months;
  `high` = credible, sourced event with direct effect on a named exposure or covenant now.
- `confidence` (0-1): how sure the model is the event is real AND relevant. Below 0.5 may never be `high`.
- `exposure_matched`: the profile exposure id (for example `E1`). A signal that matches no exposure is noise: drop it.
- `covenant_relevance`: covenant id (for example `C1`) with one sentence on the mechanism, or null.
- `sources`: http(s) URLs. At least one per signal. X posts count as `source_type = "x"`, everything else `web`.
- `limitations`: always state what the scan could not see (private data, paywalled sources, post-scan events).
- Language: neutral and factual. No recommendations to take adverse action. Say what changed and why it may matter.
