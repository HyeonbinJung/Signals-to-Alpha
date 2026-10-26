# E-Commerce Share-to-Alpha — U.S. Warehousing and Logistics

**Status: REPRODUCED RETROSPECTIVE MACRO PILOT · NOT POINT-IN-TIME · NOT EQUITY ALPHA.**  
**Research freeze:** 26 October 2026. **Target:** U.S. warehousing-and-storage employment, not company revenue or tradable returns.

## 01. Abstract

**Research question:** Does the year-over-year acceleration in U.S. e-commerce's share of retail spending, observed with a one-quarter buffer, improve two-quarter-ahead forecasts of warehousing employment growth beyond employment persistence and aggregate payroll growth? In 57 purged expanding-window forecasts (2012Q1–2026Q1 origins), the e-commerce model produced **5.172 percentage-point RMSE** versus **5.869 pp** for the macro-control model, **5.360 pp** for warehouse persistence and **7.422 pp** for the historical mean. The 2,000-draw four-quarter block-bootstrap 95% interval for macro-minus-full RMSE was **[−1.486, 2.572] pp**, which includes zero. This is a **revised-data retrospective lead association**, not a historical-vintage or investment-alpha validation.

## 02. Research Design & Hypotheses

- **H1 (transmission):** an increase in the online retail share should anticipate labor requirements at fulfillment and storage sites, conditional on the existing labor trend.
- **H2 (incremental forecasting):** a predeclared, lagged e-commerce-share factor should lower expanding-window forecast error relative to both a historical mean and a lagged-warehouse-plus-national-payroll model.
- **H3 (robustness):** any improvement should be stable across horizons, additional reporting lags, pre/post-2020 regimes and a four-quarter block-shuffle falsification.
- **Null / failure:** if the factor fails a simpler persistence benchmark or uncertainty spans zero, it is not established as an independently useful forecasting signal.
- **Counterthesis:** logistics automation, on-site inventory efficiency, retailer in-house networks, retail compositional shifts and revisions can disconnect e-commerce share from warehouse jobs.

## 03. Industry Context

The U.S. Census Bureau's seasonally adjusted retail e-commerce share reached **17.1% in 2026Q2**, versus **16.3% in 2025Q2**; the underlying Q2 2026 report was released on **18 August 2026**. The BLS CES warehousing-and-storage employment series (NAICS 493) is a direct but incomplete labor-demand proxy: automated fulfillment can expand volumes without adding workers. Courier employment (NAICS 492) is a related channel rather than a genuinely unaffected negative-control sector. These series do **not** measure the value, profitability, investment or market capitalization of logistics providers.

## 04. Data & Source Integrity

The frozen input `data/fred_quarterly_snapshot_2026-10-26.csv` contains **107 quarterly dates** from 2000Q1–2026Q3; the e-commerce share is available through **2026Q2 (106 values)**. Four observed FRED series are used: `ECOMPCTSA` (Census, quarterly, seasonally adjusted percent), `CES4349300001` (BLS warehousing, seasonally adjusted thousands of workers), `CES4349200001` (BLS couriers, same units), and `PAYEMS` (BLS total payroll, same units). BLS monthly values were aggregated to quarter means using FRED graph CSV `fq=Quarterly&fam=avg`; no observations are simulated. `data/source_register.csv` records official URLs, as-of dates, quality A, units, revisions and **UNKNOWN** historical release timestamps; see `data/exposure_map.csv` for NAICS segment mappings. Original source CSV values were transcribed from public FRED graph responses, and the committed frozen file is the sole reproduction input.

## 05. Point-in-Time Availability

At quarter-**end** formation date *t*, use only information labeled quarter *t−1* or earlier; this deliberately allows a full-quarter buffer for the Census e-commerce release and BLS payroll series. Forecast target is the warehouse YoY log change at *t+2*. An origin *u* is eligible for model training at *t* only when **u+2+1 ≤ t**, so the label has matured with one further quarter's publication buffer. **This is not verified PIT**: revised FRED snapshots and later Census/BLS benchmark changes can leak future information even after these lags. Full release-date/vintage reconstruction through ALFRED and archived Census releases is a mandatory next step.

