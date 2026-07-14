from __future__ import annotations

from pathlib import Path

import pandas as pd


def manufacturing_results_table() -> pd.DataFrame:
    """Return the synthetic manufacturing reference scenario reported in the manuscript."""
    rows = [
        ("Implementation scope", "System type", "Synthetic end-to-end reference scenario"),
        ("Data volume", "Raw manufacturing records", "18000"),
        ("Data quality", "Eligible records entering SPC", "17798"),
        ("Data quality", "Quarantined records", "202"),
        ("Data quality", "Quarantine rate", "0.0112"),
        ("Data quality", "Defect-set precision", "1.000"),
        ("Data quality", "Defect-set recall", "0.910"),
        ("Data quality", "False-quarantine rate (clean records)", "0.000"),
        ("Data quality", "Distinct data-integrity hours (Phase II)", "91"),
        ("Baseline", "Phase I duration", "336"),
        ("Monitoring", "Phase II duration", "384"),
        ("Residual baseline", "Part-level standard deviation", "0.028"),
        ("Residual baseline", "Hourly-mean standard deviation", "0.0055"),
        ("Baseline diagnostic", "Standardized hourly-mean ACF lag 1", "0.040"),
        ("Baseline diagnostic", "Standardized hourly-mean ACF lag 24", "-0.064"),
        ("EWMA configuration", "lambda", "0.20"),
        ("EWMA configuration", "L", "3.30"),
        ("EWMA performance (simulated)", "ARL0", "1447"),
        ("EWMA performance (simulated)", "ARL1 0.5 sigma", "70.6"),
        ("EWMA performance (simulated)", "ARL1 1.0 sigma", "13.6"),
        ("EWMA performance (simulated)", "ARL1 1.5 sigma", "6.5"),
        ("Raw SPC evidence", "Raw residual-EWMA signal hours (Phase II)", "166"),
        ("Raw SPC evidence", "Pre-degradation signal hours", "0"),
        ("Detection", "First post-degradation signal delay hours", "85"),
        ("Case coordination", "Incident episodes", "3"),
        ("Case coordination", "Persistent-signal escalation cases", "2"),
        ("Safety metric", "Critical false-dismissal numerator", "0"),
        ("Safety metric", "Critical false-dismissal denominator", "2"),
        ("Auditability", "Approximate ledger records", "94"),
    ]
    return pd.DataFrame(rows, columns=["Category", "Measure", "Result"])


def manufacturing_stress_results() -> pd.DataFrame:
    """Return the locked n=3 manufacturing stress-test table from the manuscript."""
    rows = [
        ("stable_null", 3, None, None, 1.00, 0.0113),
        ("gradual_machine_m2_tool_wear", 3, 1.0, 38.0, 172.00, 0.0113),
        ("intermittent_machine_m2_tool_wear", 3, 1.0, 98.0, 94.00, 0.0112),
        ("context_error", 3, 1.0, 50.0, 174.67, 0.0112),
        ("missingness_stress", 3, 1.0, 72.0, 171.33, 0.0252),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "scenario",
            "replications",
            "detection_rate",
            "median_delay_hours",
            "mean_raw_signal_hours",
            "mean_quarantine_rate",
        ],
    )


def cross_domain_comparison() -> pd.DataFrame:
    """Return the manuscript cross-domain comparison table."""
    rows = [
        ("Records ingested", "12980", "18000"),
        ("Quarantine rate", "0.88%", "1.12%"),
        ("Defect-set precision / recall", "1.000 / 1.000", "1.000 / 0.910"),
        ("Phase I / Phase II duration", "336 / 384 hours", "336 / 384 hours"),
        ("EWMA lambda, L", "0.20, 3.30", "0.20, 3.30"),
        ("Standardized residual ACF(1) / ACF(24)", "0.022 / 0.004", "0.040 / -0.064"),
        ("ARL0", "approximately 1447 hours", "approximately 1447 hours"),
        ("Pre-degradation Phase II signal hours", "0", "0"),
        ("Detection delay (primary scenario)", "5 hours", "85 hours"),
        ("Incident cases / persistent escalations", "1 / 1", "3 / 2"),
        ("Missingness-stress quarantine rate", "5.83%", "2.52%"),
        ("Full audit ledger with hash-chaining and test suite", "Yes", "Statistical/governance pathway only"),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Healthcare (TAT)", "Manufacturing (dimensional)"])


def write_manufacturing_outputs(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "manufacturing_results": output_dir / "manufacturing_results_table.csv",
        "manufacturing_stress": output_dir / "manufacturing_stress_test_results.csv",
        "cross_domain": output_dir / "cross_domain_comparison.csv",
    }
    manufacturing_results_table().to_csv(outputs["manufacturing_results"], index=False)
    manufacturing_stress_results().to_csv(outputs["manufacturing_stress"], index=False)
    cross_domain_comparison().to_csv(outputs["cross_domain"], index=False)
    return outputs
