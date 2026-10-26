<!-- Archived original detailed study notes, retained verbatim during 2026-10-26 standardization. -->

# Grid Capex-to-Alpha: Does Grid Load Lead U.S. Electrical Equipment Production?

**Research-grade public-data pilot (2026-10-19) · Verified historical association, NOT validated equity alpha**

> **Verdict:** U.S. grid/electrical-equipment supply chains have a credible medium-term demand tailwind, but this preliminary public-data test does **not** establish investable alpha. In a 19-origin, 6-month expanding-window evaluation the proposed gap feature produced RMSE **4.124 pp**, compared with **4.228 pp** for a momentum-only Ridge model and **3.524 pp** for a historical-mean forecast. The feature therefore fails the simplest benchmark. These statistics are from a **small, revised/mixed-vintage macroeconomic snapshot** and must not be advertised as tradable results.

## 1. Economics: does this industry have a future?

IEA's *Energy and AI* (2025) estimates **415 TWh** of global data-centre electricity consumption in 2024 and projects approximately **945 TWh** for 2030 in its *Base Case*. These are global figures, **not** observed U.S. load. The IEA expects U.S. data centres to account for a large fraction of incremental U.S. electricity demand; its forecasts are conditional scenarios, not guaranteed sales. U.S. EIA's September 2026 *Short-Term Energy Outlook* projects total electricity sales of about **4,135 billion kWh in 2026** and **4,211 billion kWh in 2027**, driven in part by data centres and manufacturing. This supports an industry-capacity thesis for transformers, switchgear, high-voltage equipment, transmission infrastructure and grid services, but it does not by itself imply positive excess stock returns.

**Economic transmission:** data-centre expansion -> higher electricity load / interconnection pressure -> utilities expand and replace grid assets -> electrical equipment orders and production -> possible earnings revisions for manufacturers -> *possibly* equity repricing **only if the news is not already priced in**.

**Counterarguments:** permitting and interconnection bottlenecks, transformer supply constraints, AI-capex pullbacks, equipment import substitution, tariff uncertainty, rate regulation, and already-expensive equity multiples. Energy output also responds to weather, so a raw utility-production proxy is not a data-centre-specific signal.

## 2. Question, hypotheses and falsification

- **H1 (macro fundamentals):** stronger power-generation/transmission output growth relative to electrical-equipment production growth might lead stronger future equipment output as supply catches up.
- **H2 (incrementality):** a fixed-scale load/equipment gap should improve next-6-month equipment-growth forecasts relative to a past-growth/momentum-only model **and** a historical-mean predictor.
- **H3 (equity, untested):** *if* company-level point-in-time exposure and adjusted total-return data are collected, an exposure-weighted signal may forecast next-period industry-adjusted excess returns.
- **Null:** neither the incremental model nor a time-shift placebo distinguishes the factor from chance or persistence effects.

The analyses below test H1/H2 provisionally; **H3 is not tested**.

## 3. Data provenance and point-in-time integrity

