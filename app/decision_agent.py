from __future__ import annotations

import pandas as pd


def propose_actions(validated_cases: pd.DataFrame) -> pd.DataFrame:
    records: list[dict] = []
    for _, row in validated_cases.iterrows():
        if row["validation_class"] == "data-quality concern":
            action = "open_data_integrity_ticket"
            action_class = "a1"
        elif row["priority"] == "high":
            action = "escalate_laboratory_quality_supervisor"
            action_class = "a3"
        elif row["validation_class"] == "credible":
            action = "increase_sampling_and_notify"
            action_class = "a1"
        else:
            action = "request_quality_review"
            action_class = "a2"
        records.append({**row.to_dict(), "proposed_action": action, "action_class": action_class})
    return pd.DataFrame(records)
