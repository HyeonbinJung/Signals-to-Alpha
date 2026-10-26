# Home-Care Pressure-to-Alpha — U.S. Healthcare Services

**Status: REPRODUCED RETROSPECTIVE MACRO FALSIFICATION · NOT VERIFIED PIT · NOT EQUITY ALPHA.**  
**Research freeze:** 26 October 2026. **Outcome:** U.S. nursing/residential-care employment growth, not corporate sales or stock returns.

## 01. Abstract

**Research question.** Does a predeclared two-month-lagged difference between U.S. home-health and hospital employment growth forecast nursing/residential-care employment growth six months ahead, beyond persistence and national payroll trends? Using **201** monthly official BLS observations from 2010-01 to 2026-09 and **99** purged expanding-window forecasts (2018-01-01 to 2026-03-01), the candidate **fails**: full-model RMSE **5.562 pp** versus macro controls **5.453 pp**, nursing persistence **3.760 pp**, and historical mean **4.349 pp**. These are *latest-revised fixed-snapshot* data, **not** original-release point-in-time records. **Verdict:** reproducible retrospective healthcare-labor factor falsification; no validated predictive improvement and no security-return alpha.

## 02. Research Design & Hypotheses

**H1 (economic transmission):** home-care employment growth relative to hospital employment may reflect care-setting substitution and/or rising demand for long-term services, potentially preceding nursing/residential-care hiring. **H2 (incremental prediction):** the predeclared relative-growth signal should reduce out-of-sample nursing-sector forecast error relative to mean, persistence and national-payroll/hospital controls. **H3 (robustness):** any gain should survive 3/9-month horizons, extra release buffers, 2020 regime changes, rolling training and 12-month block-aware falsifications. **Null:** no incremental information after controls. **Counterthesis:** care-setting substitution can *reduce* institutional demand, policy reimbursement differs across settings, hiring reflects labor supply rather than patient volume, and revised CES series contain benchmark breaks. We treat a failure to beat the simple persistence baseline as a decisive failure.

## 03. Industry Context

The U.S. care economy includes home health (NAICS 6216), hospitals (NAICS 622), and nursing/residential care (NAICS 623), with different reimbursement, staffing, and patient-acuity economics. In the BLS CES series, September 2026 payroll employment is **1,894.2k** home-health workers, **5,797.8k** hospital workers and **3,489.4k** nursing/residential workers; all are **workers, not revenue, profits or patient volumes**. The long-run home-care growth thesis could be favorable, but cost constraints, reimbursement changes and workforce availability may overwhelm demand. Sources: BLS/FRED series pages in §15, last updated 2026-10-02. No external revenue-size forecast is inferred from employment.

## 04. Data & Source Integrity

Five official **BLS Current Employment Statistics** monthly seasonally adjusted payroll series were retrieved via FRED CSV on **2026-10-26**, restricted to the same **201** months (2010-01 through 2026-09), and frozen in `data/fred_ces_2010_2026_snapshot.csv` (SHA-256 `f1d5a8ff28a55f2d1798cbdb9cac239d46db6c006b0a9e1801abae1b3b1665f6`). `data/source_register.csv` contains each original source URL, download URL, grade **A**, units, latest release date, coverage, usage role and revision caveat. There are no simulated observations. CES data are revised and benchmarked; the **historical observation-specific release timestamps and vintages are UNKNOWN**. An April 2025 discontinuity in home-care employment is visible in the data and must not be explained causally without archived CES documentation.

## 05. Point-in-Time Availability

At forecast formation month **t**, the signal and controls use only monthly observations labeled **t−2**, with a conservative two-month *assumed* release buffer. A historical training origin **u** is eligible only when **u+6+1 ≤ t**, allowing six months for the target to mature and one month for its release. All standardization is fitted **inside each training fold**, and ridge penalty α=10 is fixed. **This is NOT a verified PIT backtest**: the 2026-10-26 frozen FRED snapshot contains retrospective revisions to 2010–2026 observations, and fixed publication lags cannot reverse those revisions. Actual ALFRED/BLS first-release vintages must be reconstructed before any executable-signal claim.

## 06. Factor Construction

