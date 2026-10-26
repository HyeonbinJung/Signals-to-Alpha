# Textile-Mill Gap → U.S. Apparel & Leather Manufacturing

**2026-10-26 retrospective G.17 macro-factor falsification · NOT PIT · NOT EQUITY ALPHA**

## 01. Abstract

**Research question.** Does upstream U.S. textile-and-product-mill output growth relative to aggregate manufacturing anticipate U.S. apparel-and-leather manufacturing output beyond the latter's own momentum and the aggregate manufacturing cycle?

**Design.** Three monthly seasonally adjusted Federal Reserve G.17 production indexes (2017=100) cover **201 months, 2010-01 through 2026-09**. A frozen 2026-10-26 third-party redistribution is cross-checked against the Federal Reserve's October 16, 2026 release table for the latest dates. With a conservative *assumed* two-month availability buffer, **111** expanding-window, label-purged forecasts assess the 6-month-ahead endpoint (eight months of growth from the last known index).

**Primary result.** Textile-gap augmentation produces **9.507 pp** RMSE, worse than the macro control (**9.280 pp**) and historical mean (**8.568 pp**). The paired moving-block bootstrap 95% interval for control-minus-full improvement is **[-0.490, -0.046] pp**. **Verdict: negative retrospective macro-industry falsification; no verified PIT or equity alpha.**

## 02. Research Design & Hypotheses

**H1 — incremental forecast.** A fixed textile-minus-manufacturing output-growth signal improves next-six-month apparel/leather production forecasts versus own-output autoregression and manufacturing controls. **Null:** no positive paired OOS RMSE improvement.

**H2 — transmission.** Domestic textile inputs may precede apparel cutting, assembly, and downstream orders. **Counterthesis:** imported textiles and offshore garment assembly dominate, so U.S. textile output may be disconnected from domestic apparel/leather production; the apparel-and-leather category also includes leather products not sourced from textile mills.

**H3 — stability.** Any incremental gain survives 3-/9-month horizons, 3-month reporting buffer, 72-month rolling training, 2020–21 exclusion, stale-input ablation, 1,000 weight perturbations and leave-one-calendar-year-out. The factor, target and primary OOS benchmark were fixed before examining the result. This is predictive association, not causal identification, and no untouched final holdout exists.

## 03. Industry Context

**Industry scope.** NAICS 313–314 (textile and textile-product mills) provides possible fabrics, yarns and industrial textiles; NAICS 315–316 (apparel and leather products) is the downstream manufacturing target. These Federal Reserve aggregates are broader than an apparel supply-chain bill of materials. They do **not** measure U.S. clothing consumption, retail prices, import volumes, fashion brand revenue, or global sourcing.

**Measured context, not a market-size estimate.** In the frozen snapshot, textile output falls from 111.3861 (2010-01) to 75.2310 (2026-09), and apparel/leather output from 136.4047 to 79.4959 (2017=100). These are industrial indexes, not sales dollars or market capitalization. U.S. apparel manufacturing's offshoring, global textile imports, inventory timing, product mix, and labor intensity can defeat a simple domestic upstream proxy. The study makes **no unverified market-size/CAGR assertion**.

**Economic alternative.** A shared macro downturn can cause both sectors to move without any causal lead. Aggregate manufacturing contains some of the same underlying industry components, creating possible mechanical overlap.

## 04. Data & Source Integrity

**Data lineage.** The original publisher is the Federal Reserve Board, G.17; the exact numeric history used here is frozen from the public GitHub mirror `rektosaure/financial-dataset`, commit `21323f93cece664b4e052213b0a78a38e1c22b4b` dated **2026-10-26 17:00:15 UTC**. Its `macro-us/usa_industrial_production.csv` provides all 201 monthly values for each of `IPG313A4S`, `IPG315A6S`, and `IPMAN`; frozen extract SHA-256 **`e468485f066f10711bb20d5dead47f44e4edf03a1d33d15fa59eacb6046a0f30`**. The GitHub mirror is **grade B for exact numeric provenance**, not falsely labeled an official direct FRED download. Official G.17/FRED metadata and September/ August 2026 values are grade A.

