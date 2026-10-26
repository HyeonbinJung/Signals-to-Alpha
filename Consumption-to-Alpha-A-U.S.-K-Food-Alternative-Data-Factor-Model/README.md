# Consumption-to-Alpha — U.S. K-Food Demand

> **Status:** Research-grade exploratory pilot; investable alpha unproven  
> **Research date:** 2026-10-06  
> **Scope:** Annual demand-to-fundamental and equity-return association (not an executable PIT strategy)  
> **Study ID:** `kfood` · [Quality standard](../RESEARCH_QUALITY_STANDARD.md) · [Machine-readable manifest](study.json)

## 01. Abstract

This study is part of **Signals to Alpha**, which treats real-economy data as *candidate* research signals and separates observable economic relationships from investable returns. Annual K-Food demand and company category exposure show an economically plausible relationship with subsequent sales growth, but the equity signal is unstable. The five-year test's mean Rank IC is weak and the apparent return spread depends heavily on Samyang Foods. Exposure perturbations, company exclusions, regime splits and a within-year permutation placebo do not establish sector-wide investable alpha. **Verdict:** a useful demand-nowcasting hypothesis, not a validated trading strategy.

## 02. Research Design & Hypotheses

Can category-level Korean-food demand at year *t* predict exposed producers' next-year sales growth and benchmark-adjusted equity returns? H1: demand leads fundamentals; H2: it leads excess returns; H3: the signal survives constituent, exposure and time-period stress tests. The null is no incremental association.

## 03. Industry Context

U.S. demand for Korean food motivates the project, while Korean public customs/food-category series form the measurable historical core. The notebook deliberately keeps U.S. H Mart footprint and press descriptions as **context**, not backfilled numerical time series.

## 04. Data & Source Integrity

Primary references are government trade/food statistics and company disclosures (grade A), institutional financial sources (B), and contextual press items (C). See `kfood_source_register_v3.csv`, with the demand, company fundamentals, return panel and exposure matrix committed alongside the notebook. Five annual observations are not enough to establish a deployable effect.

## 05. Point-in-Time Availability

The model uses an ex-ante fixed `tanh(YoY_category_growth / 20)` transform, but the annually finalized customs data are not shown to be available at a January 1 trade formation. The historical lead test is **not** a reconstructable point-in-time trading backtest.

## 06. Factor Construction

Category signal: `S[c,t] = tanh(YoY_growth[c,t] / 20)`; firm score: `D[i,t] = Σ_c exposure[i,c] × S[c,t]`. The divisor 20 is fixed; the feature does not use full-sample fitted z-scores.

## 07. Exposure & Transmission

The analyst-defined company/category exposure matrix maps ramen, kimchi, processed rice, sauce and broader K-Food categories to producers. These are informed priors, **not** historical reported category revenue shares.

## 08. Outcomes & Baselines

Primary outcomes are next-year company sales growth (CJ Food division where available) and next-year price return minus KOSPI. Equity analysis uses rank association and top-minus-bottom spread, but does not implement actual publication-date entries, total-return/cost modeling or a survivorship-free historical universe.

## 09. Empirical Findings

The original notebook reports more encouraging fundamental associations than equity robustness. Full-period mean equity Rank IC is approximately **0.063** and the attractive spread is strongly affected by Samyang's extraordinary performance.

## 10. Robustness & Placebos

Leave-Samyang-out, sauce exclusion, momentum controls, 1,000 exposure-weight perturbations and within-year score-shuffle placebos challenge the inference. The placebo **p≈0.744** fails to reject a random assignment interpretation.

## 11. Regime Sensitivity

Post-2022 results look better than 2021–2022; this could reflect a regime, a single influential constituent or overfitting to an unusually short sample. No prospective holdout has been observed.

## 12. Bias Audit & Verdict

Publication timing, revised trade series, survivor selection, ex-post exposure priors, small annual sample, constituent concentration, omitted total-return mechanics, costs and multiple testing remain open. **Conclusion:** fundamental demand proxy promising; sector-wide investable equity alpha unproven.

## 13. Reproduction

Open `kfood_research_grade_alpha_v3.ipynb` from this directory after installing `pandas numpy scipy statsmodels matplotlib jupyter`. The committed CSVs support notebook inspection; a clean CI rerun of the K-Food notebook is **not** claimed here.

## 14. Next-Stage Protocol

Acquire publication-stamped monthly U.S. import categories, product-level retail distribution, digital attention and independently dated firm exposures; confirm filing-release lags, then run purged cross-sectional walk-forward fundamental tests before any security-level portfolio.

## 15. Sources & Artifacts

Artifacts: `kfood_research_grade_alpha_v3.ipynb`, the three CSV panels/matrix and `kfood_source_register_v3.csv`. Detailed source URLs and the study's original 15-section narrative live in the notebook.
