from app.arl_analysis import simulate_arl


def test_arl_simulation_returns_reproducible_finite_result():
    first = simulate_arl(1.0, repetitions=200, seed=7, max_steps=500)
    second = simulate_arl(1.0, repetitions=200, seed=7, max_steps=500)
    assert first == second
    assert first["repetitions"] == 200
    assert first["mean_run_length_hours"] > 0
