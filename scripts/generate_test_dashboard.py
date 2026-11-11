#!/usr/bin/env python3
"""Render pytest JUnit results as the Qualisera test dashboard."""

from __future__ import annotations

import html
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def _suite_name(classname: str) -> str:
    class_name = classname.rsplit(".", 1)[-1]
    if class_name == "test_data_loaders":
        return "Data Loader Regressions"
    if class_name.startswith("Test"):
        class_name = class_name[4:]
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", class_name)
    spaced = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", spaced)
    return spaced or "Other"


def _scenario_label(classname: str, test_name: str) -> str:
    suite = _suite_name(classname)
    if suite.endswith(" Positive") or suite.endswith(" Negative"):
        return suite

    lowered = test_name.lower()
    negative_terms = (
        "invalid",
        "reject",
        "missing",
        "unsupported",
        "duplicate",
        "malformed",
        "empty",
        "future",
        "null",
        "outside",
    )
    polarity = "Negative" if any(term in lowered for term in negative_terms) else "Positive"
    if lowered.startswith("test_synthea"):
        return f"Synthea {polarity}"
    if lowered.startswith("test_fhir"):
        return f"FHIR {polarity}"
    if lowered.startswith("test_nih"):
        return f"NIH {polarity}"
    if suite.startswith("API") or "Validation" in suite or "Performance" in suite:
        return f"API {polarity}"
    return "Other"


def _scenario_title(test_name: str) -> str:
    parameter_id = re.search(r"\[([^\]]+)\]$", test_name)
    if parameter_id:
        name = parameter_id.group(1).replace("-", " ").replace("_", " ")
    else:
        name = test_name.removeprefix("test_").replace("_", " ")
    name = name[:1].upper() + name[1:]
    for acronym in ("api", "fhir", "nih", "csv", "json", "id", "bpm"):
        name = re.sub(rf"\b{acronym}\b", acronym.upper(), name, flags=re.IGNORECASE)
    return name


def _read_results(xml_path: Path) -> list[dict[str, str | float]]:
    root = ET.parse(xml_path).getroot()
    results = []
    for case in root.findall(".//testcase"):
        classname = case.get("classname", "")
        name = case.get("name", "unnamed test")
        if case.find("failure") is not None:
            status = "Failed"
        elif case.find("error") is not None:
            status = "Error"
        elif case.find("skipped") is not None:
            status = "Skipped"
        else:
            status = "Passed"
        results.append({
            "suite": _suite_name(classname),
            "scenario": _scenario_label(classname, name),
            "title": _scenario_title(name),
            "name": name,
            "status": status,
            "duration": float(case.get("time", 0)),
        })
    return results


def _result_table(results: list[dict[str, str | float]]) -> str:
    suites: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for result in results:
        suites[str(result["suite"])].append(result)
    rows = []
    for suite, cases in sorted(suites.items()):
        passed = sum(case["status"] == "Passed" for case in cases)
        failed = sum(case["status"] in {"Failed", "Error"} for case in cases)
        skipped = sum(case["status"] == "Skipped" for case in cases)
        rows.append(
            "<tr>"
            f"<td>{html.escape(suite)}</td><td>{len(cases)}</td>"
            f'<td class="passed">{passed}</td>'
            f'<td class="failed">{failed}</td>'
            f'<td class="skipped">{skipped}</td></tr>'
        )
    return "\n".join(rows)


def _scenario_cards(
    results: list[dict[str, str | float]], polarity: str
) -> str:
    scenarios = [item for item in results if item["scenario"].endswith(polarity)]
    grouped: dict[str, list[dict[str, str | float]]] = defaultdict(list)
    for scenario in scenarios:
        grouped[str(scenario["scenario"])].append(scenario)

    rows = []
    for label, cases in sorted(grouped.items()):
        for case in sorted(cases, key=lambda item: str(item["title"])):
            status = str(case["status"]).lower()
            review = "Review the recorded result and test context."
            rows.append(
                '<div class="scenario-row">'
                f'<span class="scenario-kind">{html.escape(label)}</span>'
                '<div class="scenario-detail">'
                f'<div class="scenario-title">{html.escape(str(case["title"]))}</div>'
                f'<div class="review">{review}</div>'
                f'<span class="status {status}">{html.escape(str(case["status"]))}</span>'
                "</div></div>"
            )
    if not rows:
        return '<p class="empty">No scenarios in this category.</p>'
    return "\n".join(rows)


