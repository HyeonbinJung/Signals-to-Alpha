# Outpatient–Nursing Pressure → U.S. Hospital Employment (NAICS 622)

**Status: REPRODUCED RETROSPECTIVE HOSPITAL-EMPLOYMENT MACRO FALSIFICATION · NOT VERIFIED PIT · NOT EQUITY ALPHA.**  
**Data freeze:** 2026-10-26 inherited official BLS/FRED revised snapshot; research 2026-10-28. **Independent outcome:** U.S. hospital payroll employment, *not* admissions, corporate sales or total equity returns.

## 01. Abstract

**Question:** Does two-month-stale outpatient-care hiring growth relative to nursing/residential-care hiring improve six-month-ahead U.S. **hospital** payroll growth forecasts after hospital persistence and economy-wide hiring are controlled? A frozen **201-month** official BLS CES panel (2010-01–2026-09) provides **99 purged expanding-window forecasts** (2018-01–2026-03). Adding the factor reduces macro-control OOS RMSE from **4.5501** to **4.2742 log percentage points**, but is **far worse than hospital persistence (1.4184) and historical mean (1.7681)**; gains disappear outside 2020–2021. The 1,000-block-reorder exploratory tail fraction is **0.2248**, and the 2,000-draw paired moving-block gain interval **[-0.1782, +0.5870]** crosses zero. **Verdict:** a reproducible, pandemic-sensitive, *negative* hospital-sector macro-factor pilot, not a point-in-time or investable equity-alpha result.

## 02. Research Design & Hypotheses

**H1 (mechanism):** faster growth in ambulatory care *excluding home health* than in nursing/residential care may lead hospital referrals, diagnostic utilization and eventual hospital staffing demand. **H2 (incremental):** this fixed relative-growth score should improve six-month-ahead hospital hiring forecasts beyond hospital own-growth, national payroll and nursing growth. **H3 (robustness):** any gain should persist across pre/post-pandemic regimes, longer data-release buffers, 3/9-month horizons, rolling fits and block-aware nulls. **Null:** no incremental predictive value after controls. **Counterthesis:** outpatient substitution may *reduce* hospital demand, hospital payroll reflects staffing shortages/reimbursement rather than visits, and COVID caused correlated labor disruptions. A primary failure condition is **not beating the best simple baseline**, regardless of improvements against an overfitted multivariate control.

## 03. Industry Context

The target is **NAICS 622 Hospitals**, distinct from the prior nursing/residential-care outcome **NAICS 623**. September 2026 BLS CES payrolls in this fixed snapshot are **5,797.8 thousand** hospital workers, **9,266.4 thousand** ambulatory workers, **1,894.2 thousand** home-health workers and **3,489.4 thousand** nursing/residential workers. These are **employment levels, not industry revenues or patient volumes**. Ambulatory services (NAICS 621) include home-health care (6216), so subtracting the nested home-health series is necessary before claiming an outpatient *nonhome* proxy; this arithmetic difference remains a rough labor proxy, not patient flows. Source pages and 2026-10-02 release are in the register. The economic channel is ambiguous because referrals and substitution can operate in opposite directions.

## 04. Data & Source Integrity

Five seasonally adjusted BLS Current Employment Statistics series were frozen in the previous Signals-to-Alpha healthcare study on **2026-10-26**. The file `data/raw_fred_ces_2010_2026_snapshot.csv` is **byte-identical** to that source (**SHA-256 `f1d5a8ff28a55f2d1798cbdb9cac239d46db6c006b0a9e1801abae1b3b1665f6`**), reconstructed and verified without new web retrieval; it is **not** a fresh independently downloaded 2026-10-28 vintage. Observations: **201 monthly rows**, January 2010–September 2026; no missing/duplicate dates, all employment counts positive, and ambulatory minus home health strictly positive. The source register records publisher, original FRED/BLS URL, download URL, grade A/B/C, units, observed dates, collection date, latest release, historical vintage **UNKNOWN**, revision risk and usage. A/B/C distinguishes original government series, inherited snapshot and analyst scenario weights; grade A does **not** establish PIT availability. SEC 2025 10-K sources are descriptive issuer maps only.

