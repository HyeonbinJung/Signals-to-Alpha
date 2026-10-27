# Relative Copper–Aluminum Cost Relief and World Copper Demand (1951–1975)

**Status:** REPRODUCED RETROSPECTIVE WORLD COPPER DEMAND PILOT — NOT PIT / NOT EQUITY ALPHA

## 01. Abstract

**Question:** Does a one-year-stale copper-versus-aluminum relative-price relief factor improve next-year world copper-consumption growth forecasts? In 10 purged expanding-window origins (1965–1974), the factor-augmented model reached **6.290 log-pp RMSE**, against **6.297** for demand/income/inventory controls and **7.625** for a historical mean. The **0.0068 log-pp** improvement is economically negligible, its block-bootstrap interval crosses zero, and longer horizons fail. **Verdict: historical macro-demand association only; no reliable lead factor or equity alpha.**

## 02. Research Design & Hypotheses

**H1 (substitution):** lower lagged copper-price growth relative to aluminum predicts stronger next-year copper consumption growth. **H2 (incremental):** adding relative-cost relief to lagged consumption, income and inventory beats the fixed control model on purged expanding OOS RMSE. **H3 (stability):** improvement retains its sign across 2–3-year horizons, 1–3-year staleness, 1965–69/1970–74, block shuffles and weight perturbations. **Null:** no incremental predictive gain. Counterthesis: copper price reacts to demand/supply contemporaneously, substitution is technologically constrained, and annual aggregates are too coarse.

## 03. Industry Context

The original dataset describes **world copper consumption, 1951–1975** (3,173.0 to 7,157.2 thousand metric tonnes, *historical series only*), not current market size. Copper and aluminum compete in some industrial uses, while copper conductivity and application constraints limit substitution. The International Copper Association reported low substitution for **2020**, but this is **not** used as evidence for 1951–1975; the International Copper Study Group factbook is context only. Supply shocks, income growth and inventory cycles offer competing mechanisms; no company-level production exposure is measured.

## 04. Data & Source Integrity

The **25 annual records** are frozen from `statsmodels 0.14.6` (Gill teaching panel). See `data/source_register.csv` for exact URLs, grades, original-release dates (**UNKNOWN**), observation periods, revision policy (**UNKNOWN**), copyright note and access date. Data QA asserts year continuity, positivity, no nulls, TIME-to-year mapping and spot checks. Frozen raw SHA-256: `e8fc38e9f887dc696f578baf7cd240b53648002d53135708ae97d3bde1800d37`. Grade B curated dataset, not official contemporaneous vintage; no fabricated corporate or securities data.

## 05. Point-in-Time Availability

At formation year **t**, all predictor features use **t−1 and t−2** only. Labels for a training origin j enter the fit only if **j+h ≤ t−1**; this purges overlapping targets and adds a conservative one-year label buffer. All standardization is computed on the training window only. **However historical actual release dates and revisions are UNKNOWN**, so this remains a retrospective fixed-snapshot experiment, not an authentic PIT backtest.

## 06. Factor Construction

Let \(g^P_{x,t}=100\log(P_{x,t-1}/P_{x,t-2})\). The fixed relative-cost relief factor is **\(F_t=-g^P_{Cu,t}+g^P_{Al,t}\)**, with unit weights and no optimized scaling. Positive F means copper inflation was lower than aluminum inflation in the *prior* year. The target is \(y_{t,h}=100\log(C_{t+h}/C_t)\). Controls are lagged consumption growth, lagged real-income-index growth and lagged inventory-index change. Weight perturbations test both factor coefficients in [0.75,1.25].

## 07. Exposure & Transmission

This is a **single world copper-demand series**, not a stock universe: sector exposure is 1 by construction, not an estimated firm loading. Aluminum substitution is a hypothesized transmission channel; income and inventory are confounders. `data/exposure_map.csv` explicitly labels mining equities and firm-level weights as **NOT ESTIMATED**. A leave-one-company-out test is **not applicable**; leave-one-OOS-year-out is supplied instead. No investable exposure is asserted.

## 08. Outcomes & Baselines

