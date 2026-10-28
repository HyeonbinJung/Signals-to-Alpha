# Income–Consumption Gap → U.S. Household Demand (1959–2009)

**Scope:** cross-sector U.S. household consumption demand; NOT an NAICS-specific retail-industry forecast, NOT historical PIT, NOT an equity-alpha strategy. **Status:** REPRODUCED RETROSPECTIVE CONSUMER-DEMAND MACRO PILOT. **Research date:** 2026-10-28.

## 01. Abstract

**Question:** Does one-quarter-stale real disposable-income growth relative to real consumption growth forecast real personal consumption expenditures (PCE) over the next four quarters, after macro controls? The sample is 203 quarters from 1959Q1 to 2009Q3, bundled in a fixed 2009-accessed FRED/BLS snapshot. The primary OOS result is **{m['n_oos']}** purged expanding-window forecasts and a control-minus-augmented RMSE improvement of **{f(m['gain_log_pp'])} log-pp**. {verdict}. This is a retrospective macro factor test, not a retail sales, company-fundamentals or tradable-security return result.

## 02. Research Design & Hypotheses

- **H1:** A positive real disposable-income-minus-consumption growth gap precedes higher subsequent aggregate real consumption growth, consistent with delayed spending. **Null:** no directional relation after controls.
- **H2:** Adding the fixed gap reduces 4Q-ahead OOS RMSE relative to macro controls **and** simple historical mean/AR baselines. **Null:** incremental RMSE improvement ≤0.
- **H3:** The sign and magnitude persist across historical regimes, lag buffers, horizons, placebo blocks, bootstrap uncertainty and weight perturbations. **Null:** sensitivity and structural breaks explain apparent gains.

**Counterthesis:** permanent-income expectations, debt repayment, precautionary saving, credit rationing, and recessions can weaken or reverse the spending response. Outcome choice and period were fixed before evaluating the scorecard in this run, but the broader research program has tested many related signals, so familywise error is unadjusted.

## 03. Industry Context

Retail trade (NAICS 44–45), food services (722), arts/recreation (71) and personal services (81) are plausible consumer-demand channels. U.S. Census classifies retail trade as merchandise sales to consumers, but **real PCE includes services and goods across industries**; therefore PCE cannot be used as a retail-only or company-revenue proxy. The 2022 NAICS classification is a modern context reference, not a reconstructed historical 1959–2009 industry map. Quantified 1959–2009 sector size, sector growth, and company revenue weights are **UNKNOWN** in the available data.

## 04. Data & Source Integrity

`data/macrodata_statsmodels_2009_snapshot.csv` freezes 203 quarterly observations, 1959Q1–2009Q3, from `statsmodels.datasets.macrodata` 0.14.6. Its documentation identifies FRED as the origin for most series and BLS for unemployment, accessed **2009-12-15**. The exact original quarterly publication timestamps and underlying FRED series identifiers are **UNKNOWN**, not inferred from access date. Real PCE (`realcons`), real disposable personal income (`realdpi`), real GDP and private investment are billions of chained 2005 USD, seasonally adjusted annual rate.

**A/B/C source register:** `data/source_register.csv` records URLs, access dates, observed dates, units, revision limitations and roles. Grade A denotes official publisher/classification/release context; grade B the auditable bundled historical snapshot; grade C researcher qualitative sector mapping. The underlying official data and compiled frozen snapshot are distinguished; the snapshot is **not** an original release-vintage archive. QA rejects missing values, duplicate quarters and nonpositive real levels.

## 05. Point-in-Time Availability

Formation date `t` is a calendar quarter. All regressors end at `t−1` or earlier; the primary dependent variable ends at `t+4`. Training origin `j` is eligible only when **`j+4 ≤ t`**, so the future outcome is known by the prediction origin. The data access date 2009-12-15 does **not** establish that the 2009 snapshot's values were available at the historical formation date. A fixed one-quarter observation buffer is not a replacement for release calendars or ALFRED first-vintage reconstruction. **PIT VERIFIED: FALSE.**

## 06. Factor Construction

For a real level `X`, define `g_X(t)=100 × [ln(X_t)−ln(X_(t−4))]` in YoY log-percentage points. The primary factor is **`F_t = g_DPI(t−1) − g_PCE(t−1)`**. The four-quarter target is **`Y_(t,4)=100 × [ln(PCE_(t+4))−ln(PCE_t)]`**. This gap has no optimized weights or full-sample normalization. In the perturbation exercise, `F_t(w)=w_DPI g_DPI(t−1)−w_PCE g_PCE(t−1)` with independently drawn weights in `[0.7,1.3]`; this is a sensitivity exercise, not a tuned production factor.

## 07. Exposure & Transmission

`data/sector_exposure_map.csv` records four qualitative consumer-facing NAICS channels and the as-of year of the classification. Revenue shares and individual company weights are **UNKNOWN** and never fabricated. Income growth may increase later spending, but consumer credit and saving can offset it. No independent company revenue/EPS or total-return dataset exists here, so **leave-one-company-out, cross-sectional rank IC, long–short spreads, market-adjusted total returns and costs are NOT APPLICABLE / NOT TESTED**, rather than evidence of zero.

## 08. Outcomes & Baselines

