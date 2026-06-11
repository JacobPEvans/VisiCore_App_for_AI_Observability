#!/usr/bin/env python3
"""Validate Dashboard Studio definitions packaged as XML views.

Checks, per view file:
  1. The <definition> CDATA block parses as JSON.
  2. Referential integrity: every dataSource id referenced by a visualization
     or input exists in the top-level dataSources map.
  3. Chain resolution: every ds.chain `extend` resolves, contains no cycles,
     and terminates at a ds.search; ds.search datasources must not declare
     `extend` (chaining requires type ds.chain).
  4. Pricing guard: no inline per-token pricing (use the TA's
     ai_model_pricing.csv lookup via `calculate_cost`).

Exit code 0 on success, 1 with findings on stderr otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Dashboard view files are a constrained, repo-authored format:
#   <dashboard version="2" ...><definition><![CDATA[{json}]]></definition>...
# The CDATA payload is extracted with string operations instead of an XML
# parser, so there is no XXE / entity-expansion attack surface and no
# third-party parsing dependency.
DASHBOARD_V2 = re.compile(r"<dashboard\b[^>]*\bversion=\"2\"")
CDATA_BLOCK = re.compile(r"<definition>\s*<!\[CDATA\[(.*?)\]\]>\s*</definition>", re.DOTALL)

# Matches inline per-MTok pricing math like `15.0/1000000` (with or without
# spaces) anywhere in a query string.
PRICING_DIVISOR = re.compile(r"\d+(?:\.\d+)?\s*/\s*1[_,]?000[_,]?000\b")
# Matches model-keyed case() pricing branches like: match(model,"claude-...")
# followed by arithmetic with float literals.
PRICING_CASE = re.compile(r"match\(\s*model\s*,[^)]*\)\s*,\s*\(?\s*\w+\s*\*\s*\d+(?:\.\d+)?")


def fail(findings: list[str]) -> None:
    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    sys.exit(1)


def extract_definition(path: Path) -> dict | None:
    """Return the parsed Studio JSON for a v2 dashboard, or None for non-v2 views."""
    text = path.read_text(encoding="utf-8")
    if not DASHBOARD_V2.search(text):
        return None
    match = CDATA_BLOCK.search(text)
    if match is None or not match.group(1).strip():
        raise ValueError("missing or empty <definition> CDATA block")
    return json.loads(match.group(1))


def referenced_datasource_ids(definition: dict) -> set[str]:
    refs: set[str] = set()
    for section in ("visualizations", "inputs"):
        for item in definition.get(section, {}).values():
            for ref in item.get("dataSources", {}).values():
                refs.add(ref)
    return refs


def validate_chains(datasources: dict, findings: list[str], name: str) -> None:
    for ds_id, ds in datasources.items():
        ds_type = ds.get("type")
        extend = ds.get("options", {}).get("extend")
        if ds_type == "ds.search" and extend:
            findings.append(
                f"{name}: {ds_id} is ds.search with options.extend — chained "
                "datasources must use type ds.chain"
            )
        if ds_type != "ds.chain":
            continue
        if not extend:
            findings.append(f"{name}: ds.chain {ds_id} has no options.extend")
            continue
        # Walk the chain to a ds.search, detecting cycles and dangling refs.
        seen = {ds_id}
        current = extend
        while True:
            if current in seen:
                findings.append(f"{name}: chain cycle involving {ds_id}")
                break
            seen.add(current)
            parent = datasources.get(current)
            if parent is None:
                findings.append(f"{name}: {ds_id} extends missing datasource {current}")
                break
            if parent.get("type") == "ds.search":
                break
            if parent.get("type") != "ds.chain":
                findings.append(
                    f"{name}: chain from {ds_id} hits {current} of type "
                    f"{parent.get('type')} (must terminate at ds.search)"
                )
                break
            current = parent.get("options", {}).get("extend")
            if not current:
                findings.append(f"{name}: chain from {ds_id} dead-ends at {ds_id}")
                break


def validate_view(path: Path) -> list[str]:
    findings: list[str] = []
    name = path.name
    try:
        definition = extract_definition(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{name}: {exc}"]
    if definition is None:
        return []

    datasources = definition.get("dataSources", {})
    for ref in sorted(referenced_datasource_ids(definition)):
        if ref not in datasources:
            findings.append(f"{name}: referenced datasource {ref} is not defined")

    validate_chains(datasources, findings, name)

    for ds_id, ds in datasources.items():
        query = ds.get("options", {}).get("query", "")
        if PRICING_DIVISOR.search(query) or PRICING_CASE.search(query):
            findings.append(
                f"{name}: {ds_id} contains inline pricing math — use the TA's "
                "`calculate_cost` macro (ai_model_pricing.csv lookup) instead"
            )
    return findings


def main(argv: list[str]) -> None:
    paths = [Path(p) for p in argv] or sorted(Path("default/data/ui/views").glob("*.xml"))
    if not paths:
        fail(["no view files found"])
    findings: list[str] = []
    checked = 0
    for path in paths:
        findings.extend(validate_view(path))
        checked += 1
    if findings:
        fail(findings)
    print(f"OK: {checked} view file(s) validated")


if __name__ == "__main__":
    main(sys.argv[1:])
