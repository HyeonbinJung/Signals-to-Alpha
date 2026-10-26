<!-- Archived original detailed study notes, retained verbatim during 2026-10-26 standardization. -->

# Housing Permits-to-Alpha: Can Housing Activity Predict U.S. Building-Materials Output?

**Research-grade public-data pilot · 19 October 2026 · Fixed revised-data snapshot · NOT equity alpha**

> **Verdict:** The housing industry is economically important, but the proposed permits-and-starts feature does **not** deliver robust incremental predictive value for nonmetallic mineral products. Across **98 expanding-window six-month forecast origins (2018-01 to 2026-02)**, housing-enhanced Ridge RMSE was **5.109 pp**, worse than macro-control Ridge (**4.874 pp**) and the historical-mean forecast (**4.808 pp**). This is a negative/falsification result, not a trading strategy.

## 1. Economic rationale and industry outlook

The causal hypothesis is straightforward: housing permits lead construction starts; starts and renovation projects may translate into orders for concrete, cement, glass, ceramics, lumber and related inputs; capacity utilization and output then adjust. However, nonmetallic mineral production (NAICS 327) includes **nonhousing demand** (infrastructure, industrial glass, etc.) and homebuilding is strongly cyclical, sensitive to mortgage rates, inventory, zoning and financing. **A long-term housing need is not a forecast of near-term profits or equity returns.** No unsupported numerical market-size projection is used.