**Independent latest-date cross-check.** The official September 2026 FRED G.17 release table reports textile 75.2310, apparel/leather 79.4959, and manufacturing (NAICS) 99.4361, matching the frozen mirror exactly; August 2026 also matches (75.6765, 79.3947, 99.1776). **Historical 2010–2025 row-by-row independent reconciliation remains UNVERIFIED.** Series are seasonally adjusted, monthly, index 2017=100; G.17 is revisable.

The source register distinguishes publication date, observation date, retrieval date, known source type, grade, and unknown historical vintages. No imputed or synthetic observations enter the panel.

## 05. Point-in-Time Availability

**Not PIT.** The Federal Reserve released September 2026 industrial production on **2026-10-16 at 09:15 EDT**, with future monthly updates and occasional annual revisions. The 2010–2026 series in the frozen mirror is a **single latest-revised history**, not 201 different as-of historical releases. The original publication timestamp for every old observation and historical revisions are **UNKNOWN**.

**Conservative lag assumption.** At forecast origin month *t*, all features use only the snapshot values dated *t−2* or earlier; the earliest training label from origin *u* is admitted only if *u+6+2 ≤ t*. This models a two-month availability and target-maturation buffer. **A fixed lag does not repair historical revisions** or prove exact publication availability; the walk-forward is retrospective and not executable in real time.

No investor could trade a contemporaneous security strategy from these revised index values without historical ALFRED/G.17 vintages, security mapping and a release-time execution model.

## 06. Factor Construction

Let \(T_t\) be the textile-and-product-mill index, \(A_t\) the apparel-and-leather index and \(M_t\) the manufacturing index. At forecast origin \(t\), the last presumed available observation is \(t-2\). For any series \(X\), define \(g^X_t=100[\ln(X_{t-2})-\ln(X_{t-14})]\) (12-month log growth in percentage points).

**Predefined factor:** \(F_t=\tanh((g^T_t-g^M_t)/10)\). The scale 10 pp and signed weights (+1 textile, −1 manufacturing) are fixed analyst choices, not fitted on full-sample returns. Positive \(F_t\) means textile production has grown faster than broad manufacturing.

**Outcome:** \(Y_t=100[\ln(A_{t+6})-\ln(A_{t-2})]\). The target ends six months after origin, but spans **eight months** from the latest feature observation; it is not mislabeled a pure six-month growth rate. All models share identical forecast origins.

## 07. Exposure & Transmission

**Structural exposure, not firm exposure.** Textile/product mills (313–314) → yarns/fabrics/intermediate inputs → some apparel/leather manufacturers (315–316). The index-level fixed exposure is +1 to textile YoY and −1 to aggregate manufacturing YoY. These are not audited input-output coefficients or issuer revenue weights; their uncertainty is explicitly assessed by 1,000 independent draws with each weight in [0.5,1.5].

**Key mismatch.** Leather products may use non-textile materials; most apparel consumed in the U.S. may be manufactured overseas. The domestic upstream and downstream series can be jointly driven by cyclical inventory decisions rather than physical intermediate demand.

**No company panel.** Contemporary issuer-to-industry exposures, segment sales, supply-chain purchases, ticker survivorship lists and adjusted total returns are absent. Leave-one-company-out, fundamental Rank IC, equity Rank IC and long-short spread are **not applicable**, rather than silently replaced with an industry-level test. A leave-one-year-out diagnostic is provided instead.

## 08. Outcomes & Baselines

**Five baselines.** (1) matured training-target mean; (2) apparel YoY and 3-month own-output momentum; (3) momentum plus manufacturing YoY; (4) macro controls plus the textile gap (primary challenger); (5) gap-only. Fixed Ridge α=20, intercept unpenalized, and z-scores estimated **within each matured training fold** only.

**Purged expanding window.** Starting 2017-01, at origin *t* fit on at least 48 labels whose origins satisfy *u+8≤t*, then forecast *Y_t*. All models use the same 111 origins through 2026-03. Scoring: RMSE and MAE in percentage points, paired OOS error differences; overlapping eight-month targets make IID inference invalid.

