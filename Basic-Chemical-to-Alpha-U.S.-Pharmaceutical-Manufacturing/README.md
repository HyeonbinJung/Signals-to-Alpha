# Basic-Chemical-to-Pharma — U.S. Pharmaceutical Manufacturing

**Retrospective macro-factor falsification · 2026-10-26 · NO POINT-IN-TIME OR EQUITY ALPHA CLAIM**

## 01. Abstract

**Research question.** Does basic-chemical manufacturing output growth relative to aggregate manufacturing anticipate future U.S. pharmaceutical/medicine production beyond pharmaceutical persistence and the general manufacturing cycle?

**Design.** Three Federal Reserve G.17 industrial-production series, observed monthly from 2010-01 to 2026-09 (**201 months**), are frozen from the 2026-10-26 FRED CSV retrieval. At forecast origin *t*, all inputs are lagged two months, and the outcome is the log change in pharmaceutical output from *t−2* through *t+6*. An expanding-window, 8-month-purged forecast comparison scores **111 OOS origins**, 2017-01-01–2026-03-01.

**Result.** Basic-chemical augmentation raises RMSE from **3.953** to **4.104** percentage points (macro minus full = **-0.151 pp**); a 2,000-draw 12-month moving-block bootstrap interval is **[-0.504, 0.189] pp**. The 1,000-refit exploratory block-shuffle tail fraction is **0.925**. **Verdict: negative retrospective macro-factor pilot; no verified point-in-time or equity alpha.**

## 02. Research Design & Hypotheses

**H1 (incremental predictive value):** an ex-ante fixed basic-chemical-vs-manufacturing gap improves 6-month pharmaceutical-output forecasts relative to pharmaceutical autoregression plus manufacturing growth. **Null H1:** no paired OOS RMSE improvement.

**H2 (mechanism):** an upstream basic-chemical supply/demand cycle propagates into downstream drug manufacturing with a multi-month lag; this is only a hypothesis, not proof of a company-specific chemical input bill. **Null H2:** upstream movement is macro noise or demand driven, not a lead.

**H3 (stability):** improvement remains directionally positive across forecast horizons, release buffers, pandemic regimes, 72-month rolling training, stale-factor ablation and plausible exposure weights. **Null H3:** the effect is unstable or reverses.

The tests are **predictive**, not causal. There is no clean holdout reserved after selecting this industry and factor, so reported robustness is exploratory. A negative finding is an acceptable endpoint.

## 03. Industry Context

**Scope.** U.S. pharmaceutical and medicine manufacturing (NAICS 3254) and basic chemical manufacturing (NAICS 3251) are separate Federal Reserve G.17 output aggregates. The proposed chain is chemical intermediates/inputs → drug synthesis/formulation → pharmaceutical production. This aggregation also captures products unrelated to pharmaceuticals, creating substantial signal dilution.

**Growth context, not a forecast.** In the frozen G.17 snapshot, pharmaceutical output moves from 119.6808 in January 2010 to 124.2706 in September 2026, while basic-chemical output moves from 99.3774 to 91.2835 (both 2017=100 indexes). These are historical index endpoints, not annual market-size estimates or investable revenue. Product demand, patent cliffs, generic penetration, biologics and overseas production may dominate any domestic upstream relationship. No unverified market-size/CAGR figures are asserted.

**Counterthesis.** Modern biologic manufacturing is not proportional to broad U.S. basic-chemical production. Global procurement and contract manufacturing can disconnect domestic industry indexes; aggregate manufacturing can also subsume both series mechanically.

## 04. Data & Source Integrity

All **201 × 3** index values come from the Federal Reserve Board's G.17 release as distributed through the public FRED CSV graph endpoints. Frozen raw input: `data/official_snapshot.csv` (2010-01–2026-09); SHA-256 **`472fcd3f515a862a98a5f13b4005262ee6b6716548d7cd5b42155ad03483e5f8`**. The three original series are `IPG3254S` (pharma), `IPG3251S` (basic chemicals), `IPMAN` (aggregate manufacturing), each seasonally adjusted and indexed to 2017=100.

The FRED pages show September 2026 observations updated **2026-10-16**; extraction date is **2026-10-26**. Data were copied from machine-readable CSV and cross-checked against source record count, column sums and squared sums; the frozen snapshot is supplied for independent reproduction. `data/source_register.csv` contains publisher, exact URLs, dates, grade, units, revision policy and unknown fields.

**Source hierarchy:** A = Federal Reserve original statistics and calendar; B = institutional third-party series (not used); C = press or anecdotal commentary (not used). No synthetic observations or privately restricted data are used.

## 05. Point-in-Time Availability

**Critical failure of the strict PIT gate.** This is a **2026-10-26 revised historical snapshot**, not a reconstruction of what investors actually knew in 2010–2026. Historical source publication timestamps and original vintages for every individual observation are **UNKNOWN**. The G.17 release calendar confirms a monthly schedule and the 2026-10-16 release, but does not prove older revised values were known at their forecast origins.

