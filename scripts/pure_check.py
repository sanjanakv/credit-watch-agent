#!/usr/bin/env python3
"""Deterministic PURE hygiene check. Used by the Cursor agent, CI and the Control Gate bot."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [p for d in ("scout", "scripts", "tests") for p in (ROOT / d).rglob("*.py") if p.name != "pure_check.py"]

problems: list[str] = []

for path in FILES:
    text = path.read_text()
    rel = path.relative_to(ROOT)
    if re.search(r"xai-[A-Za-z0-9]{16,}", text):
        problems.append(f"{rel}: looks like a hard-coded API key")
    if re.search(r"verify\s*=\s*False", text):
        problems.append(f"{rel}: TLS verification disabled")
    for m in re.finditer(r"http://([^\s\"')]+)", text):
        if not m.group(1).startswith(("localhost", "127.0.0.1")):
            problems.append(f"{rel}: plain http endpoint {m.group(0)}")

scan = ROOT / "scout" / "scan.py"
schema = ROOT / "scout" / "schema.py"
if not scan.exists() or "validate_report" not in scan.read_text():
    problems.append("scout/scan.py must run validate_report on every result")
if not schema.exists() or "human_review_required" not in schema.read_text():
    problems.append("scout/schema.py must define human_review_required")

if problems:
    print("PURE CHECK: FAIL")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("PURE CHECK: PASS")
