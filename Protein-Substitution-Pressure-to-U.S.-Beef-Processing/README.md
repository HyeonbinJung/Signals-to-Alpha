# Poultry–Pork Supply Divergence → U.S. Beef Processing (NAICS 311611)

**Status:** REPRODUCED RETROSPECTIVE BEEF PROCESSING MACRO PILOT — **NOT PIT / NOT EQUITY ALPHA**.  
**Target:** U.S. beef physical production YoY log growth six months ahead, **not** Tyson revenue, EPS or total return.  
**Frozen source:** plotnine 0.15.3 redistributed USDA ERS monthly production, 1944-01–2023-12; poultry from 1960-01.  
**OOS:** 2008-01–2023-06; 186 purged expanding-window origins; assumed two-month release buffer; 2026-10-28 execution.

## 01. Abstract

**Research question.** Does a two-month-stale poultry-versus-pork production-growth divergence forecast six-month-ahead U.S. beef processing output growth beyond own-industry history and a competing-protein supply control? This is a **falsifiable, retrospective national-volume** study of beef processing (NAICS 311611), distinct from the repository's poultry slaughtering/processing study (NAICS 311615). The source is a frozen, redistributed USDA-origin monthly meat-production dataset; its historical first-release vintages are **UNKNOWN**.

**Primary result.** Across **186** purged expanding-window origins (2008-01 to 2023-06), the factor-augmented model RMSE is **5.8986 log-percentage points** versus **5.8723** for the matched supply-control model: an incremental gain of **-0.0263 log-pp** (negative means deterioration). A 1,000-draw 12-month-block exploratory placebo has upper-tail fraction **0.7522**; the 2,000-draw paired circular-block bootstrap gain interval **[-0.1152, +0.0631]** crosses zero. **Verdict: no stable incremental predictive value; NOT PIT / NOT EQUITY ALPHA.**

## 02. Research Design & Hypotheses

**H1 — substitution mechanism.** Lagged acceleration in poultry output relative to pork could proxy shifts in retail protein substitution and processing capacity allocation, with uncertain sign for beef output because beef is governed by cattle herd availability and long biological lead times. An alternative mechanism is a common protein demand cycle, which would disappear once beef and pork history is controlled.

**H2 — incremental forecast.** A fixed, nonlinear poultry-minus-pork factor improves six-month-ahead beef YoY output forecasts relative to the same training origins and four lagged own-industry/competing-protein controls.

**H3 — robustness.** Improvement survives 12-month block reordering, block bootstrap, component ablations, broiler/turkey exposure perturbation, alternative lags/horizons, regime splits, and leave-one-OOS-year-out checks.

**Null and failure criterion.** Incremental OOS RMSE gain ≤ 0, bootstrap uncertainty spanning zero, or nonpersistent regime/ablation effects fails the primary thesis. The six-month horizon, 70/30 poultry weights, lag, 2008 OOS start, Ridge penalty and baselines are fixed in code; alternate grids are post-hoc diagnostics, not model selection. This is **not** an ex ante registered investment strategy.

## 03. Industry Context

U.S. animal slaughtering and processing includes beef processing under **NAICS 311611**, while the earlier broiler research targets **NAICS 311615**. Beef processing depends on cattle supply, packer capacity, export demand, labor, input costs and margins. In the frozen physical-volume series, 2023 beef production totals **26,964.3 million lb**, versus **27,154.6 million lb** in 2019 (**-0.70%**); this is **not** industry revenue.

The USDA ERS documentation describes the federally inspected `RedMeatPoultry_Prod` compilation and different weight bases for red meat and poultry. We compare **within-series log growth rates**, never aggregate raw pounds across protein categories. Tyson Foods FY2023 SEC filing reports **$19,325 million Beef segment sales** and **−$91 million Beef segment operating income**, demonstrating why physical output does not map mechanically to margins. Tyson's fiscal year ends in September; the national production calendar-year series is not directly aligned to it.

## 04. Data & Source Integrity

**Frozen empirical input:** `data/raw_plotnine_meat_2023_snapshot.csv`, **960 monthly observations** from 1944-01 to 2023-12, exactly matching the bundled `plotnine 0.15.3` dataset, with SHA-256 `b587c1e758ae43d87fe86fac0efc73da40aaeaf4046eba370f70fced554564a5`. Poultry components begin 1960-01; the fully observed formation panel contains **748** monthly rows. No missing production is imputed. QA checks schema, continuity, duplicates, positive quantities and nonmissing formation variables.

