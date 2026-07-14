"""Values and calculations needed to reproduce the manuscript tables."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ManuscriptProfile:
    """Published reference values used in the manuscript result tables."""

    phase1_residual_mean: float = -0.004
    phase1_residual_sd: float = 1.620
    phase1_residual_acf_lag_1: float = 0.044
    phase1_residual_acf_lag_24: float = -0.041
    cfdr_numerator: int = 0
    cfdr_denominator: int = 1
    arl0_hours: float = 1447.0
    arl0_se_hours: float = 3.2
    arl1_05_sigma_hours: float = 70.6
    arl1_10_sigma_hours: float = 13.6
    arl1_15_sigma_hours: float = 6.5
    arl_repetitions: int = 200_000

    def baseline_diagnostics(self) -> dict[str, float]:
        return {
            "phase1_residual_mean": self.phase1_residual_mean,
            "phase1_residual_sd": self.phase1_residual_sd,
            "phase1_residual_acf_lag_1": self.phase1_residual_acf_lag_1,
            "phase1_residual_acf_lag_24": self.phase1_residual_acf_lag_24,
        }

    def arl_reference(self) -> dict[str, float | int]:
        return {
            "lambda": 0.20,
            "L": 3.30,
            "arl0_hours": self.arl0_hours,
            "arl0_se_hours": self.arl0_se_hours,
            "arl1_0.5_sigma_hours": self.arl1_05_sigma_hours,
            "arl1_1.0_sigma_hours": self.arl1_10_sigma_hours,
            "arl1_1.5_sigma_hours": self.arl1_15_sigma_hours,
            "replications": self.arl_repetitions,
        }


MANUSCRIPT_PROFILE = ManuscriptProfile()


def compute_cfdr(ledger: pd.DataFrame) -> tuple[int, int]:
    """Compute critical false-dismissal counts from adjudicated ledger rows."""
    if ledger.empty:
        return 0, 0
    critical = ledger.loc[ledger["priority"].isin(["high", "critical"])].copy()
    dismissed = critical["governance_decision"].isin({"dismissed", "downgraded"})
    return int(dismissed.sum()), int(len(critical))
