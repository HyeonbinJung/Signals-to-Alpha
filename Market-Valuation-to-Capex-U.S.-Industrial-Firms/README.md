# Market Valuation → Corporate Capital Investment — Historical U.S. Industrial Firms

**Status: REPRODUCED RETROSPECTIVE FIRM-FUNDAMENTALS PILOT (NOT PIT; NO EQUITY ALPHA).** Frozen 11-firm Grunfeld sample, 1935–1954; study prepared 2026-10-27. The model is tested on observed gross corporate investment, not security returns. This study is a new cross-industry industrial corporate-investment outcome, distinct from the repository's modern industry-production pilots; its historical scope prevents present-day market claims.

## 01. Abstract

**Research question:** Does a lagged valuation-to-capital proxy add predictive information for annual gross investment across 11 selected U.S. industrial firms after controlling for capital stock, prior investment and investment momentum? In **110** firm-year predictions (1945–1954), augmented Ridge achieved **0.2616** log-unit RMSE versus **0.2929** for the controls, a gain of **0.0313**. However, simple investment persistence achieved **0.2544**, better than the augmented model, and the historical data are not point-in-time vintages. **Verdict:** a limited retrospective fundamental-prediction pilot; not a reliable modern industrial alpha or investable stock-return signal.

## 02. Research Design & Hypotheses

**H1:** a lagged market-to-capital proxy reduces investment forecast RMSE against fixed firm-effect, capital and investment controls. **H2:** the signal predicts the cross-firm rank of investment residuals within each test year. **H3:** any gain survives company exclusions, proxy scaling, historical source correction and alternative feature lags. The primary loss is squared log-investment error; positive ΔRMSE = RMSE(control) − RMSE(full) favors the factor. No post-hoc parameter search was conducted; this is a retrospective pilot, not prospective preregistration.

## 03. Industry Context

The Grunfeld panel contains 11 named historical firms across metals, automotive, petroleum, electrical equipment, business machines, tires and consumer materials. Capital investment adds to productive plant/equipment, while market value may proxy for expected investment opportunities; the connection is neither mechanically guaranteed nor structurally causal. Financing frictions may alter investment responses (Fazzari, Hubbard & Petersen 1987, NBER 2387), but this later theory is interpretive and cannot authenticate the 1935–1954 release history. The selected companies do **not** represent a survivorship-free or modern manufacturing universe.

## 04. Data & Source Integrity

Frozen raw input: `data/grunfeld_statsmodels_0_14_6_frozen.csv` (220 observations = 11 firms × 20 years, 1935–1954, 1947-dollar units). Package source: `statsmodels.datasets.grunfeld` 0.14.6; original Grunfeld 1958 dissertation is **attributed but not independently inspected**; Kleiber & Zeileis 2010 document multiple versions. **Important discrepancy:** US Steel 1946 `capital` is **132.6** in this frozen statsmodels file versus **232.6** identified as corrected in CRAN AER documentation; the main dataset is never silently altered, and the correction is sensitivity-tested. `data/source_register.csv` grades provenance A/B/C and records exact URLs, known/UNKNOWN publication dates, observation periods, version and revision limitations; `data/raw_sha256.txt` freezes bytes.

## 05. Point-in-Time Availability

For target year t, all predictors come from **t−1**, with conceptual formation in June t to allow for some `value` observations that average December t−1 and January t. Model training targets stop at **t−2** (one-year embargo) and feature scaling is train-only. Original report filing dates and historical public availability for `invest`, `capital` and `value` are **UNKNOWN**. The 1958/2010 reconstructed dataset is an ex-post source, not historical release-vintage data: **PIT NOT VERIFIED** even with conservative mechanical lags.

## 06. Factor Construction

The company-specific proxy is `q_proxy_{i,t} = log(value_{i,t−1} / capital_{i,t−1})`; it is **not Tobin's marginal q**. Target `y_{i,t} = log(invest_{i,t})` uses actual observed investment in 1947-dollar millions. Control features are `log(invest_{i,t−1})`, `log(capital_{i,t−1})`, `log(invest_{i,t−1}/invest_{i,t−2})` and fixed firm indicators; full Ridge adds `q_proxy` with frozen α=12. No feature, firm dummy or scaler is fitted on future target years.

## 07. Exposure & Transmission

Each firm has **unit exposure to its own observed valuation-to-capital proxy**; there are no invented category sales weights or industry allocation fractions. `data/company_exposure_map.csv` contains researcher-inferred descriptive company groups (grade C, as-of 2026-10-27) with `quantitative_revenue_weight=UNKNOWN`; the groups do not enter the factor. The proposed transmission is valuation → expected profitability/financing → investment budgeting → realized gross capex. The 1,000-draw ±20% firm-specific factor-scaling experiment is a measurement-sensitivity check, not a historical segment-weight validation.

## 08. Outcomes & Baselines

**Independent firm-level outcome:** gross real investment; no macro industrial-production index is used as the target. Identical **110** purged expanding-window OOS firm-years, 1945–1954, minimum **77** training observations, 11 firms per year. Benchmarks: historical firm-specific training mean, lagged investment persistence, and multivariate controls. Log RMSE and MAE are primary; level RMSE in millions of 1947 dollars is also archived. The dataset contains **no issuer total returns, delisting returns, sector benchmark returns or transaction costs**, so equity IC/long–short spread cannot be computed.