Outcome: next-year **world copper consumption log growth (log percentage points)**, with alternative 2- and 3-year cumulative horizons. All models use the **same 10 OOS origins** for the primary horizon. Baselines: expanding historical mean; last observable consumption growth (persistence); fixed Ridge (alpha=8) on lagged consumption, income and inventory; factor-only Ridge; and augmented Ridge with the same controls plus F. Training-only standardization, no tuned hyperparameters or full-sample z-score.

## 09. Empirical Findings

OOS origins **1965–1974 (n=10)**: historical mean **7.625**, persistence **10.737**, controls **6.297**, full **6.290**, factor-only **7.363** RMSE (log-pp). The control-minus-full gain **0.0068 log-pp** is tiny relative to errors. These are **10 historical annual observations**, not a statistically powerful out-of-sample panel. `results/oos_predictions.csv` contains each forecast, training size and final admissible label year.

## 10. Robustness & Placebos

**1,000** three-year-block reordering placebo refits yielded exploratory upper-tail fraction **0.273** (not an exact p-value). **2,000** paired circular three-year-block bootstrap draws gave a 95% percentile interval **[-0.0040, 0.0155] log-pp**, crossing zero. **1,000** independent copper/aluminum weight perturbations were positive **66.5%** of the time; this is not independent evidence because weights are near the original. Leave-one-year-out, no-income/no-inventory ablations and 2–3-year horizons are computed in `results/`.

## 11. Regime Sensitivity

1965–1969 (n=5) control-minus-full RMSE gain **-0.0015**, 1970–1974 (n=5) **+0.0121**. Excluding formation years 1973–1974 yields **+0.0044** (n=8). The two-year horizon gain is **-0.2154** and three-year gain **-0.3857**. These tiny subperiods are descriptive only; none validates a stable effect.

## 12. Bias Audit & Verdict

**Publication/revision leakage:** original vintages unknown, cannot certify PIT. **Selection:** Gill's 25-year teaching sample, historical endpoint and a single world series are ex-post selected. **Endogeneity:** prices can react to demand and inventories. **Overlapping targets:** purged training, but OOS errors serially dependent; block bootstrap has only ten origins. **Multiple testing:** horizon/lag/ablation checks are exploratory and not corrected; do not promote best subgroup. **Survivorship:** no security universe exists. **Costs/capacity:** no tradable strategy or transaction costs. **Verdict:** tiny, unstable retrospective demand forecast gain; neither validated modern copper signal nor equity alpha.

## 13. Reproduction

From this folder: `python run_analysis.py`, `python -m pytest -q tests`, and `OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute research.ipynb --output reproduced.ipynb`. All source and output tables are versioned. The code uses deterministic RNG seed **20261027** and fixed Ridge alpha **8.0**. Logs under `logs/` record actual execution. From repository root run `python scripts/validate_studies.py`; its structural success does **not** prove PIT validity.

## 14. Next-Stage Protocol

Obtain monthly first-release refined-copper usage from ICSG, original-date aluminum/copper spot/futures quotes, independently dated GDP/industrial output and inventories; freeze publication timestamps and revision vintages. Build a preregistered modern 2000–2026 monthly design with expanding purged OOS, holdout post-2022, sector-neutral mining/smelting company exposure from contemporaneous filings and delisting-inclusive total returns. Include futures carry, slippage, fees, capacity, multiple-testing adjustment and genuine historical constituent universes. Until then, **do not trade on this pilot**.

## 15. Sources & Artifacts

**Primary:** [statsmodels World Copper Market 1951–1975](https://www.statsmodels.org/0.9.0/datasets/generated/copper.html), Gill dataset; access 2026-10-27, original release date UNKNOWN. **Context:** [ICSG Factbook 2023](https://icsg.org/download/factbook2023/) (published 2023-10-09) and [International Copper Association substitution note](https://internationalcopper.org/resource/copper-substitution-remains-low-in-2020/) (2021-04-13). **Artifacts:** `data/` frozen observations, SHA and register; `results/` OOS and 1000/2000-draw tables; `figures/` ten computed SVGs; `analysis.py`, `make_figures.py`, `tests/`, `research.ipynb`, `logs/`. Historical source release dates and revision histories remain **UNKNOWN**.

