from __future__ import annotations

import pandas as pd

from .config import Config

REQUIRED_TIME_COLUMNS = ["collected_at", "received_at", "analyzed_at", "verified_at"]
ISSUE_TYPES = [
    "missing_timestamp",
    "timestamp_order",
    "tat_out_of_range",
    "calibration_invalid",
    "missing_provenance",
    "duplicate_specimen_id",
]


def qualify_events(events: pd.DataFrame, config: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Qualify records without mutating or deleting raw source values."""
    df = events.copy()
    for col in REQUIRED_TIME_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    ordered = df.sort_values("ingest_sequence")
    duplicate_mask = ordered.duplicated(subset=["specimen_id"], keep="first")
    duplicate_mask = duplicate_mask.reindex(df.index).fillna(False)

    issue_lists: list[list[str]] = []
    for idx, row in df.iterrows():
        issues: list[str] = []
        if bool(duplicate_mask.loc[idx]):
            issues.append("duplicate_specimen_id")
        if row[REQUIRED_TIME_COLUMNS].isna().any():
            issues.append("missing_timestamp")
        else:
            chronologically_valid = bool(
                row["collected_at"] <= row["received_at"] <= row["analyzed_at"] <= row["verified_at"]
            )
            if not chronologically_valid:
                issues.append("timestamp_order")
            else:
                tat = (row["verified_at"] - row["collected_at"]).total_seconds() / 60.0
                if not (config.min_tat_minutes <= tat <= config.max_tat_minutes):
                    issues.append("tat_out_of_range")
        if str(row.get("calibration_status", "")) != "valid":
            issues.append("calibration_invalid")
        if pd.isna(row.get("source_system")) or str(row.get("source_system", "")).strip() == "":
            issues.append("missing_provenance")
        issue_lists.append(issues)

    df["dq_issues"] = issue_lists
    df["eligible_for_spc"] = df["dq_issues"].map(len).eq(0)
    df["event_hour"] = df["collected_at"].dt.floor("h")
    df["tat_minutes"] = (df["verified_at"] - df["collected_at"]).dt.total_seconds() / 60.0

    # Vector-form data quality components retained for auditability.
    df["q_complete"] = df[REQUIRED_TIME_COLUMNS].notna().all(axis=1).astype(int)
    df["q_plausible"] = (~df["dq_issues"].map(lambda x: "tat_out_of_range" in x)).astype(int)
    df["q_calibrated"] = df["calibration_status"].eq("valid").astype(int)
    df["q_synchronized"] = (~df["dq_issues"].map(lambda x: "timestamp_order" in x)).astype(int)
    df["q_provenance"] = df["source_system"].notna().astype(int)

    qualified = df.loc[df["eligible_for_spc"]].copy()
    quarantine = df.loc[~df["eligible_for_spc"]].copy()
    return qualified, quarantine


def summarize_data_quality(events: pd.DataFrame, quarantine: pd.DataFrame) -> pd.DataFrame:
    raw = events.copy()
    raw["collected_at"] = pd.to_datetime(raw["collected_at"], errors="coerce")
    raw["event_hour"] = raw["collected_at"].dt.floor("h")
    total = raw.groupby("event_hour").size().rename("raw_records")
    invalid = quarantine.groupby("event_hour").size().rename("quarantined_records")
    summary = pd.concat([total, invalid], axis=1).fillna(0)
    summary["quarantined_records"] = summary["quarantined_records"].astype(int)
    summary["dq_event"] = summary["quarantined_records"] > 0
    summary["eligibility_rate"] = 1.0 - summary["quarantined_records"] / summary["raw_records"]
    return summary.reset_index()


def data_quality_metrics(qualified: pd.DataFrame, quarantine: pd.DataFrame) -> pd.DataFrame:
    assessed = pd.concat([qualified, quarantine], ignore_index=True)
    assessed["truth_defect"] = assessed["dq_truth_issue"].fillna("").ne("")
    assessed["predicted_defect"] = ~assessed["eligible_for_spc"]

    rows: list[dict] = []

    def scores(truth: pd.Series, predicted: pd.Series) -> tuple[float, float, int, int, int]:
        tp = int((truth & predicted).sum())
        fp = int((~truth & predicted).sum())
        fn = int((truth & ~predicted).sum())
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        return precision, recall, tp, fp, fn

    p, r, tp, fp, fn = scores(assessed["truth_defect"], assessed["predicted_defect"])
    rows.append({"defect_type": "overall", "precision": p, "recall": r, "true_positive": tp, "false_positive": fp, "false_negative": fn})

    for issue in ISSUE_TYPES:
        truth = assessed["dq_truth_issue"].eq(issue)
        predicted = assessed["dq_issues"].map(lambda issues: issue in issues)
        p, r, tp, fp, fn = scores(truth, predicted)
        rows.append({"defect_type": issue, "precision": p, "recall": r, "true_positive": tp, "false_positive": fp, "false_negative": fn})

    return pd.DataFrame(rows)
