from __future__ import annotations

import pandas as pd


def validate_cases(monitoring: pd.DataFrame, baseline_sigma: float) -> pd.DataFrame:
    """Apply transparent rule-derived validation; this is not a calibrated model."""
    cases = monitoring.loc[
        monitoring["case_start"].eq(1) | monitoring["escalation_start"].eq(1)
    ].copy()
    if cases.empty:
        return cases

    validation: list[dict] = []
    for _, row in cases.iterrows():
        magnitude = max(0.0, (float(row["ewma"]) - float(row["ucl"])) / max(baseline_sigma, 1e-6))
        dq_concern = bool(row["dq_event"]) and float(row["eligibility_rate"]) < 0.85
        maintenance = bool(row["maintenance_warning"])
        a2_evidence = float(row["a2_minus_a1_residual"]) >= 0.75
        high_workload = float(row["workload"]) >= 23.0

        if dq_concern:
            validation_class = "data-quality concern"
            priority = "moderate"
            credibility_score = 0.35
        elif maintenance and a2_evidence:
            validation_class = "credible"
            priority = "high" if bool(row["escalation_start"]) or magnitude >= 0.25 else "moderate"
            credibility_score = min(0.95, 0.78 + 0.08 * magnitude + 0.05 * int(high_workload))
        elif maintenance or a2_evidence:
            validation_class = "uncertain"
            priority = "moderate"
            credibility_score = min(0.75, 0.55 + 0.10 * magnitude)
        else:
            validation_class = "uncertain"
            priority = "low"
            credibility_score = 0.50

        validation.append(
            {
                "event_hour": row["event_hour"],
                "case_event_type": "persistent_signal_escalation" if bool(row["escalation_start"]) else "initial_signal",
                "validation_class": validation_class,
                "priority": priority,
                "rule_derived_credibility_score": credibility_score,
                "signal_magnitude": magnitude,
                "validation_basis": "transparent_rule_heuristic_not_calibrated_probability",
                "context_summary": row["context_summary"],
            }
        )
    return pd.DataFrame(validation)
