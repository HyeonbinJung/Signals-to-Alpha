# Charging-to-Adoption — Global EV Charging Infrastructure

> **Status:** Executed retrospective annual adoption-factor falsification; **NOT historical PIT** and **NOT investable equity alpha**.  
> **Research date:** 2026-10-26 · **IEA data publication:** 2024-04-23 · **Frozen extract:** 2026-10-19.  
> [Reference study](../Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/kfood_research_grade_alpha_v3.ipynb) · [Research standard](../RESEARCH_QUALITY_STANDARD.md) · [Manifest](study.json)

## 01. Abstract

**Question:** Does public EV charging growth lead national electric-car sales-share growth beyond adoption momentum? In a frozen IEA-2024-derived sample of **180 country-years across 16 countries**, **96** expanding-window OOS country-year forecasts (2018–2023) show charging-augmented RMSE **4.468 percentage points**, compared with **4.483 pp** for multivariate controls and **4.416 pp** for a simpler momentum baseline. **Verdict:** plausible infrastructure complement, but stable incremental forecasting power and equity alpha are **not established**.

## 02. Research Design & Hypotheses

**H1:** faster growth in public charging points precedes an increase in next-year EV sales share. **H2:** fast/slow charging growth and fast-charger mix improve forecasts beyond lagged share, lagged adoption change, country indicators and a fixed calendar trend. **H3:** any gain survives placebo, feature ablation, country exclusions, alternative horizons and regime changes. **Null:** charging features have no incremental OOS value. Reverse causality, vehicle affordability, subsidies and EV supply are competing explanations.

## 03. Industry Context

