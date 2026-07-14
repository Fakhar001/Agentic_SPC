from __future__ import annotations

from pathlib import Path
import shutil

import pandas as pd

from app.alarm_validation_agent import validate_cases
from app.audit_ledger import AuditLedger
from app.config import Config
from app.contextual_reasoning_agent import attach_context
from app.data_generator import generate_lab_events
from app.data_quality_agent import data_quality_metrics, qualify_events, summarize_data_quality
from app.decision_agent import propose_actions
from app.governance_agent import authorize_actions
from app.manufacturing_reference import write_manufacturing_outputs
from app.reporting import create_results_plot, write_json, write_summary
from app.risk_adjustment import (
    apply_reference_model,
    autocorrelation,
    fit_phase1_reference_model,
    hourly_residual_summary,
)
from app.spc_monitoring_agent import ewma_monitor
from app.stress_testing import run_stress_tests


def _clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in output_dir.iterdir():
        # Keep the placeholder so an empty output directory remains version controlled.
        if item.name == ".gitkeep":
            continue
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def main() -> None:
    cfg = Config()
    output_dir = cfg.output_dir
    _clean_output_dir(output_dir)

    events, degradation_start = generate_lab_events(cfg)
    events.to_csv(cfg.project_root / "data" / "synthetic_lab_events.csv", index=False)

    qualified, quarantine = qualify_events(events, cfg)
    dq_summary = summarize_data_quality(events, quarantine)
    dq_metrics = data_quality_metrics(qualified, quarantine)
    dq_metrics.to_csv(output_dir / "data_quality_metrics.csv", index=False)

    reference_model = fit_phase1_reference_model(qualified, cfg)
    write_json(reference_model.to_dict(), output_dir / "reference_model.json")
    qualified = apply_reference_model(qualified, reference_model)
    hourly = hourly_residual_summary(qualified)

    monitoring, meta = ewma_monitor(hourly, cfg)
    monitoring = attach_context(monitoring, dq_summary)
    monitoring.to_csv(output_dir / "hourly_monitoring.csv", index=False)

    phase1_hourly = hourly.iloc[: cfg.phase1_hours]
    diagnostics = {
        "phase1_residual_mean": float(phase1_hourly["residual_mean"].mean()),
        "phase1_residual_sd": float(phase1_hourly["residual_mean"].std(ddof=1)),
        "phase1_residual_acf_lag_1": autocorrelation(phase1_hourly["residual_mean"], 1),
        "phase1_residual_acf_lag_24": autocorrelation(phase1_hourly["residual_mean"], 24),
        "phase1_hours": int(len(phase1_hourly)),
        "monitoring_value": meta["value_monitored"],
    }
    write_json(diagnostics, output_dir / "baseline_diagnostics.json")

    validated = validate_cases(monitoring, baseline_sigma=meta["baseline_sigma"])
    proposals = propose_actions(validated) if not validated.empty else validated
    authorized = authorize_actions(proposals, cfg.policy_version) if not proposals.empty else proposals
    if not authorized.empty:
        authorized["model_version"] = cfg.model_version
        authorized["evidence_reference"] = authorized["event_hour"].map(lambda t: f"hourly_monitoring:{t}")

    ledger = AuditLedger(output_dir / "agentic_spc.db")

    dq_cases = dq_summary.loc[dq_summary["dq_event"]].copy()
    for _, row in dq_cases.iterrows():
        ledger.append(
            {
                "event_hour": row["event_hour"],
                "case_type": "data_integrity",
                "raw_spc_signal": 0,
                "validation_class": "data-quality concern",
                "priority": "low",
                "proposed_action": "open_data_integrity_ticket",
                "governance_decision": "permitted_automatic_workflow",
                "authorized_action": "open_data_integrity_ticket",
                "human_review_required": False,
                "context_summary": (
                    f"quarantined_records={int(row['quarantined_records'])}; "
                    f"eligibility_rate={row['eligibility_rate']:.3f}"
                ),
                "model_version": cfg.model_version,
                "policy_version": cfg.policy_version,
                "evidence_reference": f"dq_summary:{row['event_hour']}",
                "outcome": "synthetic_data_stewardship_review_requested",
            }
        )

    for _, row in authorized.iterrows():
        if bool(row["human_review_required"]):
            outcome = (
                "synthetic_adjudication: evidence-linked A2-related degradation hypothesis "
                "consistent with the known synthetic scenario; not causal confirmation"
            )
        else:
            outcome = "synthetic_pre_authorized_low_risk_workflow_completed"
        record = {**row.to_dict(), "case_type": "spc_incident", "raw_spc_signal": 1, "outcome": outcome}
        ledger.append(record)

    chain_valid = ledger.validate_chain()
    ledger_df = ledger.export_csv(output_dir / "audit_ledger.csv")
    ledger.close()

    create_results_plot(monitoring, degradation_start, output_dir / "reference_results.png")

    stress_results = run_stress_tests(cfg, baseline_sigma=meta["baseline_sigma"])
    stress_results.to_csv(output_dir / "stress_test_results.csv", index=False)
    manufacturing_outputs = write_manufacturing_outputs(output_dir)

    signal_hours = monitoring.loc[monitoring["raw_spc_signal"].eq(1), "event_hour"]
    first_detection = signal_hours.min() if not signal_hours.empty else pd.NaT
    detection_delay_hours = (
        None
        if pd.isna(first_detection)
        else round((first_detection - degradation_start).total_seconds() / 3600.0, 2)
    )
    pre_degradation_signals = int(
        monitoring.loc[monitoring["event_hour"] < degradation_start, "raw_spc_signal"].sum()
    )

    action_counts = authorized["governance_decision"].value_counts().to_dict() if not authorized.empty else {}
    credible_cases = int(authorized["validation_class"].eq("credible").sum()) if not authorized.empty else 0
    overall_dq = dq_metrics.loc[dq_metrics["defect_type"].eq("overall")].iloc[0]

    metrics = [
        ("Reference implementation version", cfg.implementation_version),
        ("Raw laboratory records ingested", int(len(events))),
        ("Eligible records used for SPC", int(len(qualified))),
        ("Quarantined records", int(len(quarantine))),
        ("Distinct data-integrity hours", int(dq_cases.shape[0])),
        ("Synthetic data-quality precision", round(float(overall_dq["precision"]), 3)),
        ("Synthetic data-quality recall", round(float(overall_dq["recall"]), 3)),
        ("Phase I baseline hours", int(meta["phase1_hours"])),
        ("Phase II monitored hours", int(meta["phase2_hours"])),
        ("Phase I residual mean", round(float(diagnostics["phase1_residual_mean"]), 3)),
        ("Phase I residual standard deviation", round(float(diagnostics["phase1_residual_sd"]), 3)),
        ("Phase I residual ACF lag 1", round(float(diagnostics["phase1_residual_acf_lag_1"]), 3)),
        ("Phase I residual ACF lag 24", round(float(diagnostics["phase1_residual_acf_lag_24"]), 3)),
        ("EWMA lambda", meta["lambda"]),
        ("EWMA L", meta["L"]),
        ("Raw residual-EWMA signal hours", int(monitoring["raw_spc_signal"].sum())),
        ("Pre-degradation raw signal hours", pre_degradation_signals),
        ("Initial SPC incident episodes", int(monitoring["case_start"].sum())),
        ("Persistent-signal escalation cases", int(monitoring["escalation_start"].sum())),
        ("First residual-EWMA detection", str(first_detection)),
        ("Scenario-specific detection delay (hours)", detection_delay_hours),
        ("Credible validated incident cases", credible_cases),
        ("Automatic workflow decisions", int(action_counts.get("permitted_automatic_workflow", 0))),
        ("Human-review-required decisions", int(action_counts.get("human_review_required", 0))),
        ("Audit ledger records", int(len(ledger_df))),
        ("Tamper-evident ledger hash chain valid", bool(chain_valid)),
        ("Stress-test replications per scenario", cfg.stress_repetitions),
    ]
    results_table = pd.DataFrame(metrics, columns=["Metric", "Result"])

    summary = {
        "implementation_version": cfg.implementation_version,
        "scenario": "Synthetic risk-adjusted clinical laboratory turnaround-time monitoring",
        "degradation_start": str(degradation_start),
        "first_detection": str(first_detection),
        "detection_delay_hours": detection_delay_hours,
        "model_version": cfg.model_version,
        "policy_version": cfg.policy_version,
        "reference_model": reference_model.to_dict(),
        "baseline_diagnostics": diagnostics,
        "ledger_hash_chain_valid": bool(chain_valid),
        "notes": [
            "Results are generated from a deterministic synthetic scenario, not patient data.",
            "The implementation uses a frozen Phase I risk-adjustment model and residual EWMA monitoring.",
            "Rule-derived credibility scores are transparent heuristics, not calibrated probabilities.",
            "The prototype supports laboratory quality monitoring only; it does not make patient-specific clinical decisions.",
            "The SQLite hash chain is a tamper-evident prototype mechanism, not an enterprise immutability solution.",
            "Manufacturing outputs are locked synthetic reference tables matching the manuscript scenario.",
        ],
        "manufacturing_outputs": {key: str(path) for key, path in manufacturing_outputs.items()},
    }
    write_summary(summary, results_table, output_dir)
    print(results_table.to_string(index=False))


if __name__ == "__main__":
    main()
