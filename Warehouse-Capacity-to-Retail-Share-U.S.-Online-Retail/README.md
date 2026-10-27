# Warehouse Capacity → U.S. Online Retail Share: An Out-of-Sample Falsification

**Status: REPRODUCED MACRO PILOT — REVISED SNAPSHOT / NOT POINT-IN-TIME / NOT EQUITY ALPHA.** 2026-10-27. Industry outcome: U.S. retail trade (NAICS 44–45), e-commerce share of total retail sales. This reverses the direction of the earlier warehousing-employment study and tests a **new retail outcome**; it reuses the same previously frozen official-source dataset, so the observations are not independently new.

## 01. Abstract

**Research question:** Does a one-quarter-stale warehouse hiring premium forecast the next two-quarter change in the U.S. e-commerce share of retail sales, beyond share momentum and macro-employment controls? A 2000Q1–2026Q3 quarterly snapshot contains 107 rows; 99 fully formed signal/target rows yield **57 purged expanding-window OOS predictions**, 2011Q4–2025Q4. The augmented model's **1.2803 percentage-point RMSE** improves on the control model's **1.3233** by **0.0430**, but performs far worse than the **0.8223** historical-mean benchmark. The 2,000-draw paired circular-block bootstrap interval for control-minus-augmented RMSE is **[-0.0423, 0.1080]** and spans zero; the gain is concentrated in the 2020–2021 shock and reverses outside that regime. **Verdict:** the warehouse hiring premium is not a reliable standalone retail-share forecasting factor, and no investable equity alpha has been established.

## 02. Research Design & Hypotheses

**H1 (direction):** excess warehouse hiring, measured relative to economy-wide payroll growth, anticipates positive e-commerce retail-share change over the next two quarters because fulfillment capacity can relax delivery constraints. **H2 (incremental OOS):** adding this fixed factor to retail-share level, share momentum, payroll growth and courier growth improves purged expanding-window RMSE compared with the control model and a historical mean. **H3 (stability):** improvement persists before 2020, after 2021, under alternate feature staleness/horizons, sector-mixture perturbations, and year exclusions. **Null/counterthesis:** hiring follows e-commerce demand, not vice versa; common business cycles and the pandemic explain observed co-movement. **Failure rule:** no incremental value if the augmented model loses to the mean, bootstrap interval includes zero, or non-pandemic regimes reverse sign. Hypotheses and parameters are fixed for this documented retrospective exercise, not claimed as a prospective preregistration.

## 03. Industry Context

U.S. retail trade (NAICS 44–45) includes online and omnichannel orders. The official 2026Q2 seasonally adjusted e-commerce share was **17.1%** of total retail sales, released **2026-08-18** by the U.S. Census Bureau (FRED ECOMPCTSA; official quarterly retail e-commerce release). Warehouse labor can proxy for fulfillment throughput, but automation, outsourcing, parcel density and fulfillment efficiency break any stable one-to-one link. The pandemic sharply accelerated digital ordering, making it a stress test rather than clean evidence of an enduring causal factor. This study tests *retail-share demand structure*, not retail-firm revenue, EPS, market capitalization or stock performance.

## 04. Data & Source Integrity

**A** = original Census/BLS official series through FRED; **B** = exact byte-for-byte frozen snapshot inherited from the earlier repository study (secondary transport); **C** = unverified narrative or estimates, excluded from quantitative inputs. The complete [`data/source_register.csv`](data/source_register.csv) records exact URLs, series, units, release-date evidence, observed ranges, collection date and revision/vintage status. The raw 107-row file [`data/fred_quarterly_snapshot_2026-10-26.csv`](data/fred_quarterly_snapshot_2026-10-26.csv) has SHA-256 `17b99d105505b7c4ef7741012cf65d916bac0b907403474f18cffedcc4a99b2d` and Git blob SHA `33aee832217002135377f4bd180370727c292747`, identical to the earlier repository file. **This establishes snapshot identity, not independent authenticity of all historical observations.** The last retail-share observation is 2026Q2; the 2026Q3 retail-share value is missing and never filled. The three employment series extend to 2026Q3. CES monthly-to-quarterly averages were inherited, not independently rebuilt from each monthly vintage.