def render_dashboard(results: list[dict[str, str | float]]) -> str:
    total = len(results)
    passed = sum(item["status"] == "Passed" for item in results)
    failed = sum(item["status"] in {"Failed", "Error"} for item in results)
    skipped = sum(item["status"] == "Skipped" for item in results)
    pass_rate = (passed / total * 100) if total else 0
    duration = sum(float(item["duration"]) for item in results)
    dataset_results = [
        item
        for item in results
        if str(item["scenario"]).startswith(("Synthea ", "FHIR ", "NIH "))
    ]
    api_results = [
        item for item in results if str(item["scenario"]).startswith("API ")
    ]
    cards = (
        ("Tests collected", total, "neutral"),
        ("Dataset scenarios", len(dataset_results), "neutral"),
        ("Passed", passed, "good"),
        ("Failures", failed, "bad"),
        ("Pass rate", f"{pass_rate:.0f}%", "neutral"),
        ("Duration", f"{duration:.1f}s", "neutral"),
    )
    summary = "\n".join(
        f'<article class="metric {color}"><div>{label}</div><strong>{value}</strong></article>'
        for label, value, color in cards
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Qualisera AI Test Results</title>
<style>
:root {{ color-scheme: light; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #17212f; background: #f7f9fc; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 28px; }}
main {{ max-width: 1440px; margin: 0 auto; }}
h1 {{ margin: 0 0 6px; font-size: 25px; }}
.subtitle {{ margin: 0 0 24px; color: #64748b; }}
.metrics {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 14px; margin-bottom: 28px; }}
.metric {{ padding: 17px 19px; border: 1px solid #e1e7ef; border-radius: 12px; background: white; }}
.metric div {{ color: #64748b; font-size: 13px; font-weight: 600; }}
.metric strong {{ display: block; margin-top: 8px; font-size: 28px; }}
.metric.good {{ background: #effcf5; border-color: #b9efd0; color: #146c43; }}
.metric.bad {{ background: #fff5f4; border-color: #ffd2cd; color: #ae3027; }}
h2 {{ margin: 0 0 14px; font-size: 18px; }}
.panel {{ margin-bottom: 30px; overflow: hidden; border: 1px solid #e0e6ee; border-radius: 12px; background: white; }}
table {{ width: 100%; border-collapse: collapse; text-align: left; }}
th {{ background: #f1f5f9; color: #526174; font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }}
th, td {{ padding: 12px 15px; border-bottom: 1px solid #edf0f4; }}
tbody tr:last-child td {{ border-bottom: 0; }}
.passed {{ color: #198754; font-weight: 700; }}
.failed {{ color: #c0392b; font-weight: 700; }}
.skipped {{ color: #b7791f; font-weight: 700; }}
.scenario-columns {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
.scenario-panel {{ overflow: hidden; border: 1px solid #e1e7ef; border-radius: 12px; background: white; }}
.scenario-heading {{ display: flex; justify-content: space-between; padding: 14px 16px; font-weight: 700; }}
.positive-heading {{ color: #167447; background: #effcf5; }}
.negative-heading {{ color: #a9362d; background: #fff5f4; }}
.scenario-row {{ display: grid; grid-template-columns: 145px 1fr; gap: 14px; padding: 13px 15px; border-top: 1px solid #edf0f4; }}
.scenario-kind {{ color: #566a80; font-size: 12px; font-weight: 700; }}
.scenario-title {{ font-size: 14px; font-weight: 600; }}
.review {{ margin-top: 5px; color: #64748b; font-size: 12px; }}
.status {{ display: inline-block; margin-top: 7px; padding: 2px 7px; border-radius: 20px; font-size: 11px; font-weight: 700; }}
.status.passed {{ background: #e9f8ef; color: #167447; }}
.status.failed, .status.error {{ background: #fff0ee; color: #a9362d; }}
.status.skipped {{ background: #fff7e6; color: #946200; }}
.empty {{ padding: 15px; color: #64748b; }}
@media (max-width: 650px) {{ body {{ padding: 16px; }} .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .scenario-columns {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body><main>
<h1>Qualisera AI Test Results</h1>
<p class="subtitle">Latest automated run across the healthcare datasets and API.</p>
<section class="metrics" aria-label="Test run summary">{summary}</section>
<h2>Results by test suite</h2>
<div class="panel"><table><thead><tr><th>Test suite</th><th>Total</th><th>Passed</th><th>Failed</th><th>Skipped</th></tr></thead>
<tbody>{_result_table(results)}</tbody></table></div>
<h2>Test scenarios covered</h2>
<p class="subtitle">{len(dataset_results)} dataset scenarios across Synthea, FHIR, and NIH. API scenarios are listed separately.</p>
<section class="scenario-columns">
<div class="scenario-panel"><div class="scenario-heading positive-heading"><span>Dataset positive scenarios</span><span>{sum(str(item["scenario"]).endswith("Positive") for item in dataset_results)}</span></div>{_scenario_cards(dataset_results, "Positive")}</div>
<div class="scenario-panel"><div class="scenario-heading negative-heading"><span>Dataset negative scenarios</span><span>{sum(str(item["scenario"]).endswith("Negative") for item in dataset_results)}</span></div>{_scenario_cards(dataset_results, "Negative")}</div>
</section>
<h2 style="margin-top: 24px;">API scenarios (separate)</h2>
<section class="scenario-columns">
<div class="scenario-panel"><div class="scenario-heading positive-heading"><span>API positive scenarios</span><span>{sum(str(item["scenario"]).endswith("Positive") for item in api_results)}</span></div>{_scenario_cards(api_results, "Positive")}</div>
<div class="scenario-panel"><div class="scenario-heading negative-heading"><span>API negative scenarios</span><span>{sum(str(item["scenario"]).endswith("Negative") for item in api_results)}</span></div>{_scenario_cards(api_results, "Negative")}</div>
</section>
</main></body></html>"""


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: generate_test_dashboard.py <junit-xml> <output-html>",
            file=sys.stderr,
        )
        return 2
    xml_path, output_path = map(Path, sys.argv[1:])
    results = _read_results(xml_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_dashboard(results), encoding="utf-8")
    print(f"Test dashboard saved to {output_path} ({len(results)} tests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
