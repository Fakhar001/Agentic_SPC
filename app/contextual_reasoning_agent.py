from __future__ import annotations

import pandas as pd


def attach_context(monitoring: pd.DataFrame, dq_summary: pd.DataFrame) -> pd.DataFrame:
    df = monitoring.merge(
        dq_summary[["event_hour", "quarantined_records", "eligibility_rate", "dq_event"]],
        on="event_hour",
        how="left",
    )
    df["quarantined_records"] = df["quarantined_records"].fillna(0).astype(int)
    df["eligibility_rate"] = df["eligibility_rate"].fillna(1.0)
    df["dq_event"] = df["dq_event"].fillna(False).astype(bool)
    df["context_summary"] = df.apply(
        lambda r: (
            f"workload={r['workload']:.0f}; "
            f"A2_share={r['analyzer_a2_share']:.2f}; "
            f"A2_minus_A1_residual={r['a2_minus_a1_residual']:.2f}; "
            f"maintenance_warning={bool(r['maintenance_warning'])}; "
            f"dq_event={bool(r['dq_event'])}"
        ),
        axis=1,
    )
    return df