## 05. Point-in-Time Availability

At origin quarter *t*, define the hypothetical decision date as **end of quarter t+1**, at least one full quarter after the e-commerce share observation for *t*. Use warehouse, courier and total payroll observations only through *t−1*, conservatively two quarters stale at the decision date. The two-quarter target is `share[t+2] − share[t]`, with share[t+2] ordinarily published during quarter t+3. Training rows end at origin `i ≤ t−3`, making their target's hypothetical publication quarter `i+3 ≤ t`, before the test decision date. **Historical actual release dates, seasonal/benchmark revisions and real-time FRED ALFRED vintages have not been reconstructed**; this is an explicit operational-delay simulation on a single revised snapshot, **NOT verified PIT**. The 2025 Census methodological benchmark change is a possible structural discontinuity.

## 06. Factor Construction

For quarterly warehouse payroll `W`, courier payroll `C`, and economy-wide payroll `P`, define year-over-year log growth `g^W_q = 100 ln(W_q/W_{q−4})`, analogously for `C,P`. The fixed factor at origin `t` is **`F_t = g^W_{t−1} − g^P_{t−1}`** in log percentage points. No full-sample normalization is used. In exposure sensitivity, use **`F_t(w) = w g^W_{t−1} + (1−w)g^C_{t−1} − g^P_{t−1}`**, with 1,000 independent `w~Uniform[0.5,1]` draws; the primary specification is `w=1`. The target is **`Y_t = S_{t+2} − S_t`** in percentage points, where `S` is seasonally adjusted e-commerce retail share.

## 07. Exposure & Transmission

The [`data/exposure_map.csv`](data/exposure_map.csv) documents NAICS 493 warehousing (baseline weight 1), NAICS 492 couriers (baseline weight 0), and NAICS 44–45 retail (aggregate outcome). Warehouse and courier employment can reflect capacity expansion, outsourcing, automation and demand response. **No dated, numeric company-specific e-commerce revenue shares or issuer exposure weights are available.** The map is a sector mechanism and scenario prior, not a claimed estimate of Amazon/Walmart/Target revenue exposure. Accordingly, no leave-one-company-out or firm-level performance claim is fabricated; leave-one-*year*-out tests measure temporal fragility instead.

## 08. Outcomes & Baselines

All 57 OOS forecasts share identical origin dates. Baselines: (1) expanding historical mean of training targets; (2) retail-share persistence `S_t−S_{t−2}`; (3) fixed Ridge (`alpha=8`) on current share level, two-quarter share momentum, one-quarter-stale total payroll YoY and courier YoY; (4) augmented Ridge with `F_t`; (5) factor-only Ridge. Ridge predictors are **standardized within each training fold only**, never across the full panel. Minimum training size is 40 origins; the three-origin target-availability purge is enforced. Metrics are RMSE/MAE/bias in share percentage points. Cross-sectional equity IC, spreads, Sharpe, costs and corporate fundamentals are **not applicable**; the full-panel Spearman correlation is descriptive only, not an OOS alpha statistic.

## 09. Empirical Findings

| Model | OOS RMSE (pp) | MAE (pp) | N |
|---|---:|---:|---:|
| Historical mean | **0.8223** | **0.3795** | 57 |
| Share persistence | 1.3267 | 0.5523 | 57 |
| Macro + share controls | 1.3233 | 0.5889 | 57 |
| **Controls + warehouse factor** | **1.2803** | **0.5947** | 57 |
| Warehouse factor alone | 0.8696 | 0.4162 | 57 |

The augmented factor improves RMSE by **0.0430 pp** over controls, but **worsens MAE** and loses to the historical mean by **0.4580 pp**. The in-sample descriptive rank correlation between factor and subsequent target is **0.1114**; it is not a tradable cross-sectional Rank IC. Actual predictions and fold training counts are saved in `results/oos_predictions.csv`.

## 10. Robustness & Placebos

