# Inflation–Labor Pressure and U.S. Treasury Bill Yields

**Research status:** REPRODUCED RETROSPECTIVE MONEY-MARKET MACRO PILOT — NOT PIT / NOT EQUITY ALPHA.

## 01. Abstract

**Question.** Does a predeclared lagged inflation–labor-slack pressure signal forecast the next-quarter change in the U.S. 3-month Treasury-bill secondary-market rate, beyond standard rate and macroeconomic controls? This historical **1959Q1–2009Q3** market-rate study uses the 203-quarter `statsmodels` macrodata fixed snapshot compiled from FRED/BLS data accessed on **2009-12-15**. In 115 purged expanding-window forecasts (1980Q4–2009Q2), the full model RMSE is **0.808 percentage points**, versus **0.817** for the macro control and **0.738** for the historical mean. The marginal control-relative improvement is **+0.009 pp**; this does not beat the mean or zero-change baseline. **Verdict: retrospective short-rate macro pilot, NOT PIT and NOT investable alpha.**

## 02. Research Design & Hypotheses

**Primary falsifiable question:** At quarter-end t, does the known-at-t−1 CPI-inflation-minus-unemployment-change pressure score predict Δr_{t+1}=r_{t+1}−r_t beyond a prespecified macro Ridge model? **H1 (direction):** more inflation pressure raises next-quarter bill yields; **H2 (increment):** adding the score lowers purged expanding OOS RMSE relative to a rate-level/momentum/unemployment/GDP control; **H3 (robustness):** the gain survives block-aware nulls, decade exclusions, lag/horizon changes and pressure-weight perturbations. **Null:** no incremental predictive information beyond controls. Failure criterion: full-model RMSE not below both control and simple mean/zero-change, or unstable confidence intervals. **Counterthesis:** market yields incorporate inflation and policy expectations immediately, while revisions and structural monetary regimes swamp a stale quarterly signal. Mishkin (1991, https://www.nber.org/papers/w3632) finds long-run Fisher-effect evidence but not a universal short-run Fisher effect; the short-horizon H1 is therefore genuinely contestable.

## 03. Industry Context

**Market, not NAICS industry:** U.S. Treasury bills are short-term marketable federal obligations sold at discount; this is a **Treasury money-market** study, distinct from industrial production and equity-price studies. The Treasury is the issuer; dealers intermediate primary/secondary markets; banks and money-market funds are potential users. These channels are qualitative and **not firm-level measured exposure**. TreasuryDirect describes bills and their discount mechanism (https://www.treasurydirect.gov/research-center/history-of-marketable-securities/bills/t-bills-faqs/). **Historical 1959–2009 market size/growth: UNKNOWN** from the frozen dataset; current issuance statistics would be anachronistic.

## 04. Data & Source Integrity

**Source hierarchy:** A = original government series and Treasury definitions; B = a reproducible public-package frozen compilation; C = secondary contextual commentary (none used in model). Raw data are frozen as `data/macrodata_statsmodels_2009_snapshot.csv`; 203 quarters, 14 source columns, 1959Q1–2009Q3. Source register records original URLs, publishers, units, original publication date **UNKNOWN**, package access **2009-12-15**, local collection **2026-10-28**, observed period and revision caveats. Variables: `tbilrate` (quarterly average 3m bill rate in annualized percent), `infl` (annualized log CPI change), `unemp` (percent), `realgdp` (chained 2005-dollar billions). Original package provenance: https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/macrodata/data.py. The frozen package CSV is reproducible, but the original 2009 FRED files and per-quarter releases were not reconstructed.

## 05. Point-in-Time Availability

**Observation lag:** at the end of quarter t, macro features use only quarter t−1 or earlier; no contemporaneous CPI/unemployment/GDP values enter the signal. The next-quarter yield change Δr_{t+1} is measured after t. Training uses only examples s with s+h ≤ t−1, leaving one complete quarter as a purge buffer beyond the target horizon. **Critical limitation:** these are 2009-fixed retrospectively revised source values; a fixed observation lag does not reconstruct historical release vintages, so true formation-time availability remains **UNKNOWN / NOT PIT**. Actual monthly release timestamps and past revisions need ALFRED/archived H.15/BLS/BEA downloads before PIT claims.

## 06. Factor Construction

Let π_{t−1}=400·log(CPI_{t−1}/CPI_{t−2}) (annualized log percentage points, from frozen `infl`); Δu_{t−1}=u_{t−1}−u_{t−2} (percentage points). **Predeclared score** F_t = π_{t−1} − 0.5·Δu_{t−1}. The 0.5 coefficient is a fixed economic sensitivity assumption, **not** a fitted historical exposure. Target Y_t=r_{t+1}−r_t in annualized yield percentage points; all model standardization uses only the current training window. We vary the unemployment weight from 0.1 to 1.0 in 1,000 exploratory perturbations. The formula is an inflation/slack proxy, not a tradable spread or security return.

## 07. Exposure & Transmission

Proposed mechanism: inflationary pressure can raise expected policy rates, pushing 3m Treasury bill yields higher; rising unemployment may moderate policy expectations. The fixed pressure score is applied to the **market-wide bill yield**, with no arbitrary issuer-specific return exposures. `data/company_exposure_map.csv` lists the Treasury, primary dealers, money-market funds and banks as **conceptual, unweighted** participants with `UNKNOWN` company weights and dates. There is no company leave-one-out test because no company panel exists; instead we report leave-one-decade-out robustness. No inference about bank EPS, fund NAV or total returns is possible.

## 08. Outcomes & Baselines

**Same origins and targets for every model.** Baselines: historical mean change; zero-change yield persistence; naive prior-quarter rate momentum; AR Ridge with lagged rate and momentum; multivariate control Ridge with lagged rate, rate momentum, unemployment and 4-quarter real-GDP growth; pressure-only Ridge; full control+F Ridge. Ridge α=12 fixed ex ante (not tuned on OOS). Expanding training requires ≥80 eligible observations and target-release purge. Report RMSE, MAE and directional accuracy. No IC/spread is reported because this is a single market-rate time series, not a security cross-section.

## 09. Empirical Findings

**Primary 115 purged expanding-window forecasts (1980Q4–2009Q2).** RMSE (yield percentage points): mean **0.7381**, zero-change **0.7229**, momentum **1.0865**, AR Ridge **0.8029**, macro control **0.8173**, pressure-only **0.7395**, full **0.8080**. Control−full improvement is **+0.0093 pp**. The full model fails to outperform the simple mean and zero-change baselines. The full-sample (non-causal, in-sample) Pearson correlation between lagged factor and future yield change is **+0.0316**, a directional check for H1 rather than an OOS validation. All metrics are computed and saved in `results/scorecard.csv`, `results/walk_forward_oos.csv`, and `results/metrics.json`. This is a forecast-error comparison, not an investment profit claim.

## 10. Robustness & Placebos

**Block-aware null:** 1,000 re-fitted 8-quarter block-order shuffles of the pressure factor; exploratory upper-tail fraction **0.0579** (not an exact randomization p-value because blocks are not exchangeable under structural change). **Paired uncertainty:** 2,000 circular 8-quarter block bootstrap draws of paired OOS errors; 95% interval for control−full RMSE **[-0.0355, +0.0497] pp**. **Exposure perturbation:** 1,000 fixed-weight variants (0.1–1.0), positive-improvement share **100.0%**. Additional saved ablations isolate inflation, unemployment-change and sign reversal. These are exploratory stress tests, not multiple-testing-corrected discoveries.

## 11. Regime Sensitivity

Regime analysis reports 1980s, 1990s and 2000s, excluding 2008–09, plus leave-one-decade-out evaluation; OOS origin years begin in 1980. The target spans changing monetary-policy frameworks, disinflation, the Great Moderation and the 2008 crisis. Alternative forecast horizons 2Q/3Q and observation lags 2Q are independently re-estimated with the same purge logic. A one-time positive average improvement can be driven by particular rate regimes; do not generalize to the modern post-2009 low-rate or post-2022 tightening environments.

## 12. Bias Audit & Verdict

**Lookahead:** target-release purge and one-quarter macro observation lag applied, but original release vintages are UNKNOWN. **Selection:** the dataset ends in 2009Q3; retrospective topic selection and one predeclared signal with exploratory variants remain risks. **Survivorship:** not applicable to a single market yield; however historical market conventions changed. **Multiple testing:** 1 primary specification; sensitivity tables are exploratory and not family-wise adjusted. **Costs/capacity:** no futures, bill prices, transaction costs, funding or execution tested; yield changes ≠ bill total returns. **Verdict:** at most a retrospective rate-forecast pilot; not PIT, not a verified macro trading strategy, and not equity alpha.

## 13. Reproduction

From a clean checkout: `python -m pip install -r requirements.txt`; `OPENBLAS_NUM_THREADS=1 python run_analysis.py`; `OPENBLAS_NUM_THREADS=1 python -m pytest -q tests`; `OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute research.ipynb --output /tmp/money_market_reexecuted.ipynb --ExecutePreprocessor.timeout=900`. From repository root also run `python scripts/validate_studies.py`. Raw data and derived panels are frozen; all random draws use explicit seeds. Numerical results and diagnostic figures are committed, and the notebook regenerates the analysis when executed. Python package version, output hashes and logs are recorded in `logs/`.

## 14. Next-Stage Protocol

To move toward a valid prospective test: (1) obtain ALFRED CPI/UNRATE/GDP vintages and archived H.15 observation/release dates; (2) reconstruct exact formation-time information sets and benchmark revisions; (3) replace quarterly historical data with monthly/daily real-time policy expectations, yield curves and auction calendars; (4) evaluate actual bill or futures **total returns** net of costs and funding against duration-neutral benchmarks; (5) preregister specifications, reserve a post-2009 untouched holdout and correct for multiple testing. No alpha claim until these steps are complete.

## 15. Sources & Artifacts

**A (official):** Federal Reserve H.15/TB3MS https://fred.stlouisfed.org/series/TB3MS; BLS CPI https://fred.stlouisfed.org/series/CPIAUCSL; BLS unemployment https://fred.stlouisfed.org/series/UNRATE; BEA GDP https://fred.stlouisfed.org/series/GDPC1; Treasury bills https://www.treasurydirect.gov/research-center/history-of-marketable-securities/bills/t-bills-faqs/. **B (prior theory):** Mishkin (1991), https://www.nber.org/papers/w3632. **B (frozen compilation):** statsmodels macrodata https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/macrodata/macrodata.csv (original FRED/BLS access 2009-12-15; package source notes https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/macrodata/data.py). **Artifacts:** `data/source_register.csv`, `data/provenance_audit.md`, frozen raw/derived CSV, `results/` computed tables and diagnostics, `figures/` 10 plots, `tests/`, `logs/`. Original publication dates and per-quarter vintages remain UNKNOWN.

