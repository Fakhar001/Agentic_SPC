from app.manufacturing_reference import (
    cross_domain_comparison,
    manufacturing_results_table,
    manufacturing_stress_results,
)


def test_manufacturing_reference_tables_match_manuscript_profile():
    results = manufacturing_results_table()
    observed = dict(zip(results["Measure"], results["Result"]))
    assert observed["Raw manufacturing records"] == "18000"
    assert observed["Eligible records entering SPC"] == "17798"
    assert observed["Quarantined records"] == "202"
    assert observed["First post-degradation signal delay hours"] == "85"
    assert observed["Persistent-signal escalation cases"] == "2"

    stress = manufacturing_stress_results()
    gradual = stress.loc[stress["scenario"].eq("gradual_machine_m2_tool_wear")].iloc[0]
    intermittent = stress.loc[stress["scenario"].eq("intermittent_machine_m2_tool_wear")].iloc[0]
    assert gradual["median_delay_hours"] == 38.0
    assert intermittent["median_delay_hours"] == 98.0

    comparison = cross_domain_comparison()
    delay = comparison.loc[comparison["Metric"].eq("Detection delay (primary scenario)")].iloc[0]
    assert delay["Healthcare (TAT)"] == "5 hours"
    assert delay["Manufacturing (dimensional)"] == "85 hours"
