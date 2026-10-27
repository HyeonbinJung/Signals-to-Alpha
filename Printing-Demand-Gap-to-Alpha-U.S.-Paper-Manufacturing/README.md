# Printing Demand Pressure and U.S. Paper Manufacturing

**Evidence status:** REPRODUCED RETROSPECTIVE MACRO PILOT — **NOT POINT-IN-TIME** — **NOT EQUITY ALPHA**. Research frozen 2026-10-27; underlying G.17 revised snapshot dated 2026-10-16, inherited from a 2026-10-26 manual transcription.

## 01. Abstract

**Question:** Does lagged printing-industry production growth relative to broad manufacturing improve forecasts of U.S. paper manufacturing production three months ahead? In **120 purged expanding-window origins (2016-07 through 2026-06)**, a predeclared printing-demand gap improves paper output-growth RMSE from **4.448** to **4.175 log percentage points** relative to paper-persistence/manufacturing controls, and also narrowly beats persistence **4.291** and historical mean **4.559**. The paired 2,000-draw circular 12-month block-bootstrap interval for the RMSE improvement is **[0.033, 0.570] log-pp**, but this is **not** an independently validated PIT result; historical release vintages are missing and the series were inherited from a manually transcribed fixed snapshot. The **pre-2020 subperiod is negative**, 12-month horizons reverse sign, and the unconditional factor-quintile growth spread is negative; therefore this is a **conditional macro lead-factor candidate requiring independent verification**, not investable equity alpha.

## 02. Research Design & Hypotheses

Primary null: adding the printing-demand gap does not lower genuinely out-of-sample paper-production forecast error relative to identical-origin macro controls. **H1:** lagged printing growth relative to the manufacturing cycle carries incremental information for paper output (positive control-minus-augmented RMSE). **H2:** the augmented model also beats the historical mean and paper-output persistence on the same forecast origins. **H3:** any apparent gain survives a 12-month block-aware placebo, 2,000-draw paired bootstrap, exposure-weight perturbations, year deletions, horizon/lag changes and pre/post-pandemic regimes. Alternative thesis: printing is a shrinking fraction of total paper end-use, packaging/tissue demand dominate, and both series are contemporaneously driven by aggregate manufacturing. H1/H2 pass in the revised retrospective panel; H3 is **mixed**, failing the pre-2020 and 12-month-horizon checks. These are predeclared primary horizon/lag settings; additional settings are exploratory.

## 03. Industry Context

The U.S. Census **2022 NAICS** defines paper manufacturing as **322**, including pulp, paper, paperboard and converted paper products; **323** comprises printing and related support activities. Printing uses paper but is **not representative of all NAICS 322 output**; demand for packaging, tissue, hygiene and industrial paper can dominate, and technology substitution can weaken the historical linkage. The paper industry’s **2026 market size and segment-specific revenue shares are UNKNOWN** in the available research inputs; we do not manufacture a dollar-market-size estimate. The industrial-production index measures real domestic output (2017=100), **not nominal revenue, profits, equity returns or capacity utilization**. See Census NAICS manual and Federal Reserve G.17 source register.

## 04. Data & Source Integrity

The frozen panel contains **201 monthly rows from 2010-01 through 2026-09**, for G.17 seasonally adjusted indices **G322 paper**, **G323 printing** and **B00004 manufacturing**. These are **inherited from the previously published printing-sector study's manually transcribed 2026-10-26 snapshot**, not independently recollected or row-by-row verified; **10 of 603 index values (May–September 2026 for paper and printing) were independently matched against FRED on 2026-10-27** (`data/official_spot_checks_2026-10-27.csv`). The original release is dated **2026-10-16**; the precise historical observation-release dates and vintage histories are **UNKNOWN**. `data/source_register.csv` documents A-grade official publishers, B-grade FRED/ALFRED metadata and C-grade classification context, exact source URLs, units, periods, revisions, extraction provenance and limitations. `load_data()` asserts dates, continuity, uniqueness, nonmissing values and positivity; raw data are frozen and derived features saved separately. The existence of official A-grade source series does not upgrade an unaudited manual transcription to A-grade numerical integrity.

