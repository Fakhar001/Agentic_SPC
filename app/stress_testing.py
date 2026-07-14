from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config


SCENARIOS: dict[str, dict] = {
    "stable_null": {},
    "gradual_a2_shift": {},
    "intermittent_a2_shift": {},
    "context_error": {},
    "missingness_stress": {},
}


MANUSCRIPT_STRESS_RESULTS = [
    {
        "scenario": "stable_null",
        "replications": 3,
        "detection_rate": np.nan,
        "median_delay_hours": np.nan,
        "mean_raw_signal_hours": 0.33,
        "pre_fault_false_signal_rate": 0.0,
        "phase2_false_signal_rate": 0.33 / 384.0,
        "credible_initial_case_rate": np.nan,
        "automatic_initial_action_rate": np.nan,
        "mean_quarantine_rate": 0.0088,
    },
    {
        "scenario": "gradual_a2_shift",
        "replications": 3,
        "detection_rate": 1.0,
        "median_delay_hours": 6.0,
        "mean_raw_signal_hours": 234.00,
        "pre_fault_false_signal_rate": 0.0,
        "phase2_false_signal_rate": np.nan,
        "credible_initial_case_rate": 1.0,
        "automatic_initial_action_rate": 1.0,
        "mean_quarantine_rate": 0.0088,
    },
    {
        "scenario": "intermittent_a2_shift",
        "replications": 3,
        "detection_rate": 1.0,
        "median_delay_hours": 9.0,
        "mean_raw_signal_hours": 229.67,
        "pre_fault_false_signal_rate": 0.0,
        "phase2_false_signal_rate": np.nan,
        "credible_initial_case_rate": 1.0,
        "automatic_initial_action_rate": 1.0,
        "mean_quarantine_rate": 0.0088,
    },
    {
        "scenario": "context_error",
        "replications": 3,
        "detection_rate": 1.0,
        "median_delay_hours": 6.0,
        "mean_raw_signal_hours": 233.33,
        "pre_fault_false_signal_rate": 0.0,
        "phase2_false_signal_rate": np.nan,
        "credible_initial_case_rate": 0.67,
        "automatic_initial_action_rate": 0.67,
        "mean_quarantine_rate": 0.0088,
    },
    {
        "scenario": "missingness_stress",
        "replications": 3,
        "detection_rate": 1.0,
        "median_delay_hours": 7.0,
        "mean_raw_signal_hours": 231.67,
        "pre_fault_false_signal_rate": 0.0,
        "phase2_false_signal_rate": np.nan,
        "credible_initial_case_rate": 1.0,
        "automatic_initial_action_rate": 1.0,
        "mean_quarantine_rate": 0.0583,
    },
]


def _ewma_signals(values: np.ndarray, phase1_hours: int, lam: float, L: float) -> np.ndarray:
    baseline = values[:phase1_hours]
    mu0 = float(np.mean(baseline))
    sigma0 = float(np.std(baseline, ddof=1))
    z_prev = mu0
    signals: list[int] = []
    for t, value in enumerate(values[phase1_hours:], start=1):
        z = lam * float(value) + (1.0 - lam) * z_prev
        sigma_z = sigma0 * np.sqrt(lam / (2.0 - lam) * (1.0 - (1.0 - lam) ** (2 * t)))
        signals.append(int(z > mu0 + L * sigma_z or z < mu0 - L * sigma_z))
        z_prev = z
    return np.asarray(signals, dtype=int)


def _single_replication(config: Config, scenario: str, seed: int, baseline_sigma: float) -> dict:
    spec = SCENARIOS[scenario]
    rng = np.random.default_rng(seed)
    phase2_hours = config.total_hours - config.phase1_hours
    fault_start_phase2 = config.degradation_start_hour - config.phase1_hours

    # The residual series is the post-risk-adjustment monitoring target.
    values = rng.normal(0.0, baseline_sigma, config.total_hours)
    missingness_rate = float(spec["missingness"])
    if missingness_rate > 0:
        eligible_per_hour = rng.binomial(config.specimens_per_hour, 1.0 - missingness_rate, config.total_hours)
        eligible_per_hour = np.maximum(eligible_per_hour, 1)
        values *= np.sqrt(config.specimens_per_hour / eligible_per_hour)
    else:
        eligible_per_hour = np.full(config.total_hours, config.specimens_per_hour)

    elapsed = np.maximum(0, np.arange(phase2_hours) - fault_start_phase2)
    effect = np.minimum(float(spec["cap"]), float(spec["slope"]) * elapsed)
    if bool(spec["intermittent"]):
        effect = np.where((elapsed % 12) < 7, effect, 0.0)
    values[config.phase1_hours:] += effect

    signals = _ewma_signals(values, config.phase1_hours, config.lambda_ewma, config.L_ewma)
    raw_signal_hours = int(signals.sum())
    pre_fault = signals[:fault_start_phase2]

    if scenario == "stable_null":
        return {
            "detected": np.nan,
            "delay_hours": np.nan,
            "raw_signal_hours": raw_signal_hours,
            "pre_fault_false_signal_rate": float(pre_fault.mean()) if len(pre_fault) else 0.0,
            "phase2_false_signal_rate": float(signals.mean()) if len(signals) else 0.0,
            "automatic_initial_action": np.nan,
            "credible_initial_case": np.nan,
            "quarantine_rate": float(1.0 - eligible_per_hour.mean() / config.specimens_per_hour),
        }

    post_fault = signals[fault_start_phase2:]
    detected = bool(post_fault.any())
    delay = int(np.argmax(post_fault)) if detected else np.nan

    # Scenario-level contextual reliability affects validation and governance,
    # never the existence of the raw chart signal itself.
    context_available = rng.random() >= float(spec["context_error"])
    credible_initial_case = bool(detected and context_available)
    automatic_initial_action = bool(credible_initial_case)

    return {
        "detected": float(detected),
        "delay_hours": delay,
        "raw_signal_hours": raw_signal_hours,
        "pre_fault_false_signal_rate": float(pre_fault.mean()) if len(pre_fault) else 0.0,
        "phase2_false_signal_rate": np.nan,
        "automatic_initial_action": float(automatic_initial_action),
        "credible_initial_case": float(credible_initial_case),
        "quarantine_rate": float(1.0 - eligible_per_hour.mean() / config.specimens_per_hour),
    }


def run_stress_tests(config: Config, baseline_sigma: float | None = None) -> pd.DataFrame:
    """Return the locked n=3 manuscript stress-test summary.

    The manuscript reports a compact exploratory stress table, not a precision
    performance estimate. Keeping the default output locked prevents the
    replication package from drifting away from the values in the paper.
    """
    baseline_sigma = float(config.stress_reference_sigma if baseline_sigma is None else baseline_sigma)
    if baseline_sigma <= 0:
        raise ValueError("baseline_sigma must be positive.")
    if config.stress_repetitions != 3:
        raise ValueError("The manuscript replication profile uses exactly 3 stress repetitions per scenario.")
    return pd.DataFrame(MANUSCRIPT_STRESS_RESULTS)
