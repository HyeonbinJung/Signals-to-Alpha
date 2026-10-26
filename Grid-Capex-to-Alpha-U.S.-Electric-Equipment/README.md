# Grid-Capex-to-Alpha — U.S. Electrical Equipment

> **Status:** Reproduced fixed-snapshot macro pilot; no equity alpha  
> **Research date:** 2026-10-19  
> **Scope:** U.S. power-output lead indicator for electrical-equipment production  
> **Study ID:** `grid` · [Quality standard](../RESEARCH_QUALITY_STANDARD.md) · [Machine-readable manifest](study.json)

## 01. Abstract

This study is part of **Signals to Alpha**, which treats real-economy data as *candidate* research signals and separates observable economic relationships from investable returns. Electricity demand and infrastructure investment provide a strong economic thesis, but a macro lead factor must still beat predictive baselines. The grid-output gap achieved six-month RMSE **4.124 pp** versus **4.228 pp** for momentum controls, yet lagged the historical-mean forecast (**3.524 pp**). An exploratory time-shift placebo (**p≈0.32**) did not support robust incremental value, and source vintages were not reconstructed. **Verdict:** useful structural context, but neither a verified point-in-time factor nor tested equity alpha.

## 02. Research Design & Hypotheses

Does U.S. power production growth lead electrical-equipment industrial production beyond persistence and macro controls? H1: positive load growth precedes equipment output; H2: a gap helps six-month forecasts out of sample; H3: any improvement survives timing and regime falsification.

## 03. Industry Context

Grid expansion, electrification and data-centre construction can raise medium-run equipment demand. IEA forward estimates motivate the sector but are **not** inserted as historical predictors or interpreted as a stock recommendation.

## 04. Data & Source Integrity

Official Federal Reserve G.17 series form the fixed snapshot (`fed_industrial_production_snapshot_2022_2026.csv`); publisher, retrieval and vintage caveats are in `source_register.csv`. August 2026 power output was ~7.00% YoY and electrical equipment ~5.38% YoY in this snapshot.

## 05. Point-in-Time Availability

A conservative lag is imposed, but the panel includes revised/mixed-vintage observations. Without archived release histories the exercise is a fixed-snapshot retrospective, not a fully point-in-time backtest.

## 06. Factor Construction

The pre-specified power-load versus equipment-output growth gap is transformed to a bounded lead feature; see `grid_alpha.py` and notebook for exact formula, fixed scaling and formation lag. No stock returns are used to tune it.

## 07. Exposure & Transmission

Industrial-production series proxy sector demand and supply, not company-specific business mix. Historical security-level revenue segmentation and firm exposures have not been assembled.

## 08. Outcomes & Baselines

Outcome: future electrical-equipment output growth, not security-level alpha. Compare historical mean and lagged-growth/momentum controls with an incrementally augmented Ridge forecast on matched out-of-sample origins.

## 09. Empirical Findings

Primary six-month RMSE: gap-augmented **4.124 pp**; momentum controls **4.228 pp**; historical mean **3.524 pp**. Improvement against one selected baseline is not success when a simpler benchmark beats both.

## 10. Robustness & Placebos

Exploratory temporal-shift placebo yields **p≈0.32**; the study also examines lag/horizon and feature sensitivity. The inference is weak, and exploratory shift tests are not valid exact randomization tests.

## 11. Regime Sensitivity

The newest observation and IEA outlook can support a demand narrative, but not stable predictive advantage across vintages or demand cycles. Later release revisions could alter retrospective fits.

## 12. Bias Audit & Verdict

Mixed historical vintages, publication lag, macro regimes, overlapping horizons, selective sector hypotheses and absent company returns all limit inference. **Conclusion:** grid investment story plausible, forecast factor not robustly validated.

## 13. Reproduction

Run from this directory: `python -m pip install -r requirements.txt`; `python grid_alpha.py`; `python -m pytest -q test_grid_alpha.py`; open `grid_capex_alpha_research.ipynb`. Existing notebook execution was validated on the 2026-10-19 CI; future executions need their own run logs.

## 14. Next-Stage Protocol

Obtain original FRED/ALFRED release vintages, orders/backlog and firm-specific product exposure; evaluate earnings surprises and industry-adjusted total returns under a purged walk-forward design, with costs, controls and an untouched holdout.

## 15. Sources & Artifacts

Primary provenance in `source_register.csv`; detailed published methodology and tables retained in [research notes](DETAILS.md). Official source series and references are linked there.