`data/source_register.csv` has **Grade A** USDA/SEC original documentation and filing, and **Grade B** the frozen redistributed numerical series. There is **no Grade A historical numerical-vintage panel**; the official USDA current page is NOT the vintage of the frozen file. The 2023 SEC filing supplies a **separate, dated** nine-row FY2021–FY2023 Tyson segment-fundamentals table, not an OOS issuer forecast panel. No Grade C source is used numerically. Original publication dates for the bundled monthly observations are **UNKNOWN**; the dataset's bundled assembly date is also **UNKNOWN**.

## 05. Point-in-Time Availability

At forecast formation month *t*, every model input is observed no later than **t−2 months**. This is a conservative **assumed** publication buffer, not verified historical release metadata. For a training origin *s* with horizon *h=6*, its label is permitted only when **s+6+2 ≤ t**, i.e. *s ≤ t−8*. The expanding window includes only labels available by the origin; all standardization and Ridge coefficients are fit on each training fold, never on the full dataset.

The actual training set spans **555–740** rows per forecast. Because the fixed plotnine file may incorporate revisions made after each historical formation month, even this purge cannot prove true **point-in-time** validity. No feature's historical initial publication date has been independently archived and matched. Any apparent gain is retrospective association only.

## 06. Factor Construction

Let \(Q_{j,t}\) be USDA-origin physical monthly output for category \(j\), in million lb, and define \(g_{j,t}=100\log(Q_{j,t}/Q_{j,t-12})\) in log-percentage points. At formation month \(t\) with assumed two-month publication buffer, the fixed candidate is

\[F_t=\tanh\!\left(\frac{0.7g_{broiler,t-2}+0.3g_{turkey,t-2}-g_{pork,t-2}}{20}\right).\]

The target is \(Y_t=g_{beef,t+6}\), six-month-ahead **beef production YoY growth**, not beef price, company sales, EPS or shareholder total return. No beef outcome enters the candidate factor. The 70/30 and divisor 20 are prespecified descriptive scale choices; exposure-weight sensitivity is reported separately and not used to pick a favorable weight. Factor sign is economically ambiguous and must be tested rather than assumed.

## 07. Exposure & Transmission

The company mapping is **dated and descriptive**, not a fitted security panel. The SEC-filed Tyson FY2023 Form 10-K (filed 2023-11-13) distinguishes Beef ($19,325m sales), Pork ($5,768m) and Chicken ($17,060m) segments. These are issuer-specific FY2023 accounting categories, not U.S. national production shares, and **must not** be backdated to 2008–2022. See `data/company_exposure_map.csv` and `data/tyson_fy2023_sec_fundamentals.csv`.

**Transmission chain:** poultry/pork output divergence → hypothesized substitution/packer allocation → later national beef production → potentially issuer volumes, pricing and operating margins → **unmeasured** stock returns. Every arrow beyond national beef production is a hypothesis. The FY2021–FY2023 Tyson segment fundamentals are displayed as a small descriptive cross-check only; there is **no credible issuer-level OOS validation** and leave-one-company-out is **not estimable** with one mapped issuer.

## 08. Outcomes & Baselines

All models forecast the same beef-production target at exactly the same formation dates. **Historical mean** uses training labels only. **Persistence** uses two-month-stale beef YoY growth; **momentum** extrapolates the difference between stale beef YoY and its six-month-older value. **AR Ridge** uses three stale beef lags; **supply control** adds stale pork YoY; **factor only** uses just the candidate; **augmented** adds the factor to the supply control.

Ridge minimizes \(\sum_{s\in train}(Y_s-a-X_s\beta)^2+10\lVert\beta\rVert_2^2\) after **train-fold-only** centering and standardization, with unpenalized intercept. No full-sample scaling, target-dependent feature selection or hyperparameter optimization. The primary metric is OOS RMSE in log-pp; MAE and forecast bias are supplementary. There is no equity cross-section, so stock IC, top-minus-bottom return spreads, transaction costs and benchmark-adjusted total returns are **NOT COMPUTABLE**.

## 09. Empirical Findings

**Primary scorecard (lower RMSE better; identical 186 OOS origins):**

| model           |   n_oos |   rmse_log_pp |   mae_log_pp |   bias_log_pp |
|:----------------|--------:|--------------:|-------------:|--------------:|
| ar_ridge        |     186 |        5.8591 |       4.3729 |        0.8078 |
| supply_control  |     186 |        5.8723 |       4.3719 |        0.7991 |
| augmented       |     186 |        5.8986 |       4.3964 |        1.1146 |
| historical_mean |     186 |        6.0721 |       4.5443 |        1.0201 |
| factor_only     |     186 |        6.0761 |       4.5474 |        1.0091 |
| persistence     |     186 |        7.5926 |       5.8064 |        0.3029 |
| momentum        |     186 |       12.7314 |       9.4347 |        0.1578 |

