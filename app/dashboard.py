from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

st.set_page_config(page_title="Agentic SPC Lab TAT", layout="wide")
st.title("Agentic SPC: Risk-Adjusted Clinical Laboratory TAT Monitoring")
st.caption("Synthetic research prototype for laboratory quality monitoring; not a clinical decision system.")

summary = pd.read_json(OUT / "summary.json", typ="series")
st.subheader("Run summary")
st.json(summary.to_dict())

monitoring = pd.read_csv(OUT / "hourly_monitoring.csv", parse_dates=["event_hour"])
st.subheader("Risk-adjusted EWMA monitoring")
st.line_chart(monitoring.set_index("event_hour")[["residual_mean", "ewma", "ucl", "lcl"]])

st.subheader("Data-quality evaluation against controlled synthetic defects")
st.dataframe(pd.read_csv(OUT / "data_quality_metrics.csv"), use_container_width=True)

st.subheader("500-replication stress-test summary")
st.dataframe(pd.read_csv(OUT / "stress_test_results.csv"), use_container_width=True)

st.subheader("Tamper-evident audit ledger")
st.dataframe(pd.read_csv(OUT / "audit_ledger.csv"), use_container_width=True)