For care-setting employment levels `H` (home health), `B` (hospitals), `N` (nursing/residential) and `P` (national payroll), define at month **t**: `g_X(t)=100·ln[X(t−2)/X(t−14)]`. The **fixed factor** is `F(t)=tanh([g_H(t)−g_B(t)]/5)`; the 5 percentage-point saturation scale is not estimated from future data. Controls: `g_N(t)`, `g_P(t)` and `g_B(t)`. The independent target is `Y(t)=100·ln[N(t+6)/N(t−6)]`, the **YoY growth of nursing employment observed six months after formation**. Ridge α=10, train-only mean/std, expanding training; no future normalization or optimized factor weights.

## 07. Exposure & Transmission

The exposure map is **industry-segment**, not an equity issuer portfolio: NAICS 6216 home health (positive factor leg), NAICS 622 hospitals (negative factor leg), NAICS 623 nursing/residential care (outcome), and NAICS 621 ambulatory care (overlapping alternate signal). `data/exposure_map.csv` documents these mappings. For sensitivity, replace home growth with `w·home+(1−w)·ambulatory`, with **w uniformly drawn 0.5–1.0 in 1,000 scenarios**; these are **scenario priors**, not measured company revenue exposures. No historical issuer segment weights or corporate filing-date fundamentals were assembled, so leave-one-company-out and equity Rank IC/long-short returns are **not applicable**, not silently assumed passed.

## 08. Outcomes & Baselines

The outcome is future **nursing/residential employment YoY log growth**, not sector earnings or stock performance. From 2018-01-01 through 2026-03-01 there are **99 identical monthly OOS origins**. Compare (1) expanding historical mean, (2) nursing persistence ridge, (3) nursing persistence + national payroll + hospital growth ridge, (4) the same controls plus fixed `F(t)`, (5) factor-only ridge, plus alternate/ablation specifications. Train on labels matured at least 7 months earlier, minimum 60 origins. Primary metrics are RMSE and MAE in **percentage points**; IC, excess-return spread, Sharpe and transaction costs cannot be computed without securities.

## 09. Empirical Findings

| Model | RMSE (pp) | MAE (pp) | OOS n |
|:--|--:|--:|--:|
| mean | 4.349 | 3.534 | 99 |
| persistence | 3.760 | 2.551 | 99 |
| macro | 5.453 | 3.240 | 99 |
| full | 5.562 | 3.364 | 99 |
| factor only | 4.454 | 3.579 | 99 |
| home only | 5.578 | 3.287 | 99 |
| alt ambulatory | 4.989 | 3.057 | 99 |
| no payroll | 3.739 | 2.573 | 99 |
| no hospital | 5.560 | 3.330 | 99 |

The full model **worsens** RMSE by **0.109 pp** versus macro controls and **1.803 pp** versus nursing persistence. A historical mean also beats the full model. Forecasts and paired losses are saved in `results/walk_forward_oos.csv`; Figures 01–05 visualize the level, growth, factor, predictions and loss-difference structure. No p-hacking can turn this negative result into evidence of an investable alpha.

## 10. Robustness & Placebos

**1,000 twelve-month block-shuffle refits** of the factor yield an exploratory right-tail fraction **0.730** for the observed macro-minus-full RMSE gain **-0.109 pp**; nonstationary blocks are not exchangeable, so this is **not an exact permutation p-value**. **2,000 moving-block bootstrap resamples** of paired OOS errors produce a 95% interval for macro-minus-full RMSE **[-0.268, -0.017] pp** (descriptive dependence-aware interval, not causal inference). Across **1,000 home/ambulatory exposure mixtures**, median improvement is **+0.025 pp** and the improvement is positive in **57.5%** of scenarios, showing exposure-definition sensitivity rather than a robust base factor. Alternative factor, factor-only, no-payroll/no-hospital ablations and leave-one-calendar-year-out evaluations are saved in the scorecard/robustness files. None validates the predeclared base signal.

## 11. Regime Sensitivity

| Test | N | Macro RMSE | Full RMSE | Macro−Full |
|:--|--:|--:|--:|--:|
| pre 2020 | 24 | 2.079 | 2.084 | -0.005 |
| 2020 onward | 75 | 6.154 | 6.281 | -0.126 |
| excluding 2020 2021 | 75 | 2.374 | 2.578 | -0.204 |
| horizon 3m | 102 | 3.201 | 3.331 | -0.130 |
| horizon 9m | 96 | 8.815 | 9.122 | -0.307 |
| lag 3m | 99 | 6.471 | 6.623 | -0.152 |
| lag 4m | 99 | 7.684 | 7.944 | -0.259 |
| rolling 84m | 99 | 6.663 | 6.558 | +0.105 |

