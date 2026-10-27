# Air-Traffic Demand Gap → U.S. Aerospace Manufacturing (NAICS 3364)

**Status: REPRODUCED MACRO PILOT / NOT POINT-IN-TIME / NOT EQUITY ALPHA.** As-of snapshot: **2026-10-26**. Reference standard: K-Food v3's falsifiable mechanism, data hierarchy, executed diagnostics and explicit negative verdict.

## 01. Abstract

**Research question:** Does lagged U.S. air revenue passenger-mile growth, relative to broad manufacturing momentum, improve **six-month-ahead year-on-year aerospace industrial production** forecasts beyond expanding-window macro controls? The fixed-snapshot panel contains **201** monthly aerospace and manufacturing observations (2010-01–2026-09) and **150** airline observations (2014-01–2026-06). A purged expanding-window experiment generates **77** common-origin forecasts (2019-11–2026-03). The airline-gap model **fails**: RMSE **19.890 pp** versus **16.967 pp** for macro controls and **13.810 pp** for the historical mean. This is an industrial production falsification, not a company sales or stock-return study.

## 02. Research Design & Hypotheses

- **H1:** Lagged airline traffic growth adds positive incremental OOS forecast accuracy (RMSE_macro − RMSE_full > 0).
- **H2:** The incremental gain persists when the 2020–21 disruption is excluded and the horizon changes from six months to three or twelve.
- **H3:** The improvement is robust to bounded ±20% economic-exposure weight changes and block-aware placebo shuffles.
- **Null/counterthesis:** Airline passenger miles mainly affect **utilization and aftermarket**, while aerospace factory output reflects multi-year order backlogs, defense procurement, supply-chain constraints, safety oversight and labor. Contemporary airline growth may be too late or too noisy to lead production.
- **Predeclared failure rule:** A challenger that fails either the macro-control or simple-mean baseline cannot be called a useful forecast improvement; no security-return inference is permitted without separate equity data.

## 03. Industry Context

