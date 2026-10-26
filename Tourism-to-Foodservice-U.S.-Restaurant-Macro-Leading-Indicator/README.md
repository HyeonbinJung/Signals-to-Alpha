# Tourism Demand Gap → U.S. Food Services Employment (Retrospective Macro Pilot)

**Status:** Executed retrospective macro lead-indicator falsification; **NOT historical point-in-time**, **NOT investable equity alpha**. 2026-10-26 fixed source snapshot. This is a **different target industry (NAICS 722 food services)** from the previously indexed accommodation study (NAICS 721), but it deliberately reuses the same BTS/BLS frozen source panel; it is not independent data replication.

## 01. Abstract

**Research question:** Does lagged U.S. airline passenger activity relative to accommodation hiring improve prediction of **three-month-ahead year-over-year employment growth in food services and drinking places**, beyond simple foodservice persistence and lodging controls? The demand mechanism is plausible: leisure and business travel can stimulate restaurant visits, yet domestic neighborhood dining, prices, labor productivity and local substitution may overwhelm it. The predeclared model is evaluated with purged expanding-window origins against mean, persistence, multivariate controls and factor-only baselines. The observed **70** common OOS origins (2019-09 to 2025-06) yield RMSE **71.659 percentage points** for the augmented model versus **66.047** for controls and **15.186** for the historical mean: a **negative** incremental result. The unusually large pandemic errors, historical revisions, transcription limitations and absent issuer-level outcomes rule out a validated equity alpha claim.

## 02. Research Design & Hypotheses

- **H1 (economic lead):** growth in BTS revenue passenger miles reflects travel-driven incremental restaurant demand and should predict subsequent foodservice employment.
- **H2 (incremental value):** the fixed tourism gap improves three-month-ahead OOS RMSE against foodservice momentum, lodging controls and the expanding historical mean.
- **H3 (robustness):** the gain survives 12-month block shuffles, paired moving-block uncertainty, ±30% proxy exposure weights, alternative horizons, conservative release buffers and pandemic exclusions.
- **Null/failure rule:** any failure to beat the best simple baseline or consistent sign reversals means the factor fails; a statistically interesting association alone does not establish tradability.
- **Counterthesis:** restaurant hiring is local, largely unrelated to airline travel; the gap mixes different industry scales, the pandemic introduces extreme structural breaks, and historical revised observations are unavailable in real time.

This study predefines a 3-month horizon, a fixed Ridge penalty of 10, a minimum of 48 training origins, and fixed release buffers of four months for BTS and two months for BLS. These are modeling assumptions rather than recovered historical publication timestamps.

## 03. Industry Context

The forecast target is **BLS CES7072200001: Food Services and Drinking Places**, a seasonally adjusted payroll series, **not restaurant revenue, profitability or returns**. Its September 2026 observation was **12,393.0 thousand employees**, as displayed by FRED on 2026-10-26 following the BLS October 2, 2026 release. Accommodation (CES7072100001) is a related but separate NAICS 721 industry, while air transport passenger miles proxy a narrower travel-intensive demand component. BTS's AIRRPMTSID11 June 2026 reading was **94,921,559 thousand passenger miles**, as reported on the FRED page updated October 1, 2026. These latest levels describe scale and are not used as future information in formation-date features. This sector includes full-service, limited-service and drinking-place operators; their tourism exposures are heterogeneous and historical issuer segment weights are **UNKNOWN**.

## 04. Data & Source Integrity

Frozen raw CSV: [`data/bts_bls_snapshot_2026-10-26.csv`](data/bts_bls_snapshot_2026-10-26.csv), **153** calendar months from 2014-01 through 2026-09; BTS air series ends 2026-06 and subsequent months are missing rather than imputed. Source file SHA-256: `98ad34cabef652c021869fcfa74515a322272ddfb53c3e84dcfa65a5d9af5cc0`. The file is copied byte-for-byte from the prior accommodation research pilot's manually transcribed FRED/BTS/BLS snapshot; its prior transcription QA notes are retained. We independently spot-checked the last published BLS foodservice, BLS accommodation and BTS air observations against current FRED pages, **not every historical row**. Full historical row-by-row provenance remains **UNVERIFIED**. See `data/source_register.csv` for A-grade original publishers, B-grade inherited frozen file and C-grade unused commentary, with URLs, latest update dates, observation ranges, units, vintage and revision status. All source IDs are fixed; no fabricated fundamentals, market returns or missing observations are inserted.

## 05. Point-in-Time Availability