The **1,000-refit 4-quarter block shuffle** randomizes contiguous signal blocks while holding the target and controls fixed. Its **exploratory upper-tail fraction is 0.05994**, not an exact permutation p-value because the shuffled null is not an exchangeable data-generating process. A **2,000-draw paired circular-block bootstrap** of the 57 OOS error pairs gives a 95% interval **[-0.0423, 0.1080] pp** for control-minus-full RMSE, crossing zero. All 1,000 warehouse/courier exposure mixtures yield positive control-relative improvements, but this is a *conditional* comparison and does not overturn the failed historical-mean benchmark. Removing courier controls changes the sign of incremental improvement to **−0.00955 pp**, while removing all macro controls yields **−0.02462 pp**. Alternate 1/2/4-quarter target horizons and 1/2/3-quarter payroll staleness are computed in separate tables; these are exploratory checks, not hyperparameter selection.

## 11. Regime Sensitivity

**Pre-2020:** 33 OOS origins, control-minus-full RMSE **−0.00365 pp**. **2020–2021:** 8 origins, **+0.15633 pp**. **Post-2021:** 16 origins, **−0.08065 pp**. **Excluding 2020–2021:** 49 origins, **−0.01638 pp**. The gain is therefore concentrated in a short pandemic regime and fails outside it. `results/leave_one_year_out.csv` shows every test-year exclusion's impact; the small pandemic block and 2025 benchmark change are nonstationarity warnings, not ex post justifications for a strategy.

## 12. Bias Audit & Verdict

**Lookahead/revisions:** hypothetical lag and purge protect against obvious within-snapshot future-value use but cannot recover vintage-revised past values. **Selection:** the retail outcome was chosen after earlier warehousing work; the reverse-direction hypothesis and choice of horizons were not independently preregistered. **Survivorship:** national aggregates do not suffer firm-delisting bias but are subject to sampling/definition changes. **Overlap:** two-quarter targets overlap across origins; paired block uncertainty is approximate. **Multiple testing:** robustness grids and exposure perturbations are not separate independent confirmations. **Economic interpretation:** employment may follow demand; no causality identified. **Trading/costs:** no equity returns, execution lags, market-cap universe, turnover or costs were tested. **Final verdict: FAIL as a robust independent retail-share forecasting factor; REPRODUCED RETROSPECTIVE MACRO PILOT ONLY.**

## 13. Reproduction

From a clean checkout in this study directory: `python -m pip install -r requirements.txt`, `OPENBLAS_NUM_THREADS=1 python run_analysis.py`, `PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python -m pytest -q tests`, `OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute research.ipynb --output reproduced.ipynb`. From repository root run `python scripts/validate_studies.py`. The notebook runs the computations from frozen inputs, displays real calculated tables and figures, and persists executed outputs. The `logs/` directory records observed test and notebook runs. This is local reproducibility, **not a claim that the GitHub layout CI re-executes numerical analysis**.

## 14. Next-Stage Protocol

Acquire quarterly ALFRED vintages for ECOMPCTSA and monthly BLS CES historical releases; reconstruct true decision-date observations and data revisions. Obtain a versioned 2025 Census definition-break bridge and rerun pre-/post-break tests. Add independently sourced retailer quarterly U.S. digital revenue and dated 10-Q/10-K disclosures, then an issuer universe with delisted names and dividend/split-adjusted total returns. Freeze exposure weights from contemporaneous filings and preregister one horizon and a 2027 onward holdout before any equity-alpha, transaction-cost or capacity claim.

## 15. Sources & Artifacts

Official series: [Census/FRED ECOMPCTSA](https://fred.stlouisfed.org/series/ECOMPCTSA), [BLS/FRED warehousing CES4349300001](https://fred.stlouisfed.org/series/CES4349300001), [couriers CES4349200001](https://fred.stlouisfed.org/series/CES4349200001), [total payroll PAYEMS](https://fred.stlouisfed.org/series/PAYEMS). Latest retail-share official release: 2026-08-18; latest payroll release: 2026-10-02. See `data/source_register.csv` for exact source, release, observation, revision and collection fields. The frozen raw CSV, derived panel, 11 result files, 10 calculated SVG figures, Python modules, unit tests, executed `research.ipynb`, and logs are included. The earlier warehousing study provided the byte-identical frozen data, not independent confirmation of this new reverse-direction claim.
