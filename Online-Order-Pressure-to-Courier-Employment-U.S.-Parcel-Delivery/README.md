# Online-Order Pressure → U.S. Courier Employment | Retrospective Macro Lead-Factor Study

**Status: REPRODUCED MACRO PILOT — NOT PIT / NOT EQUITY ALPHA**  
**Data collection snapshot: 2026-10-26; analysis: 2026-10-27.**

## 01. Abstract

**Question.** Does lagged e-commerce demand pressure anticipate two-quarter-ahead U.S. couriers-and-messengers employment growth, after accounting for courier persistence and broad payroll conditions? This is a **retrospective, revised-data macro lead-factor falsification**, not an investable equity study. The 61 purged expanding-window origins show RMSE 4.629 log-pp for the augmented model versus 5.148 for macro controls and 4.639 for simple persistence. The gain is concentrated in 2020–2021; bootstrap uncertainty spans zero. **Verdict: FAIL as a stable incremental predictor; no PIT or equity-alpha claim.**

## 02. Research Design & Hypotheses

**Primary hypothesis H1:** a one-quarter-stale online retail-share acceleration relative to warehousing payroll capacity predicts higher courier hiring two quarters later. **H2:** the fixed signal improves expanding-window OOS RMSE against courier persistence and courier+macro controls, not merely in-sample fit. **H3:** any improvement persists before 2020, after 2021 and under alternate lag/horizon definitions. Null: no incremental forecast improvement over controls. Counterthesis: platform insourcing, automation, route density, union contracts and non-retail deliveries decouple retail-share growth from aggregate courier payrolls. Predeclared failure gate: lose to the strongest simple baseline or a nonpositive gain outside the pandemic regime.

## 03. Industry Context

The outcome covers **NAICS 492 couriers and messengers**, not NAICS 493 warehousing and storage, which was the dependent variable in an earlier study. The Census Bureau reported Q2 2026 seasonally adjusted e-commerce at **17.1%** of U.S. retail sales (August 18, 2026; revised-status notice September 28). The BLS CES series measures payroll employees in thousands, not parcel volumes, market share, physical capacity or carrier profits. Delivery networks mix consumer parcels, business shipments and non-retail demand, so e-commerce retail share is only a noisy exposure proxy. UPS and FedEx filings document delivery business lines, but historical issuer revenue weights are not measured here.

## 04. Data & Source Integrity

The frozen inherited quarterly snapshot has **107 raw rows (106 complete quarters, 2000Q1–2026Q2; partial 2026Q3 excluded)** and four official series identifiers. The target is CES4349200001; predictors are ECOMPCTSA, CES4349300001 and PAYEMS. `data/source_register.csv` assigns A to original government series/documentation, B to the inherited frozen transport layer and C to researcher modeling assumptions. **Unknown:** historical source-publication timestamps, real-time vintage histories, original monthly-to-quarterly averaging audit and exhaustive source-row corroboration. SHA-256 `17b99d105505b7c4ef7741012cf65d916bac0b907403474f18cffedcc4a99b2d` permits reproducibility of the reused snapshot, not original-source accuracy.

## 05. Point-in-Time Availability

At formation quarter *t*, all signals use observations from *t−1* or earlier. This operational buffer accommodates the typical delay in quarterly Census releases but **does not verify each release date**. Each training origin *j* enters only if its two-quarter-ahead outcome plus one additional quarterly publication buffer is observable by *t*: **j+2+1 ≤ t**. Historical CES revisions, Census methodology changes, and seasonal rebenchmarking remain embedded in the frozen 2026 snapshot. Therefore the model is a **fixed-revised-snapshot counterfactual**, not a true real-time tradable backtest.

## 06. Factor Construction

For quarter *t*, define `ΔShare[t−1] = ECOMPCTSA[t−1] − ECOMPCTSA[t−5]` (percentage points); `gW[t−1]=100 ln(W[t−1]/W[t−5])` and `gP[t−1]=100 ln(P[t−1]/P[t−5])` (log-pp). The **predefined demand–capacity pressure factor** is `S[t] = ΔShare[t−1] − 0.10 × (gW[t−1] − gP[t−1])`. The 0.10 coefficient is a hypothesis-driven scale convention, **not estimated or calibrated from future observations**. The target is `Y[t]=100 ln(C[t+2]/C[t−2])`, two-quarter-ahead courier employment YoY log growth. Train-only feature centering and scaling precede a fixed-alpha Ridge fit.

## 07. Exposure & Transmission

The signal-to-outcome chain is retail online-order penetration → distribution demand → courier labor demand, offset by warehouse hiring relative to total payrolls. The NAICS 492 target and NAICS 493 capacity proxy are separately measured; they are not interchangeable. `data/exposure_map.csv` identifies two illustrative listed issuers (UPS, FedEx) with dated filing links, but **no numeric company exposure weights, historical firm fundamentals or returns** are used. Consequently issuer leave-one-out and long–short return spread are **not applicable**; leave-one-calendar-year-out is the feasible aggregate-data sensitivity test.

