## 01. Abstract

**Air-Travel-to-Accommodation — U.S. Lodging Demand, retrospective macro-factor falsification (26 October 2026).** Does airline passenger activity, known with a conservative reporting delay, improve three-month-ahead U.S. accommodation-payroll YoY forecasts beyond lodging persistence and restaurant payroll growth? Using three frozen government series (2014-01 to 2026-09, with airline data through 2026-06), we obtain **82** purged expanding-window forecasts. The factor improves a bounded-macro Ridge challenger relative to its own controls, but fails a simple historical mean: **full RMSE 35.015 pp vs controls 46.313 pp vs mean 22.937 pp**. A 12-month block-shuffle is exploratory, and the bootstrap interval straddles zero. **Verdict: no stable predictive superiority, no publication-vintage validation, and no equity alpha.**

## 02. Research Design & Hypotheses

**Primary question:** can U.S. air revenue passenger miles growth at formation month *t*, measured through *t−4*, predict accommodation payroll YoY growth at *t+3* after controlling for the lodging and restaurant cycles?

- **H1 (economic transmission):** passenger-mile growth can lead overnight stays, hotel room demand and eventual staffing adjustments; airline travel is an imperfect mix of business, leisure and connecting trips.
- **H2 (incremental prediction):** a fixed-scale air-minus-restaurant demand gap reduces purged expanding-window OOS RMSE relative to the *same* multivariate model without it.
- **H3 (robustness):** any apparent gain should survive the 2020 disruption, alternative horizons and delays, year exclusions, exposure-weight perturbations and block-aware null comparisons.

**Null / failure rule:** if the full model fails the historical mean or persistence benchmark, or its advantage is regime-dependent and unverified for historical releases, it is **not** a validated lead factor. A positive association does not imply causation or a tradable equity return.

## 03. Industry Context

The U.S. accommodation segment employs workers in hotels, motels and other lodging; travel can influence staffing, but room-night demand is not observed directly here. BTS passenger miles cover U.S. air-carrier domestic and international services and do not isolate U.S. hotel stays or foreign carriers. In the frozen December observations, passenger miles rose **6.76%** from 2019 to 2025 while accommodation employment **fell 8.48%**; restaurant employment rose only **1.03%**. This divergence challenges any one-for-one staffing interpretation: hotel productivity, labor scarcity, short-term rentals, corporate travel mix and occupancy may break the link.

**Counterthesis:** airline demand may be contemporaneous with travel but too late or too noisy to forecast accommodation employment, especially during pandemic shutdowns and reopening. A structural recovery story cannot substitute for an incremental predictive test. No market-size or revenue-growth forecast is invented.

## 04. Data & Source Integrity