## 05. Point-in-Time Availability

At formation month **t**, every candidate input is measured at **t−2** or earlier, a conservative assumed two-month delay for monthly payroll data. For each expanding-window training example **u**, its six-month-forward YoY target must mature by **u+6+1 ≤ t**, including a one-month assumed target-release buffer; no model sees a future target. All model centering and scaling are fitted **within each training fold**; ridge penalty **α=10** and signal scale **5 log-pp** are fixed. This is **not verified PIT**: 2026-10-26 CES revisions are embedded throughout 2010–2026, and neither original observation-specific release timestamps nor ALFRED first-release vintages have been reconstructed. Release-buffer assumptions cannot repair revision leakage.

## 06. Factor Construction

Let H=hospital payroll, A=all ambulatory payroll, C=home-health payroll, N=nursing/residential payroll and P=total nonfarm payroll; all are seasonally adjusted thousands. Define **O=A−C**, a strictly positive outpatient-nonhome labor proxy. For any series X, at formation month **t** use `g_X(t)=100 ln[X(t−2)/X(t−14)]`. The *predeclared fixed* factor is `F(t)=tanh((g_O(t)−g_N(t))/5)`, with **5 log-pp** a saturation scale selected without fitting outcomes. Controls are `g_H(t)`, `g_P(t)` and `g_N(t)`; `g_N` also appears in the factor, so multicollinearity is a known limitation. The independent target is `Y(t)=100 ln[H(t+6)/H(t−6)]` (future six-month-ahead **YoY** hospital employment growth, **not** a six-month growth rate). Lagged hospital six-month momentum is a separate baseline. No full-sample z-score or return-optimized weights are used.

## 07. Exposure & Transmission

`data/sector_exposure_map.csv` maps NAICS 621 (ambulatory, positive), 6216 (home health, excluded from positive leg), 623 (nursing, negative leg/control) and 622 (hospital outcome), all as of the 2026-10-26 frozen CES snapshot. **Issuer exposure is descriptive only**: the 2025 SEC filings dated **2026-02-10** (HCA Healthcare) and **2026-02-17** (Tenet Healthcare) establish that HCA operated 190 hospitals and 121 freestanding ambulatory surgery centers, while Tenet reported 50 hospitals and a separate ambulatory segment with interests in 533 ASCs; segment accounting does not map one-to-one to CES payroll. Their **historical revenue exposure weights are UNKNOWN**, not backfilled to 2010; no issuer is a model observation. HCA's reported 2024/2025 consolidated revenue **$70.603B/$75.600B** is stored in `data/issuer_fundamentals_descriptive.csv` only to demonstrate a dated actual fundamental, **not** an OOS revenue forecast. Consequently leave-one-company-out and security IC/spreads are **not applicable**; leave-one-*calendar-year*-out is the available macro stability test.

## 08. Outcomes & Baselines

The sole predictive outcome is future **hospital payroll YoY log growth**. **99 common monthly origins** from 2018-01-01 through 2026-03-01 use expanding training with ≥60 matured observations. Comparators: (1) expanding historical mean, (2) hospital-growth persistence ridge, (3) hospital six-month momentum ridge, (4) hospital growth + momentum AR Ridge, (5) macro controls (hospital + total payroll + nursing growth), (6) the identical controls + factor, (7) factor-only, plus no-nursing/no-payroll ablations. Ridge α=10 is fixed, standardization is train-only, and forecasts share the exact same origins. Report RMSE/MAE in log-pp and paired losses. A **temporal Spearman rank association** is not a cross-sectional equity Rank IC. No issuer total returns, benchmark-adjusted returns, long-short spread, Sharpe or costs are computed.

## 09. Empirical Findings