The factor increases RMSE by **0.0263 log-pp** relative to supply controls; the AR Ridge baseline (**5.8591**) also beats the augmented model (**5.8986**). Full-panel factor-versus-future-beef-growth Spearman association is **+0.00024**, an exploratory association rather than an OOS rank IC. The paired loss chart shows when the factor harmed the forecast; a favorable subperiod is not sufficient to claim a stable effect. Separate SEC fundamentals table records Tyson FY2021–2023 Beef sales and operating income, but is not merged into the forecasting target.

## 10. Robustness & Placebos

**Exploratory 12-month-block factor reorder:** **1,000** full OOS refits with factor calendar blocks shuffled, preserving within-block structure. Upper-tail fraction for observed control-minus-augmented RMSE gain is **0.7522**; this is **not** an exact conditional permutation p-value because block reordering distorts long-run dependence and may alter correlations with controls.

**Paired circular-block bootstrap:** **2,000** 12-month-block resamples of the same 186 OOS forecast pairs; 95% gain interval **[-0.1152, +0.0631] log-pp**, spanning zero. **Weight perturbation:** **1,000** draws of broiler weight uniformly 0.1–0.9 (turkey = 1−w); **0.0%** beat the control. Component ablations:

| case                             |   n_oos |   gain_log_pp |
|:---------------------------------|--------:|--------------:|
| primary_70_30_poultry_minus_pork |     186 |       -0.0263 |
| broiler_only_minus_pork          |     186 |       -0.0099 |
| turkey_only_minus_pork           |     186 |       -0.0411 |
| poultry_only_no_pork             |     186 |       -0.0297 |
| negative_pork_only               |     186 |        0.0040 |
| linear_unbounded_factor          |     186 |       -0.0246 |

The **leave-one-OOS-year-out** test excludes each evaluation calendar year from score computation (16 years; no model refit) and retains a negative gain in **all 16 exclusions**. This is a stability diagnostic, not issuer leave-one-out. Company leave-one-out cannot be estimated from one firm and is explicitly **NOT TESTED**.

## 11. Regime Sensitivity

**Fixed primary specification by OOS calendar regime:**

| regime    |   n |   control_rmse |   augmented_rmse |   gain_log_pp |
|:----------|----:|---------------:|-----------------:|--------------:|
| 2008-2014 |  84 |         5.1407 |           5.2578 |       -0.1171 |
| 2015-2019 |  60 |         6.3568 |           6.2422 |        0.1146 |
| 2020-2021 |  24 |         6.5600 |           6.6002 |       -0.0401 |
| 2022-2023 |  18 |         6.3983 |           6.5237 |       -0.1254 |

A positive gain in 2015–2019 is offset by negative gains in 2008–2014, 2020–2021 and 2022–2023. The full lag/horizon grid is **post-hoc** and must not be used to reselect a new primary result:

|   lag_months |   horizon_months |    n_oos |   control_rmse |   augmented_rmse |   gain_log_pp |
|-------------:|-----------------:|---------:|---------------:|-----------------:|--------------:|
|       1.0000 |           1.0000 | 191.0000 |         5.9698 |           5.9517 |        0.0181 |
|       1.0000 |           3.0000 | 189.0000 |         6.0377 |           6.0289 |        0.0088 |
|       1.0000 |           6.0000 | 186.0000 |         5.8513 |           5.9028 |       -0.0515 |
|       1.0000 |          12.0000 | 180.0000 |         6.0144 |           6.0818 |       -0.0674 |
|       2.0000 |           1.0000 | 191.0000 |         5.6292 |           5.6144 |        0.0148 |
|       2.0000 |           3.0000 | 189.0000 |         5.9626 |           5.9804 |       -0.0178 |
|       2.0000 |           6.0000 | 186.0000 |         5.8723 |           5.8986 |       -0.0263 |
|       2.0000 |          12.0000 | 180.0000 |         5.8509 |           5.8854 |       -0.0345 |
|       3.0000 |           1.0000 | 191.0000 |         6.0082 |           5.9994 |        0.0088 |
|       3.0000 |           3.0000 | 189.0000 |         5.7096 |           5.6986 |        0.0110 |
|       3.0000 |           6.0000 | 186.0000 |         5.6458 |           5.6479 |       -0.0022 |
|       3.0000 |          12.0000 | 180.0000 |         6.0126 |           6.1230 |       -0.1104 |
|       6.0000 |           1.0000 | 191.0000 |         5.8383 |           5.8862 |       -0.0479 |
|       6.0000 |           3.0000 | 189.0000 |         5.6422 |           5.6445 |       -0.0024 |
|       6.0000 |           6.0000 | 186.0000 |         6.0599 |           6.0664 |       -0.0066 |
|       6.0000 |          12.0000 | 180.0000 |         5.9065 |           5.9771 |       -0.0706 |