## 06. Factor Construction

Let `E(t)` be the Census e-commerce percentage of total retail, `W(t)` BLS warehouse employment and `P(t)` total payroll, all at quarterly frequency. The **fixed** factor is `F(t) = tanh([E(t−1) − E(t−5)] / 2)`; the denominator is an ex-ante two-percentage-point saturation scale, not a fitted normalization. Controls are `100 log[W(t−1)/W(t−5)]` and `100 log[P(t−1)/P(t−5)]`. Target is `Y(t)=100 log[W(t+2)/W(t−2)]`. Only training-window means and standard deviations are used for the ridge model (`alpha=10`, fixed), with no full-sample z-scores.

## 07. Exposure & Transmission

Primary exposure is **100% NAICS 493 warehousing-and-storage employment** (a segment-level outcome, not a security portfolio). A **scenario** mixes 50–100% NAICS 493 with 0–50% NAICS 492 courier employment and recomputes the entire forecast 1,000 times; this probes segment-definition sensitivity, not firm exposure estimation. Dated historical company revenue-share maps are **NOT AVAILABLE**. Accordingly, neither individual firm fundamentals nor securities' excess total returns are claimed or backtested. Retailer automation and non-retail warehouse demand are potential confounders.

## 08. Outcomes & Baselines

For each origin in 2012Q1–2026Q1, predict the same two-quarter-ahead warehouse YoY target using an expanding training window and a three-quarter label-maturity purge (minimum 41 training origins). Compare five models: (1) historical mean, (2) warehouse persistence ridge, (3) warehouse persistence plus national payroll ridge, (4) those controls plus `F(t)`, (5) e-commerce factor only. Evaluate **57 identical origins** with RMSE and MAE in percentage points; there are no return IC, portfolio spreads or Sharpe ratios because no security return panel exists.

## 09. Empirical Findings

| Model | RMSE (pp) | MAE (pp) | N |
|---|---:|---:|---:|
| Historical mean | 7.422 | 6.388 | 57 |
| Warehouse persistence | 5.360 | 3.878 | 57 |
| Persistence + payroll | 5.869 | 4.147 | 57 |
| Persistence + payroll + e-commerce | **5.172** | **3.616** | 57 |
| E-commerce only | 7.111 | 4.643 | 57 |

The candidate improves RMSE **0.696 pp** over the multivariate macro baseline and **0.188 pp** over the simpler persistence baseline. It does **not** demonstrate a causal effect or reliable future edge: the sample is short for regime analysis, the input is revised, and forecast errors overlap. Actual forecasts, scorecard and error series are committed in `results/`.

## 10. Robustness & Placebos

- **1,000 four-quarter block-shuffle refits:** observed macro-minus-full RMSE improvement **0.696 pp**; exploratory right-tail fraction **0.001**. Because the signal trends, blocks are not exchangeable; **this is not an exact statistical p-value** and cannot rescue the PIT defect.
- **2,000 four-quarter moving-block bootstrap resamples of paired OOS errors:** 95% interval **[−1.486, 2.572] pp** includes zero, so sampling uncertainty is substantial.
- **1,000 segment-mix perturbations (warehouse weight 0.5–1):** improvement median **0.674 pp**; this is a scenario analysis, not independent stock exposure evidence.
- **Alternative horizons:** 1Q full **4.053** vs macro **4.553** pp; 4Q full **5.435** vs macro **7.347** pp. Different horizons are exploratory comparisons, not preregistered independent tests.
- **Publication-buffer stress:** 2Q factor lag full **5.300** vs macro **5.979** pp; 3Q lag full **5.436** vs macro **6.015** pp.
- **Related-sector check:** courier outcome full **4.757** vs macro **5.303** pp; the effect is **not specific to warehousing**, and courier is not a valid unaffected placebo.