For an origin at month-end *t*, the design only uses index observations through *t−2*, deliberately leaving a two-month publication buffer. Training labels for origin *u* enter the model only when *u+6+2 ≤ t*. **Neither safeguard cures revisions/backfills**: a proper PIT implementation requires ALFRED or original G.17 archive vintages and as-of timestamps, which were not retrieved.

**Verdict for this gate:** retrospective association/falsification only. No executable signal date, price formation or trade timing is claimed.

## 06. Factor Construction

Let \(P_t\) be pharmaceutical output, \(C_t\) basic-chemical output, and \(M_t\) aggregate manufacturing, all strictly positive seasonally adjusted indexes. Define lagged 12-month log growth \(g^X_t=100[\log X_{t-2}-\log X_{t-14}]\). The fixed factor is

\[F_t=\tanh\{[g^C_t-g^M_t]/10\}.\]

The 10-percentage-point scale is **fixed**, not tuned on the target. A positive value means upstream chemicals have grown faster than manufacturing. The outcome is \(Y_t=100[\log P_{t+6}-\log P_{t-2}]\), an **eight-month interval** from the latest presumed available observation to the six-month-forward endpoint; do not mislabel this as a pure six-month growth rate. All models use the same origins and target.

The factor is neither a company revenue exposure nor a security-return forecast. Manufacturing contains chemical/pharma industries; shared components can create mechanical correlation.

## 07. Exposure & Transmission

**Industry exposure mapping (qualitative, not a company panel):** chemical manufacturers (NAICS 3251) → possible feedstocks and intermediates → pharmaceutical manufacturers (NAICS 3254). The exposure proxy is a **fixed weight +1.0** on basic-chemical YoY growth and **−1.0** on manufacturing YoY growth. This is an analyst prior and **not** a reported drug-industry chemical cost share.

Exposure perturbation draws 1,000 independent weight pairs uniformly over [0.5, 1.5] and re-runs the complete expanding OOS comparison. No company security identifiers, historical constituent list, firm filings or chemical procurement matrices were acquired. Consequently, **leave-one-company-out, firm revenue lead and equity IC/long-short tests are not applicable and not claimed**. Future research must first construct a contemporaneous manufacturer-to-input mapping from filings.

## 08. Outcomes & Baselines

**Target:** 100 × log pharmaceutical output at *t+6* divided by output at *t−2*. **Models:** (i) training-sample historical mean, (ii) pharma 12-month and 3-month growth persistence Ridge, (iii) persistence plus aggregate manufacturing YoY Ridge, (iv) same controls plus the fixed upstream factor, (v) gap-only Ridge. Ridge α=20 is fixed before analysis; feature means/standard deviations are estimated **only on matured training labels**, and intercept is unpenalized.

**OOS protocol:** origins 2017-01 through 2026-03, expanding training with minimum 48 matured observations; for each origin *t*, only training rows with *u+8≤t* are eligible. All OOS rows have the same realized target. Scores are RMSE and MAE in percentage points. No stock benchmark, Sharpe, IC, long-short returns, costs or capacity are available.

## 09. Empirical Findings

| Model | OOS RMSE (pp) | MAE (pp) |
|:--|--:|--:|
| Historical mean | 4.347 | 3.793 |
| Pharma persistence | 4.451 | 3.898 |
| Pharma + manufacturing macro | **3.953** | **3.444** |
| Macro + upstream factor | 4.104 | 3.479 |
| Upstream factor only | 4.519 | 3.815 |

The predeclared challenger **loses 0.151 pp of RMSE** versus its macro control across **111** overlapping monthly OOS forecasts. The macro baseline is also better than the historical mean and own-output persistence in this fixed snapshot. Because the target spans overlapping eight-month intervals, 111 forecast origins do not represent 111 independent trials; naive iid t-tests would be misleading. Saved row-level predictions and errors are in `results/oos_forecasts.csv`.

## 10. Robustness & Placebos

**Alignment placebo:** 1,000 complete refits after shuffling non-overlapping 12-month blocks of the factor (the final block may be shorter); one-sided exploratory fraction of placebo improvements ≥ observed = **0.925**. This is **not** an exact exchangeability-based p-value, because blocks are dependent and the null distribution is not guaranteed.

**Uncertainty:** 2,000 circular moving-block bootstrap resamples of the paired OOS forecast-loss rows (block=12 months) yield 95% percentile interval **[-0.504, 0.189] pp** for macro RMSE minus augmented RMSE, including zero. This conditions on already-fitted forecasts and does not re-estimate the full model in each bootstrap.

**Exposure perturbation:** 1,000 weight pairs in [0.5,1.5] each; positive-improvement fraction = **0.000**, central 95% range **[-0.154, -0.124] pp**. This tests chosen prior weights, not true firm exposure.

