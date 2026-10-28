# Protein Supply Divergence → U.S. Broiler Production (NAICS 311615)

**Status:** REPRODUCED RETROSPECTIVE POULTRY PRODUCTION MACRO PILOT — **NOT PIT / NOT EQUITY ALPHA**.  
**Data:** frozen `plotnine.data.meat` (USDA ERS-derived), 1944-01–2023-12; broilers/turkey from 1960-01.  
**Target:** three-month-ahead U.S. broiler-production YoY log growth, **not** company revenue or securities returns.  
**Run date:** 2026-10-28. **Primary lag:** 2 months. **Primary OOS:** 2010-01–2023-09, 165 monthly origins.

## 01. Abstract

**Research question:** Does the two-month-stale difference between U.S. beef/pork production growth and turkey production growth improve forecasts of broiler output three months ahead? A fixed nonlinear factor is evaluated against a historical mean, persistence, extrapolated momentum, autoregressive Ridge and a multivariate supply control. Across **165** purged expanding-window OOS forecasts, the augmented model RMSE is **4.7754 log-percentage points** versus **4.7506** for the multivariate control: **-0.0248 log-pp** improvement (negative = deterioration). The 1,000-block-reorder exploratory tail fraction is **0.8432**; the 2,000-draw paired block-bootstrap gain interval **[-0.0787, +0.0257]** includes zero. **Verdict:** a reproducible **negative** retrospective production-only test, not a PIT factor or equity alpha.

## 02. Research Design & Hypotheses

- **H1 / mechanism:** changes in beef and pork supply relative to turkey may anticipate broiler slaughter output through retail substitution, pricing, feed procurement and capacity decisions. The sign is uncertain because broiler production has its own biological and contractual lead times; substitution can also operate through prices rather than output.
- **H2 / forecast:** a fixed two-month-stale red-meat-versus-turkey signal improves **three-month-ahead broiler YoY log-growth** RMSE over the exact same expanding-window multivariate control forecasts.
- **H3 / stability:** gains survive input-component ablations, beef/pork weight perturbation, 12-month block-reorder placebo, paired block bootstrap, alternative lags and horizons, and structural regimes.
- **Null and failure standard:** the candidate adds no OOS improvement (RMSE gain ≤0), or any apparent gain is fragile under uncertainty/robustness. A macro volume association is not sufficient for an equity-return claim.

The primary factor, outcome, lag, horizon, 2010 holdout start, Ridge penalty and baseline set are **fixed in the source code**. There is no hyperparameter search for a favorable result. Post-hoc alternatives are explicitly reported but not substituted into the primary specification.

## 03. Industry Context

U.S. poultry slaughter and processing (NAICS **311615**) has a biological production cycle, federally inspected slaughter facilities and exposure to competing animal proteins. In the frozen source, 2023 U.S. broiler output sums to **46,383.4 million pounds**, **+5.64%** relative to 2019. These are **physical pounds**, not industry dollar revenue or an estimate of company addressable markets. Beef and pork are recorded on a different weight basis from ready-to-cook poultry; the factor uses within-category log changes rather than mixing pounds directly.

