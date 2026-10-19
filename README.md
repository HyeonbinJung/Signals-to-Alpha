<div align="center">

# 🍜 Signals to Alpha

**머신러닝 / 알파 팩터를 통한 경제, 산업 분석**<br>
<sub>Machine learning and alpha-factor research for economic and industry analysis</sub>

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" height="26">
<img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" height="26">
<img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" height="26">
<img src="https://img.shields.io/badge/statsmodels-4051B5?style=for-the-badge" height="26">
<img src="https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white" height="26">
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" height="26">
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" height="26">

[Overview](#-overview) · [Studies](#-studies) · [Summaries](#-research-summaries) · [Method](#-method--k-food-study) · [Getting Started](#-getting-started) · [Structure](#%EF%B8%8F-project-structure) · [Notes](#-notes--limitations)

</div>

---

## 📌 Overview

A collection of research notebooks that turn **real-economy signals** — trade flows, consumer demand, industry data — into **testable alpha factors**, with an emphasis on honest evaluation: point-in-time construction, placebo tests and bias audits rather than headline backtests.

## 📚 Studies

| Study | Question | Status |
|---|---|---|
| [**Consumption-to-Alpha**](Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/) — a U.S. K-Food alternative-data factor model | Can K-food demand at *t* predict revenue growth and excess equity returns at *t + 1*? | Research-grade pilot (v3) |
| [**Grid Capex-to-Alpha**](Grid-Capex-to-Alpha-U.S.-Electric-Equipment/) — U.S. electricity / electrical-equipment lead-factor pilot | Does power-system output growth lead U.S. electrical-equipment production and imply testable alpha? | Fixed-vintage macro pilot · **no equity alpha established** |
| [**Housing Permits-to-Alpha**](Housing-Permits-to-Alpha-U.S.-Building-Materials/) — U.S. building-materials macro factor falsification | Do housing permits and starts improve forward building-materials output forecasts? | Fixed-vintage OOS test · **housing factor fails baselines** |
| [**Gas–Oil Divergence-to-Alpha**](Gas-Oil-Divergence-to-Alpha-U.S.-LNG/) — U.S. LNG / natural-gas relative-price pilot | Does WTI-to-Henry Hub divergence predict future natural-gas spot prices beyond momentum? | Purged OOS · **negative factor result, no equity alpha** |
| [**Revenue Dip Lab**](Revenue-Dip-Lab/) — fundamental resilience & price-drawdown backtesting engine | Do companies with resilient revenue offer systematic opportunities after sharp price declines? | Interactive platform · rule-based backtests |

## 🧾 Research Summaries

### 🍜 Consumption-to-Alpha — K-Food demand
The economic hypothesis is that K-Food demand growth precedes related food producers' reported sales growth and possibly market-adjusted equity returns. The pilot's fundamental signal appears more encouraging than its equity signal, especially after 2022, but equity performance is concentrated in Samyang Foods and weakens materially without it. Annual public customs observations become available after year-end and five annual periods cannot establish a point-in-time executable factor. **Verdict: plausible fundamental demand indicator; sector-wide investable alpha unproven.**

### ⚡ Grid Capex-to-Alpha — U.S. power and electrical equipment
IEA's outlook suggests strong medium-term demand for power infrastructure, but projected electricity use is not itself a tradable equity signal. In official Federal Reserve monthly indices, August 2026 U.S. power output rose about **7.00% YoY** and electrical-equipment production about **5.38% YoY** (latest/mixed-vintage snapshot). The proposed load-equipment gap marginally improved six-month Ridge forecast RMSE against historical growth controls (**4.124 vs 4.228 percentage points**) but lost to a historical-mean forecast (**3.524 percentage points**) and did not survive an exploratory time-shift placebo (**p≈0.32**). **Verdict: promising structural industry thesis; macro predictor unproven, equity alpha not tested, and historical vintages still need auditing.** [Study, code and sources](Grid-Capex-to-Alpha-U.S.-Electric-Equipment/).

### 🏠 Housing Permits-to-Alpha — U.S. building materials
The Census/FRED August 2026 data show housing starts of **1.275 million SAAR** and revised permits of **1.403 million SAAR**, but these cyclical pipeline measures are not themselves equity-return signals. Across **98** six-month-ahead expanding-window forecasts (2018-01 to 2026-02), housing-enhanced Ridge **worsened** building-materials output-growth RMSE to **5.109 pp**, versus **4.874 pp** for manufacturing/rate controls and **4.808 pp** for a historical-mean forecast. Three-month, wood-product, regime and lag-only placebo checks did not establish stable incremental predictive value. **Verdict: plausible industrial-demand mechanism but no validated point-in-time forecast advantage or investable equity alpha; historical FRED revisions remain unaudited.** [Study, code and source register](Housing-Permits-to-Alpha-U.S.-Building-Materials/).

### 🔥 Gas–Oil Divergence-to-Alpha — U.S. LNG and natural gas
EIA's 2026 LNG export outlook supports a structural capacity/volume growth thesis, but that does not establish predictable spot-price or equity returns. Across **242** expanding-window monthly OOS forecasts (2006-05–2026-06), the oil–gas relative-price spread **worsened** the primary forecast RMSE to **32.707 pp** versus **30.911 pp** for momentum controls and **30.825 pp** for a historical-mean baseline. One-/six-month horizons, LNG-era regime checks, 2022 exclusion and stale-spread placebos failed to establish robust incremental forecasting power. **Verdict: promising LNG industry, failed spot-price factor, unaudited historical data vintages, and no tested futures/equity alpha.** [Study, reproducible code and source register](Gas-Oil-Divergence-to-Alpha-U.S.-LNG/).

## ✅ Research Quality & Reproduction

Every new study is evaluated against the original [K-Food v3 research notebook](Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/kfood_research_grade_alpha_v3.ipynb), not merely by repository file count. See the [**Research Quality Standard**](RESEARCH_QUALITY_STANDARD.md) for required research design, frozen data provenance, point-in-time caveats, hypotheses, forecasting baselines, falsification, execution validation and a complete notebook with interpretable charts.

The three subsequent macro/commodity pilots have now been expanded into 34–35-cell auditable notebooks. **This is a documentation and diagnostic-code improvement, not a change to the reported empirical evidence.** Executed figures and additional diagnostic outputs are validated and saved only if the [notebook integrity workflow](.github/workflows/research-notebook-validation.yml) passes all study tests and executes every cell. A macro-output forecast does not establish equity alpha.

## 🔬 Method — K-Food Study

| Step | What it does |
|---|---|
| 🧾 **Data hierarchy** | Sources graded A (government / company filings) · B (institutional databases) · C (press, descriptive only) |
| ⏱️ **Point-in-time signal** | `Signal = tanh(YoY growth / 20)` — a fixed transform, no full-sample z-scores |
| 🗺️ **Exposure map** | Company demand = Σ category exposure × category signal (ramen, kimchi, rice, sauce, broad) |
| 📈 **Equity lead test** | Demand score vs next-year return minus KOSPI (rank IC, long-short spread) |
| 🏭 **Fundamental lead test** | Demand score vs next-year sales growth (CJ uses Food-division sales) |
| 🧪 **Robustness** | Samyang removal, sauce exclusion, momentum control, 1,000 exposure-weight perturbations |
| 🎲 **Permutation placebo** | Shuffles scores across companies within each year |
| 🔍 **Bias audit** | Look-ahead, survivorship and exposure look-ahead checks |

**Verdict.** The economic thesis is credible and the **fundamental** signal is more promising than the equity factor, but five annual periods are **not enough to claim sector-wide alpha** — results strengthen after 2022 and remain regime-sensitive.

## 🧰 Tech Stack

| Layer | Tools |
|---|---|
| Analysis | Python, Jupyter, pandas, NumPy |
| Statistics | statsmodels (OLS), SciPy (Spearman / Pearson), permutation tests |
| Visualization | Matplotlib, browser charts and 3D CAGR surfaces |
| Platforms | FastAPI, shared JavaScript backtest engine, Web Workers, SQLite |
| Data | MAFRA, Korea Customs Service, company IR and filings, FRED / IMF, MarketScreener, SEC EDGAR, Yahoo Finance, Financial Modeling Prep |

## 🚀 Getting Started

```bash
pip install pandas numpy scipy statsmodels matplotlib jupyter
cd Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model
jupyter notebook kfood_research_grade_alpha_v3.ipynb
```

## 🗂️ Project Structure

```text
Signals-to-Alpha
├── Gas-Oil-Divergence-to-Alpha-U.S.-LNG/    LNG spot-price factor falsification
├── Housing-Permits-to-Alpha-U.S.-Building-Materials/   housing-activity macro factor falsification
├── Grid-Capex-to-Alpha-U.S.-Electric-Equipment/        grid-equipment macro factor pilot
├── Revenue-Dip-Lab/                               backtesting platform — see its README
└── Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/
    ├── kfood_research_grade_alpha_v3.ipynb        research notebook (v3)
    ├── kfood_research_grade_panel.csv             demand score → next-year return panel
    ├── kfood_research_grade_fundamental_panel.csv demand score → next-year sales panel
    ├── kfood_exposure_matrix_v3.csv               company × category exposure priors
    └── kfood_source_register_v3.csv               data sources, coverage and quality grade
```

## 📝 Notes & Limitations

- Annual customs data are finalized after year-end, so the equity test is a **lead-association test**, not an executable January-1 backtest.
- Exposure weights are **analyst priors** informed by public product mix, not reported category revenue shares.
- The company universe is selected ex post (survivorship). H Mart appears only as a structural distribution proxy from press reporting.
- Research only — not investment advice.

---

<div align="center"><sub>Built by <a href="https://github.com/HyeonbinJung">Hyeonbin Jung</a></sub></div>
