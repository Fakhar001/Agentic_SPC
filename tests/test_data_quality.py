from app.config import Config
from app.data_generator import generate_lab_events
from app.data_quality_agent import data_quality_metrics, qualify_events
from app.data_quality_agent import summarize_data_quality


def test_controlled_synthetic_defects_are_quarantined_and_scored():
    cfg = Config()
    events, _ = generate_lab_events(cfg)
    qualified, quarantine = qualify_events(events, cfg)
    metrics = data_quality_metrics(qualified, quarantine)
    overall = metrics.loc[metrics["defect_type"].eq("overall")].iloc[0]

    assert len(events) == 12_980
    assert len(quarantine) == 114
    assert len(qualified) + len(quarantine) == len(events)
    assert int(summarize_data_quality(events, quarantine)["dq_event"].sum()) == 85
    assert overall["precision"] == 1.0
    assert overall["recall"] == 1.0