| Model | OOS n | RMSE (log-pp) | MAE (log-pp) |
|:--|--:|--:|--:|
| mean | 99 | 1.7681 | 1.3999 |
| persistence | 99 | 1.4184 | 1.0506 |
| momentum | 99 | 1.4670 | 1.0604 |
| ar_ridge | 99 | 1.4933 | 1.0691 |
| macro_controls | 99 | 4.5501 | 2.3372 |
| full | 99 | 4.2742 | 2.3173 |
| factor_only | 99 | 1.7955 | 1.3466 |
| no_nursing | 99 | 4.7427 | 2.3648 |
| no_payroll | 99 | 1.8955 | 1.3646 |

The augmented model's **+0.2759 log-pp** RMSE improvement over a poor multivariate control does **not** constitute useful forecast alpha: hospital persistence is **1.4184** and historical mean **1.7681**, both dramatically better. The full model's residual performance is disproportionately harmed by COVID-era joint movements; the pre-2020 improvement is small and the post-2021 improvement is negative. Effective OOS squared-loss difference sample size under a 12-lag autocorrelation heuristic is **33.8**, not 99 independent observations. The entire 99-origin forecast panel and scorecard are saved in `results/` and Figures 01–07 display actual computed levels, growth, factor, forecasts and paired errors.

## 10. Robustness & Placebos

**1,000 twelve-month block-order randomizations** of the factor, each with a full purged refit, give an **exploratory right-tail fraction 0.2248** for observed control-minus-full RMSE gain; because nonstationary time blocks are not exchangeable, this is **not an exact randomization p-value**. **2,000 paired moving-block bootstrap** resamples (12-month blocks) give a 95% gain interval **[-0.1782, +0.5870] log-pp**, which includes zero. **1,000 scenario weight perturbations** use `F_w=tanh([w*g_O+(1−w)*g_C−g_N]/5)` for `w∈[0.5,1]`; **100.0%** beat the weak macro controls, but **none of this validates the factor against hospital persistence**. Ablations, rolling/expanding comparison, 3/9-month horizons, 3/4-month assumed input lags, regime splits and leave-one-year-out are saved. A leave-one-company-out test is not possible without historical issuer observations.

## 11. Regime Sensitivity

| Test | OOS n | Control RMSE | Full RMSE | Control − full (log-pp) |
|:--|--:|--:|--:|--:|
| horizon_3m | 102 | 2.6737 | 2.4093 | +0.2643 |
| horizon_9m | 96 | 6.8064 | 6.5516 | +0.2548 |
| lag_3m | 99 | 5.1525 | 4.7857 | +0.3668 |
| lag_4m | 99 | 5.8023 | 5.3710 | +0.4313 |
| rolling_84m | 99 | 6.9875 | 6.8399 | +0.1477 |
| pre_2020 | 24 | 1.1259 | 1.0553 | +0.0706 |
| pandemic_2020_2021 | 24 | 8.9311 | 8.3469 | +0.5842 |
| post_2021 | 51 | 1.4338 | 1.4672 | -0.0333 |
| exclude_2020_2021 | 75 | 1.3430 | 1.3491 | -0.0061 |

The control-relative benefit is concentrated in 2020–2021 (**+0.5842**), while 2022+ is **-0.0333** and excluding 2020–2021 gives **-0.0061**. Excluding **2020** alone reverses the full-sample control-relative sign (**-0.2362**), an important falsification. Alternative horizons/lags do not solve the much larger failure against persistence. Monthly overlapping YoY labels and structural breaks invalidate naive independent-observation significance tests.

## 12. Bias Audit & Verdict