## 11. Regime Sensitivity

Pre-2020 OOS origins: **32**, full RMSE **2.544** versus macro **3.136** pp; 2020+ origins: **25**, full **7.260** versus macro **8.120** pp. Excluding 2020–2021 test origins: **49**, full **4.014** versus macro **4.792** pp. This direction is not purely a 2020 anomaly, but the pandemic discontinuity, sector-specific hiring cycle and repeated forecast targets make a stable long-run relationship uncertain. The same model is not independently tuned by regime.

## 12. Bias Audit & Verdict

| Risk | Finding |
|---|---|
| Vintage/revision leakage | **Unresolved.** Latest-revised Census/BLS history; no historical-vintage replay. |
| Look-ahead | Predictors lagged; labels purged by 3Q; **not sufficient** to prove PIT. |
| Multiple testing | Horizon, lag, regime and sector variants are exploratory, not adjusted for multiplicity. |
| Selection | U.S. national series chosen after recognizing e-commerce/logistics connection; no cross-country validation. |
| Overlap | 2Q-ahead YoY targets overlap; IID t-tests are invalid. |
| Company/survivorship | No company sample, historical exposure or delisting data. |
| Costs/capacity | No securities, trade prices, costs, market impact or investable backtest. |
| Placebo validity | Block shuffle is exploratory under nonstationarity; couriers are exposed to e-commerce too. |

**Verdict: reproducible retrospective macro lead-factor pilot with positive observed incremental OOS accuracy, but uncertain robustness and no verified PIT or equity alpha.** An apparently small block-shuffle tail fraction is not sufficient evidence of a tradable edge.

## 13. Reproduction

From this directory with Python 3.10+:

```bash
pip install -r requirements.txt
python run_analysis.py
pytest -q tests
jupyter nbconvert --to notebook --execute research.ipynb --output /tmp/logistics-reexecuted.ipynb
```

Run `python scripts/validate_studies.py` from repository root. The frozen CSV is checked in; no network connection is needed to reproduce analysis. See `results/run_log.txt`, `results/metrics.json`, `results/walk_forward_oos.csv`, `results/block_placebo_null.csv`, `results/robustness.csv`, `figures/` and notebook saved outputs. The one-time `create_frozen_inputs.py` documents the initial public-CSV transcription but is not used by `run_analysis.py`.

## 14. Next-Stage Protocol

(1) Obtain quarter-by-quarter **historical Census release PDFs** and BLS CES vintages from ALFRED, storing release timestamps and hash-verified immutable raw files. (2) Pre-register the warehouse target, horizon, controls and factor scale on the pre-2022 window and reserve 2022–2027 for a genuine forward-vintage holdout. (3) Add warehouse square footage, capacity utilization, automation capex and independent firm segment disclosures with filing dates. (4) Only after validating fundamentals, build a historical universe of adjusted total returns with transaction costs and sector-neutral benchmarks. (5) Retest against simpler warehouse-persistence baselines and correct for research-selection multiplicity.

## 15. Sources & Artifacts

Official primary series: [Census e-commerce share via FRED](https://fred.stlouisfed.org/series/ECOMPCTSA), [BLS warehousing employment](https://fred.stlouisfed.org/series/CES4349300001), [BLS courier employment](https://fred.stlouisfed.org/series/CES4349200001), [BLS national payroll](https://fred.stlouisfed.org/series/PAYEMS). The latest quarterly e-commerce share release date **2026-08-18** and latest CES release **2026-10-02** are not substitutes for historical observation-level publication timestamps. Source register and immutable snapshot are in `data/`; executable analysis in `run_analysis.py`; numerical outputs in `results/`; at least six genuine calculated charts in `figures/`; reproducibility tests in `tests/`. Research only, not investment advice.