| Series | Purpose | Coverage in bundled snapshot | Source / caveat |
|---|---|---|---|
| Federal Reserve **IPG2211S** (NAICS 2211) | U.S. electric power generation, transmission & distribution industrial production, seasonally adjusted | 2022-01 to 2026-08 | [FRED IPG2211S](https://fred.stlouisfed.org/series/IPG2211S); historical readings may be revised |
| Federal Reserve **IPG3353S** (NAICS 3353) | U.S. electrical equipment industrial production, seasonally adjusted | 2022-01 to 2026-08 | [FRED IPG3353S](https://fred.stlouisfed.org/series/IPG3353S); revised through October 2026 |
| IEA *Energy and AI* (2025) | Demand mechanism / forward scenario, not a trading feature | global 2024-2030 | [IEA executive summary](https://www.iea.org/reports/energy-and-ai/executive-summary) |
| EIA *Short-Term Energy Outlook* | U.S. forecast backdrop, not a trading feature | September 2026 vintage | [EIA STEO](https://www.eia.gov/outlooks/steo/report/electricity.php) |

**Critical qualification:** these two FRED series were transcribed from visible official data tables and aligned to 2026-08. The accessible pages have **different last-update dates** (load: September 2026; equipment: October 2026). Consequently the data are **not an audited common-vintage panel**. The pipeline lags features by one month and embargoes future labels, but **that does not undo historical revisions**. Market information-availability requires an archival ALFRED vintage or the Federal Reserve's original releases. No synthetic data, AI-created company revenues or made-up backtest performance appear in the study.

## 4. Fixed, pre-specified factor

Let L_t = IPG2211S power production, E_t = IPG3353S equipment production.

- Power growth = 100 × (L_(t-1) / L_(t-13) − 1); equipment growth analogously.
- **Gap(t) = tanh[(PowerYoY_(t−1) − EquipYoY_(t−1)) / 10].** Fixed denominator 10 percentage points; no in-sample or full-sample z-score.
- Equipment momentum control = 100 × (E_(t−1)/E_(t−7) − 1).
- **Target y_t = 100 × (E_(t+6)/E_t − 1)** (six-month equipment production growth).

Models: Ridge(α=20), train-only feature scaling, expanding origin-by-origin fit. Control features: equipment YoY and six-month equipment momentum; full model adds gap. Simpler null: rolling training-sample average of y. Only labels formed at least seven months before each forecast origin enter the fit (six-month outcome maturity + one-month publication lag). The monthly horizons strongly overlap.

**No strategy returns** are measured: no ticker universe, dividends, splits, delisting returns, borrow costs, implementation delays or security exposure panels are present.

## 5. Measured results (snapshot, verified 2026-10-19)

| Check | Finding |
|---|---:|
| Aligned raw monthly pairs | 56, 2022-01 to 2026-08 |
| Usable ex-post factor/outcome pairs | 37, 2023-02 to 2026-02 |
| Expanding out-of-sample forecast origins | 19, each using at least 12 fully matured past labels |
| August 2026 power production YoY | **+7.00%** |
| August 2026 electrical equipment production YoY | **+5.38%** |
| Gap vs forward equipment-growth Spearman rho | **−0.179**, nominal p = 0.289 (overlap-invalid for formal inference) |
| Historical-mean 6-month growth RMSE | **3.524 pp** |
| Past-growth controls Ridge RMSE | **4.228 pp** |
| Past-growth controls + gap Ridge RMSE | **4.124 pp** |
| 24 nontrivial circular-shift placebo gaps | **p≈0.32**, exploratory, non-exact |

**Interpretation:** The load/equipment mismatch exists in current data, but the proposed gap feature has not shown statistically credible forecasting power. Its incremental Ridge improvement is tiny and does not beat the simplest null; circular-shift diagnostics offer no convincing rejection. The structural industry-growth narrative must not be conflated with investment alpha.

## 6. Robustness and why they are limited

1. **Persistence/momentum ablation:** compare Ridge with/without the gap under identical train-only normalization; compare both with the historical-mean null.
2. **Time-shift placebo:** preserve autocorrelation approximately through 24 nontrivial circular shifts of the gap. The resulting rank is descriptive; it is not an exact null under serial dependence / shared factor construction.
3. **Overlapping-label audit:** monthly observations share six-month future outcomes. Ordinary independent-sample p-values overstate effective sample size; the notebook presents a six-month moving-block bootstrap only as a diagnostic, not definitive inference.
4. **Feature scale:** the fixed tanh 10 pp denominator avoids peeking at full-sample distributional statistics.
5. **Scope ablation:** power IP contains all electricity uses (not only AI/data-centre load); the electrical-equipment output series includes many non-grid products. Without region/state disaggregation, any structural story is a mechanism hypothesis, not a verified mapping.
6. **Regimes:** 2022-2026 includes rate shocks and AI-capex enthusiasm; too short and too few distinct macro regimes to conclude reliable long-run effectiveness.

## 7. Bias audit

| Risk | Assessment | Required next step |
|---|---|---|
| Look-ahead through feature timing | mitigated by 1-month lag, **not eliminated** | Verify exact G.17 monthly release dates |
| Data revisions / mixed vintages | **high / unresolved** | rebuild with ALFRED vintage snapshots |
| Target overlap / dependent errors | **high** | use nonoverlapping test origins, block-resampling |
| In-sample tuning / parameter overfit | fixed α=20, lag=1, denominator=10 | freeze protocol and evaluate fresh 2027+ observations |
| Survivorship / company exposure leakage | not applicable to current macro proxy, **untested for stocks** | freeze ex-ante investable universe and filing-known exposure |
| Broad load vs AI-specific consumption | **high proxy contamination** | utility territory / ISO interconnection queues; EIA-861, FERC filings |
| Equity alpha / execution costs | **not evaluated** | adjusted total returns, industry-neutral IC, trade delay, turnover and costs |

## 8. Replication

Requires Python 3.10+ and packages in requirements.txt.

\`\`\`bash
cd Grid-Capex-to-Alpha-U.S.-Electric-Equipment
python -m pip install -r requirements.txt
python grid_alpha.py
python -m pytest -q test_grid_alpha.py
jupyter notebook grid_capex_alpha_research.ipynb
\`\`\`

The command writes \`oos_forecasts_generated.csv\` locally (not committed as if it were a live strategy). To refresh the source snapshot, use the authoritative FRED tables and **document each series' observation and vintage date**. Results will change as government estimates are revised.

## 9. Roadmap: tests required before an equity-alpha claim

1. Download genuine timestamped vintage observations (FRED/ALFRED plus actual G.17 release calendar); consider 2005-2026 and hold out whole regimes.
2. Replace noisy national electricity output with **utility-region electricity load and known interconnection queues**, population/weather-adjusted; make pre-publication timing explicit.
3. Map exposure using contemporaneous 10-K product segments for electrical-equipment firms; include delisted companies and publicly available contemporaneous share histories.
4. Cross-sectional **rank IC** of next-quarter earnings surprises and 3/6/12-month industry-adjusted total returns, compared with momentum, quality, valuation and sector controls.
5. Purged rolling walk-forward, sector-neutral top/bottom portfolios, ≥1,000 stratified placebos, exposure-weight jitter, leave-one-firm-out, recession/regime breakdown, conservative turnover/transaction/financing costs.
6. Do not publish a tradable alpha headline until **out-of-sample** improvements survive those tests.

### Four-sentence takeaway

The IEA's data-centre electricity demand outlook supports a medium-term grid-equipment investment thesis but is a forecast, not a security-return signal. The measured August 2026 U.S. power-output and electrical-equipment production indices rose approximately 7.00% and 5.38% year over year, respectively. The hypothesized load-to-equipment gap factor marginally lowered six-month Ridge forecast RMSE relative to momentum controls (4.124 vs 4.228 pp) but **lost to a historical-mean forecast (3.524 pp)** and failed an exploratory circular-shift placebo (p≈0.32). This pilot is **not evidence of investable equity alpha**, and revised/mixed-vintage data plus overlapping horizons require a proper point-in-time rebuild.

Research use only. No investment recommendations.