| Risk | Finding |
|:--|:--|
| Historical revision / lookahead | **UNRESOLVED** — latest-revised 2026-10-26 CES snapshot, no original-release ALFRED panel. |
| Release timing | Two-month input buffer and seven-month target maturity are assumptions, not verified archival timestamps. |
| Feature and fit leakage | Deterministic predeclared factor, train-only centering and target purge verified in unit tests. |
| Overlap / effective n | Monthly origins with 12-month growth labels; block-bootstrap descriptive only; n_eff≈33.8. |
| Multiple testing | This is one of many sequential industry studies; p-value familywise corrections and untouched holdout absent. |
| Sector composition | Ambulatory includes home care; subtracting counts does not identify referrals or patient volumes. |
| Firm survivorship / selection | 2025 HCA/Tenet examples chosen for description, not historical issuer universe; no firm-level OOS. |
| Security alpha / costs | No dividends, delistings, benchmark, transaction costs or capacity; **not tested**. |
| Structural break | 2020 dominates apparent improvement; post-2021 and leave-2020-out gains fail. |

**Verdict: REPRODUCED RETROSPECTIVE HOSPITAL-EMPLOYMENT MACRO FALSIFICATION — NOT PIT / NOT EQUITY ALPHA.** An apparent control-relative improvement is **economically unconvincing** because simpler hospital persistence beats the full model by a wide margin, and its timing is unstable.

## 13. Reproduction

Python 3.10+ from this directory:

```bash
pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python run_analysis.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 pytest -q tests
jupyter nbconvert --to notebook --execute research.ipynb --output /tmp/hospital-reexecuted.ipynb
```

From repository root: `python scripts/validate_studies.py`. The frozen source hash is asserted at runtime; `results/metrics.json`, complete placebo/bootstrap/weight draws, `results/walk_forward_oos.csv`, 12 computed figures and the executed notebook are reproducible offline. Local run logs in `logs/` record actual execution; repository CI's structural gate does **not** establish numerical reproduction or historical PIT.

## 14. Next-Stage Protocol

(1) Download **ALFRED CES first-release vintages** and actual release calendars, archive checksums and rebuild a formation-date availability panel. (2) Obtain **CMS hospital admissions, utilization and claims** as independent hospital-demand outcomes with release dates; avoid treating hiring as patient volume. (3) Add dated issuer-specific hospital/ASC segment revenue and earnings for a **predeclared complete historical issuer universe** with filing-date lags; test issuer-level sales/EPS against naive and sector baselines. (4) Only after credible fundamental lead, acquire delisting-inclusive **total returns**, market/healthcare benchmark returns and execution costs; evaluate sector-neutral portfolio spreads, capacity and realistic trading dates. (5) Freeze hypotheses before a new holdout and correct for the broad family of industry studies and scenario searches.

## 15. Sources & Artifacts

**Original A-grade series:** [BLS hospitals](https://fred.stlouisfed.org/series/CES6562200001), [ambulatory](https://fred.stlouisfed.org/series/CES6562100001), [home health](https://fred.stlouisfed.org/series/CES6562160001), [nursing](https://fred.stlouisfed.org/series/CES6562300001), [national payroll](https://fred.stlouisfed.org/series/PAYEMS). **Issuer filings:** [HCA 2025 SEC 10-K, filed 2026-02-10](https://www.sec.gov/Archives/edgar/data/860730/000119312526044769/hca-20251231.htm) and [Tenet 2025 SEC 10-K, filed 2026-02-17](https://www.sec.gov/Archives/edgar/data/70318/000007031826000012/thc-20251231.htm). **Inherited snapshot provenance:** [prior healthcare study frozen CES CSV](https://github.com/HyeonbinJung/Signals-to-Alpha/blob/main/Home-Care-Pressure-to-Alpha-U.S.-Healthcare-Services/data/fred_ces_2010_2026_snapshot.csv). The BLS/FRED series were last released 2026-10-02 in this snapshot; original observation-specific timestamps **UNKNOWN**. All URLs, units, revisions, grades and roles are in `data/source_register.csv`. Raw/derived data and dated issuer maps: `data/`; models: `run_analysis.py`; real scorecards/distributions: `results/`; 12 computed diagnostic charts: `figures/`; execution and tests: `logs/` and `tests/`.