Pre-2020 and 2020+ tests both fail the macro-control comparison, as does exclusion of 2020–2021. A rolling 84-month model may change the sign of the macro comparison, but it does **not** establish victory over simpler nursing persistence and is a **post-hoc specification**. Alternative horizons and longer release buffers do not rescue the base signal. Overlapping 12-month growth labels create substantial serial dependence; independent-observation t-tests would be misleading.

## 12. Bias Audit & Verdict

| Risk | Finding |
|:--|:--|
| Historical-vintage leakage | **Unresolved.** Latest-revised BLS CES snapshot; ALFRED vintages not assembled. |
| Publication timing | 2-month input buffer and 7-month training purge are assumptions, not archival release proof. |
| Look-ahead | Train-only scaling and target purge implemented; revision leakage remains. |
| Overlap/dependence | Monthly origins share 12-month target windows; moving-block bootstrap exploratory. |
| Selection/multiple tests | Care-setting hypothesis selected ex post; alternate horizons/lags and exposure mixtures exploratory. |
| Exposure | NAICS segment mapping is not a firm revenue share; ambulatory includes home health. |
| Survivorship/returns | No securities universe, filings, delistings, total returns or costs. |
| Structural breaks | 2020 disruptions and an unexplained April 2025 home-care level drop. |

**Verdict: REPRODUCED RETROSPECTIVE MACRO FALSIFICATION; the predeclared home–hospital relative-growth factor fails incremental prediction, and no PIT or investable equity alpha is established.**

## 13. Reproduction

From this directory on Python 3.10+:

```bash
pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python run_analysis.py
PYTHONPATH=. pytest -q tests
jupyter nbconvert --to notebook --execute research.ipynb --output /tmp/healthcare-reexecuted.ipynb
```

From repository root run `python scripts/validate_studies.py`. The frozen input is committed and offline reproducible. The notebook recomputes the primary model, 1,000 block shuffles, 1,000 exposure mixtures and 2,000 bootstrap draws, then displays computed diagnostics. `results/run_log.txt` and `results/metrics.json` contain the reproducibility record; CI structure checks are not a historical-vintage audit.

## 14. Next-Stage Protocol

(1) Archive **ALFRED/BLS historical CES first-release vintages** and actual monthly release calendars with hashes; re-run the *same* predeclared factor with formation-date releases. (2) Audit the April 2025 home-health level break against CES reclassification and benchmark notes. (3) Obtain CMS Medicare home-health claims, hospital utilization, nursing occupancy and reimbursement policy dates as independent outcomes, with appropriate lag/vintage. (4) Add dated issuer-specific segment disclosures only after a defensible universe and exposure map exist; then test future revenue/EPS with filing-date lags. (5) Only after fundamental evidence, test delisting-inclusive total returns, sector neutralization, costs and a genuinely held-out period; adjust for the full family of industry-factor searches.

## 15. Sources & Artifacts

Primary official source URLs: [BLS home-health employment](https://fred.stlouisfed.org/series/CES6562160001), [BLS hospitals](https://fred.stlouisfed.org/series/CES6562200001), [BLS nursing/residential care](https://fred.stlouisfed.org/series/CES6562300001), [BLS ambulatory care](https://fred.stlouisfed.org/series/CES6562100001), [BLS national payroll](https://fred.stlouisfed.org/series/PAYEMS), and [BLS September 2026 Employment Situation table](https://www.bls.gov/news.release/empsit.t17.htm). Latest series release **2026-10-02**; source retrieval **2026-10-26**. See `data/source_register.csv` for full provenance, UNKNOWN historical release timestamps and revision risk. Frozen input, derived panel and exposure map are in `data/`; executable analysis in `run_analysis.py`; 1,000-shuffle and 1,000-exposure distributions, scorecard, forecasts and metrics in `results/`; eight genuine computed diagnostics in `figures/`; nine tests in `tests/`. No proprietary patient records or security returns are used.

