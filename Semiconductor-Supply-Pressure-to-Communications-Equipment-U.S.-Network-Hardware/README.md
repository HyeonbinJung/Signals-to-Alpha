# Semiconductor Supply Pressure → U.S. Communications Equipment Production

**Research date:** 2026-10-28 · **Sector:** NAICS 3342 communications equipment manufacturing · **Status:** REPRODUCED RETROSPECTIVE MACRO PILOT, NOT PIT, NOT EQUITY ALPHA.  
**Original upstream data:** 2026-10-19 fixed G.17 snapshot reused *verbatim* from this repository's semiconductor study. **No independent bulk redownload or historical-vintage reconstruction.**

## 01. Abstract

**Question:** Does a two-month-stale upstream semiconductor-production premium over aggregate manufacturing predict three-month-ahead U.S. communications-equipment manufacturing output growth beyond simple persistence and macro controls? This study reverses the economic transmission tested in the existing semiconductor study: here **communications equipment (NAICS 3342) is the target**, not the semiconductor industry. On 189 monthly observations (2011-01–2026-09), 110 expanding-window OOS origins (2017-05–2026-06) show an incremental RMSE gain of **0.0676 log percentage points** over a communications/momentum/manufacturing/computer control model (**8.3840 vs 8.4516**). The gain is modest, the exploratory 1,000-refit block placebo tail fraction is **0.1678**, and a 2,000-draw paired block bootstrap 95% interval **[−0.1885, 0.2816]** includes zero. **Verdict: a small, statistically inconclusive retrospective macro forecast improvement, not a PIT or investable alpha result.**

## 02. Research Design & Hypotheses

**H1 (mechanism):** upstream semiconductor production relative to aggregate manufacturing conveys future network-hardware production information. **H2 (incremental forecasting):** the fixed factor improves same-origin 3-month-ahead OOS RMSE over mean, stale persistence, momentum and a macro Ridge control. **H3 (robustness):** improvements survive 1,000 block-shuffle refits, 2,000 paired moving-block bootstrap draws, 1,000 exposure perturbations, regime exclusions, lag/horizon shifts and ablations. **Null:** conditional on controls the upstream premium adds no stable predictive information. A failure of the strongest simple baseline, a bootstrap interval containing zero, or reversal across sensible horizons blocks a strong conclusion. The mechanism can fail because U.S. network-hardware manufacturing uses imported semiconductors, offshore assembly, inventories and multi-quarter ordering cycles.

## 03. Industry Context

U.S. communications equipment manufacturing is classified under **NAICS 3342** and includes wired, wireless, broadcast and related network hardware; it is not the same as semiconductor manufacturing (NAICS 3344) or computer/peripheral manufacturing (NAICS 3341). U.S. Census NAICS is a classification, not a time-varying issuer exposure. Federal Reserve G.17 reports monthly manufacturing output indexes (2017=100, seasonally adjusted), **not sector revenue, market size in USD, or securities returns**. The 2026-10-16 G.17 release covers September 2026 and is an aggregate macro release; it cannot identify the firm-level transmission chain. The 2025 annual filings of Ciena and Cisco document networking businesses but do not identify their historical U.S.-manufactured NAICS 3342 share. No unsupported TAM or revenue-growth forecast is inserted.

## 04. Data & Source Integrity

Four frozen monthly series: `IPG3342S` (communications output, target), `IPG3344S` (semiconductor components), `IPG3341S` (computer equipment control) and `IPMAN` (aggregate manufacturing). The raw CSV has 189 complete monthly observations from January 2011 to September 2026, and matches **Git blob SHA `3d111120b93de0a5eb153d794772225f5dd1a6c4`** of the earlier semiconductor research input byte-for-byte. Source register `data/source_register.csv` records original URLs, publishers, grade A official provenance versus grade B inherited copy, release date, observation span, units and revision caveats. Checks verify continuous months, positive values, nonmissing data and expected columns. No source publication date is invented: historical release-vintage timestamps remain UNKNOWN.

## 05. Point-in-Time Availability

