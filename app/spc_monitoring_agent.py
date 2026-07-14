from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config


def ewma_monitor(hourly: pd.DataFrame, config: Config) -> tuple[pd.DataFrame, dict]:
    """Run a frozen-Phase-I EWMA over hourly risk-adjusted residual means."""
    df = hourly.sort_values("event_hour").copy()
    phase1 = df.iloc[: config.phase1_hours].copy()
    phase2 = df.iloc[config.phase1_hours :].copy()
    if len(phase1) != config.phase1_hours:
        raise ValueError("Hourly series does not contain the required Phase I duration.")

    mu0 = float(phase1["residual_mean"].mean())
    sigma0 = float(phase1["residual_mean"].std(ddof=1))
    lam = config.lambda_ewma
    L = config.L_ewma

    z_prev = mu0
    records: list[dict] = []
    for t, (_, row) in enumerate(phase2.iterrows(), start=1):
        z = lam * float(row["residual_mean"]) + (1.0 - lam) * z_prev
        sigma_z = sigma0 * np.sqrt(lam / (2.0 - lam) * (1.0 - (1.0 - lam) ** (2 * t)))
        ucl = mu0 + L * sigma_z
        lcl = mu0 - L * sigma_z
        signal = int(z > ucl or z < lcl)
        records.append(
            {
                **row.to_dict(),
                "phase": "II",
                "ewma": z,
                "ucl": ucl,
                "lcl": lcl,
                "raw_spc_signal": signal,
            }
        )
        z_prev = z

    out = pd.DataFrame(records)
    out["case_start"] = (
        out["raw_spc_signal"].eq(1) & out["raw_spc_signal"].shift(fill_value=0).eq(0)
    ).astype(int)

    run_length: list[int] = []
    current_run = 0
    for signal in out["raw_spc_signal"]:
        current_run = current_run + 1 if signal else 0
        run_length.append(current_run)
    out["signal_run_length"] = run_length
    out["escalation_start"] = out["signal_run_length"].eq(config.persistent_signal_periods).astype(int)

    metadata = {
        "baseline_mu": mu0,
        "baseline_sigma": sigma0,
        "lambda": lam,
        "L": L,
        "phase1_hours": int(len(phase1)),
        "phase2_hours": int(len(phase2)),
        "value_monitored": "hourly_mean_risk_adjusted_tat_residual",
        "model_version": config.model_version,
    }
    return out, metadata
