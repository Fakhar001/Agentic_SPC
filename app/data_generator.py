from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config


def generate_lab_events(config: Config) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Create a deterministic synthetic laboratory event stream.

    The ground-truth fault is retained only for evaluation and is never used by
    the monitoring, validation, or governance agents.
    """
    rng = np.random.default_rng(config.seed)
    start = pd.Timestamp(config.start_time)
    degradation_start = start + pd.Timedelta(hours=config.degradation_start_hour)

    categories = ["chemistry", "hematology", "coagulation"]
    category_effect = {"chemistry": 4.0, "hematology": 0.0, "coagulation": 6.0}
    shift_effect = {"night": 2.5, "day": 0.0, "evening": 1.2}
    analyzer_effect = {"A1": 0.0, "A2": 1.5}

    rows: list[dict] = []
    specimen_counter = 0

    for hour_idx in range(config.total_hours):
        hour_start = start + pd.Timedelta(hours=hour_idx)
        shift = "night" if hour_start.hour < 8 else ("day" if hour_start.hour < 16 else "evening")
        workload = config.specimens_per_hour + int(rng.integers(-3, 4))
        if hour_idx >= config.degradation_start_hour and config.fault_mode != "null":
            workload += int(rng.integers(3, 8))

        maintenance_warning = bool(
            hour_idx >= config.degradation_start_hour + 3 and config.fault_mode != "null"
        )

        for _ in range(config.specimens_per_hour):
            specimen_counter += 1
            analyzer = "A2" if rng.random() < 0.72 else "A1"
            category = str(rng.choice(categories, p=[0.50, 0.35, 0.15]))
            elapsed = max(0, hour_idx - config.degradation_start_hour)

            degradation = 0.0
            if analyzer == "A2" and elapsed > 0:
                if config.fault_mode == "gradual":
                    degradation = config.fault_scale * min(24.0, 0.60 * elapsed)
                elif config.fault_mode == "intermittent":
                    active = (elapsed % 12) < 7
                    degradation = config.fault_scale * (min(18.0, 0.70 * elapsed) if active else 0.0)

            workload_effect = max(0.0, workload - config.specimens_per_hour) * 0.35
            tat = (
                config.baseline_tat_minutes
                + category_effect[category]
                + shift_effect[shift]
                + analyzer_effect[analyzer]
                + workload_effect
                + degradation
                + rng.normal(0.0, 4.5)
            )
            tat = max(35.0, tat)

            collected = hour_start + pd.Timedelta(minutes=int(rng.integers(0, 60)))
            received = collected + pd.Timedelta(minutes=max(1.0, rng.normal(8.0, 1.5)))
            analyzed = received + pd.Timedelta(minutes=max(2.0, rng.normal(18.0, 3.0)))
            min_verified_offset = (analyzed - collected).total_seconds() / 60.0 + 3.0
            verified = collected + pd.Timedelta(minutes=max(tat, min_verified_offset))

            rows.append(
                {
                    "specimen_id": f"SP-{specimen_counter:06d}",
                    "ingest_sequence": specimen_counter,
                    "collected_at": collected,
                    "received_at": received,
                    "analyzed_at": analyzed,
                    "verified_at": verified,
                    "analyzer_id": analyzer,
                    "test_category": category,
                    "shift": shift,
                    "workload": workload,
                    "maintenance_warning": maintenance_warning,
                    "calibration_status": "valid",
                    "known_degradation": bool(hour_start >= degradation_start and config.fault_mode != "null"),
                    "source_system": "LIS-SIM-01",
                    "dq_truth_issue": "",
                }
            )

    events = pd.DataFrame(rows)

    # Disjoint, known synthetic defects. There are 94 invalid base events and
    # 20 duplicate retry events, giving 114 quarantined rows in total. The
    # target hours intentionally concentrate those rows into 85 distinct
    # data-integrity hours, matching the case-level grouping used in the
    # manuscript audit-ledger accounting.
    target_hour_idx = sorted(rng.choice(config.total_hours, size=85, replace=False).tolist())
    per_hour_counts = {hour_idx: 2 if pos < 29 else 1 for pos, hour_idx in enumerate(target_hour_idx)}
    selected_by_hour: list[int] = []
    used: set[int] = set()
    for hour_idx in target_hour_idx:
        hour_start = start + pd.Timedelta(hours=int(hour_idx))
        hour_candidates = events.index[events["collected_at"].dt.floor("h").eq(hour_start)].tolist()
        rng.shuffle(hour_candidates)
        for idx in hour_candidates:
            if idx not in used:
                selected_by_hour.append(idx)
                used.add(idx)
                if sum(1 for chosen in selected_by_hour if events.loc[chosen, "collected_at"].floor("h") == hour_start) == per_hour_counts[hour_idx]:
                    break
    if len(selected_by_hour) != 114:
        raise RuntimeError("Could not allocate the configured synthetic data-quality defects.")

    issue_plan = (
        ["missing_timestamp"] * 28
        + ["timestamp_order"] * 18
        + ["tat_out_of_range"] * 12
        + ["calibration_invalid"] * 16
        + ["missing_provenance"] * 20
        + ["duplicate_specimen_id"] * 20
    )
    rng.shuffle(issue_plan)
    assignments = dict(zip(selected_by_hour, issue_plan))

    missing_idx = [idx for idx, issue in assignments.items() if issue == "missing_timestamp"]
    bad_order_idx = [idx for idx, issue in assignments.items() if issue == "timestamp_order"]
    extreme_idx = [idx for idx, issue in assignments.items() if issue == "tat_out_of_range"]
    calibration_idx = [idx for idx, issue in assignments.items() if issue == "calibration_invalid"]
    provenance_idx = [idx for idx, issue in assignments.items() if issue == "missing_provenance"]
    duplicate_idx = [idx for idx, issue in assignments.items() if issue == "duplicate_specimen_id"]

    events.loc[missing_idx, "verified_at"] = pd.NaT
    events.loc[missing_idx, "dq_truth_issue"] = "missing_timestamp"

    events.loc[bad_order_idx, "verified_at"] = (
        events.loc[bad_order_idx, "collected_at"] - pd.Timedelta(minutes=5)
    )
    events.loc[bad_order_idx, "dq_truth_issue"] = "timestamp_order"

    events.loc[extreme_idx, "verified_at"] = (
        events.loc[extreme_idx, "collected_at"] + pd.Timedelta(minutes=500)
    )
    events.loc[extreme_idx, "dq_truth_issue"] = "tat_out_of_range"

    events.loc[calibration_idx, "calibration_status"] = "invalid"
    events.loc[calibration_idx, "dq_truth_issue"] = "calibration_invalid"

    events.loc[provenance_idx, "source_system"] = None
    events.loc[provenance_idx, "dq_truth_issue"] = "missing_provenance"

    duplicates = events.loc[duplicate_idx].copy()
    duplicates["ingest_sequence"] = duplicates["ingest_sequence"] + len(events)
    duplicates["source_system"] = "LIS-SIM-01-RETRY"
    duplicates["dq_truth_issue"] = "duplicate_specimen_id"
    events = pd.concat([events, duplicates], ignore_index=True)

    events = events.sample(frac=1.0, random_state=config.seed).reset_index(drop=True)
    return events, degradation_start
