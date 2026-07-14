"""Monte Carlo ARL analysis for the manuscript EWMA configuration."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def simulate_arl(
    shift: float,
    *,
    repetitions: int = 200_000,
    seed: int = 20260627,
    lambda_ewma: float = 0.20,
    limit_multiplier: float = 3.30,
    max_steps: int = 20_000,
) -> dict[str, float | int]:
    """Estimate EWMA run length for i.i.d. standard-normal residuals."""
    rng = np.random.default_rng(seed)
    limit = limit_multiplier * np.sqrt(lambda_ewma / (2.0 - lambda_ewma))
    ewma = np.zeros(repetitions, dtype=float)
    run_length = np.zeros(repetitions, dtype=np.int32)
    active = np.ones(repetitions, dtype=bool)

    for step in range(1, max_steps + 1):
        if not active.any():
            break
        count = int(active.sum())
        ewma[active] = (1.0 - lambda_ewma) * ewma[active] + lambda_ewma * rng.normal(
            loc=shift, scale=1.0, size=count
        )
        signalled = active & (np.abs(ewma) >= limit)
        run_length[signalled] = step
        active[signalled] = False

    run_length[active] = max_steps
    return {
        "shift_sigma": shift,
        "repetitions": repetitions,
        "mean_run_length_hours": float(run_length.mean()),
        "standard_error_hours": float(run_length.std(ddof=1) / np.sqrt(repetitions)),
        "median_run_length_hours": float(np.median(run_length)),
        "censored_at_hours": max_steps,
    }


def run_reference_arl(
    output_path: Path,
    *,
    repetitions: int = 200_000,
    seed: int = 20260627,
) -> pd.DataFrame:
    """Run the paper's ARL0/ARL1 reference analysis and write a CSV."""
    rows = [
        simulate_arl(shift, repetitions=repetitions, seed=seed + offset)
        for offset, shift in enumerate((0.0, 0.5, 1.0, 1.5))
    ]
    table = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_path, index=False)
    return table