## 09. Empirical Findings

| Model | OOS log RMSE | OOS log MAE | N |
|---|---:|---:|---:|
| historical_mean | 0.5358 | 0.4520 | 110 |
| persistence | 0.2544 | 0.1990 | 110 |
| control | 0.2929 | 0.2226 | 110 |
| full | 0.2616 | 0.2029 | 110 |


Incremental control-model gain is **0.0313 log RMSE**, but the augmented model **does not beat persistence** (0.2544). Mean within-year **fundamental residual** Spearman rank IC is **0.518**, and top-three-minus-bottom-three realized **investment residual** spread is **0.344 log units**. Exploratory 2,000-draw paired year-block uncertainty intervals are **[0.396, 0.632]** for mean fundamental rank IC and **[0.251, 0.490]** for mean investment residual spread; with only 10 year clusters these intervals are not population-wide guarantees. These are *not* security-return IC or tradable portfolio spreads. Figures 01–05 and 10 show original company trajectories, proxy scatter, baseline scorecard, year-level errors, paired loss accumulation and fundamental rank diagnostics.

## 10. Robustness & Placebos

- **1,000** within-firm three-year block-shuffle refits: exploratory upper-tail fraction **0.0030**, **not** an exact randomization p-value because time-block exchangeability is unproven.
- **2,000** paired two-year circular year-block bootstrap draws (cross-firm dependence retained): 95% interval for control-minus-full RMSE **[0.0112, 0.0488]**.
- **1,000** firm-specific ±20% factor scaling refits: positive-gain fraction **1.000**.
- **11** leave-one-company-out refits: observed gain range **[0.0164, 0.0409]**, with 100 held-in OOS firm-years each. These tests do not create a new historical universe.
- `results/robustness_scenarios.csv` includes factor lag 1/2/3 years, 1945–1949 vs 1950–1954, source-version correction and control ablations. No false precision or exact permutation significance is asserted.

## 11. Regime Sensitivity

The 1945–1949 RMSE gain is **0.0428** and 1950–1954 gain **0.0174**, each based on only 55 firm-years (five effective calendar-year clusters). Feature-lag-2 gain is **0.0334** and lag-3 gain **0.0335**; changing the US Steel 1946 capital value to the documented 232.6 yields **0.0312**. Dropping the capital control changes the gain to **-0.0021**, highlighting model-specification dependence. The postwar context and small year-cluster count severely limit extrapolation.

## 12. Bias Audit & Verdict

**Lookahead/revisions:** historic publication vintages unavailable; a reconstructed source cannot establish PIT. **Selection/survivorship:** 11 historically selected firms, no contemporaneous full industrial universe. **Mechanical factor overlap:** capital appears in q-proxy denominator and controls; ablation can change conclusions. **Multiple testing:** exploratory scenario family is not familywise-adjusted. **Regime/structural break:** wartime-to-postwar industrial change. **Market frictions:** no adjusted total returns, corporate actions, delisting histories, turnover, costs, or capacity. **Verdict: REPRODUCED RETROSPECTIVE FIRM-FUNDAMENTALS PILOT; no validated PIT signal and no investable equity alpha.**

## 13. Reproduction

From a fresh study directory with Python and dependencies: `python -m pip install -r requirements.txt`, then `python run_analysis.py` (full 1,000 + 2,000 + 1,000 repetitions), `python rank_uncertainty.py`, `python make_figures.py`, `python -m pytest -q tests`, and `jupyter nbconvert --to notebook --execute --inplace research.ipynb` (or equivalent `nbclient`). `research.ipynb` contains **saved executed output tables and figures**, re-fits core OOS predictions, and reads the frozen full-draw resampling tables rather than repeating 4,000 refits. `logs/` stores independent run and test evidence; GitHub layout CI is structural only, not a substitute for numerical reproduction.

## 14. Next-Stage Protocol

For a modern, genuinely tradable follow-up, predeclare a historically complete industrial issuer universe and collect SEC 10-K/10-Q capex/plant assets with original filing timestamps, dated capital-structure/market-value snapshots and independently sourced security total returns including delistings. Rebuild q-like proxies at each formation date, test quarterly expanding/rolling purged OOS with sector/size/momentum baselines, reserve a final holdout, adjust for multiple testing, and estimate realistic trading frictions and capacity. Do not claim current investability from 1935–1954 Grunfeld data.

## 15. Sources & Artifacts

- Grunfeld dataset (statsmodels package documentation, version 0.14.6 frozen): https://www.statsmodels.org/v0.12.2/datasets/generated/grunfeld.html
- Source implementation: https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/grunfeld/data.py
- Independent data discrepancy documentation: https://search.r-project.org/CRAN/refmans/AER/html/Grunfeld.html
- Kleiber & Zeileis (2010), *The Grunfeld Data at 50*: https://www.zeileis.org/papers/Kleiber%2BZeileis-2010.pdf
- Fazzari, Hubbard & Petersen (1987), *Financing Constraints and Corporate Investment*: https://www.nber.org/papers/w2387
- Local files: `study.json`, `data/source_register.csv`, `data/company_exposure_map.csv`, frozen raw/derived CSV, `analysis.py`, `run_analysis.py`, `make_figures.py`, `requirements.txt`, `tests/test_analysis.py`, `results/*.csv`, `results/summary.json`, `figures/*.svg`, `research.ipynb`, `logs/`.
