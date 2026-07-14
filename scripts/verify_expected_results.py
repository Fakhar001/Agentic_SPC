"""Verify that generated outputs match the manuscript replication profile."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


EXPECTED_HEALTHCARE = {
    "Raw laboratory records ingested": "12980",
    "Eligible records used for SPC": "12866",
    "Quarantined records": "114",
    "Distinct data-integrity hours": "85",
    "Synthetic data-quality precision": "1.0",
    "Synthetic data-quality recall": "1.0",
    "Phase I baseline hours": "336",
    "Phase II monitored hours": "384",
    "EWMA lambda": "0.2",
    "EWMA L": "3.3",
    "Raw residual-EWMA signal hours": "235",
    "Pre-degradation raw signal hours": "0",
    "Initial SPC incident episodes": "1",
    "Persistent-signal escalation cases": "1",
    "First residual-EWMA detection": "2026-01-21 05:00:00",
    "Scenario-specific detection delay (hours)": "5.0",
    "Automatic workflow decisions": "1",
    "Human-review-required decisions": "1",
    "Audit ledger records": "87",
    "Tamper-evident ledger hash chain valid": "True",
    "Stress-test replications per scenario": "3",
}

EXPECTED_HEALTHCARE_STRESS = {
    "stable_null": {"replications": 3, "mean_raw_signal_hours": 0.33, "mean_quarantine_rate": 0.0088},
    "gradual_a2_shift": {
        "replications": 3,
        "detection_rate": 1.0,
        "median_delay_hours": 6.0,
        "mean_raw_signal_hours": 234.00,
        "mean_quarantine_rate": 0.0088,
    },
    "intermittent_a2_shift": {
        "replications": 3,
        "detection_rate": 1.0,
        "median_delay_hours": 9.0,
        "mean_raw_signal_hours": 229.67,
        "mean_quarantine_rate": 0.0088,
    },
    "context_error": {
        "replications": 3,
        "detection_rate": 1.0,
        "median_delay_hours": 6.0,
        "mean_raw_signal_hours": 233.33,
        "mean_quarantine_rate": 0.0088,
    },
    "missingness_stress": {
        "replications": 3,
        "detection_rate": 1.0,
        "median_delay_hours": 7.0,
        "mean_raw_signal_hours": 231.67,
        "mean_quarantine_rate": 0.0583,
    },
}

EXPECTED_MANUFACTURING = {
    "Raw manufacturing records": "18000",
    "Eligible records entering SPC": "17798",
    "Quarantined records": "202",
    "Quarantine rate": "0.0112",
    "Defect-set precision": "1.000",
    "Defect-set recall": "0.910",
    "Distinct data-integrity hours (Phase II)": "91",
    "Raw residual-EWMA signal hours (Phase II)": "166",
    "Pre-degradation signal hours": "0",
    "First post-degradation signal delay hours": "85",
    "Incident episodes": "3",
    "Persistent-signal escalation cases": "2",
    "Approximate ledger records": "94",
}


def normalise(value: object) -> str:
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text


def assert_close(name: str, actual: object, expected: float, mismatches: list[str], tolerance: float = 1e-9) -> None:
    if pd.isna(expected):
        if not pd.isna(actual):
            mismatches.append(f"{name}: expected NaN, actual={actual!r}")
        return
    if abs(float(actual) - float(expected)) > tolerance:
        mismatches.append(f"{name}: expected={expected!r}, actual={actual!r}")


def verify_healthcare(results_path: Path, mismatches: list[str]) -> None:
    table = pd.read_csv(results_path)
    observed = {str(row["Metric"]): normalise(row["Result"]) for _, row in table.iterrows()}
    for metric, expected in EXPECTED_HEALTHCARE.items():
        actual = observed.get(metric)
        if actual != normalise(expected):
            mismatches.append(f"healthcare {metric}: expected={expected!r}, actual={actual!r}")


def verify_healthcare_stress(stress_path: Path, mismatches: list[str]) -> None:
    table = pd.read_csv(stress_path)
    observed = {str(row["scenario"]): row for _, row in table.iterrows()}
    for scenario, expected_values in EXPECTED_HEALTHCARE_STRESS.items():
        if scenario not in observed:
            mismatches.append(f"healthcare stress missing scenario {scenario!r}")
            continue
        row = observed[scenario]
        for metric, expected in expected_values.items():
            assert_close(f"healthcare stress {scenario} {metric}", row[metric], expected, mismatches)


def verify_manufacturing(results_path: Path, mismatches: list[str]) -> None:
    table = pd.read_csv(results_path)
    observed = {str(row["Measure"]): normalise(row["Result"]) for _, row in table.iterrows()}
    for metric, expected in EXPECTED_MANUFACTURING.items():
        actual = observed.get(metric)
        if actual != normalise(expected):
            mismatches.append(f"manufacturing {metric}: expected={expected!r}, actual={actual!r}")


def verify_required_files(output_dir: Path, mismatches: list[str]) -> None:
    required = [
        "results_table.csv",
        "stress_test_results.csv",
        "manufacturing_results_table.csv",
        "manufacturing_stress_test_results.csv",
        "cross_domain_comparison.csv",
        "reference_results.png",
        "audit_ledger.csv",
        "agentic_spc.db",
    ]
    for filename in required:
        path = output_dir / filename
        if not path.exists() or path.stat().st_size <= 0:
            mismatches.append(f"required output missing or empty: {filename}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--results", type=Path, default=None, help="Backward-compatible healthcare results path")
    args = parser.parse_args()

    output_dir = args.output_dir
    results_path = args.results or output_dir / "results_table.csv"
    mismatches: list[str] = []

    verify_required_files(output_dir, mismatches)
    verify_healthcare(results_path, mismatches)
    verify_healthcare_stress(output_dir / "stress_test_results.csv", mismatches)
    verify_manufacturing(output_dir / "manufacturing_results_table.csv", mismatches)

    if mismatches:
        raise SystemExit("Replication check failed:\n" + "\n".join(mismatches))
    print("Replication check passed: healthcare, stress-test, manufacturing, and required outputs match.")


if __name__ == "__main__":
    main()
