from dataclasses import replace

from app.config import Config
from app.stress_testing import SCENARIOS, run_stress_tests


def test_stress_test_runs_all_governed_scenarios_with_small_replication_count():
    result = run_stress_tests(replace(Config(), stress_repetitions=3))
    assert set(result["scenario"]) == set(SCENARIOS)
    assert (result["replications"] == 3).all()
    assert "automatic_initial_action_rate" in result.columns
    gradual = result.loc[result["scenario"].eq("gradual_a2_shift")].iloc[0]
    missingness = result.loc[result["scenario"].eq("missingness_stress")].iloc[0]
    assert gradual["median_delay_hours"] == 6.0
    assert gradual["mean_raw_signal_hours"] == 234.00
    assert missingness["median_delay_hours"] == 7.0
    assert round(float(missingness["mean_quarantine_rate"]), 4) == 0.0583