The [USDA ERS documentation](https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data/documentation) describes the `RedMeatPoultry_Prod` compilation from USDA NASS slaughter reports and its weight-basis differences. The [USDA NASS Poultry Slaughter survey](https://data.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Poultry_Slaughter/index.php) reports national slaughter and a next-month release schedule. Market growth does not imply predictable excess stock returns.

## 04. Data & Source Integrity

The **only numerical empirical input** is `data/raw_plotnine_meat_2023_snapshot.csv`, copied without modification from local **plotnine 0.15.3**, described in [plotnine's US Meat Production documentation](https://plotnine.org/reference/meat.html). Its SHA-256 is `b587c1e758ae43d87fe86fac0efc73da40aaeaf4046eba370f70fced554564a5`. It contains **960** monthly rows (1944-01–2023-12); **768** nonmissing broiler observations (1960-01–2023-12), as well as beef, pork and turkey. The original date on which the plotnine CSV was assembled and the original release dates of its historical monthly values are **UNKNOWN**. This is a redistributed, fixed, potentially revised dataset—not a directly retrieved 2026 ERS historical-vintage panel.

`data/source_register.csv` records each source's grade, exact URL, observed period, release date when known, vintage and revision caveats. **Grade A** is official USDA/SEC primary documentation; **Grade B** is the frozen redistributed plotnine numerical copy; **Grade C** is descriptive secondary material, not used. The current ERS page (updated **2026-10-27**) is a methodological and next-stage source, **not** evidence that this particular frozen file is the same revision. The QA asserts unique continuous monthly dates, positive production, expected schema and expected poultry availability. No missing poultry observations are filled or fabricated.

## 05. Point-in-Time Availability

At formation month `t`, every input uses an observation month **no later than `t−2`**. USDA NASS states that the poultry report appears around the 25th of the following month and revises the prior month; two months is a conservative observation-to-formation buffer. But the data are **not archived original-release vintages**, so the study cannot prove what an analyst in 1980 or 2010 would have seen. This unresolved revision leakage is a hard limit on any PIT claim.

For forecast origin `t`, the training set includes a prior formation origin `s` only when its target month `s+h` plus the two-month reporting buffer is ≤ `t`. With primary `h=3`, this is **`s ≤ t−5`**, purging labels that were not yet available. Each training fold re-estimates means/scales from its own training observations only. OOS training sizes range from **579** to **743**; no future target is used in fitting.

## 06. Factor Construction

Let `P(c,t)` denote monthly physical output for category `c` and define `g(c,t)=100×ln[P(c,t)/P(c,t−12)]` (log-percentage points). The predeclared candidate is:

`F(t) = tanh( {0.5*g(beef,t−2) + 0.5*g(pork,t−2) − g(turkey,t−2)} / 20 )`.

The weights **0.5/0.5/−1**, lag **2** and scale **20** are fixed, not fit or tuned on the outcomes. The tanh transformation bounds extreme growth observations without full-sample standardization. A positive value indicates a red-meat supply-growth premium over turkey; whether that should raise or lower broiler output is an empirically falsifiable channel, not a guaranteed sign. The 1,000 sensitivity draws perturb beef weight over `[0.2,0.8]`, with pork weight `1−beef_weight`.

## 07. Exposure & Transmission

`data/company_exposure_map.csv` contains **qualitative**, explicitly dated company examples: **Tyson Foods (TSN)** reported separate Beef, Pork, Chicken and Prepared Foods segments in its [2023 Form 10-K filed 2023-11-13](https://www.sec.gov/Archives/edgar/data/100493/000010049323000105/tsn-20230930.htm); **Pilgrim's Pride (PPC)** reported poultry operations and geographical exposure in its [2023 Form 10-K filed 2024-02-27](https://www.sec.gov/Archives/edgar/data/802481/000080248124000015/ppc-20231231.htm). Those filing dates are **later than most of the empirical sample**; the filings are not retrospectively assigned as historical exposures. No invented segment weights, share prices, company revenue series or dividend returns enter this model.

A national broiler production increase may coincide with weaker margins if feed costs or output prices move adversely. The observed industry target therefore **cannot** be equated with Tyson or Pilgrim's earnings, let alone stock returns. **Leave-one-company-out is not applicable**; the robustness section instead removes one factor-input component at a time.

## 08. Outcomes & Baselines

Primary target: `Y(t+3)=100×ln[B(t+3)/B(t−9)]`, the **future** YoY broiler production log-growth, where `B` is monthly broiler output. This is a production-level macro lead test, not a security panel. At each eligible origin, all models are fitted on the same target observations available by the formation month and predict the same outcome.

Baselines: expanding **historical target mean**; last observable **broiler YoY persistence**; fixed two-point **momentum extrapolation**; **AR Ridge** on stale broiler YoY and three-month momentum; and **macro/supply control Ridge** on stale broiler YoY, stale broiler YoY at a longer lag, stale three-month broiler momentum and stale red-meat YoY. **Augmented Ridge** adds `F(t)` to the macro control; **factor-only Ridge** uses `F(t)` alone. Ridge penalty **α=10** is fixed for all models. Train-only centering and standardization avoid full-sample z-score leakage.

## 09. Empirical Findings

**Primary scorecard, 165 common OOS origins (2010-01 to 2023-09; RMSE/MAE in log-pp):**

| Model | N | RMSE ↓ | MAE ↓ |
|---|---:|---:|---:|
| ar_ridge | 165 | 4.7309 | 3.7209 |
| macro_control | 165 | 4.7506 | 3.7592 |
| augmented | 165 | 4.7754 | 3.7757 |
| factor_only | 165 | 4.8531 | 3.8113 |
| historical_mean | 165 | 4.8879 | 3.8526 |
| persistence | 165 | 5.9102 | 4.7783 |
| momentum | 165 | 8.2512 | 6.6074 |

The augmented model's **-0.0248 log-pp** RMSE gain relative to controls is **negative**, so H2 fails. The historical-mean and AR baselines are essential: adding complexity is not automatically better. The full-panel factor/future-target Spearman correlation is **-0.0937**, a descriptive *time-series* correlation, **not** an equity Rank IC. Figures `05_oos_predictions.svg`, `06_rmse_scorecard.svg` and `07_loss_gain.svg` show forecasts, baseline ranking and cumulative paired squared-loss gain.

## 10. Robustness & Placebos

**Block-aware exploratory placebo:** 1,000 factor reorders preserve contiguous 12-month blocks, shuffle the blocks, then re-fit the augmented Ridge for every OOS origin. The fraction of placebo RMSE gains ≥ observed is **0.8432** (add-one count). This is an **exploratory tail fraction, not an exact p-value**, because reordering blocks does not condition on all cross-series dependence.

**Paired moving-block bootstrap:** 2,000 circular 12-month block resamples of the OOS error pairs yield a 95% interval for control-minus-augmented RMSE of **[-0.0787, +0.0257] log-pp**, crossing zero. **Exposure perturbation:** 1,000 draws of the beef/pork mix produce positive gain in **0.0%** of draws. These are not 1,000 independent market histories.

**Leave-one-component-out and ablations:**

| Factor input case | RMSE gain vs same control (log-pp) |
|---|---:|
| base_equal_beef_pork_minus_turkey | -0.0248 |
| beef_only_minus_turkey | -0.0167 |
| pork_only_minus_turkey | -0.0196 |
| red_meat_only | +0.0032 |
| negative_turkey_only | -0.0293 |
| factor_sign_flipped | -0.0248 |

The tiny positive `red_meat_only` result is a **post-hoc ablation**, not evidence for the original candidate; multiple comparisons are unadjusted. A sign-flipped factor is algebraically equivalent under symmetric Ridge and is **not** a valid independent falsification. Leave-one-security-out is unavailable because no security-level target exists.

## 11. Regime Sensitivity

| OOS regime | N | Control RMSE | Augmented RMSE | Gain (log-pp) |
|---|---:|---:|---:|---:|
| 2010-2019 | 120 | 4.5982 | 4.6106 | -0.0124 |
| 2020-2021 | 24 | 5.2992 | 5.4403 | -0.1411 |
| 2022-2023 | 21 | 4.9401 | 4.8864 | +0.0536 |

The pre-2020 and pandemic-era slices fail, while the short 2022–2023 slice is positive; the latter cannot rescue the overall negative result. The full lag/horizon grid is reported rather than choosing the most favorable cell:

| Observation lag (months) | Forecast horizon (months) | OOS N | Gain (log-pp) |
|---:|---:|---:|---:|
| 1 | 1 | 167 | -0.0058 |
| 1 | 3 | 165 | -0.0130 |
| 1 | 6 | 162 | -0.0591 |
| 1 | 12 | 156 | -0.0428 |
| 2 | 1 | 167 | -0.0021 |
| 2 | 3 | 165 | -0.0248 |
| 2 | 6 | 162 | -0.1371 |
| 2 | 12 | 156 | -0.0960 |
| 3 | 1 | 167 | -0.0135 |
| 3 | 3 | 165 | -0.0487 |
| 3 | 6 | 162 | -0.1201 |
| 3 | 12 | 156 | -0.0606 |
| 6 | 1 | 167 | -0.0674 |
| 6 | 3 | 165 | -0.1248 |
| 6 | 6 | 162 | -0.0379 |
| 6 | 12 | 156 | -0.0471 |

No alternative specification is promoted to the headline. Structural changes in poultry processing, product mix, feed costs, biological cycles and the pandemic can all invalidate stable relationships.

## 12. Bias Audit & Verdict

- **Lookahead:** release-proxy lags and purged training labels are enforced, but historical revision/vintage leakage remains unresolved.
- **Selection:** the factor was selected on economic intuition; this is not a preregistered untouched holdout or a causal experiment.
- **Survivorship:** physical national production is not an equity universe; the two company examples are 2023-only and not a historical security sample.
- **Multiple testing:** 16 alternative lag/horizon checks and component ablations are descriptive; their best result is not reported as an independent discovery.
- **Dependence and uncertainty:** overlapping future YoY outcomes and time-series autocorrelation motivate block-aware null and bootstrap; neither is a definitive inferential test.
- **Costs and capacity:** no security strategy is implemented, so trading costs, dividend adjustments, delistings, capacity and investability are untested.
- **Unit consistency:** red meat and poultry have different reported weight bases; only within-series growth is compared.

**Verdict:** **H2 fails** (the primary augmented RMSE is worse than control); H3 is not supported by the exploratory placebo, bootstrap and weight checks. H1 remains a plausible economic mechanism but is **not demonstrated as a predictive factor**. This is a reproducible retrospective **broiler-production macro falsification pilot**, not a PIT fundamental lead or equity alpha.

## 13. Reproduction

From the study directory in a clean checkout with Python ≥3.10:

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m pytest -q tests
jupyter nbconvert --to notebook --execute research.ipynb --output research.executed.ipynb
# from repository root:
python scripts/validate_studies.py
```

The notebook is not a stub: it contains 15 substantive chapters, executable formulas, data QA, OOS scorecards, release cutoff checks, placebo/bootstrap outputs, robustness tables, industry interpretation and embedded SVG/Matplotlib figures. The frozen source and output files allow numeric recomputation. **GitHub Actions structural validation is a separate check**, and success does not establish point-in-time correctness. Execution evidence is recorded in `logs/`; when running independently, record the installed package versions and any numerical differences.

## 14. Next-Stage Protocol

1. **PIT source:** acquire each historical NASS monthly Poultry Slaughter and ERS revision file with publication date and re-create the real-time broiler/red-meat/turkey vintage panel. The current 2026 ERS data page is not a substitute.
2. **Mechanism:** join hatchery placements, feed-price futures, cold-storage inventories, wholesale protein prices and weather/biosecurity shocks, respecting their actual publication calendars.
3. **Firm fundamentals:** collect dated Tyson/Pilgrim's segment-level sales, unit volume, margins and guidance from filings **as originally published**; evaluate lead-lag with separate company outcomes and exclusions.
4. **Returns:** obtain historical dividend/split-adjusted **total** returns, delisted peers and industry benchmark, then test security-level IC/spreads with transaction costs and borrow/turnover.
5. **Statistical design:** preregister one signal, one target and an unseen evaluation period; control for correlated alternative factors and the multiplicity of tested horizons.
6. **Fail honestly:** if real-time and fundamentals tests do not improve simple baselines, retain the negative result rather than rebranding it as alpha.

## 15. Sources & Artifacts

| Grade | Source | Exact URL | Role / date |
|---|---|---|---|
| B | plotnine `meat` dataset | https://plotnine.org/reference/meat.html | Empirical frozen copy, original bundle publication date **UNKNOWN**, observed 1944–2023 |
| A | USDA ERS Livestock and Meat Domestic Data | https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data | Updated **2026-10-27**; current page only, not the frozen input |
| A | USDA ERS methodology | https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data/documentation | Updated **2026-09-29**, series definitions and revisions |
| A | USDA NASS Poultry Slaughter | https://data.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Poultry_Slaughter/index.php | Undated survey guide; next-month release/revisions |
| A | Tyson 2023 Form 10-K | https://www.sec.gov/Archives/edgar/data/100493/000010049323000105/tsn-20230930.htm | Filed **2023-11-13**, qualitative company mapping only |
| A | Pilgrim's Pride 2023 Form 10-K | https://www.sec.gov/Archives/edgar/data/802481/000080248124000015/ppc-20231231.htm | Filed **2024-02-27**, qualitative company mapping only |

**Artifact map:** `data/raw_plotnine_meat_2023_snapshot.csv` (immutable frozen input), `data/derived_formation_panel.csv`, `data/source_register.csv`, `data/company_exposure_map.csv`, `run_analysis.py`, `research.ipynb`, `results/summary.json`, `results/baseline_scorecard.csv`, `results/oos_predictions.csv`, `results/placebo_draws.csv`, `results/bootstrap_draws.csv`, `results/weight_perturbations.csv`, `results/lag_horizon_checks.csv`, `results/ablation_checks.csv`, `results/regime_checks.csv`, 13 diagnostic SVGs in `figures/`, tests in `tests/` and execution logs in `logs/`.