**Claim separation.** These are forecasts of a production index, not issuer earnings, adjusted equity total returns, benchmark-relative alpha, Sharpe, portfolio turnover, transaction costs or capacity. All security-return metrics are intentionally omitted.

## 09. Empirical Findings

| Model | OOS RMSE (pp) | MAE (pp) |
|:--|--:|--:|
| Historical mean | 8.568 | 5.756 |
| Apparel persistence | 8.889 | 6.326 |
| Persistence + manufacturing | 9.280 | 6.766 |
| **Macro + textile gap** | **9.507** | **7.048** |
| Textile gap only | 8.680 | 5.875 |

The primary macro-minus-augmented RMSE difference is **-0.227 pp** (negative means adding textiles is worse). The historical mean is the strongest tested forecast and outperforms the full model by **0.939 pp**. There are **111 overlapping forecast origins**, not 111 independent trials. The target's pandemic shock generates large losses; report absolute error scales rather than presenting a return or Sharpe chart. Exact row-level forecasts are in `results/oos_forecasts.csv`.

## 10. Robustness & Placebos

**Block placebo.** Shuffle non-overlapping 12-month blocks of the factor and refit the entire expanding-window full model **1,000 times**, keeping targets and controls fixed. The exploratory one-sided tail fraction for null improvements ≥ actual is **0.855**. This is **not** a valid exact randomization p-value: nonstationarity, temporal dependence and the short terminal block violate exchangeability assumptions.

**Paired uncertainty.** Resample 12-month circular blocks of the saved paired OOS squared errors **2,000 times**. The percentile 95% interval for control-minus-full RMSE is **[-0.490, -0.046] pp**, negative throughout. This conditions on already-fitted forecasts; it does not rerun full training inside each bootstrap and cannot fix vintage leakage.

**Weight sensitivity.** Draw 1,000 textile/manufacturing weight pairs independently from [0.5,1.5], refit full OOS for each. Positive-gain fraction = **0.000**, central 95% interval **[-0.255, -0.140] pp**. This is robustness to analyst priors, not firm input exposure.

**Further falsifications.** Alternate 3-/9-month targets, 3-month release buffer, stale textile growth and 72-month rolling training are saved; leave-one-calendar-year-out reports the impact of each OOS year. All robustness checks are exploratory, not multiple-testing-adjusted discoveries.

## 11. Regime Sensitivity

- **pre_2020**: n=36, macro-minus-full ΔRMSE=0.000 pp.
- **pandemic_2020_21**: n=24, macro-minus-full ΔRMSE=-0.281 pp.
- **post_2022**: n=51, macro-minus-full ΔRMSE=-0.447 pp.
- **excluding_2020_21**: n=87, macro-minus-full ΔRMSE=-0.215 pp.

The 2020–2021 shock is especially relevant because both industries experienced shutdowns and unusual restocking. A nominally positive pre-2020 split is not enough to establish a stable lead; other regime signs and alternative model settings must be read together. The leave-one-year-out diagnostics avoid hiding a single exceptional period but cannot establish a new out-of-sample sample after model choice.

**Alternate horizons and buffers:**
- horizon_3m: n=114, ΔRMSE=-0.204 pp.
- horizon_9m: n=108, ΔRMSE=-0.104 pp.
- lag_3m: n=111, ΔRMSE=-0.207 pp.
- stale_textile_12m: n=111, ΔRMSE=-0.134 pp.
- rolling_72m: n=111, ΔRMSE=-0.204 pp.

## 12. Bias Audit & Verdict

**Bias register.** (i) **Historical-vintage leakage: HIGH** — revised 2026 snapshot, no ALFRED as-of panel. (ii) **Sector selection: HIGH** — economic chain selected ex post, no untouched final holdout. (iii) **Imported inputs and composition: HIGH** — textiles are not a contemporaneous firm procurement map, leather is mixed into the target. (iv) **Overlap/serial dependence: HIGH** — 8-month label windows overlap; 12-month block diagnostics are approximations. (v) **Mechanical controls: MEDIUM** — manufacturing index includes both studied sectors. (vi) **Multiple testing: MEDIUM** — five models and multiple sensitivity windows explored; no false-discovery adjustment. (vii) **Transaction costs/capacity: NOT APPLICABLE** — no investable strategy or security returns.

