from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

from .config import Config


@dataclass(frozen=True)
class Phase1ReferenceModel:
    version: str
    workload_center: float
    column_names: list[str]
    coefficients: list[float]
    phase1_start: str
    phase1_end: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


BASE_CATEGORY = "hematology"
BASE_SHIFT = "day"
BASE_ANALYZER = "A1"


def _design_matrix(df: pd.DataFrame, workload_center: float) -> tuple[np.ndarray, list[str]]:
    workload = df["workload"].astype(float).to_numpy() - workload_center
    matrix = np.column_stack(
        [
            np.ones(len(df)),
            workload,
            df["test_category"].eq("chemistry").astype(float).to_numpy(),
            df["test_category"].eq("coagulation").astype(float).to_numpy(),
            df["shift"].eq("night").astype(float).to_numpy(),
            df["shift"].eq("evening").astype(float).to_numpy(),
            df["analyzer_id"].eq("A2").astype(float).to_numpy(),
        ]
    )
    names = [
        "intercept",
        "workload_centered",
        "test_category[chemistry]",
        "test_category[coagulation]",
        "shift[night]",
        "shift[evening]",
        "analyzer[A2]",
    ]
    return matrix, names


def fit_phase1_reference_model(qualified: pd.DataFrame, config: Config) -> Phase1ReferenceModel:
    cutoff = pd.Timestamp(config.start_time) + pd.Timedelta(hours=config.phase1_hours)
    phase1 = qualified.loc[qualified["event_hour"] < cutoff].copy()
    if len(phase1) < 20:
        raise ValueError("Insufficient eligible Phase I records for risk adjustment.")

    workload_center = float(phase1["workload"].mean())
    x, names = _design_matrix(phase1, workload_center)
    y = phase1["tat_minutes"].astype(float).to_numpy()
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)

    return Phase1ReferenceModel(
        version=config.model_version,
        workload_center=workload_center,
        column_names=names,
        coefficients=[float(v) for v in beta],
        phase1_start=str(pd.Timestamp(config.start_time)),
        phase1_end=str(cutoff),
    )


def apply_reference_model(qualified: pd.DataFrame, model: Phase1ReferenceModel) -> pd.DataFrame:
    df = qualified.copy()
    x, _ = _design_matrix(df, model.workload_center)
    beta = np.asarray(model.coefficients, dtype=float)
    df["tat_predicted"] = x @ beta
    df["tat_residual"] = df["tat_minutes"].astype(float) - df["tat_predicted"]
    return df


def hourly_residual_summary(qualified_with_residuals: pd.DataFrame) -> pd.DataFrame:
    df = qualified_with_residuals.copy()

    def analyzer_mean(group: pd.DataFrame, analyzer: str) -> float:
        subset = group.loc[group["analyzer_id"].eq(analyzer), "tat_residual"]
        return float(subset.mean()) if not subset.empty else float("nan")

    rows: list[dict] = []
    for hour, group in df.groupby("event_hour", sort=True):
        a1 = analyzer_mean(group, "A1")
        a2 = analyzer_mean(group, "A2")
        rows.append(
            {
                "event_hour": hour,
                "residual_mean": float(group["tat_residual"].mean()),
                "tat_mean": float(group["tat_minutes"].mean()),
                "eligible_records": int(len(group)),
                "workload": float(group["workload"].mean()),
                "analyzer_a2_share": float(group["analyzer_id"].eq("A2").mean()),
                "a1_residual_mean": a1,
                "a2_residual_mean": a2,
                "a2_minus_a1_residual": float(a2 - a1) if np.isfinite(a1) and np.isfinite(a2) else float("nan"),
                "maintenance_warning": bool(group["maintenance_warning"].max()),
                "known_degradation": bool(group["known_degradation"].max()),
            }
        )
    return pd.DataFrame(rows)


def autocorrelation(values: pd.Series, lag: int) -> float:
    arr = values.astype(float).to_numpy()
    if len(arr) <= lag:
        return float("nan")
    return float(pd.Series(arr).autocorr(lag=lag))
