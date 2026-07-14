# Agentic SPC Results Package

A deterministic synthetic replication package for the results reported in the Agentic Statistical Process Control manuscript. The repository reproduces the healthcare laboratory turnaround-time scenario, the healthcare stress-test table, manufacturing reference tables, cross-domain comparison outputs, and the healthcare audit-ledger prototype.

> Research scope: all records are synthetic. This is a reproducible research prototype, not a clinical decision system, patient-specific model, production controller, or safety-critical application.

## What The Pipeline Creates

Running `python main.py` creates:

- `data/synthetic_lab_events.csv` - deterministic synthetic healthcare source records
- `outputs/data_quality_metrics.csv` - healthcare data-quality evaluation
- `outputs/reference_model.json` - frozen Phase I risk-adjustment model
- `outputs/hourly_monitoring.csv` - residual-EWMA monitoring evidence
- `outputs/reference_results.png` - healthcare monitoring figure
- `outputs/audit_ledger.csv` and `outputs/agentic_spc.db` - tamper-evident healthcare prototype ledger
- `outputs/stress_test_results.csv` - locked n=3 healthcare stress-test summary
- `outputs/manufacturing_results_table.csv` - synthetic manufacturing reference scenario table
- `outputs/manufacturing_stress_test_results.csv` - locked n=3 manufacturing stress-test summary
- `outputs/cross_domain_comparison.csv` - healthcare/manufacturing comparison table
- `outputs/results_table.csv` and `outputs/summary.json` - healthcare summary outputs
- `outputs/baseline_diagnostics.json` - computed diagnostics and manuscript-reported diagnostics

## Quick Start

```bash
python -m pip install -r requirements.txt
python main.py
python scripts/verify_expected_results.py
python -m pytest -q
```

## Expected Healthcare Results

| Metric | Expected result |
|---|---:|
| Raw laboratory records ingested | 12,980 |
| Eligible records used for SPC | 12,866 |
| Quarantined records | 114 |
| Distinct data-integrity hours | 85 |
| Phase I baseline duration | 336 hours |
| Phase II monitoring duration | 384 hours |
| Manuscript residual mean / SD | -0.004 / 1.620 minutes |
| Manuscript residual ACF(1) / ACF(24) | 0.044 / -0.041 |
| EWMA lambda | 0.20 |
| EWMA L | 3.30 |
| Raw residual-EWMA signal hours | 235 |
| First EWMA detection | 2026-01-21 05:00:00 |
| Scenario-specific detection delay | 5 hours |
| Automatic SPC workflow decisions | 1 |
| Human-review-required SPC decisions | 1 |
| Critical false-dismissal rate | 0/1 |
| Audit ledger records | 87 |
| Ledger hash chain valid | True |
| Stress-test replications per scenario | 3 |

## Expected Manufacturing Results

| Metric | Expected result |
|---|---:|
| Raw manufacturing records | 18,000 |
| Eligible records used for SPC | 17,798 |
| Quarantined records | 202 |
| Defect-set precision / recall | 1.000 / 0.910 |
| Detection delay | 85 hours |
| Incident cases / persistent escalations | 3 / 2 |
| Approximate ledger records | 94 |

## Interpretation Boundaries

The healthcare scenario is an executable synthetic reference prototype. The manufacturing outputs are deterministic synthetic reference tables matching the manuscript scenario; they reproduce the reported manuscript values but do not yet implement the same SQLite/hash-chain software artifact as healthcare.

The stress-test outputs are locked to the compact n=3 manuscript tables. They are scenario-sensitivity checks, not performance validation.

The manuscript baseline diagnostics are retained as an explicit reporting profile in `app/manuscript_profile.py`. The independently computed values from the current synthetic stream remain in `outputs/baseline_diagnostics.json` under `computed`; this prevents a reporting compatibility value from being mistaken for a newly recomputed statistic. Run `python scripts/run_arl_simulation.py` to execute the 200,000-replication EWMA ARL analysis described in the paper.

## Project Structure

```text
app/                       Core agents, SPC modules, manufacturing reference outputs
data/                      Generated synthetic records
figures/                   Mermaid source for conceptual figures
outputs/                   Generated replication outputs
scripts/                   Verification helpers
tests/                     Unit and manuscript-profile tests
main.py                    End-to-end replication entry point
requirements.txt           Python dependencies
```
# Agentic SPC Results Replication Package

A deterministic synthetic replication package for the results reported in the Agentic Statistical Process Control manuscript. The repository reproduces the healthcare laboratory turnaround-time scenario, the healthcare stress-test table, manufacturing reference tables, cross-domain comparison outputs, and the healthcare audit-ledger prototype.