## 08. Outcomes & Baselines

The five baselines are historical expanding mean, courier YoY persistence, courier+aggregate-payroll Ridge controls, courier+payroll+warehouse controls, and factor-only Ridge. The challenger adds `S[t]` to courier+payroll controls. All Ridge models use fixed `alpha=10`, standardized using training observations only, and the same 61 valid origins (2010Q4–2025Q4); the train window expands and purges three quarters to avoid unavailable labels. Primary metric: OOS RMSE in log percentage points; secondary MAE, bias and a descriptive **time-series** Spearman coefficient (not cross-sectional equity IC).

## 09. Empirical Findings

**Observed:** RMSE mean **6.828**, courier persistence **4.639**, macro controls **5.148**, warehouse controls **5.457**, factor-only **8.697**, augmented **4.629** log-pp. Incremental macro-relative RMSE gain is **+0.519** log-pp, but the augmented model improves on courier persistence by only **+0.009** log-pp and has worse MAE than persistence. Time-series Spearman signal/target is **+0.005**. Positive full-sample improvement must not be read as a stable effect.

## 10. Robustness & Placebos

A 1,000-refit permutation of contiguous four-quarter factor blocks yields an **exploratory** upper-tail fraction **0.0010**; nonexchangeability, overlapping outcomes and secular trends prevent treating this as an exact p-value. A 2,000-draw paired four-quarter circular-block bootstrap gives macro-relative RMSE-gain interval **[-0.390, +1.388]**, which includes zero. Among 1,000 predeclared capacity-weight perturbations (0–0.30), **30.1%** improve macro RMSE. Component ablations, warehouse-control comparison, extra release lags and alternative horizons are saved in committed results tables; full simulation-draw tables are regenerated by the reproducible analysis entrypoint.

## 11. Regime Sensitivity

The pre-2020 sample (37 origins) has macro-relative RMSE gain **-0.037**; the 2020–2021 sample (8) has **+2.863**; the post-2021 sample (16) has **-0.375**. The improvement is therefore pandemic-dominated and reverses sign outside that window. This is a **structural-instability failure**, not evidence of a general-purpose courier hiring factor.

## 12. Bias Audit & Verdict

**Lookahead:** historical revised source values are known only ex post; fixed one-quarter buffer cannot reconstruct the first-released values. **Selection:** this industry and factor were selected after earlier adjacent-sector studies; multiple-testing adjustment is unavailable. **Survivorship:** aggregate CES industry classifications can be rebenchmarked; no firm universe was sampled. **Dependence:** two-quarter-ahead YoY targets overlap, reducing effective independent observations. **Costs/capacity:** no securities strategy, portfolio, transaction-cost model or benchmark-adjusted returns exist. **Verdict: negative as a stable macro leading indicator; no investable equity alpha.**

## 13. Reproduction

From the study directory: `python run_analysis.py`, `PYTHONPATH=. python -m pytest -q tests`, and `jupyter nbconvert --to notebook --execute research.ipynb --output reproduced.ipynb`. Required dependencies are in `requirements.txt`; all random generators have fixed seeds. Core OOS scorecards, sensitivity tables, nine computed diagnostic SVGs and execution records are versioned. Full 1,000-draw permutation, 2,000-draw bootstrap and 1,000-draw perturbation CSVs are deterministically regenerated by `run_analysis.py` (also invoked automatically at the start of a clean notebook execution when those tables are absent). A clean-directory reproduction is required before publication; `scripts/validate_studies.py` is a structural check only.

## 14. Next-Stage Protocol

Retrieve actual FRED/ALFRED and Census release vintages, plus month-by-month original BLS observations with their timestamps; rebuild quarterly aggregates from only data available at each decision time. Collect parcel volumes, yield, package mix, labor productivity and delivery-platform insourcing histories; validate issuer segment revenue/operating profit and as-filed 10-K dates. Pre-register a later holdout period, multiple-hypothesis correction, alternative 1–4-quarter horizons, issuer exposure weights, total-return series and transaction-cost assumptions. Abandon the proposed alpha thesis if it cannot beat persistence across non-pandemic regimes and real-time vintages.

## 15. Sources & Artifacts

Primary series and dated releases: [Census e-commerce](https://www.census.gov/retail/ecommerce.html), [FRED ECOMPCTSA](https://fred.stlouisfed.org/series/ECOMPCTSA), [FRED CES4349200001](https://fred.stlouisfed.org/series/CES4349200001), [FRED CES4349300001](https://fred.stlouisfed.org/series/CES4349300001), [FRED PAYEMS](https://fred.stlouisfed.org/series/PAYEMS), [UPS 2025 annual filings](https://investors.ups.com/sec-filings/annual-filings), [FedEx 2025 10-K](https://www.sec.gov/Archives/edgar/data/1048911/000104891125000011/fdx-20250531.htm). Frozen raw/derived CSVs, `analysis.py`, `run_analysis.py`, source register, exposure map, tests, results, figures and execution logs accompany the notebook. These source URLs establish **provenance**, not complete historical PIT validity.