At a forecast formation month **t**, use BTS revenue passenger miles no later than **t−4 months** and BLS payrolls no later than **t−2 months**. Train only on earlier origins **s ≤ t−(h+2) months** so their **h-month-ahead** foodservice labels have an assumed two-month BLS release buffer. This is a *conservative temporal embargo on a fixed revised snapshot*, **not proof of true historical availability**: each underlying vintage was downloaded/transcribed as of October 26, 2026, and revisions/seasonal re-estimation can leak later knowledge. Historical ALFRED/BLS/BTS release archives and timestamp-specific transformations are required for PIT validation. We do not claim historical PIT or verified live implementation.

## 06. Factor Construction

For a level series X, define \(g^{12}_{X,t}=100(X_t/X_{t-12}-1)\), in percentage points. Fix a nonlinear compression **without full-sample fitted moments**: \(z(x)=\tanh(x/20)\). The primary tourism gap is

\[F_t=z(g^{12}_{AIR,t-4})-z(g^{12}_{HOTEL,t-2}).\]

The dependent variable is \(y_t=g^{12}_{FOOD,t+3}\). The control vector is \(C_t=[g^{12}_{FOOD,t-2},g^{3}_{FOOD,t-2},g^{12}_{HOTEL,t-2}]\). The augmented model adds \(F_t\) to \(C_t\). Ridge regression standardizes features using **training-window moments only**, penalizes coefficients with fixed λ=10 and leaves the intercept unpenalized. No parameters are selected on the OOS results.

## 07. Exposure & Transmission

The analyst-defined weights are **+1.0** for air-travel demand and **−1.0** for accommodation hiring, not company-specific sales exposure estimates. The intuition is that airline activity in excess of lodging employment may reflect demand not yet fully reflected in hospitality labor supply. This interpretation is fragile: passengers may eat outside the U.S., hotel staffing may respond with a lag, and restaurant employment may not scale proportionally with demand. `data/exposure_map.csv` documents NAICS 481, 721 and 722 roles, evidence and as-of date. We vary both weights independently over [0.7, 1.3] in 1,000 seeded draws. **No issuer-level exposure mapping can be validated** with these aggregate series; a leave-one-company-out test is inapplicable, and a leave-one-year-out diagnostic is provided instead.

## 08. Outcomes & Baselines

The primary endpoint is the BLS **aggregate payroll growth**, not firm revenue/EPS, price return or total shareholder return. On **identical 70 OOS origins**, compare: (1) expanding historical target mean; (2) Ridge on lagged foodservice YoY persistence; (3) Ridge on foodservice YoY, foodservice three-month growth and lodging YoY; (4) those controls plus tourism gap; (5) tourism gap alone. Origins use expanding training sets with a five-month training-label embargo for the three-month target and two-month label release. Compute RMSE and MAE in percentage points; Rank IC, long-short spread, benchmark-adjusted equity return and transaction-cost net alpha are **NOT APPLICABLE** without securities observations.

## 09. Empirical Findings

| Model | OOS RMSE (pp) | OOS MAE (pp) | N |
|---|---:|---:|---:|
| Expanding historical mean | 15.186 | 9.368 | 70 |
| Foodservice persistence | 15.619 | 8.714 | 70 |
| Multivariate lodging controls | 66.047 | 23.879 | 70 |
| **Controls + tourism gap** | **71.659** | **25.185** | **70** |
| Tourism gap only | 15.089 | 9.381 | 70 |

**Primary delta (control RMSE − augmented RMSE): −5.611 pp**. The multivariate models show large pandemic-related extrapolation errors; their poor scores are a warning, not a reason to celebrate the factor-only model's small advantage over the mean. A factor-only fit is not a credible incremental-alpha demonstration. Figures 01–09 show raw demand, labor series, factor components, OOS predictions, baseline comparison, cumulative paired loss, block-shuffle null, bootstrap distribution and exposure perturbation. `results/walk_forward_oos.csv` contains each observed target and prediction; `results/scorecard.csv` and `results/metrics.json` are computed outputs.

## 10. Robustness & Placebos

- **1,000 12-month block-shuffle refits:** exploratory upper-tail fraction **0.896** for control-minus-full RMSE. Block order is shuffled with within-block chronology preserved; because the pandemic and structural trends violate exchangeability, this is **not an exact p-value**.
- **2,000 paired 12-month circular moving-block bootstrap draws:** 95% percentile interval for RMSE improvement **[−9.725, −0.115] pp**. Nominal OOS N=70 is not 70 independent outcomes because monthly overlapping target windows are serially dependent.
- **1,000 exposure perturbations:** independently vary air and lodging weights from 0.7 to 1.3; **0%** of draws produced positive incremental RMSE improvement versus controls.
- **Leave-one-year-out (OOS scoring only):** removing 2020 changes the RMSE delta to **−0.428 pp**; this is a sensitivity deletion, **not** a new training sample cross-validation or leave-one-company-out.
- **Alternative horizon/release-lag experiments:** at h=1 the delta was **+1.513 pp** (N=72); at h=6 it was **−1.942 pp** (N=67). Increasing BTS lag to 5 months gave **−4.381 pp** (N=69) and to 6 months gave **+0.042 pp** (N=68); increasing BLS lag to 3 months gave **−1.001 pp** (N=70). Changing the horizon or lag also changes eligible origins, so these are *exploratory* robustness diagnostics, not identical-sample causal effects.