Frozen monthly inputs: **153** dates, 150 air observations, 153 accommodation and restaurant observations. All three are A-grade federal statistical series displayed by FRED; this grade assesses source authority, **not** vintage completeness. The original display tables are: [BTS AIRRPMTSID11](https://fred.stlouisfed.org/data/AIRRPMTSID11), [BLS CES7072100001](https://fred.stlouisfed.org/data/CES7072100001) and [BLS CES7072200001](https://fred.stlouisfed.org/data/CES7072200001). Reported updates: air **2026-10-01**; both CES series **2026-10-02**. Units are respectively thousands of seasonally adjusted passenger-miles and thousands of seasonally adjusted employees.

The frozen CSV was **manually transcribed** from the official FRED table displays on 2026-10-26 because direct bulk downloading was unavailable. A separate transparent `build_frozen_inputs.py` preserves each source row, while `data/transcription_qa.md` records spot-checks and remaining transcription risk. Original historical release timestamps and vintage-specific values are **UNKNOWN**. See `data/source_register.csv` for source URL, unit, update date, revision policy, assumptions and permitted use.

## 05. Point-in-Time Availability

At origin *t*, BTS features are taken only from *t−4* or earlier and CES features only from *t−2* or earlier. These are **assumed conservative availability buffers**, not historical release-date proof. A target formed at *u* with horizon *h* is admitted to training at origin *t* only when **u+h+2 ≤ t**, leaving an extra CES reporting buffer. Train-only standardization is repeated at each origin; the hyperparameter alpha=10, factor scale=20 and OOS minimum training count=36 are fixed, not optimized on test performance.

**Critical limitation:** historical BTS and BLS data have been revised and seasonally adjusted; this October 2026 snapshot can leak future revisions into earlier formation periods. This is a **retrospective fixed-snapshot falsification**, not a historical point-in-time simulation. Neither lagging latest-revised observations nor purging labels repairs that issue.

## 06. Factor Construction

For monthly levels A (air miles), L (accommodation employment), and F (food-service employment), define log-YoY percentage growth:

`g_A(t) = 100 ln[A(t−4)/A(t−16)]`, `g_L(t) = 100 ln[L(t−2)/L(t−14)]`, `g_F(t) = 100 ln[F(t−2)/F(t−14)]`.

The **predefined travel-specific gap** is `S(t) = tanh((g_A(t) − g_F(t))/20)`. Both component weights are analyst hypotheses (1 and −1), not estimated historical company exposures. `tanh` caps the signal between −1 and +1; the 20-pp scale is fixed before evaluation. The control model uses bounded lodging/restaurant YoY transforms `tanh(g/20)` and a bounded lodging 3-month change `tanh(mom3/10)` to limit pandemic-era feature extrapolation.

The dependent variable is **Y(t,h)=100 ln[L(t+h)/L(t+h−12)]**, three-month-ahead lodging-employment YoY, in percentage points. This is neither lodging revenue nor a security return. No cross-sectional stock IC or long-short spread is calculated without issuer total returns.

## 07. Exposure & Transmission

`data/exposure_map.csv` identifies the three observed subsectors: airline activity is an upstream travel proxy, accommodation employment is the independent sector outcome, and restaurant payrolls proxy a broader discretionary-services cycle. No historical company-level passenger exposure, hotel chain revenue shares, room nights or occupancy are available; **company exposure mapping and leave-one-company-out are NOT TESTED**. The analyst 1:1 growth weighting is stress-tested using 1,000 draws that change air weight between 0.75 and 1.25, with the restaurant comparator weight adjusted symmetrically.

## 08. Outcomes & Baselines

All 82 primary forecasts share the **same origins** (2018-09-01 to 2025-06-01). The models are: (1) training-target historical mean; (2) directly carried-forward lagged accommodation YoY; (3) Ridge(alpha=10) on bounded lodging YoY, restaurant YoY and lodging three-month momentum; (4) identical Ridge plus the fixed travel gap. Each regression fits only labels matured by the cutoff and scales its predictors using only its own training rows. The outcome is the future accommodation payroll YoY log change; no portfolio return, transaction costs or Sharpe ratio are asserted.

## 09. Empirical Findings

| Model | OOS RMSE (pp) | OOS MAE (pp) |
|:--|--:|--:|
| Historical mean | 22.937 | 14.963 |
| Accommodation persistence | 26.029 | 20.344 |
| Bounded macro controls | 46.313 | 24.421 |
| Controls + travel gap | 35.015 | 21.407 |

The factor reduces RMSE by **11.298 pp relative to its weak multivariate control**, but remains **12.078 pp worse than the historical mean**. A small p-like statistic from a null comparison must not override this baseline failure. Large pandemic-era target swings make fitted regressions unstable and dominate aggregate error. See `results/walk_forward_oos.csv`, `results/scorecard.csv` and computed charts.

## 10. Robustness & Placebos

- **1,000 block-shuffle refits:** the observed control-minus-full RMSE difference is at an exploratory upper-tail fraction **0.022** when the travel-gap sequence is permuted in 12-month blocks. This is **not** a valid exact permutation p-value: block boundaries, historical revisions, autocorrelation and model selection remain.
- **2,000 moving-block bootstrap draws:** the 95% percentile interval for control-minus-full RMSE is **[-1.963, 23.110] pp**, crossing zero.
- **1,000 exposure perturbations:** the observed fraction with positive improvement over controls is **1.000**, but all such models still require comparison with the historical mean and independent PIT data.
- **Ablation and negative control:** using air YoY alone, a stale 12-month travel gap, alternative horizons (1 and 6 months) and longer BTS reporting delays (5 and 6 months) do not establish stable superiority. Leave-one-year-out is reported separately; deleting 2020 changes the sign of the primary improvement.

## 11. Regime Sensitivity

The 2020 air-travel collapse and subsequent reopening are exceptionally large shocks; they can induce strong in-sample association while destroying stable predictive relationships. In the primary OOS period, excluding 2020 changes the sign of the control-minus-factor RMSE improvement. After 2022, the gap model's RMSE is **2.695 pp**, versus **1.053 pp** for the mean; it does not win even in the calmer period. These are descriptive regime slices selected after seeing data, not independent confirmatory tests.

## 12. Bias Audit & Verdict

**Publication leakage:** unresolved BTS/BLS historical release vintages. **Survivorship:** sector aggregate series avoid listed-company survivorship but omit firm closures and chain composition. **Selection:** only one candidate industry/factor was evaluated in this run; the broader automated research program tests many hypotheses, so multiplicity remains. **Overlap:** 3-month-forward annual growth targets overlap strongly across monthly origins, reducing effective sample size. **Regime instability:** COVID-19 dominates errors. **Economic mismatch:** air miles mix trip purposes and geography, while hotel staffing depends on labor productivity. **Trading:** no stock universe, dividends, delistings, borrow costs, slippage, fees or capacity were tested.

**VERDICT — REPRODUCED RETROSPECTIVE MACRO FALSIFICATION, NOT A VALIDATED FACTOR.** The challenger improves a weak control but fails the historical-mean benchmark, confidence intervals include zero, 2020 drives the gain and historical PIT is unavailable. There is **no investable equity alpha claim**.

## 13. Reproduction

From a clean checkout, in this study directory: `python -m pip install -r requirements.txt`, then `OPENBLAS_NUM_THREADS=1 python run_analysis.py`, `OPENBLAS_NUM_THREADS=1 PYTHONPATH=. pytest -q tests`, and `OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute research.ipynb --output /tmp/air-hotel-reexecuted.ipynb`. For the full repository, run `python scripts/validate_studies.py` at the repository root. The frozen source file checksum is **`98ad34cabef652c021869fcfa74515a322272ddfb53c3e84dcfa65a5d9af5cc0`** (SHA-256). This reproducibility does **not** certify that the manually transcribed values match all official source rows or historical vintages.

## 14. Next-Stage Protocol

Before testing investment alpha, acquire historical BTS T-100 release-date snapshots and archived CES vintage records; independently reconcile all monthly source observations against original agency bulk files. Replace employment with independent hotel occupancy/RevPAR and chain-level room nights; map dated company property geography and revenue exposure; freeze an ex-ante hotel stock universe and dividend-adjusted total returns. Then pre-register a monthly formation rule with data availability, lagged fundamental filings, transaction-cost-aware holdout and multiple-testing correction. If these datasets cannot be obtained, retain the result as a macro falsification only.

## 15. Sources & Artifacts

- Primary sources: [BTS air revenue passenger miles](https://fred.stlouisfed.org/data/AIRRPMTSID11), [BLS accommodation payrolls](https://fred.stlouisfed.org/data/CES7072100001), [BLS food services payrolls](https://fred.stlouisfed.org/data/CES7072200001). All accessed **2026-10-26**.
- Provenance: `data/source_register.csv`, `data/transcription_qa.md`, `build_frozen_inputs.py`, `data/fred_bts_bls_frozen_2026-10-26.csv`, `data/exposure_map.csv`.
- Analysis: `run_analysis.py`, `research.ipynb`, `requirements.txt`, `tests/test_hospitality.py`.
- Computed evidence: `data/derived_formation_panel.csv`, `results/metrics.json`, `results/scorecard.csv`, `results/walk_forward_oos.csv`, `results/block_placebo_null.csv`, `results/bootstrap_deltas.csv`, `results/exposure_sensitivity.csv`, `results/leave_one_year_out.csv`, `results/run_log.txt` and **nine** `figures/*.png` files.
