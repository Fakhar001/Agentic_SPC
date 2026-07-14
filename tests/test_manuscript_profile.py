import pandas as pd

from app.manuscript_profile import MANUSCRIPT_PROFILE, compute_cfdr


def test_manuscript_profile_matches_paper_baseline_and_cfdr():
    assert MANUSCRIPT_PROFILE.baseline_diagnostics() == {
        "phase1_residual_mean": -0.004,
        "phase1_residual_sd": 1.620,
        "phase1_residual_acf_lag_1": 0.044,
        "phase1_residual_acf_lag_24": -0.041,
    }
    ledger = pd.DataFrame(
        [
            {"priority": "moderate", "governance_decision": "permitted_automatic_workflow"},
            {"priority": "high", "governance_decision": "human_review_required"},
        ]
    )
    assert compute_cfdr(ledger) == (0, 1)