## 11. Regime Sensitivity

The pre-2020 OOS regime has only **4** observations and is **too small to interpret**. The 2020–2022 window has **36** origins with a control-minus-full RMSE delta **−7.825 pp**; the post-2022 window has **30** origins with **−0.060 pp**. Excluding 2020 leaves **58** origins with **−0.428 pp**. The observed harm is dominated by the pandemic but is not rescued by excluding 2020. This is a structural-break falsification, not a proof that the sign is stable in all future conditions.

## 12. Bias Audit & Verdict

**Lookahead:** lagged inputs and purged labels reduce obvious temporal leakage; 2026 revised values and unknown release vintages remain material lookahead risks. **Selection:** three series and the tourism-gap construction are analyst chosen, not prospectively preregistered. **Survivorship:** aggregate industries avoid a stock-universe filter but hide establishment turnover. **Multiple testing:** horizons, lags, weights and regimes are diagnostic searches; no multiple-testing adjusted alpha inference is claimed. **Nonstationarity:** COVID-era dynamics make linear Ridge extrapolation unstable. **Costs/capacity:** no security is traded; trading costs, shorting and market impact are not modeled. **Target proxy:** payroll employment reflects labor supply, productivity and wage constraints, not just dining demand. **Provenance:** the inherited manual transcription is spot-checked but not independently bulk verified. **Verdict: FAIL as an incremental macro predictor; NO EQUITY ALPHA CLAIM.**

## 13. Reproduction

From the study directory on Python 3.10+: `python -m pip install -r requirements.txt`, `OPENBLAS_NUM_THREADS=1 python run_analysis.py`, `OPENBLAS_NUM_THREADS=1 python -m pytest -q tests`, then `OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute --inplace research.ipynb` (or run all in Jupyter). The analysis uses seed **20261026**, fixed λ=10 and writes frozen derived panel, 1,000 block-shuffle refits, 2,000 bootstrap draws, 1,000 exposure draws, metrics, nine figures and run logs. Reproduction must compare CSV row counts, frozen SHA and RMSE to the committed results. `python scripts/validate_studies.py` must also pass at repository root. The notebook contains substantial independent analytical code and stored computed outputs; it is not an empty wrapper.

## 14. Next-Stage Protocol

(1) Replace inherited manual CSV with official downloadable BTS/BLS bulk releases, compare **every** historical row and pin SHA. (2) Reconstruct monthly release-vintage values, including benchmark revisions and publication timestamps, and rerun formation-date features on true archived vintages. (3) Add restaurant receipts, card-spend or tax data to test demand before employment. (4) Map contemporaneous full-service versus limited-service exposure using actual historical company filings and establishment geography, with survivorship-aware firm coverage. (5) Only after fundamental validation, assemble total-return-adjusted securities and benchmark/momentum/size/value controls, transaction costs, realistic turnover and capacity. A failed macro proxy does not warrant optimized equity backtests.

## 15. Sources & Artifacts

- [BTS AIRRPMTSID11](https://fred.stlouisfed.org/series/AIRRPMTSID11), monthly SA, reported updated 2026-10-01.
- [BLS CES7072100001](https://fred.stlouisfed.org/series/CES7072100001), monthly SA, reported updated 2026-10-02.
- [BLS CES7072200001](https://fred.stlouisfed.org/series/CES7072200001), monthly SA, reported updated 2026-10-02.
- [BLS Employment Situation September 2026](https://www.bls.gov/news.release/empsit.htm), published 2026-10-02; labor-market context only.
- [Prior frozen-data provenance](https://github.com/HyeonbinJung/Signals-to-Alpha/tree/main/Air-Travel-to-Alpha-U.S.-Accommodation-Hospitality), reused fixed snapshot and original QA notes, **not an independent new source**.
- [`data/source_register.csv`](data/source_register.csv), [`data/exposure_map.csv`](data/exposure_map.csv), [`data/derived_formation_panel.csv`](data/derived_formation_panel.csv), [`results/metrics.json`](results/metrics.json), [`results/scorecard.csv`](results/scorecard.csv), [`results/walk_forward_oos.csv`](results/walk_forward_oos.csv), [`figures/`](figures/), [`tests/`](tests/), [`research.ipynb`](research.ipynb).
