from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Configuration for the synthetic Agentic SPC reference prototype."""

    implementation_version: str = "0.2.1"
    seed: int = 20260627
    start_time: str = "2026-01-01 00:00:00"
    total_days: int = 30
    phase1_days: int = 14
    specimens_per_hour: int = 18
    baseline_tat_minutes: float = 55.0
    degradation_start_hour: int = 480  # 00:00 on 21 January 2026
    fault_mode: str = "gradual"  # null | gradual | intermittent
    fault_scale: float = 1.0
    lambda_ewma: float = 0.20
    L_ewma: float = 3.30
    min_tat_minutes: float = 5.0
    max_tat_minutes: float = 360.0
    persistent_signal_periods: int = 6
    stress_repetitions: int = 3
    # Fallback only for direct stress-test invocation; main.py passes the fitted Phase I scale.
    stress_reference_sigma: float = 1.132
    policy_version: str = "lab_tat_policy_v0.2.1"
    model_version: str = "tat_residual_ewma_v0.2.1"

    @property
    def total_hours(self) -> int:
        return self.total_days * 24

    @property
    def phase1_hours(self) -> int:
        return self.phase1_days * 24

    @property
    def output_dir(self) -> Path:
        return Path(__file__).resolve().parents[1] / "outputs"

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[1]
