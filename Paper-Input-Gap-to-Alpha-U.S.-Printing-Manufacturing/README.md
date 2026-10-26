# Paper-Input Gap → U.S. Printing Production: A Retrospective Macro Falsification

**Research date:** 2026-10-26 · **Data release:** 2026-10-16 · **Scope:** U.S. NAICS 323 printing and related support activities · **Evidence level:** REPRODUCED RETROSPECTIVE MACRO PILOT; NOT PIT; NOT EQUITY ALPHA.

## 01. Abstract

**Research question:** Does a fixed paper-production-minus-manufacturing growth gap, observed before a forecast origin, improve three-month-ahead year-over-year U.S. printing output forecasts relative to printing persistence and general manufacturing conditions? In **201** official G.17 monthly observations (2010-01–2026-09), **114** purged expanding-window OOS origins (2017-01–2026-06) show the paper-augmented model at **6.366 log percentage-point RMSE** versus **6.184** for the multivariate control, **6.326** for a historical mean, and **7.071** for persistence. The incremental RMSE effect (control minus full) is **−0.182**, an observed deterioration. This is a fixed, revised-snapshot **falsification**, not a vintage-valid forecast or investable security signal.

## 02. Research Design & Hypotheses

**H1 (mechanism):** Upstream paper production growth in excess of aggregate manufacturing growth anticipates later printing production growth. **H2 (incrementality):** The pre-specified paper gap reduces OOS RMSE against a printing-persistence-plus-manufacturing baseline. **H3 (stability):** Any improvement remains positive outside the 2020 pandemic and across 1/3/6-month horizons and 1/2/3-month input buffers. **Null:** The factor adds no OOS forecasting value once printing persistence and broad manufacturing are known. Failure criterion: no gain over a simple baseline, no positive incremental RMSE, or unstable regime/exposure sensitivity. Counterthesis: digitization, printing's secular decline, inventory cycles, import substitution and nonprinting paper demand may decouple paper production from domestic print activity.

## 03. Industry Context

The Federal Reserve's G.17 series identify **G322** as paper manufacturing (NAICS 322) and **G323** as printing and related support activities (NAICS 323); **B00004** is the manufacturing aggregate. Paper is a physical substrate for parts of the printing supply chain, but packaging, tissue and other paper categories are not synonymous with printing demand. Printing's digital substitution, product mix and imported inputs can weaken the proposed lead. The official release and its source definitions are dated in the register; **reliable market size, issuer share and forward growth forecasts were not collected**, so no invented TAM or sector CAGR is offered. Official G.17 source: https://www.federalreserve.gov/releases/g17/Current/ipdisk/alltables.htm (last update 2026-10-16).

## 04. Data & Source Integrity

**Primary A-grade**: 2026-10-16 Federal Reserve G.17 `ip_sa.txt` year rows for G322, G323, B00004, 2010–2026 (201 months per series), industrial production index 2017=100, seasonally adjusted. The 51 original year rows are preserved in `data/fed_g17_transcribed_rows_2026-10-16.txt`; the deterministic parser exports `data/frozen_g17_2010_2026.csv`. **Manual transcription** is explicitly disclosed: three spot dates were checked, but full independent row-level extraction was unavailable. **B-grade**: FRED paper series metadata; **C-grade**: G.17 methodology. Exact URLs, observed ranges, revision limitations and known/unknown release dates appear in `data/source_register.csv`. The frozen raw-row SHA-256 is `147f482e7f59d8692fd7f2a44d0a2d5ce531156fba28325addc69e5167837459`. Data QA rejects duplicates, nonpositive observations, missing months and source spot-check mismatches.

## 05. Point-in-Time Availability

At forecast origin month **t**, the model uses only snapshot observations dated **t−1** or earlier. The target is printing production YoY growth at **t+3**. A historical training origin **j** is allowed only if **j+3+1 ≤ t−1**, i.e., **j ≤ t−5**, assuming one additional month for outcome publication. **These buffers do not reconstruct historical vintages:** all indices were taken from the revised 2026-10-16 snapshot; original release-date values and back revisions are **UNKNOWN**. No claim of historical real-time feasibility is made. ALFRED/G.17 vintage collection is required before PIT publication.

## 06. Factor Construction

Let `g_s(t) = 100 ln(IP_s(t)/IP_s(t−12))` in log percentage points. At origin `t` with one-month buffer, the **fixed, untuned** factor is `F_t = g_paper(t−1) − g_manufacturing(t−1)`. The target is `Y_t = g_printing(t+3)`; controls are `[g_printing(t−1), g_manufacturing(t−1)]`. The augmented model adds `F_t` to these controls; paper-only is an ablation. No ex-post smoothing, look-ahead z-scoring, fitted sector weights or target-based feature selection. Ridge penalty is **8** for all regression models; each training window alone supplies feature means/standard deviations.

## 07. Exposure & Transmission

The mechanism is **industry-level** (G322 input → G323 outcome), not a dated issuer-level sales-exposure model. `data/exposure_map.csv` identifies each industry code, role, observation date, source URL and limitations. Paper-versus-manufacturing coefficients of **0.7–1.3** are perturbed in **200** pre-specified sensitivity refits. Issuer exposures, public-company revenue segments, corporate fundamentals and total-return histories are **UNKNOWN/NOT TESTED**; leave-one-company-out is inapplicable. Leave-one-forecast-year-out is used instead, and cannot substitute for issuer exclusion.

## 08. Outcomes & Baselines