The [IEA Global EV Outlook 2024](https://www.iea.org/reports/global-ev-outlook-2024), **published 23 April 2024**, reports almost **14 million** electric-car sales in 2023 (**18%** of global new-car sales), with installed public charging points increasing by more than **40%** year on year. Infrastructure could reduce range anxiety, but industry growth, company profitability and security returns are separate hypotheses. The IEA's 2024 scenarios are used for **context only**, not as realized historical observations.

## 04. Data & Source Integrity

**Primary publisher:** [IEA Global EV Data Explorer](https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer); **attributed 2024 mirror:** [IEA-EV-Data-2024.csv](https://github.com/WRicd/IEA-Data-Project/blob/main/data/raw/IEA-EV-Data-2024.csv). Frozen derived extract: `data/iea_ev_2024_selected.csv`, **180 observed country-years, 2011–2023, 16 selected countries**, with EV new-car sales share (%), publicly available fast chargers and slow chargers (points). The original full CSV was **not** frozen here; immutable original-release hash is **UNKNOWN**. `source_register.csv` records URLs, publisher, quality A/B, original publication date, collection date, coverage, release assumptions, license and vintage caveats. `data/extract_methodology.md` documents original IEA field filters and sample selection. No interpolated corporate financials or fabricated market returns are included.

## 05. Point-in-Time Availability

At forecast year *t*, predictors use observed values from *t−1* and *t−2*, while model training uses outcomes from years before *t*. **This is a retrospective, fixed-2024-snapshot association test**, not a historical point-in-time test: the 2024 extract was not available in 2018–2023, original national release timestamps are **UNKNOWN**, and revisions may have changed older values. A one-year lag reduces arithmetic look-ahead but does not solve vintage leakage.

## 06. Factor Construction

For country *i* and forecast year *t*: `f_fast=log(1+Fast[i,t-1])-log(1+Fast[i,t-2])`, `f_slow=log(1+Slow[i,t-1])-log(1+Slow[i,t-2])`, `fast_mix=Fast[i,t-1]/(Fast[i,t-1]+Slow[i,t-1])`. The fixed descriptive score is `0.5*tanh(f_fast)+0.5*tanh(f_slow)`; neither weights nor tanh scale are fitted to returns. The predictive Ridge model uses fixed `alpha=10` with **training-fold-only** standardization.

## 07. Exposure & Transmission

**Exposure unit: country × year, not company.** Public charging access may enable more EV purchases; country dummies control for time-invariant adoption differences. National charging-point definitions, charger uptime, charging price, incentives and model availability can alter this transmission. No issuer-level revenue-by-country exposure, corporate earnings or investable stock universe is claimed; the 16-country sample is selected ex post for coverage.

## 08. Outcomes & Baselines

Target: `EV_share[i,t]-EV_share[i,t-1]`, in **percentage points**. OOS test years **2018–2023** with **96** predictions, expanding training using only matured earlier annual labels. Comparators: expanding global historical mean, expanding country historical mean, prior-year adoption momentum, Ridge controls (lagged share/change + country indicators + fixed trend), and controls plus charger features. RMSE/MAE and cross-country adoption Rank IC are **demand** metrics, not tradable alpha statistics.

## 09. Empirical Findings

| Model | OOS N | RMSE (pp) | MAE (pp) |
|:--|--:|--:|--:|
| Historical mean | 96 | 5.195 | 3.423 |
| Country mean | 96 | 4.955 | 3.390 |
| EV-share momentum | 96 | **4.416** | **2.963** |
| Country/trend/persistence controls | 96 | 4.483 | 3.091 |
| Controls + charger features | 96 | 4.468 | 3.079 |

Incremental RMSE improvement against controls is only **0.0155 pp**; the full model is worse than momentum. Mean annual cross-country charging-score Rank IC with future **EV adoption**, not returns, is **0.042**. Detailed observed outputs are in `results/metrics.json`, `results/walk_forward_oos.csv` and eight measured figures.

## 10. Robustness & Placebos

**1,000** within-year joint charging-feature shuffles, each refitting the walk-forward model, give an exploratory one-sided **p≈0.132**. The shuffle does not preserve all country-level temporal dependence and is **not an exact permutation p-value**. **2,000** whole-OOS-year block bootstrap draws yield a 95% RMSE-improvement interval of **[-0.0173, +0.0524] pp**, crossing zero; just six unique OOS years make precision weak. Additional checks: **1,000** fast/slow descriptive-weight perturbations, fast/slow/mix ablations, stale-signal timing and two-year horizon. Country leave-one-out is a **post-hoc exclusion from predictions**, not a refitted cross-validation procedure.

## 11. Regime Sensitivity

Control-minus-full RMSE improvement: **2018–19 -0.0106 pp**, **2020–21 +0.0563 pp**, **2022–23 -0.0121 pp**. Excluding **Norway -0.0109 pp**, **China +0.0280 pp**, or **both +0.0019 pp** shows unstable sign and concentration. The six-year OOS window is too short for definitive regime inference.

## 12. Bias Audit & Verdict

**Open risks:** retrospective-vintage leakage, unverifiable original mirror hash, ex-post country selection, country/year dependence, reverse causality, omitted policies and car prices, heterogeneous charging definitions, multiple exploratory tests, and no issuer returns or costs. No survivorship-free total returns, equity factor IC, portfolio spread, delisting adjustment, trading capacity or security-level fundamentals are measured. **Final verdict:** structurally relevant EV charging industry, **unproven incremental adoption predictor** and **no investable equity alpha claim**.

## 13. Reproduction

From this study directory with Python 3.10+: `python -m pip install -r requirements.txt`; `python -m pytest -q tests`; `python ev_charging_alpha.py`; `python plot_results.py`; `jupyter nbconvert --to notebook --execute --inplace research.ipynb`. The notebook contains the same canonical 15 sections with **69 cells, 23 executed code cells and saved actual outputs**. The optional `python fetch_source.py` performs an online mirror audit and **was not executed** in offline validation. From the repository root, run `python scripts/validate_studies.py`.

## 14. Next-Stage Protocol

Collect archived national/IEA **release vintages**, exact registration publication dates, uptime-adjusted charger availability, incentive and price controls, and issuer-by-country revenue exposure. Pre-register a monthly point-in-time factor, use a future untouched holdout, then test corporate fundamentals and delisting-adjusted security total returns net of realistic costs. Compare against momentum, country/sector and common macro controls before any investable claim.

## 15. Sources & Artifacts

- [IEA Global EV Outlook 2024](https://www.iea.org/reports/global-ev-outlook-2024) and [executive summary](https://www.iea.org/reports/global-ev-outlook-2024/executive-summary), published 2024-04-23, CC BY 4.0.
- [IEA Global EV Data Explorer](https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer) and [attributed 2024 dataset mirror](https://github.com/WRicd/IEA-Data-Project/blob/main/data/raw/IEA-EV-Data-2024.csv), original-release hash **UNKNOWN**.
- `source_register.csv`, `data/extract_methodology.md`, frozen `data/iea_ev_2024_selected.csv`, `ev_charging_alpha.py`, `research.ipynb`, `results/` scorecards/predictions/null draws, `figures/` eight computed PNGs, and `tests/` unit checks.