Primary dependent variable: next-four-quarter log real PCE growth, not sector sales or equity returns. All models use exactly the same OOS origins and training purge. Benchmarks are (1) expanding historical mean, (2) lagged PCE growth scaled to horizon, (3) AR Ridge with lagged consumption growth and unemployment change, (4) multivariate macro Ridge with lagged PCE, GDP, private investment and unemployment change, (5) factor-only Ridge, and (6) macro controls plus factor. Ridge `alpha=2.0` is fixed, and all scaling is fit on training observations only.

## 09. Empirical Findings

**{m['n_oos']}** expanding-window purged forecasts from **{m['first_oos']} to {m['last_oos']}**. Units are log-percentage points of four-quarter real PCE growth.

| Model | OOS origins | RMSE (log-pp) | MAE (log-pp) |
|:--|--:|--:|--:|
{score}

The primary gain is `RMSE(controls) − RMSE(controls+factor) = **{f(m['gain_log_pp'])} log-pp**`; a positive value means improvement. Descriptive full-panel factor/target Pearson correlation is **{f(m['factor_target_corr_in_sample'])}**. This is a *time-series association*, **not** a security cross-sectional information coefficient. Charts 01–06 show level integrity, factor evolution, scatter, OOS baselines, forecasts and cumulative paired losses.

## 10. Robustness & Placebos

A **1,000-refit eight-quarter block-reorder** of the factor preserves within-block serial dependence while breaking original alignment; the exploratory upper-tail fraction is **{f(m['placebo_tail_fraction_exploratory'])}**. It is not an exact permutation p-value because the conditional null and structural nonstationarity are not fully exchangeable. A **2,000-draw paired eight-quarter moving-block bootstrap** on the same OOS error vectors gives the control-minus-augmented RMSE gain 95% percentile interval **[{f(m['bootstrap_ci95'][0])}, {f(m['bootstrap_ci95'][1])}] log-pp**. The **1,000-draw factor-weight perturbation** yields a positive control-relative gain in **{100*m['exposure_gain_positive_fraction']:.1f}%** of draws; these weights are sensitivity settings, not fitted exposure shares.

| Horizon (quarters) | Observation buffer (quarters) | OOS n | Control-minus-full RMSE |
|--:|--:|--:|--:|
{horiz}

Ablations and evaluation-decade exclusions are in `results/ablations.csv` and `results/leave_one_decade_out.csv`. Multiple exploratory robustness results are presented without post-hoc selection of a winning horizon.

## 11. Regime Sensitivity

Regime breaks are descriptive and not chosen to maximize gain.

| Regime | OOS n | Control-minus-full RMSE (log-pp) |
|:--|--:|--:|
{reg}

The sample ends in 2009Q3 and cannot speak to the 2020 pandemic or modern consumer behavior. Leave-one-decade-out **scores** omit a decade from evaluation but preserve chronological expanding training; they do not refit the entire history without that decade.

## 12. Bias Audit & Verdict

**Look-ahead:** feature observation lags and purged target labels are enforced, but historical publication-vintage leakage remains. **Selection/multiple testing:** aggregate outcome and mechanism chosen among a growing set of industry hypotheses, no global false-discovery adjustment. **Survivorship:** aggregate national series has no firm survivorship filter, but no historical security universe. **Temporal overlap:** 4Q target overlaps, so paired block uncertainty is used. **Structural change:** recessions, 1980s regime shifts and 2009 cutoff can dominate estimates. **Costs and capacity:** not measurable without a tradable portfolio.

**Verdict:** {verdict}. The test remains a **retrospective consumer-demand macro falsification**, with neither historically valid PIT alpha nor independent retail-sector fundamentals or investable equity alpha established.

## 13. Reproduction

From a fresh checkout with Python 3.11+:

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m pytest -q tests/
python -m jupyter nbconvert --to notebook --execute research.ipynb --output executed.ipynb
```

The frozen input CSV is committed; no network call is made by the analysis. `analysis.py` contains the walk-forward, tests and diagnostics. `results/` contains raw placebo/bootstrap/perturbation draws, scorecard and forecasts. `figures/` contains nine independently computed PNG diagnostics. `logs/` stores the observed local execution and test evidence. `study.json` enumerates all tracked artifacts.

## 14. Next-Stage Protocol

First reconstruct quarter-specific ALFRED and BEA first-release data with publication timestamps, including benchmark revisions and base-year changes. Then pre-register a fresh modern holdout and collect **retail trade, restaurant, recreation and service-industry-specific outcomes**, which are absent here. Obtain historical filing-dated company revenue segment exposures and survivorship-safe total returns only if an equity question is pursued. Evaluate sector-neutral portfolios, realistic execution, costs, capacity and false-discovery adjustments before an investable-alpha claim.

## 15. Sources & Artifacts

Primary bundled data and provenance: [statsmodels macrodata CSV](https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/macrodata/macrodata.csv) and [metadata](https://www.statsmodels.org/stable/datasets/generated/macrodata.html). Original publishers: [FRED](https://fred.stlouisfed.org/), [BLS](https://www.bls.gov/data/) and [BEA release schedule](https://www.bea.gov/news/schedule/). Industry context: [2022 Census retail trade](https://www.census.gov/data/tables/2022/econ/economic-census/naics-sector-44-45.html). See `data/source_register.csv`, `data/provenance_audit.md`, frozen raw/derived data, nine figures, ten result tables, tests, and executed `research.ipynb`.