Overlapping six-month YoY targets create strong serial dependence; the paired 12-month block bootstrap is a sensitivity exercise, not a guarantee of valid asymptotic coverage under regime shifts. The 2022–2023 regime has only 18 OOS origins.

## 12. Bias Audit & Verdict

**Lookahead:** all features shifted by the assumed two-month buffer, training labels purged until target month + buffer, train-only preprocessing. **Unresolved:** historical revisions and exact first-publication vintages. **Selection:** industry and formula chosen after surveying repository topics; 70/30 weights and horizon were fixed before running the primary scorecard, but the study is not preregistered. **Multiple testing:** 16 lag/horizon combinations and ablations are descriptive, not family-wise-corrected discoveries. **Survivorship:** the national series has no security-universe selection, while the one-issuer SEC mapping is a surviving-company illustration and cannot validate equity effects. **Regimes:** pandemic, cattle-cycle and structural-break exposure. **Costs/capacity:** not computable without tradable return signals. **Issuer fundamentals:** three SEC fiscal-year rows, not a historical matched panel; company returns and benchmark-adjusted total returns absent.

**Verdict: negative retrospective beef-production macro-factor falsification.** Do not describe the factor as an investable alpha, a PIT backtest, or a reliable fundamental lead. The null is not rejected by the exploratory placebo and bootstrap uncertainty; the primary model worsens the benchmark.

## 13. Reproduction

From this study directory, with Python 3.11+ and dependencies installed, run:

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python run_analysis.py
jupyter nbconvert --to notebook --execute research.ipynb --output executed_research.ipynb
```

`run_analysis.py` writes a frozen formation panel, OOS forecast table, baseline scorecard, 1,000 placebo draws, 2,000 bootstrap draws, 1,000 exposure perturbations, lag/horizon and ablation tables, 16 leave-one-year-out scores, regime checks, summary JSON and **15 computed SVG diagnostics**. The committed notebook contains executed code outputs and SVG images; `logs/` includes actual analysis/test/notebook execution records. The fast cumulative sufficient-statistics Ridge routine is unit-tested against the slow fold-by-fold implementation. For the repository-wide structure check, run `python scripts/validate_studies.py` from repository root. GitHub Actions structural CI is a separate gate, not numerical/PIT validation.

## 14. Next-Stage Protocol

1. Acquire dated USDA NASS *Livestock Slaughter* first-release PDFs/CSVs and monthly ERS historical revisions; build an observation-level `(observation_month, first_release_timestamp, revision_vintage, value)` panel. Freeze retrieval hashes and compare the plotnine file to the corresponding official monthly values.
2. Add cattle-on-feed placements, slaughter counts, feed prices, cold-storage inventory, boxed-beef spreads, imports/exports, plant utilization and weekly retail price series. Predefine mechanistic lags before a fresh holdout and test substitution versus common-demand explanations.
3. Build a multi-issuer, historical-universe SEC segment dataset with actual 10-K/10-Q filing timestamps and consistent fiscal quarters; test sales and margins separately from physical output, with issuer exclusions and revision-aware alignment.
4. Only after successful fundamental evidence, obtain delisting-inclusive, dividend/split-adjusted security total returns, benchmark and factor exposures, execution timing, borrow and costs. Pre-register a clean future holdout, report multiple-testing adjustments and decline an alpha claim if net OOS gains fail.

## 15. Sources & Artifacts

**Primary references:** [plotnine frozen-source documentation](https://plotnine.org/reference/meat.html) (Grade B numerical redistribution; assembly date UNKNOWN); [USDA ERS production documentation](https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data/documentation) (Grade A definitions; page date UNKNOWN); [USDA ERS Livestock and Meat Domestic Data](https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data) (Grade A current source, updated 2026-10-27; NOT the numerical vintage); [Tyson FY2023 SEC 10-K](https://www.sec.gov/Archives/edgar/data/100493/000010049323000105/tsn-20230930.htm) (Grade A, filed 2023-11-13; segment fundamentals only). Exact observation periods, revision/vintage caveats and roles are in `data/source_register.csv`.

**Artifacts:** `data/raw_plotnine_meat_2023_snapshot.csv`, `data/derived_formation_panel.csv`, `data/tyson_fy2023_sec_fundamentals.csv`, `data/company_exposure_map.csv`, `results/*.csv`, `results/summary.json`, `figures/*.svg`, `research.ipynb`, `run_analysis.py`, `tests/test_analysis.py`, `requirements.txt`, `study.json`, `logs/`. Source grades describe provenance and do **not** certify point-in-time numerical integrity.