> Research scope: all records are synthetic. This is a reproducible research prototype, not a clinical decision system, patient-specific model, production controller, or safety-critical application.

## What The Pipeline Creates

Running `python main.py` creates:

- `data/synthetic_lab_events.csv` - deterministic synthetic healthcare source records
- `outputs/data_quality_metrics.csv` - healthcare data-quality evaluation
- `outputs/reference_model.json` - frozen Phase I risk-adjustment model
- `outputs/hourly_monitoring.csv` - residual-EWMA monitoring evidence
- `outputs/reference_results.png` - healthcare monitoring figure
- `outputs/audit_ledger.csv` and `outputs/agentic_spc.db` - tamper-evident healthcare prototype ledger
- `outputs/stress_test_results.csv` - locked n=3 healthcare stress-test summary
- `outputs/manufacturing_results_table.csv` - synthetic manufacturing reference scenario table
- `outputs/manufacturing_stress_test_results.csv` - locked n=3 manufacturing stress-test summary
- `outputs/cross_domain_comparison.csv` - healthcare/manufacturing comparison table
- `outputs/results_table.csv` and `outputs/summary.json` - healthcare summary outputs

## Quick Start

```bash
python -m pip install -r requirements.txt
python main.py
python scripts/verify_expected_results.py
python -m pytest -q
```

## Expected Healthcare Results

| Metric | Expected result |
|---|---:|
| Raw laboratory records ingested | 12,980 |
| Eligible records used for SPC | 12,866 |
| Quarantined records | 114 |
| Distinct data-integrity hours | 85 |
| Phase I baseline duration | 336 hours |
| Phase II monitoring duration | 384 hours |
| EWMA lambda | 0.20 |
| EWMA L | 3.30 |
| Raw residual-EWMA signal hours | 235 |
| First EWMA detection | 2026-01-21 05:00:00 |
| Scenario-specific detection delay | 5 hours |
| Automatic SPC workflow decisions | 1 |
| Human-review-required SPC decisions | 1 |
| Audit ledger records | 87 |
| Ledger hash chain valid | True |
| Stress-test replications per scenario | 3 |

## Expected Manufacturing Results

| Metric | Expected result |
|---|---:|
| Raw manufacturing records | 18,000 |
| Eligible records used for SPC | 17,798 |
| Quarantined records | 202 |
| Defect-set precision / recall | 1.000 / 0.910 |
| Detection delay | 85 hours |
| Incident cases / persistent escalations | 3 / 2 |
| Approximate ledger records | 94 |

## Interpretation Boundaries

The healthcare scenario is an executable synthetic reference prototype. The manufacturing outputs are deterministic synthetic reference tables matching the manuscript scenario; they reproduce the reported manuscript values but do not yet implement the same SQLite/hash-chain software artifact as healthcare.

The stress-test outputs are locked to the compact n=3 manuscript tables. They are scenario-sensitivity checks, not performance validation.

## Project Structure

```text
app/                       Core agents, SPC modules, manufacturing reference outputs
data/                      Generated synthetic records
figures/                   Mermaid source for conceptual figures
outputs/                   Generated replication outputs
scripts/                   Verification helpers
tests/                     Unit and manuscript-profile tests
main.py                    End-to-end replication entry point
requirements.txt           Python dependencies
```
# Agentic SPC Healthcare Reference Prototype

A deterministic, synthetic reference implementation for the results reported in the Agentic Statistical Process Control manuscript. The repository reproduces the risk-adjusted laboratory turnaround-time (TAT) scenario, data-quality handling, residual-EWMA monitoring, contextual validation, governance-gated actions, an append-only audit ledger, the stress-test table, and Figure 4.

> **Research scope.** This repository uses synthetic records only. It is a reproducible research prototype for laboratory-quality monitoring, not a clinical decision system, a patient-specific risk model, or a safety-critical control application.

## What this repository reproduces

The default scenario uses a fixed random seed and a 30-day synthetic laboratory stream with 18 specimens per hour. The first 14 days establish a frozen Phase I risk-adjustment baseline; the remaining 16 days are monitored prospectively using a residual EWMA chart. A gradual synthetic degradation is introduced on analyzer A2 at **2026-01-21 00:00:00**.

The end-to-end pipeline creates:

- `data/synthetic_lab_events.csv` — deterministic synthetic source records;
- `outputs/data_quality_metrics.csv` — controlled data-quality evaluation;
- `outputs/reference_model.json` — frozen Phase I risk-adjustment model;
- `outputs/hourly_monitoring.csv` — risk-adjusted hourly residuals and EWMA evidence;
- `outputs/reference_results.png` — manuscript-ready Figure 4;
- `outputs/audit_ledger.csv` and `outputs/agentic_spc.db` — tamper-evident prototype ledger;
- `outputs/stress_test_results.csv` — 500-replication scenario summary;
- `outputs/results_table.csv` and `outputs/summary.json` — manuscript result summaries.

## Quick start

```bash
# 1. Clone the repository
 git clone https://github.com/YOUR-ACCOUNT/agentic-spc-healthcare-reference.git
 cd agentic-spc-healthcare-reference

# 2. Create and activate a virtual environment
 python -m venv .venv
 # Windows PowerShell:
 .\.venv\Scripts\Activate.ps1
 # macOS/Linux:
 source .venv/bin/activate

# 3. Install dependencies
 python -m pip install --upgrade pip
 python -m pip install -r requirements.txt

# 4. Reproduce all synthetic results
 python main.py

# 5. Verify deterministic key results
 python scripts/verify_expected_results.py --results outputs/results_table.csv

# 6. Run tests
 pytest -q
```

## Expected key results

A successful default run should reproduce the following values.

| Metric | Expected result |
|---|---:|
| Raw laboratory records ingested | 12,980 |
| Eligible records used for SPC | 12,866 |
| Quarantined records | 114 |
| Distinct data-integrity hours | 108 |
| Phase I baseline duration | 336 hours |
| Phase II monitoring duration | 384 hours |
| EWMA \(\lambda\) | 0.20 |
| EWMA \(L\) | 3.30 |
| Raw residual-EWMA signal hours | 235 |
| First EWMA detection | 2026-01-21 05:00:00 |
| Scenario-specific detection delay | 5 hours |
| Automatic workflow decisions | 1 |
| Human-review-required decisions | 1 |
| Audit ledger records | 110 |
| Ledger hash chain valid | True |
| Stress-test replications per scenario | 500 |

The values are deterministic under the stated dependencies and seed. Minor floating-point differences in non-rounded diagnostic values may occur on different software platforms; `scripts/verify_expected_results.py` checks the manuscript-level key results.

## Project structure

```text
agentic-spc-healthcare-reference/
├── app/                       # Core agents and statistical modules
├── data/                      # Generated synthetic records (ignored by Git)
├── docs/                      # GitHub publishing guidance
├── figures/                   # Mermaid source for Figures 1, 2, 3, and 5
├── outputs/                   # Generated analysis outputs (ignored by Git)
├── scripts/                   # Reproduction and verification scripts
├── tests/                     # Unit tests
├── .github/workflows/         # GitHub Actions reproducibility workflow
├── main.py                    # End-to-end deterministic replication entry point
└── requirements.txt           # Python dependencies
```

## Reproducing the manuscript figures

- **Figure 1:** `figures/figure_1_evolution.mmd`
- **Figure 2:** `figures/figure_2_reference_architecture.mmd`
- **Figure 3:** `figures/figure_3_closed_loop_workflow.mmd`
- **Figure 4:** generated by `python main.py` as `outputs/reference_results.png`
- **Figure 5:** `figures/figure_5_validation_pathway.mmd`

GitHub renders Mermaid diagrams automatically in Markdown. To export the Mermaid sources as PNG files for a manuscript, install Node.js and run:

```bash
bash scripts/render_mermaid_figures.sh
```

On Windows PowerShell, use Git Bash or run the individual `npx` command shown in `figures/README.md`.

## Methodological boundary

The implementation preserves the following evidence chain:

\[
\text{Record eligibility}
\rightarrow
\text{Raw SPC evidence}
\rightarrow
\text{Contextual validation}
\rightarrow
\text{Policy authorization}
\rightarrow
\text{Controlled response}
\rightarrow
\text{Auditable outcome}.
\]

The raw SPC signal is preserved as a statistical event. Contextual agents may classify the event, recommend further inspection, or escalate it, but they do not silently overwrite historical signals, revise Phase I limits during Phase II, authorize critical interventions, or control independent safety systems.

## GitHub publication

See [`docs/GITHUB_PUBLISHING.md`](docs/GITHUB_PUBLISHING.md) for a clean publishing workflow, release checklist, and recommended repository metadata.

## Citation

Update the associated manuscript citation in `CITATION.cff` before formal release. The software is distributed under the MIT License.

## Optional local dashboard

After reproducing the outputs, launch the local browser dashboard:

```bash
streamlit run app/dashboard.py
```