## 05. Point-in-Time Availability

For a formation month **t**, predictors are calculated only from the index levels observed at **t−2** (two-month stale); the target is paper YoY log growth at **t+3**. An origin's training set includes a prior example j only if its outcome month **j+3 ≤ t−2**; hence training labels are purged by an assumed two-month publication buffer. The G.17 release calendar confirms monthly publication but **does not validate historical revision vintages or each past release timestamp**. Because all historical observations come from the **same 2026-10-16 revised snapshot**, this is **not historical PIT**, even with strict mechanical lags. Historical ALFRED/Federal Reserve release archives must be reconstructed before forward-trading or causal claims.

## 06. Factor Construction

Let `g^X_t = 100[ln(IP^X_t) − ln(IP^X_{t−12})]` in **log percentage points**. The fixed printing-demand gap is `F_t = g^printing_{t−2} − g^manufacturing_{t−2}`; target `Y_t = g^paper_{t+3}`. A 12-month log difference reduces seasonality but introduces overlapping-target autocorrelation. No full-sample z-scoring or fitted exposure weights are used. Each Ridge model standardizes its own predictors using **training-only** mean/standard deviation and fixed `alpha=10`; model coefficients are re-estimated each expanding origin. The primary two-month stale buffer and three-month horizon were set before the reported robustness grid.

## 07. Exposure & Transmission

`data/exposure_map.csv` maps NAICS 323 to the downstream printing activity signal, NAICS 322 to paper manufacturing output, and manufacturing NAICS 31–33 to cyclical control, with dated source URLs. The `1.0` values are **unit proxy indicators, not issuer revenue weights**. A printing-to-paper demand transmission is economically plausible but neither the fraction of paper sales attributable to printing nor the lag of inventory orders is measured. No firm-level audited segment revenue exposure, firm-fundamental panel or security return panel is available. **Leave-one-company-out is NOT APPLICABLE**; instead we report leave-one-calendar-year-out to test temporal concentration.

## 08. Outcomes & Baselines

Outcome is **3-month-ahead YoY paper industrial-production log growth**, not share-price return. Baselines use **identical origins and training windows**: historical training-target mean; paper YoY persistence; Ridge on paper persistence plus manufacturing YoY; fixed factor-only Ridge; augmented Ridge on both controls plus printing gap. Forecasts start only after at least **60 fully released training labels**, and all models share **120** OOS origins. Temporal Pearson IC here is a correlation of **macro forecasts with future macro outcomes**, not cross-sectional equity IC; no long-short equity spread or benchmark-adjusted return is claimed. `results/scorecard.csv` records RMSE, MAE and temporal IC.

## 09. Empirical Findings

| Model | OOS RMSE (log-pp) | OOS MAE (log-pp) |
|---|---:|---:|
| Historical mean | 4.559 | 3.323 |
| Paper persistence | 4.291 | 3.164 |
| Paper + manufacturing controls | 4.448 | 3.391 |
| Printing-demand factor alone | 4.539 | 3.374 |
| **Augmented controls + factor** | **4.175** | **3.082** |

Incremental control-minus-augmented RMSE improvement: **+0.2724 log-pp**. It is modest, retrospective and should not be annualized or converted into expected equity returns. Unconditional quintile sorting on the raw factor gives top-minus-bottom **−2.045 log-pp** of subsequent paper growth (24 observations per quintile), in the opposite direction to a naive monotone-demand thesis. This tension suggests a conditional interaction with manufacturing/persistence, selection or nonstationarity, not a clean standalone trading signal. See the executed notebook and ten computed SVG figures.

## 10. Robustness & Placebos

A **2,000-draw paired circular 12-month block bootstrap** on OOS forecast errors gives control-minus-augmented RMSE improvement **95% interval [0.033, 0.570] log-pp**; the interval is conditional on this fixed retrospective data and model selection. A **1,000-refit 12-month contiguous-block shuffle** of the factor yields an **exploratory upper-tail fraction 0.01499** (plus-one correction), **not an exact inferential p-value** because target overlap, nonstationarity and revised-vintage bias remain. In **1,000** pre-specified ±20% printing/manufacturing weight perturbations, **100%** retain positive incremental RMSE gain; this is not 1,000 independent factors, because the macro-control basis makes the weights nearly redundant. Leave-one-year-out and no-pandemic windows are reported, as are factor-only/controls-only ablations, four horizons and three assumed release lags. No company-level ablation can be performed without issuer exposure data.

