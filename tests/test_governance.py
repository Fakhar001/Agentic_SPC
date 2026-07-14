import pandas as pd

from app.governance_agent import authorize_actions


def test_high_priority_requires_human_review_and_prohibited_action_is_blocked():
    proposals = pd.DataFrame(
        [
            {
                "event_hour": "2026-01-01",
                "validation_class": "credible",
                "priority": "high",
                "proposed_action": "escalate_laboratory_quality_supervisor",
                "action_class": "a3",
            },
            {
                "event_hour": "2026-01-01",
                "validation_class": "credible",
                "priority": "critical",
                "proposed_action": "modify_clinical_treatment",
                "action_class": "a4",
            },
        ]
    )
    out = authorize_actions(proposals)
    assert bool(out.loc[0, "human_review_required"]) is True
    assert out.loc[1, "governance_decision"] == "prohibited"
    assert out.loc[1, "authorized_action"] == "none"