At month *t* the formation features use observations at **t−2** or earlier, allowing for publication delay; the 3-month-ahead target is `g_comm(t+3)`. Training origin *u* is eligible only when **u+3 ≤ t−2**, so all training labels are mature before formation. The 2026-revised snapshot was **not** available in 2011–2025, however; applying a two-month buffer does not cure vintage leakage. This is a retrospective fixed-snapshot study, explicitly **not PIT**. Future work requires a Federal Reserve/ALFRED release-vintage panel and exact publication timestamps.

## 06. Factor Construction

For series *j*, define `g_j(s)=100 ln(IP_j(s)/IP_j(s−12))`, in log percentage points. The predeclared, bounded signal is **`F(t)=tanh((g_sem(t−2)−g_man(t−2))/15)`**; 15 is a fixed scale in log percentage points, not fitted on the full sample. The target is `Y(t)=g_comm(t+3)`. The fixed sensitivity family replaces `g_sem` with `w*g_sem+(1−w)*g_computer` for 1,000 weights `w~Uniform(0.8,1.0)`, with seed 20261030; this is a *perturbation*, not an optimized production factor. All feature transforms are computed without looking ahead.

## 07. Exposure & Transmission

`data/company_exposure_map.csv` separates the **NAICS industry-level** 3342 target (weight 1.0), upstream 3344 input (weight 1.0 in the factor) and 3341 control from **descriptive issuer mapping**. Ciena's fiscal 2025 10-K reports Networking Platforms revenue **$3,676,377 thousand**, while Cisco's fiscal 2025 annual report reports Networking product revenue **$28,304 million**. These are *2025 global company categories*, not historical domestic NAICS production weights; issuer model weights are **NA**. Neither issuer is in the statistical target or return backtest. There is **no company panel**, so leave-one-company-out is **not applicable**; leave-one-OOS-year-out is used only as a time robustness diagnostic.

## 08. Outcomes & Baselines

The sole modeled outcome is **future U.S. communications-equipment industrial production YoY log growth**. Independent firm revenue, EPS, total-return and benchmark-adjusted return tests are **NOT PERFORMED**. All six forecasts share the same 110 OOS origins: expanding historical mean; stale communications persistence; persistence plus 3-month momentum; macro Ridge with stale communications, momentum, aggregate manufacturing and computer production; macro plus `F(t)`; and factor-only Ridge. Ridge penalty is fixed `alpha=10`; predictors are standardized **within each training window**; no post-selection tuning. First origin is 2017-05, and training labels are purged through `u+3<=t−2`. Evaluation uses RMSE, MAE, paired squared-loss diagnostics and sample counts, not invented stock IC or long-short spreads.

## 09. Empirical Findings

On 110 origins, OOS RMSE (log pp) is **mean 10.2697**, **persistence 8.9788**, **momentum 8.6808**, **macro 8.4516**, **macro + factor 8.3840**, and **factor only 9.6435**. The observed macro-minus-full improvement is **+0.0676 log pp** (about **0.8% of the macro RMSE**), with full-model MAE **6.7356** vs macro **6.8027**. The full-panel contemporaneous formation-factor/future-target correlation is **−0.3577**, contradicting a simple monotone positive mechanism and cautioning against interpreting the small OOS gain as a causal supply relationship. See `results/scorecard.csv`, `results/walk_forward_oos.csv`, and ten actual computed figures.

## 10. Robustness & Placebos

**Block-aware placebo:** 1,000 random reorderings of contiguous 12-month signal blocks, with the same expanding-window full-model refits; the upper-tail fraction `(1+#{null gain>=observed})/1001` is **0.1678**. This is an *exploratory randomization diagnostic*, not an exact p-value for a dependent time series. **Uncertainty:** 2,000 paired 12-month moving-block bootstrap resamples of the OOS forecast-error vectors give 95% RMSE-improvement interval **[−0.1885, 0.2816] log pp**, including zero. **Exposure:** 1,000 `w∈[0.8,1.0]` mixes yielded positive macro-relative improvements, but they are highly correlated variants of the same source and cannot establish significance. **Ablations:** removing the computer control improves fit, while removing momentum or manufacturing harms fit; the factor is not a stable standalone replacement. **Year exclusions:** every OOS year is excluded in turn and scored on remaining predictions; this is not leave-one-firm-out.

