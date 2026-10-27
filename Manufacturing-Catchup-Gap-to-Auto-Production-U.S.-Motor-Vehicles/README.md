# Manufacturing Catch-up Gap → U.S. Motor Vehicles & Parts Production

**2026-10-27 | REPRODUCED RETROSPECTIVE MACRO PILOT — NOT PIT / NOT EQUITY ALPHA**

## 01. Abstract

**Primary research question:** Does a two-month-stale manufacturing-minus-auto momentum gap predict three-month-ahead U.S. motor-vehicle-and-parts output growth beyond simple and multivariate baselines? In a 2026-10-16 revised G.17 snapshot, **201 monthly observations** yield **120 purged expanding-window OOS forecasts** (2016-07-01 to 2026-06-01). The augmented model's RMSE is **29.526 log-pp**, versus **28.532** for controls and **24.621** for the historical mean; incremental improvement is **-0.994 log-pp** (negative means worse). **Verdict:** negative incremental forecast; **REPRODUCED RETROSPECTIVE MACRO PILOT — NOT PIT / NOT EQUITY ALPHA**. The 201 automobile observations were manually transcribed and only 12 spot-checked; first-release historical vintages and securities returns are unavailable.

## 02. Research Design & Hypotheses

**H1:** a positive manufacturing–auto momentum premium signals delayed automotive catch-up. **H2:** adding the fixed nonlinear factor improves OOS RMSE versus a lagged auto/manufacturing control, and must also be compared with historical mean and persistence. **H3:** any incremental improvement survives block-aware placebos, bootstrap uncertainty, scale/momentum-mix perturbations, ablations, year deletions, regime splits, and alternative horizons. The null is no incremental predictive value; failure against the historical mean or instability rejects a useful signal. Mechanism: shared business-cycle orders and supplier constraints could lead auto output; counterthesis: idiosyncratic shutdowns, strikes and model transitions dominate.

## 03. Industry Context

The dependent series is U.S. **NAICS 3361–3363** motor vehicles and parts, seasonally adjusted physical industrial production, index 2017=100. Aggregate U.S. manufacturing production (`IPMAN`) is the comparator; it includes the auto industry, creating mechanical overlap. Auto manufacturing is highly cyclical and susceptible to inventory, chip shortages, strikes, and plant closures; a positive macro gap can equally mean automotive weakness rather than catch-up. The Fed's **2026-10-16 G.17** release reported September manufacturing output rose 0.3% and motor-vehicle-and-parts output fell 3.0%. For **NAICS 3361 only** (vehicle manufacturing, excluding bodies and parts), the Census 2024 AIES reported **$424.662 billion** in value of shipments, released **2026-09-03**; this must **not** be misrepresented as the full NAICS 3361–3363 market size. Official context: [dated G.17](https://www.federalreserve.gov/releases/g17/20261016/default.htm), [Census 2024 AIES NAICS 3361](https://test.data.census.gov/table/AIESBASIC2024.AIES31BASIC02?codeset=naics~3361&g=010XX00US), [NAICS](https://www.census.gov/naics/).

## 04. Data & Source Integrity

