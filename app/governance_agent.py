from __future__ import annotations

import pandas as pd

PREAUTHORIZED = {"increase_sampling_and_notify", "open_data_integrity_ticket"}
PROHIBITED = {"modify_clinical_treatment", "change_medication", "override_safety_system"}


def authorize_actions(proposals: pd.DataFrame, policy_version: str = "lab_tat_policy_v0.2.0") -> pd.DataFrame:
    records: list[dict] = []
    for _, row in proposals.iterrows():
        action = row["proposed_action"]
        priority = row["priority"]
        conflict = False  # Reference scenario has no unresolved source conflict at case creation.
        if action in PROHIBITED:
            decision = "prohibited"
            authorized_action = "none"
            human_review_required = True
        elif action in PREAUTHORIZED and priority in {"low", "moderate"} and not conflict:
            decision = "permitted_automatic_workflow"
            authorized_action = action
            human_review_required = False
        elif action == "escalate_laboratory_quality_supervisor":
            decision = "human_review_required"
            authorized_action = "pending_quality_supervisor_authorization"
            human_review_required = True
        else:
            decision = "defer_to_quality_review"
            authorized_action = "pending_quality_review"
            human_review_required = True

        records.append(
            {
                **row.to_dict(),
                "governance_decision": decision,
                "authorized_action": authorized_action,
                "human_review_required": human_review_required,
                "policy_version": policy_version,
            }
        )
    return pd.DataFrame(records)