One dependent variable only: **three-month-ahead printing YoY log growth**, not future price, revenue or stock returns. All five models use the **same 114 origins**: expanding historical mean, last available printing YoY persistence, Ridge controls (printing persistence + aggregate manufacturing), Ridge controls + paper gap, and Ridge paper gap alone. Train labels are purged by five origin months, with ≥36 training samples and no future target values in training. Metrics: OOS RMSE, MAE, paired squared-error differences and uncertainty. Cross-sectional Rank IC, long-short return spreads, transaction-cost-adjusted returns and leave-one-security-out are **not defined** for this single macro series.

## 09. Empirical Findings

| Model | N | RMSE (log pp) | MAE (log pp) |
|:--|--:|--:|--:|
| Historical mean | 114 | 6.326 | 4.349 |
| Printing persistence | 114 | 7.071 | 4.475 |
| Printing + manufacturing controls | 114 | **6.184** | **3.884** |
| Controls + paper gap | 114 | **6.366** | 4.181 |
| Paper gap alone | 114 | 6.703 | 4.690 |

The primary paper gap **worsens** RMSE by **0.182 log pp** versus the multivariate control and fails the historical mean as well. The scorecard and individual forecasts are in `results/scorecard.csv` and `results/walk_forward_oos.csv`. Figures show industry levels, YoY growth, factor path, forecasts, baseline comparison, cumulative loss and uncertainty; these are computed from the actual frozen rows, not illustrative charts.

## 10. Robustness & Placebos

A **1,000-refit 12-month block-aware exploratory placebo** shuffles/resamples the paper-factor sequence and re-estimates OOS models; its upper-tail fraction relative to the observed incremental RMSE is **0.987**. This is **not an exact exchangeability-valid permutation p-value** because block resampling changes temporal dependence and the data are revised. A **2,000-draw paired 12-month moving-block bootstrap** yields a 95% interval **[−0.657, 0.085] log pp** for control-minus-full RMSE, containing zero. All **200** paper-weight perturbations in `[0.7,1.3]` fail to produce positive incremental improvement. Leave-one-forecast-year-out improvements range **−0.307 to −0.023 log pp**. The control-versus-paper ablation and paper-only baseline fail to rescue the proposed incremental signal. Numerical draws and plots are committed in `results/` and `figures/`.

## 11. Regime Sensitivity

With 1-month, 3-month and 6-month prediction horizons, all tested one-to-three-month release-buffer combinations produce **negative** control-minus-full RMSE improvements (`results/robustness.csv`). Excluding 2020 produces **−0.206 log pp**; pre-2020 origins produce **−0.201**; post-2021 origins produce **−0.583**. These subgroup diagnostics reuse the original fitted OOS forecasts rather than re-optimizing within each regime, and overlapping forward YoY outcomes make naive independent-sample inference invalid.

## 12. Bias Audit & Verdict

**Look-ahead:** formation input dates and training-label purges are enforced; historical revised values remain a major unresolved look-ahead channel. **Selection:** one prespecified signal and one target; the study was chosen after reviewing prior sector coverage, so broader research-family multiple testing remains unadjusted. **Survivorship:** no issuer universe or security data. **Macro confounding:** paper and printing co-move with aggregate demand; aggregate manufacturing includes both industries, so causal identification is impossible. **Regime:** pandemic, digitization, import competition and structural decline. **Costs/capacity:** inapplicable without an investable asset and total-return panel. **Verdict: NEGATIVE RETROSPECTIVE MACRO-FACTOR FALSIFICATION; NO PIT, NO FIRM FUNDAMENTAL LEAD, NO EQUITY ALPHA.** The failed result is retained rather than optimized into significance.

## 13. Reproduction

From this directory after installing `requirements.txt`, run `OPENBLAS_NUM_THREADS=1 python run_analysis.py`, `OPENBLAS_NUM_THREADS=1 PYTHONPATH=. pytest -q tests`, and `OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute --inplace research.ipynb`. The run writes raw-derived data, metrics, forecasts, **1,000** placebo refits, **2,000** bootstrap draws, **200** exposure refits, regime checks, ten SVG figures and execution logs. From repository root run `python scripts/validate_studies.py`. The notebook contains executable code, tables and saved image outputs, not a small wrapper. **CI structural validation is separate from numerical reproduction and from PIT validity.**

## 14. Next-Stage Protocol

(1) Download and hash the full original G.17 release to independently reconcile all 603 transcribed values. (2) Build an ALFRED/archived G.17 vintage panel with actual month-by-month publication timestamps, and refit without revised-data leakage. (3) Split paper into packaging versus commercial-print substrate series; pre-register alternate mechanisms and exclude demand-cycle proxies that mechanically contain printing. (4) Acquire dated SEC segment sales and a survivorship-complete universe of printing companies; independently test revenue/EPS and then dividend-adjusted total returns against sector benchmarks, realistic costs and false-discovery corrections. (5) Hold out a genuinely future window and require consistent improvement over the mean and control before considering the factor further.

## 15. Sources & Artifacts

- Federal Reserve G.17 official seasonally adjusted table (release 2026-10-16): https://www.federalreserve.gov/releases/g17/Current/ipdisk/ip_sa.txt
- Federal Reserve historical table landing page (last update 2026-10-16): https://www.federalreserve.gov/releases/g17/Current/ipdisk/alltables.htm
- FRED IPG322S metadata (accessed 2026-10-26): https://fred.stlouisfed.org/series/IPG322S
- G.17 explanatory methodology: https://www.federalreserve.gov/releases/g17/About.htm
- `data/source_register.csv`, `data/source_qa.md`, `data/exposure_map.csv`, frozen raw text/CSV, derived formation panel; `run_analysis.py`, `requirements.txt`, `tests/`; `results/metrics.json`, scorecard, 114-origin forecasts, placebo, bootstrap, perturbations, leave-year-out, robustness and execution logs; ten actual-computation SVGs; fully executed `research.ipynb`.