**Ablations:** a stale 12-month chemical factor, alternate 3-/9-month horizons, three-month publication buffer and 72-month rolling training are calculated and saved. They are sensitivity diagnostics, not separate discoveries.

## 11. Regime Sensitivity

| Evaluation regime | OOS n | Macro minus augmented RMSE (pp) |
|:--|--:|--:|
| Before 2020 | 36 | 0.031 |
| 2020–2021 | 24 | -0.342 |
| 2022 onward | 51 | -0.178 |
| Exclude 2020–2021 | 87 | -0.089 |

**Interpretation:** the small pre-pandemic positive result does not persist in the pandemic or post-pandemic segments. A 72-month rolling training window yields **0.177 pp** improvement, in conflict with the predeclared expanding design. This is model-instability evidence, not permission to switch the headline method after observing results.

| Robustness | OOS n | ΔRMSE (pp) |
|:--|--:|--:|
| horizon_3m | 114 | -0.148 |
| horizon_9m | 108 | -0.121 |
| lag_3m | 111 | -0.123 |
| stale_chemical_12m | 111 | -0.121 |
| rolling_72m | 111 | 0.177 |


## 12. Bias Audit & Verdict

**Publication/revision leakage: HIGH.** A current FRED history is not a collection of original monthly vintages; lagging by two months cannot cure retroactive index revisions. **Survivorship/selection: HIGH.** The three aggregates and the proposed economic mechanism were selected ex post; no systematic search log or untouched holdout exists. **Mechanical correlation: MEDIUM.** IPMAN includes parts of both studied industries. **Overlap/serial dependence: HIGH.** Eight-month target windows overlap; even 12-month blocks are only an approximation. **Multiple testing: MEDIUM.** Horizons, regimes and weight sensitivity are exploratory and not corrected for multiple comparisons. **Trading costs/capacity: NOT APPLICABLE** because there is no security-level strategy.

**Verdict:** the fixed chemical-production gap fails the primary macro baseline in retrospective OOS and is not a verified PIT, firm-fundamental or investable equity alpha. Its negative result is a falsification of this specific signal and target—not a claim that pharmaceuticals lack investment opportunities.

## 13. Reproduction

```bash
python -m pip install -r requirements.txt
python -m pytest tests -q
python compute_heavy.py           # deterministic 1,000 placebo / 1,000 sensitivity / 2,000 bootstrap
jupyter nbconvert --to notebook --execute research.ipynb --output reproduced.ipynb
```

No API key is required because `data/official_snapshot.csv` is frozen. `run_analysis.py` implements the formulas, purged walk-forward and all diagnostics; `compute_heavy.py` parallelizes the expensive refits with fixed seeds. The study's stored outputs were computed on 2026-10-26; `results/execution.log` records the full analysis. All published result values should be recomputed before extending the sample. Data SHA-256: `472fcd3f515a862a98a5f13b4005262ee6b6716548d7cd5b42155ad03483e5f8`.

## 14. Next-Stage Protocol

**Stage 1:** collect monthly as-published Federal Reserve G.17 industry tables/ALFRED vintages and verify the first available date for each series and revision; rerun on original vintage snapshots. **Stage 2:** replace broad chemical output with pharma-specific chemical intermediates and import/export volumes using a contemporaneous product-input crosswalk, without ex-post weight tuning. **Stage 3:** test independent firm fundamentals using SEC 10-K/10-Q filing acceptance timestamps, then separately evaluate a survivorship-free total-return universe after trading costs and sector-neutral controls. **Stage 4:** reserve a genuinely unseen holdout and preregister one primary horizon and null before examining it.

Until these stages succeed, classify the study as **REPRODUCED MACRO PILOT / NOT PIT / NO EQUITY ALPHA**. No future alpha forecast or Sharpe estimate is presented.

## 15. Sources & Artifacts

**Primary sources (A):** [Federal Reserve G.17 release and dated calendar](https://www.federalreserve.gov/releases/g17/); [IPG3254S pharmaceutical manufacturing](https://fred.stlouisfed.org/series/IPG3254S); [IPG3251S basic chemicals](https://fred.stlouisfed.org/series/IPG3251S); [IPMAN aggregate manufacturing](https://fred.stlouisfed.org/series/IPMAN). Raw CSV retrievals use `fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`. Historical observation-level publication vintages are **UNKNOWN**.

**Artifacts:** `study.json`, `data/source_register.csv`, `data/official_snapshot.csv`, `data/derived_panel.csv`, `run_analysis.py`, `compute_heavy.py`, `requirements.txt`, `tests/test_pharma.py`, `results/metrics.json`, `results/oos_forecasts.csv`, `results/placebo_1000.csv`, `results/bootstrap_2000.csv`, `results/exposure_1000.csv`, `results/execution.log`, and 8 independently computed SVG figures in `figures/`. `research.ipynb` is an executed narrative/computational record with saved tables and charts.