The [Aerospace Industries Association 2026 report](https://www.aia-aerospace.org/news/2026-aia-facts-figures-u-s-aerospace-defense-industry-leads-the-world-with-1-trillion-in-sale/) reports approximately **$988.6 billion** of 2025 U.S. aerospace-and-defense sales (broader than the G.17 aerospace manufacturing production index), and **$506 billion** in direct output. Commercial aerospace and defense operate under different demand regimes. Airline miles proxy flight utilization; aircraft production responds to backlogs and capacity over longer horizons, so the factor's sign and timing are not mechanically guaranteed.

## 04. Data & Source Integrity

`data/source_register.csv` provides A/B/C evidence grades, publisher, exact URL, source release date, frozen observation coverage, units, revisions, role and caveats. **A**: [Federal Reserve G.17 aerospace IP](https://fred.stlouisfed.org/data/IPG3364S), updated **2026-10-16**, 201 rows from 2010-01 to 2026-09. **B**: [Federal Reserve manufacturing IP](https://fred.stlouisfed.org/data/IPMAN), updated **2026-10-16**, previously frozen in the printing study; **B**: [BTS airline passenger miles](https://fred.stlouisfed.org/data/AIRRPMTSID11), updated **2026-10-01**, previously frozen in the hospitality study. The complete CSV is frozen in `data/frozen_observations_2026-10-26.csv` with a SHA-256 in `results/metrics.json`. Aerospace values **84.8531** (2010-01), **54.3996** (2020-04), **99.2876** (2026-09) were independently spot-checked against FRED. **Important:** reuse of previously manually transcribed series is not a new row-level audit; see `data/provenance_audit.md`.

## 05. Point-in-Time Availability

For formation month **t**, the signal uses airline data only through **t−4 months** and manufacturing/aerospace data only through **t−2 months**. Training observation **s** is admitted only if its six-month-ahead outcome plus a one-month release buffer is available by t: **s + 6 + 1 ≤ t**. These delays are conservative assumptions, **not original release-date proof**. Historical vintages, contemporaneous revisions, and month-specific initial publication timestamps remain **UNKNOWN**; all values are latest-revised as of 2026-10-26. This is therefore a **retrospective association/falsification pilot**.

## 06. Factor Construction

Define `g^X_t = 100 ln(X_t / X_{t−12})` (percentage points of log YoY growth). At month t, `a_t = g^AIR_{t−4}`, `m_t = g^MFG_{t−2}`, `p_t = g^AERO_{t−2}`. The fixed nonlinear gap is `F_t = 30 tanh[(a_t − m_t)/30]`; the 30 pp scale is fixed **ex ante**, not fitted using future data. Outcome is `y_t = g^AERO_{t+6}`. All regression scaling uses training-only means and standard deviations. Fixed Ridge penalty **α=10**, no hyperparameter search on the OOS sample.

## 07. Exposure & Transmission

`data/company_exposure_map.csv` contains dated **qualitative**, not fitted, company exposure: Boeing commercial airplanes versus defense/services ([2025 results published 2026-01-27](https://investors.boeing.com/investors/news/press-release-details/2026/Boeing-Reports-Fourth-Quarter-Results/default.aspx)); GE Aerospace commercial/defense engines and aftermarket ([2025-02-03 report](https://www.geaerospace.com/news/articles/smooth-takeoff-ge-aerospace-releases-first-annual-report-standalone-company)); RTX Pratt & Whitney, Collins and Raytheon ([2025 results published 2026-01-27](https://www.rtx.com/news/news-center/2026/01/27/rtx-reports-2025-results-and-announces-2026-outlook-)). Historical exposure **weights are UNKNOWN**; no company observations enter the statistical panel. The factor sensitivity perturbs **economic formula weights**, not estimated company revenue exposures. A **leave-one-company-out** statistic is inapplicable without a company panel; `results/leave_one_year_out.csv` instead reports temporal dependence.

## 08. Outcomes & Baselines

Primary outcome: U.S. G.17 **aerospace manufacturing industrial production** (NAICS 3364), six-month-ahead YoY log growth. Models on identical **77** origins: expanding historical target mean; direct lagged aerospace YoY persistence; two-variable standardized Ridge (`p_t,m_t`); augmented Ridge (`p_t,m_t,F_t`); gap-only Ridge; and no-manufacturing-control ablation. **No** firm revenue/EPS, dividend-adjusted stock returns, sector-neutral long/short spread, trading cost or capacity data were collected. Equity Rank IC and return spreads are **NOT APPLICABLE**.

## 09. Empirical Findings

| Model | RMSE (pp) | MAE (pp) |
|---|---:|---:|
| Historical mean | **13.810** | **11.800** |
| Aerospace persistence | 17.539 | 12.807 |
| Macro Ridge | 16.967 | 13.005 |
| **Macro + air gap** | **19.890** | **16.489** |
| Air gap alone | 25.421 | 18.844 |
| Aero + air gap, no manufacturing | 20.374 | 16.538 |

The **predeclared incremental RMSE difference is −2.923 pp** (macro minus augmented), and the full model is **6.080 pp worse** than the historical mean. The raw full-model Pearson forecast/outcome correlation is **0.262**, but this does not compensate for large calibration errors. Figures 01–06 show levels, growth inputs, factor, forecast trajectories, scorecard and paired cumulative loss; all are computed from frozen observations and OOS outputs.

## 10. Robustness & Placebos

- **1,000** randomized **12-month block-order shuffles** of the candidate factor with a complete expanding-window refit: observed improvement is exceeded by **93.2%** of shuffled outcomes; this is an *exploratory tail fraction*, **not an exact randomization p-value** under serial dependence or regime change.
- **2,000** paired circular moving-block bootstrap draws (12-month blocks): 95% interval for macro-minus-full RMSE **[−6.511, −0.369] pp**, entirely negative in this resampling specification; dependence and finite-sample coverage remain concerns.
- **1,000** ±20% perturbations of the airline and manufacturing factor coefficients: **0%** improved over macro controls. A separate ablation without manufacturing controls has RMSE **20.374 pp**.
- Leave-one-year-out scores are saved; this is *score sensitivity*, not a leave-one-company-out backtest.

## 11. Regime Sensitivity

Alternative three-month and twelve-month horizons yield macro-minus-full RMSE **−6.286 pp** (83 origins) and **−4.083 pp** (65 origins). Using a six-month airline release lag yields **−0.368 pp** (75 origins); using a three-month G.17 lag yields **−4.231 pp** (77 origins). Excluding **2020–2021** yields **−2.220 pp** on 53 scored origins, still negative. The pre-2020 segment has **only two** OOS origins and **must not** be interpreted as reliable regime evidence.

## 12. Bias Audit & Verdict

**Publication/revision leakage:** historic G.17/BTS initial releases not reconstructed; conservative fixed lags cannot eliminate revised-snapshot leakage. **Selection/multiple testing:** one predeclared principal factor, with horizons/lags/regimes labeled secondary and no familywise correction; previous failed studies imply portfolio-level publication-selection risk. **Survivorship:** aggregate industrial index avoids single-stock survivor screening but is subject to industry definition/reclassification and benchmark revision. **Causality:** correlation does not identify airline fleet orders, export demand, defense, labor or production capacity. **Execution/costs:** no stock portfolio or trade cost model; no alpha claim. **Verdict: REPRODUCED NEGATIVE MACRO LEAD-FACTOR PILOT; NOT PIT; NOT INVESTABLE EQUITY ALPHA.**

## 13. Reproduction

From this directory with Python 3.11+: `python -m pip install -r requirements.txt`; `python run_analysis.py`; `python -m pytest tests -q`; `jupyter nbconvert --to notebook --execute research.ipynb --output research_reexecuted.ipynb --ExecutePreprocessor.timeout=900`. The analysis creates `data/derived_formation_panel.csv`, `results/` tables and **10** computed `figures/` PNGs; the notebook stores its own calculated tables and plots. All 1,000+ placebo/perturbation and 2,000 bootstrap draws use fixed seeds. The root `python scripts/validate_studies.py` is required in a full repository checkout. Structural validation is **not** an empirical reproduction certificate.

## 14. Next-Stage Protocol

Obtain ALFRED/Federal Reserve **original release vintages** and exact BTS initial-release timestamps; independently compare every frozen raw row against downloadable originals and preserve hashes. Add FAA airline fleet/orders/backlog and export controls to separate utilization from OEM production. Construct a historical quarterly company panel from Boeing/GE Aerospace/RTX filings with dated revenue segment exposures, and independently obtain dividend/split-adjusted total returns, market/sector benchmarks, turnover and execution costs. Reserve a later, untouched holdout period and correct across all industry-factor searches before considering investment claims.

## 15. Sources & Artifacts

The complete A/B/C register and revision notes are in [`data/source_register.csv`](data/source_register.csv); original data and checks are in [`data/provenance_audit.md`](data/provenance_audit.md). Computed OOS forecasts and scorecards are in [`results/`](results/), 10 diagnostic charts in [`figures/`](figures/), the executable analysis in [`run_analysis.py`](run_analysis.py), the executed research narrative in [`research.ipynb`](research.ipynb), and reproducibility checks in [`tests/`](tests/). This study explicitly **does not** claim security alpha, historical PIT validity or firm-level causality.
