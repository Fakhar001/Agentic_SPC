from __future__ import annotations

from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd


def create_results_plot(monitoring: pd.DataFrame, degradation_start, output_path: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    event_hour = monitoring["event_hour"].to_numpy()

    axes[0].plot(event_hour, monitoring["residual_mean"].to_numpy(), alpha=0.40, label="Hourly mean residual")
    axes[0].plot(event_hour, monitoring["ewma"].to_numpy(), linewidth=2, label="Residual EWMA")
    axes[0].plot(event_hour, monitoring["ucl"].to_numpy(), linestyle="--", label="EWMA UCL")
    axes[0].plot(event_hour, monitoring["lcl"].to_numpy(), linestyle="--", label="EWMA LCL")
    signals = monitoring.loc[monitoring["raw_spc_signal"].eq(1)]
    if not signals.empty:
        axes[0].scatter(
            signals["event_hour"].to_numpy(),
            signals["ewma"].to_numpy(),
            marker="x",
            s=40,
            label="Raw SPC signal",
        )
    axes[0].axvline(degradation_start, linestyle=":", linewidth=2, label="Synthetic degradation start")
    axes[0].set_title("Risk-Adjusted Laboratory TAT Monitoring")
    axes[0].set_ylabel("Minutes")
    axes[0].legend(ncol=3, fontsize=8)

    axes[1].plot(event_hour, monitoring["a2_minus_a1_residual"].to_numpy(), label="A2 - A1 residual contrast")
    axes[1].axhline(0.0, linestyle="--", linewidth=1)
    axes[1].axvline(degradation_start, linestyle=":", linewidth=2, label="Synthetic degradation start")
    axes[1].set_xlabel("Time")
    axes[1].set_ylabel("Minutes")
    axes[1].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def write_json(data: dict, output_path: Path) -> None:
    output_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def write_summary(summary: dict, results_table: pd.DataFrame, output_dir: Path) -> None:
    write_json(summary, output_dir / "summary.json")
    results_table.to_csv(output_dir / "results_table.csv", index=False)