**Verdict.** This particular textile-output gap does **not** improve the primary macro control or simple historical mean for apparel/leather output. The result falsifies a narrow retrospective index-level predictive claim, not the commercial potential of apparel, domestic reshoring or textile suppliers. **Status: REPRODUCED RETROSPECTIVE MACRO PILOT / NOT PIT / NO EQUITY ALPHA.**

## 13. Reproduction

From a clean checkout in this directory:

```bash
python -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python run_analysis.py
OPENBLAS_NUM_THREADS=1 python make_figures.py
OPENBLAS_NUM_THREADS=1 python -m pytest tests -q
OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute research.ipynb --output reexecuted.ipynb
# from repository root:
python scripts/validate_studies.py
```

`run_analysis.py` computes the 1,000 block-shuffle refits, 2,000 block-bootstrap draws and 1,000 weight perturbations with deterministic seeds; `make_figures.py` regenerates eight actual-data SVGs. The frozen CSV and its SHA-256 (`e468485f066f10711bb20d5dead47f44e4edf03a1d33d15fa59eacb6046a0f30`) are supplied; no API key is needed. Saved `results/execution.log` and `results/notebook_execution.log` document observed local runs. The repository-wide structural check **does not prove** historical PIT validity or numerical alpha.

## 14. Next-Stage Protocol

**Stage 1: true PIT.** Obtain archived as-published Federal Reserve G.17 tables or ALFRED series for each forecast origin, preserving release timestamps, revisions, rebasing and data-access lag; rerun strictly on vintage-specific histories.

**Stage 2: real textile/apparel supply chain.** Build a dated import share and intermediate-input crosswalk using Census trade flows, Bureau of Economic Analysis input-output tables and company filings; separate leather from textiles and domestic from foreign production.

**Stage 3: independent fundamentals.** Pre-register an issuer universe, link historical segment revenues to supply exposure with SEC filing acceptance dates, and test sales/EPS growth independent of the macro target. Explicitly include delisted companies.

**Stage 4: investability.** Only after fundamentals work, test dividend/split-adjusted total returns versus a sector benchmark with formation-day release times, trading costs, liquidity and a sealed future holdout. Until then, no stock-picking alpha, Sharpe or backtested portfolio is claimed.

## 15. Sources & Artifacts

**Grade A original publisher:** [Federal Reserve G.17 release, 2026-10-16](https://www.federalreserve.gov/releases/g17/20261016/g17.pdf), [official release calendar](https://www.federalreserve.gov/releases/g17/), and [FRED September 2026 official industry table](https://fred.stlouisfed.org/release/tables?eid=49745&rid=13); individual series [IPG313A4S](https://fred.stlouisfed.org/series/IPG313A4S), [IPG315A6S](https://fred.stlouisfed.org/series/IPG315A6S), [IPMAN](https://fred.stlouisfed.org/series/IPMAN).

**Grade B frozen numeric distributor:** [public GitHub industrial production CSV at fixed 2026-10-26 commit](https://github.com/rektosaure/financial-dataset/blob/21323f93cece664b4e052213b0a78a38e1c22b4b/macro-us/usa_industrial_production.csv). The source file is a redistribution, not original publication vintages; historical 2010–2025 source-row audit remains incomplete.

**Artifacts:** `data/frozen_g17_2010_2026.csv`, `data/source_register.csv`, `data/source_qa.md`, `data/derived_panel.csv`, `results/metrics.json`, `results/oos_forecasts.csv`, 1,000/2,000/1,000 simulation CSVs, eight computed `figures/*.svg`, `run_analysis.py`, `make_figures.py`, `tests/test_analysis.py`, `research.ipynb` and execution logs. All code and data are research-only, not investment advice.
