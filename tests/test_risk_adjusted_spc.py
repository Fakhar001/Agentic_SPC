import pandas as pd

from app.config import Config
from app.data_generator import generate_lab_events
from app.data_quality_agent import qualify_events
from app.risk_adjustment import apply_reference_model, fit_phase1_reference_model, hourly_residual_summary
from app.spc_monitoring_agent import ewma_monitor


def test_frozen_phase1_residual_ewma_detects_fault_without_pre_fault_signal():
    cfg = Config()
    events, degradation_start = generate_lab_events(cfg)
    qualified, _ = qualify_events(events, cfg)
    model = fit_phase1_reference_model(qualified, cfg)
    scored = apply_reference_model(qualified, model)
    hourly = hourly_residual_summary(scored)
    monitoring, metadata = ewma_monitor(hourly, cfg)

    phase1_hourly = hourly.iloc[: cfg.phase1_hours]
    assert abs(float(phase1_hourly["residual_mean"].mean())) < 0.02
    assert metadata["value_monitored"] == "hourly_mean_risk_adjusted_tat_residual"
    assert monitoring.loc[monitoring["event_hour"] < degradation_start, "raw_spc_signal"].sum() == 0
    assert monitoring.loc[monitoring["event_hour"] >= degradation_start, "raw_spc_signal"].sum() > 0