## 11. Regime Sensitivity

Macro-minus-full OOS RMSE improvements are **+0.1405** across 32 pre-2020 origins, **−0.3527** across 24 2020–2021 origins, and **+0.1792** across 54 post-2021 origins. The pre-2020 full model still fails that subsample's historical mean (**7.9670 vs 7.6122**). Horizon/lag tests find the main 3-month horizon benefit turns negative at **6 months** for all tested publication buffers (1–4 months), and at **4-month lag** even the 3-month forecast loses the gain. These are exploratory robustness diagnostics, not newly selected optimal parameters.

## 12. Bias Audit & Verdict

**Vintage/revisions:** 2026 snapshot retroactively applied to past origins; **PIT unverified**. **Selection/multiple testing:** new sector and directional hypothesis follow 23 prior studies; no familywise error adjustment; optimistic risk. **Survivorship/exposure:** aggregate NAICS data hide firm exits and offshore manufacturing; no issuer panel. **Time dependence:** overlapping YoY targets and 3-month horizons reduce effective independent sample size; block bootstrap is approximate. **Execution/costs:** no prices, portfolio, transaction costs, slippage, borrow or capacity. **Economic interpretation:** upstream growth could reflect global demand rather than domestic component availability, and factor–target correlation sign conflicts with the simplest thesis. **Verdict: weak retrospective incremental predictive gain, statistically inconclusive, no validated PIT fundamental lead or investable equity alpha.**

## 13. Reproduction

From this directory in a clean Python environment, install `python -m pip install -r requirements.txt`; run `OPENBLAS_NUM_THREADS=1 python run_analysis.py` to regenerate all results, then `OPENBLAS_NUM_THREADS=1 python -m pytest -q tests`, and `OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute --inplace research.ipynb --ExecutePreprocessor.timeout=900`. Run `python scripts/validate_studies.py` **from the repository root**. The full 1,000/2,000/1,000 resampling draws are stored as CSV, and all notebook code cells have executed outputs. Reproduction should not require network access because the raw snapshot is frozen. GitHub Actions structural validation is distinct from numeric reruns.

## 14. Next-Stage Protocol

(1) Independently retrieve official machine-readable G.17 data and reconcile every 2011–2026 observation, then reconstruct first-available vintages and precise release times. (2) Obtain historical firm product/segment revenues and filing timestamps for a defensible issuer-by-year NAICS exposure map; test fundamental growth on genuinely independent firm observations. (3) Obtain delisting-inclusive total returns, benchmark and sector controls, point-in-time investable universe, transaction costs and out-of-sample selection-adjusted holdouts. (4) Pre-register one horizon and a finite set of features before looking at post-2026 data; report multiple-testing adjustment across prior hypotheses. No claim of investability is warranted until these steps succeed.

## 15. Sources & Artifacts

Official sources: [Federal Reserve G.17](https://www.federalreserve.gov/releases/g17/) (2026-10-16 release), [IPG3342S](https://fred.stlouisfed.org/series/IPG3342S), [IPG3344S](https://fred.stlouisfed.org/series/IPG3344S), [IPG3341S](https://fred.stlouisfed.org/series/IPG3341S), [IPMAN](https://fred.stlouisfed.org/series/IPMAN), [U.S. Census NAICS](https://www.census.gov/naics/), [Ciena fiscal 2025 10-K](https://www.sec.gov/Archives/edgar/data/936395/000162828025056698/cien-20251101.htm) and [Cisco annual reports](https://www.cisco.com/c/en/us/about/annual-reports.html). Original inherited frozen file: [Semiconductor study G.17 CSV](../Semiconductor-Device-Gap-to-Alpha-U.S.-Chip-Manufacturing/data/fred_g17_snapshot_2011_2026.csv). Machine-readable source register and publication caveats: `data/source_register.csv` and `data/provenance_audit.md`. Raw/derived: `data/`; Python analysis: `run_analysis.py`; executed computational paper: `research.ipynb`; empirical tables: `results/`; ten diagnostics: `figures/`; tests: `tests/`. Research failure and uncertainty are part of the deliverable, not grounds for changing the headline ex post.