## 11. Regime Sensitivity

**Pre-2020** (42 origins): control-minus-augmented RMSE **−0.107 log-pp**; **2020–2021** (24): **+0.549**; **post-2021** (54): **+0.317**; excluding 2020–2021 (96): **+0.195**. Thus the overall gain is **not stable across historical regimes**, and a pre-pandemic-only application would have failed. The primary 3-month/2-month-lag gain is positive, but at a **12-month horizon** the corresponding gain turns negative (**−0.392 log-pp**). These tests were explored after the primary specification and are not separate confirmatory discoveries.

## 12. Bias Audit & Verdict

**Publication leakage:** no release-vintage panel; assumed stale inputs cannot prove real-time availability. **Revision leakage:** official G.17 seasonality, benchmark and monthly revisions affect historical rows. **Source transcription:** inherited manual rows were not fully independently verified. **Selection:** one new target was chosen after multiple previous industry studies; cross-study selection and multiple testing are not adjusted. **Temporal overlap:** 12-month YoY targets induce strong dependence; bootstrap/permutation are descriptive approximations. **Survivorship:** aggregate NAICS series include changing firms, but no historical issuer universe is available. **Costs/capacity:** no tradable portfolio, borrow, turnover, transaction costs or risk adjustment exists. **Verdict:** conditional positive **retrospective macro lead-factor candidate**, **UNVERIFIED PIT**, **NO investable equity alpha**. H3 fails on pre-2020 and long-horizon robustness; neither a robust causal effect nor a stable standalone predictor is established.

## 13. Reproduction

From this directory with Python 3.11+ and installed `requirements.txt`, run `python run_analysis.py`, `python -m pytest -q tests`, and `python -m jupyter nbconvert --to notebook --execute --inplace research.ipynb`. The notebook embeds executed numeric tables and diagnostic plots; results and SVGs are persisted in `results/` and `figures/`. To check the repository layout from the repository root, run `python scripts/validate_studies.py`. Local run logs and independent fresh-directory reproduction checks are in `logs/`; the layout validator and GitHub CI are **structural checks**, not historical PIT proof.

## 14. Next-Stage Protocol

First reconstruct monthly release-specific G.17 **ALFRED vintages**, with actual publication timestamps and same-day available predictors, and independently download/check all 603 raw index values. Next replace the single printing proxy with separately dated paperboard/packaging, tissue, box shipments, corrugated container orders and printer activity to measure which end markets drive paper production. Then build issuer-year exposure weights from historical SEC filings, adjust for mergers/divestitures, validate quarterly issuer revenue and margins using filing dates, and only afterward test delisting-aware **total returns**, sector benchmarks, costs, turnover and capacity. Pre-register a fresh forward holdout and false-discovery adjustment across industries before upgrading this macro pilot.

## 15. Sources & Artifacts

Official sources: Federal Reserve G.17 release calendar and 2026-10-16 release ([release index](https://www.federalreserve.gov/releases/g17/)); [industrial production series download](https://www.federalreserve.gov/releases/g17/Current/ipdisk/ip_sa.txt); [FRED paper IPG322S](https://fred.stlouisfed.org/series/IPG322S); [FRED printing IPG323S](https://fred.stlouisfed.org/series/IPG323S); [Census 2022 NAICS manual](https://www.census.gov/naics/reference_files_tools/2022_NAICS_Manual.pdf); [ALFRED archive](https://alfred.stlouisfed.org/release?rid=13). Exact provenance fields are in `data/source_register.csv`. Artifacts: `research.ipynb`, `analysis.py`, `run_analysis.py`, `data/` raw and derived CSVs, `results/` scorecards and 1,000/2,000-draw diagnostics, `figures/` ten real SVG plots, `tests/`, `logs/`, `study.json`, `requirements.txt`. **No company fundamentals, total-return or historical PIT panel is included.**
