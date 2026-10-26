# Housing-Permits-to-Alpha — U.S. Building Materials

> **Status:** Reproduced fixed-snapshot macro falsification; no equity alpha  
> **Research date:** 2026-10-19  
> **Scope:** Housing starts/permits as leads for building-materials production  
> **Study ID:** `housing` · [Quality standard](../RESEARCH_QUALITY_STANDARD.md) · [Machine-readable manifest](study.json)

## 01. Abstract

This study is part of **Signals to Alpha**, which treats real-economy data as *candidate* research signals and separates observable economic relationships from investable returns. Housing permits and starts are plausible precursors to construction-material demand but do not automatically forecast producer output. In **98** six-month-ahead expanding-window origins, housing-augmented Ridge had RMSE **5.109 pp**, worse than macro controls (**4.874 pp**) and a historical mean (**4.808 pp**). Alternative horizons, wood-products outcomes, regime splits and lag-only placebos did not establish consistent incremental value; historic vintages remain unaudited. **Verdict:** an informative negative macro-factor result, with no tested equity alpha.

## 02. Research Design & Hypotheses

Do permits and starts improve six-month-ahead U.S. nonmetallic-mineral production forecasts? H1: permits/starts lead output; H2: incremental signals beat mean, autoregression and manufacturing/rates controls; H3: effects survive industry, horizon and timing alternatives.

## 03. Industry Context

Construction permits can become starts, construction orders and input demand, but rates, policy, inventory, infrastructure and substitution can break this transmission. Output is not corporate profits or a security return.

## 04. Data & Source Integrity

Six official FRED/Census/Federal Reserve series over January 2010–August 2026 (200 monthly aligned observations) are frozen in `fred_housing_materials_snapshot_2010_2026.csv`. Source list includes PERMIT, HOUST, IPG327S, IPG321S, IPMAN and FEDFUNDS.

## 05. Point-in-Time Availability

All formation features use observations at least two months old, and training labels receive additional maturity purge. Nonetheless the September 2026 initial permit estimate (**1.394m SAAR**) differs from revised FRED (**1.403m**), proving that static revised CSVs are **not** historical publication vintages.

## 06. Factor Construction

Let `YoY(X,t)=100 × ln(X[t]/X[t−12])`; `gap[t]=YoY(PERMIT,t−2)−YoY(HOUST,t−2)`. Train-fold-only scaling and fixed Ridge `α=25`; target `YoY(IPG327S,t+6)`. Full definitions and validity guards in `housing_alpha.py`.

## 07. Exposure & Transmission

NAICS 327 nonmetallic minerals is the primary output; NAICS 321 wood products is a cross-sector check. The pipeline feature is a macro proxy, not timestamped issuer-level exposure.

## 08. Outcomes & Baselines

Expanding-window forecast origins begin 2018-01 with 98 primary forecasts, using purged mature labels. Baselines: historical mean, target-only Ridge, manufacturing/rate Ridge; challengers add permits/starts or pipeline gap.

## 09. Empirical Findings

Six-month RMSE: mean **4.8079 pp**, target-only **4.8690**, macro **4.8737**, macro+housing **5.1094**, macro+gap **4.8751**. Full housing indicators worsened RMSE **0.3015 pp** vs historical mean.

## 10. Robustness & Placebos

Three-month target, wood-products outcome, pre/post-2022 slices, COVID exclusions and 12/24/36-month older-signal checks do not show robust incremental gain. Older-lag checks are timing falsifications, **not** exact permutation p-values.

## 11. Regime Sensitivity

Mortgage rates and COVID-era housing dynamics affect the mapping; six-month forward outcomes overlap heavily and retrospective snapshots embed revisions. Post-2022 test results still fail to demonstrate a robust advantage.

## 12. Bias Audit & Verdict

Publication-vintage leakage, overlapping labels, sector selection and the absence of firm fundamental/return panels remain material. **Conclusion:** interpretable demand pipeline, negative forecast-factor result.

## 13. Reproduction

From this directory: `python -m pip install -r requirements.txt`; `python housing_alpha.py`; `python -m pytest -q test_housing_alpha.py`; inspect `housing_permits_alpha_research.ipynb`. Reference outputs are `results_snapshot.json` and `oos_forecasts_snapshot.csv`.

## 14. Next-Stage Protocol

Rebuild period-correct Census/ALFRED data, add material orders and geographically aligned exposure, and examine firm earnings plus total-return rank IC against sector, rates, quality, momentum and cost baselines.

## 15. Sources & Artifacts

See `source_register.csv` for original series, and [research notes](DETAILS.md) for original full scorecards, cited dates and robustness breakdown.