**A-grade**: Fed G.17 `IPG3361T3S` auto index and `IPMAN` manufacturing index (2010-01–2026-09, 2017=100, monthly SA); G.17 release dated **2026-10-16**. Auto index values were manually transcribed from the [official FRED table](https://fred.stlouisfed.org/data/IPG3361T3S) on 2026-10-27 and **12 of 201** were spot-checked, not all independently machine-verified. IPMAN was inherited from the prior Basic Chemicals frozen study; the full 201 values were not independently re-downloaded. **B-grade**: FRED metadata and ALFRED archival-vintage discovery. **C-grade**: Census 2022 NAICS classification. `data/source_register.csv` gives exact URLs, dates, observed windows, grades, revision notes, release lags, and roles. Missing observations were not imputed; all index values are positive.

## 05. Point-in-Time Availability

At formation month `t`, every signal/control uses an observation no later than **t−2**. Target is motor-vehicle output YoY growth at **t+3**; the model trains only on historical examples whose target month is **≤t−2**. This yields a conservative five-month origin gap for the primary horizon, but historical Fed first-publication dates and revised index values are **UNKNOWN**. Therefore this is a retrospective fixed-snapshot exercise, **not a verified point-in-time strategy**. The Fed explicitly revises historical G.17 readings; the lag alone cannot repair vintage leakage.

## 06. Factor Construction

Let `A_t` be auto IP and `M_t` aggregate manufacturing IP. Define `g^k_{Z,t}=100[ln(Z_t)-ln(Z_{t-k})]`. **Fixed primary factor:** `F_t = tanh((g^3_{M,t-2} - g^3_{A,t-2}) / 10)`. **Target:** `Y_t=g^12_{A,t+3}` in log percentage points. Primary scale 10 and 3-month weight 1 are fixed, not selected on OOS results. For perturbations, replace the numerator with `w*(g^3_M-g^3_A)+(1-w)*(g^12_M-g^12_A)`, with `w∈[0.6,1]` and tanh scale `5–20`; the primary remains `w=1,scale=10`. Model standardization is estimated on training data only.

## 07. Exposure & Transmission

`data/exposure_map.csv` maps the industry to NAICS 3361 (vehicles), 3362 (bodies/trailers) and 3363 (parts), based on the [2022 Census NAICS](https://www.census.gov/naics/). FY2025 [GM 10-K](https://www.sec.gov/Archives/edgar/data/1467858/000146785826000013/gm-20251231.htm) (filed 2026-01-27) and [Ford 10-K](https://www.sec.gov/Archives/edgar/data/37996/000003799626000015/f-20251231.htm) (filed 2026-02-11) identify **qualitative** automotive company exposure. Their U.S. physical production weights and historic changes are UNKNOWN; no invented company exposure coefficients enter the factor. The proposed channel is broad manufacturing momentum → auto supply/production catch-up, not a demonstrated causal chain. **Firm fundamentals, leave-one-company-out and total returns: NOT TESTED.**

## 08. Outcomes & Baselines

All models use identical forecast origins and a **purged expanding training window** (minimum 60 eligible origins), Ridge alpha=12 and train-only feature scaling. Baselines: expanding historical mean; auto YoY persistence; macro controls (lagged auto YoY, lagged manufacturing YoY, lagged auto 3-month momentum); factor-only Ridge; augmented controls plus the nonlinear factor. Outcomes are industrial production YoY, not firm revenue/EPS, stock prices or adjusted total returns. RMSE/MAE are in log-pp; time-series Spearman correlation is descriptive and **not** cross-sectional stock IC.

## 09. Empirical Findings

**Same-origin OOS scorecard (n=120):**

| Model | RMSE log-pp | MAE log-pp | Time-series Spearman |
|---|---:|---:|---:|
| mean | 24.621 | 10.333 | -0.192 |
| persistence | 27.806 | 11.836 | -0.144 |
| macro_control | 28.532 | 13.023 | -0.061 |
| factor_only | 24.778 | 10.591 | -0.298 |
| augmented | 29.526 | 13.346 | -0.088 |

**Incremental RMSE improvement:** -0.994 log-pp (macro-control minus augmented). The large 2020 auto shutdown and 2021 rebound inflate squared-error metrics; compare pre/post periods rather than generalizing from pooled RMSE. The scorecard is calculated from `results/oos_predictions.csv` and reproduced in the executed notebook.

## 10. Robustness & Placebos

**1,000** 12-month contiguous-block factor reorders with full purged model refits produce an exploratory one-sided tail fraction of **0.9870**, not an exact exchangeable permutation p-value. **2,000** paired circular moving-block bootstrap draws (block 12) yield an OOS RMSE-improvement 95% interval **[-1.868, -0.014] log-pp**. **1,000** nonlinear-scale/momentum-mix perturbations improve the control in **0.0%** of cases. Ablations, leave-one-calendar-year-out and 16 horizon/lag variants are in `results/`. No firm-level leave-one-company-out is possible. Multiple-testing adjustment is absent: all robustness comparisons are exploratory.

## 11. Regime Sensitivity

With the **same originally fitted forecasts**, RMSE improvement is **-0.023** log-pp before 2020 (n=42), **-2.244** in 2020–21 (n=24), **-0.121** after 2022 (n=54), and **-0.079** with pandemic origins excluded (n=96). Horizons 1/3/6/12 months and observation lags 1/2/3/4 months are recomputed in `results/horizon_lag_sensitivity.csv`; leave-one-calendar-year-out is `results/leave_one_year_out.csv`. A year deletion is not a company deletion.

## 12. Bias Audit & Verdict

**Publication/vintage leakage:** unresolved; 2026-revised data cannot support PIT. **Lookahead:** mechanical 2-month lag and target purge implemented, but not sufficient for vintage validity. **Survivorship:** no security universe; qualitative FY2025 company examples are not backfilled. **Selection/multiple tests:** one of many industry hypotheses, with exploratory 16 horizon/lag checks and no false-discovery correction. **Nonstationarity:** 2020 shutdown, auto supply shortages, strikes and EV transition. **Costs/capacity/benchmark-adjusted total returns:** NOT TESTED. **Verdict:** a negative, reproducible retrospective **macro-leading-indicator falsification**, not firm-fundamental prediction or investable equity alpha.

## 13. Reproduction

From this study directory after installing `requirements.txt`, run:

```bash
OPENBLAS_NUM_THREADS=1 python run_analysis.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python -m pytest -q tests
OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute --inplace research.ipynb
```

The full analysis recomputes 1,000 block reorders, 2,000 bootstraps and 1,000 perturbations. `research.ipynb` recomputes the baseline forecasts and embeds saved tables/plots. `make_data.py` reconstructs the manually transcribed auto series from its source-code literals and the included inherited frozen manufacturing CSV; it is not an official machine download. `logs/` records actual execution and clean-copy reproduction; `scripts/validate_studies.py` must be run **from the full repository root** to check indexed-study layout.

## 14. Next-Stage Protocol

(1) Programmatically re-download all 201 official auto/manufacturing rows and verify hashes/values; (2) reconstruct archival ALFRED/Fed monthly release vintages and exact release timestamps; (3) obtain historical OEM/model-level production, supplier shipments, inventory, strikes and chip-shortage data; (4) map contemporaneous SEC filing dates to firm revenue and margins with a historical exposure matrix; (5) only after these pass, evaluate delisting-adjusted total returns, sector/market benchmarks, trading costs/capacity, clean holdout and multiple-testing corrections. Pre-register sign, horizon and universe before new collection; do not tune away the current negative result.

## 15. Sources & Artifacts

Official [G.17 2026-10-16](https://www.federalreserve.gov/releases/g17/20261016/default.htm); [FRED auto table](https://fred.stlouisfed.org/data/IPG3361T3S); [FRED manufacturing table](https://fred.stlouisfed.org/data/IPMAN); [GM SEC FY2025](https://www.sec.gov/Archives/edgar/data/1467858/000146785826000013/gm-20251231.htm); [Ford SEC FY2025](https://www.sec.gov/Archives/edgar/data/37996/000003799626000015/f-20251231.htm); [Census NAICS](https://www.census.gov/naics/); [2024 AIES NAICS 3361](https://test.data.census.gov/table/AIESBASIC2024.AIES31BASIC02?codeset=naics~3361&g=010XX00US); [ALFRED archive](https://alfred.stlouisfed.org/). See `data/source_register.csv` and `data/source_qa.md` for precise source roles, grades, publication dates, observation ranges and UNKNOWN vintage fields. Artifacts: frozen raw/derived CSVs, `results/` full diagnostics, `figures/` 11 calculated SVG charts, `tests/` unit checks, `logs/` execution evidence, and the 49-cell executed `research.ipynb`.