The [U.S. Census September 17, 2026 new-residential-construction release](https://www.census.gov/construction/nrc/current/index.html) reported August 2026 housing starts at **1.275 million SAAR**; the contemporaneous release reported permits at **1.394 million SAAR**. The [FRED PERMIT snapshot](https://fred.stlouisfed.org/series/PERMIT), subsequently updated **September 24**, instead reads **1.403 million SAAR** for August, directly illustrating **revisions/vintage drift**. The [Federal Reserve G.17](https://www.federalreserve.gov/releases/g17/current/default.htm) was released October 16 for September production. These contextual figures are **not** used as contemporaneous backtest labels or price signals.

**Counterthesis:** tighter credit and affordability can restrain new construction; public-infrastructure demand can overwhelm residential signals in NAICS 327; imported products and material substitution can sever domestic production links. Industry output growth is distinct from profit growth, valuation changes and stock-price alpha.

## 2. Hypotheses and strict scope

- **H1 — economic lead:** lagged housing permits/starts YoY may predict nonmetallic-mineral industrial-production YoY six months ahead.
- **H2 — incremental factor:** housing features should beat a simple historical-mean model, a target-autoregressive model and manufacturing/rates macro controls under the **same** expanding-window protocol.
- **H3 — robustness:** results should be consistent at a 3-month horizon, for wood products (NAICS 321), outside COVID and against lag-only placebos.
- **H4 — equity alpha (NOT TESTED):** company-level, filing-known housing exposure might predict future earnings revisions or industry-adjusted total returns. No security-level returns, valuation, turnover, cost or universe are present.

The **null** is that permits/starts do not improve out-of-sample forecasts beyond simple controls. Negative results are publishable.

## 3. Data and integrity

Bundled file: `fred_housing_materials_snapshot_2010_2026.csv`, six monthly official FRED series, **200 aligned months from January 2010 to August 2026**. All raw data are measured public series, not AI-generated synthetic financial histories. `source_register.csv` lists publisher, grade, units, coverage, latest update and publication caveats.

| Series | Source / units | Role |
|---|---|---|
| [PERMIT](https://fred.stlouisfed.org/series/PERMIT) | Census/HUD, thousands of units SAAR | building permits YoY |
| [HOUST](https://fred.stlouisfed.org/series/HOUST) | Census/HUD, thousands of units SAAR | housing starts YoY |
| [IPG327S](https://fred.stlouisfed.org/series/IPG327S) | Fed G.17, index 2017=100 SA | primary building-materials outcome |
| [IPG321S](https://fred.stlouisfed.org/series/IPG321S) | Fed G.17, index 2017=100 SA | wood-products cross-industry check |
| [IPMAN](https://fred.stlouisfed.org/series/IPMAN) | Fed G.17, index 2017=100 SA | manufacturing control |
| [FEDFUNDS](https://fred.stlouisfed.org/series/FEDFUNDS) | Fed H.15, monthly percent | policy-rate control |

**Snapshot/vintage warning:** FRED's CSV reflects the **latest available revised observations** on retrieval date. A two-month publication lag helps avoid using obviously unpublished monthly values, but **cannot reconstruct what the market actually knew historically**. Census August permits were revised from the initial September release. Formal point-in-time evaluation requires ALFRED/release archives, not just timestamp shifts.

## 4. Predefined factor, target and model

For a monthly positive series X, `YoY(X,t)=100·ln(X_t/X_(t−12))`. At formation month t, every feature uses **t−2** or older observations:
- `p_t = YoY(PERMIT,t−2)` and `s_t = YoY(HOUST,t−2)`.
- `g_t = p_t − s_t` is the fixed housing pipeline gap (percentage points), not a fitted z-score.
- Controls: `YoY(IPG327S,t−2)`, `YoY(IPMAN,t−2)`, `FEDFUNDS_(t−2)`.
- **Outcome** `y_t = YoY(IPG327S,t+6)`, i.e., the **year-over-year** production growth observed six months after formation. It is *not* the return from t to t+6.
- Models: historical-mean, target-only Ridge, macro Ridge, macro+both housing indicators Ridge, macro+gap Ridge. **Ridge α=25** and train-fold-only scaling (zero-variance feature uses unit scale), no hyperparameter tuning on the test.
- Origins from **2018-01**. For each t, training origins s must satisfy **s≤t−8** (six-month label maturity + two-month conservative reporting buffer), begin no earlier than 2012-01 and number at least 35. Thus every fit is an expanding-window, purged forecast.
- Monthly overlapping six-month outcomes have **serially dependent errors**; do not treat 98 origins as 98 independent economic regimes.

## 5. Measured quantitative findings

### Main target: nonmetallic-mineral products, six-month lead (98 origins)

| Model | RMSE (pp) | MAE (pp) | Sign accuracy |
|---|---:|---:|---:|
| Historical-mean growth | **4.8079** | 3.4701 | 50.00% |
| Target-only Ridge | 4.8690 | 3.5638 | 42.86% |
| Manufacturing/rates macro Ridge | 4.8737 | 3.4246 | **63.27%** |
| Macro + housing permits/starts | **5.1094** | 3.6197 | 59.18% |
| Macro + permits-minus-starts gap | 4.8751 | 3.4231 | 62.24% |

**Result:** full housing indicators **increase** RMSE by **0.3015 pp vs historical mean** and **0.2357 pp vs macro controls**. The compact gap variant is essentially indistinguishable from macro controls. Sign accuracy alone does not rescue a model with worse squared-error calibration.

### Robustness and falsification

| Check | Comparison / outcome |
|---|---|
| 3-month primary-target horizon (101 origins) | mean **4.7096**, macro **4.2930**, housing **4.4627** pp RMSE — housing loses to macro |
| Wood-product target (98 origins) | mean **5.3932**, macro **5.8194**, housing **5.6401** pp — housing beats macro but loses to mean |
| Excluding 2020-03 through 2021-12 (76 origins) | mean **4.8098**, macro **4.4118**, housing **4.7247** pp |
| Post-2022 test (50 origins) | mean **4.4084**, macro **4.0323**, housing **4.0589** pp |
| Lag-only housing placebo, extra 12 months | housing RMSE **4.9262** pp |
| Lag-only housing placebo, extra 24 months | housing RMSE **5.1244** pp |
| Lag-only housing placebo, extra 36 months | housing RMSE **5.0055** pp |

**Placebo caution:** older housing features are lagged by 12/24/36 months without wraparound, so they do not leak future observations. Their eligible training lengths and origin coverage may differ from the main model. They are **exploratory timing falsifications, not permutation-test p-values**; no statistically significant alpha is claimed.

## 6. Bias audit

| Bias | Assessment | Fix |
|---|---|---|
| Feature publication lag | t−2 buffer is conservative, not exact | use release calendars and per-observation timestamps |
| Historical revisions / vintages | **high unresolved**; current FRED values revised | rebuild with ALFRED vintages and archived Census releases |
| Training label maturity | explicitly purged t−8 | verify true availability for every label vintage |
| Training-sample leakage | train-only mean/SD; fixed α | freeze before new prospective observations |
| Outcome overlap / serial dependence | **high**; monthly 6-month forward targets overlap | nonoverlapping folds, HAC/block bootstrap |
| Target definition | industrial output YoY, **not equity excess return** | construct return panel with adjusted prices and delistings |
| Selection bias | researcher chose NAICS 327 after seeing industry story | preregister industry list and test all industries |
| Housing proxy contamination | infrastructure, exports, substitution and rates | product-category exposures and region-level construction data |
| Regime instability | COVID, rates, 2022+ divergence | longer pre-2010 panel, future 2027+ untouched holdout |

## 7. Replication and validation

Python 3.10+:

```bash
cd Housing-Permits-to-Alpha-U.S.-Building-Materials
python -m pip install -r requirements.txt
python housing_alpha.py
python -m pytest -q test_housing_alpha.py
jupyter notebook housing_permits_alpha_research.ipynb
```

The script recomputes all headline metrics and writes `results_generated.json` and `oos_forecasts_generated.csv` locally. The repository also includes the fixed reference `results_snapshot.json` and `oos_forecasts_snapshot.csv`, generated from the same deterministic linear-algebra protocol and official data; tests check three headline RMSEs against the reference. Re-running against later revised FRED downloads will change results. **Do not replace a historical snapshot without preserving its as-of date.**

## 8. Required next work before security-level alpha

1. Pull original publication vintages via [ALFRED](https://alfred.stlouisfed.org/) and Census PDF releases; reconstruct exactly what was known on every formation date.
2. Add monthly product-level cement, concrete, glass and wood shipments/orders and regional building permits; control for government infrastructure capex and housing inventory.
3. Build a contemporaneous U.S.-listed producer universe with historical 10-K housing revenue exposure, earnings announcements, adjusted total returns and delisting histories.
4. Test firm-level earnings-surprise and forward industry-neutral return **rank IC**, control for value/quality/momentum, apply trading lags and conservative transaction costs.
5. Pre-register sector selection, evaluate nonoverlapping regimes and hold out prospective observations; only claim alpha after robust out-of-sample improvement.

### Four-sentence takeaway

August 2026 U.S. housing starts were **1.275 million SAAR**, while the subsequently revised FRED permits snapshot was **1.403 million SAAR**, illustrating both the industry's measurable demand pipeline and historical-data revision risk. In 98 six-month-ahead expanding-window forecasts, adding permits and starts **worsened** building-materials production-growth RMSE to **5.109 pp**, versus **4.874 pp** for macro controls and **4.808 pp** for the historical mean. Three-month, wood-industry, post-2022 and lag-only timing checks failed to establish stable incremental predictive power. **Conclusion: an economically interpretable demand indicator, but no verified point-in-time or investable equity alpha.**

Research only; not investment advice.
