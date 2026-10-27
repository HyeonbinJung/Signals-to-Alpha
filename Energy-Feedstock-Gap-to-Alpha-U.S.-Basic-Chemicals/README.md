# Energy-Feedstock Gap — U.S. Basic Chemical Manufacturing

**Evidence:** REPRODUCED RETROSPECTIVE MACRO-FACTOR FALSIFICATION; NOT historical point-in-time; NOT investable equity alpha. 2026-10-26 frozen source snapshots. Target is **NAICS 3251 basic chemical manufacturing**, a new outcome industry relative to earlier pharmaceutical manufacturing and gas-price studies. Inputs deliberately reuse two earlier frozen datasets; **this is not a new primary data collection**.

## 01. Abstract

**Research question:** Does relatively lower U.S. natural-gas price inflation versus WTI crude oil anticipate six-month-ahead growth in U.S. basic chemical manufacturing output? Across **111 purged expanding-window origins** (2017-01 to 2026-03), the energy-gap-augmented Ridge has RMSE **9.034 log pp**, worse than manufacturing/chemical/oil controls (**8.971**) and historical mean (**8.271**). The estimated incremental RMSE gain is **−0.0625 log pp**, with a 2,000-draw paired circular-block bootstrap 95% interval **[−0.373, 0.219]** and exploratory 1,000-refit block-shuffle tail **0.521**. **Verdict:** negative retrospective macro-factor test, not PIT or equity alpha.

## 02. Research Design & Hypotheses

**H1:** When natural gas becomes cheaper relative to oil in year-over-year growth terms, U.S. petrochemical feedstock competitiveness improves and later basic-chemicals production growth rises, all else equal. **H2:** The fixed energy gap adds OOS accuracy beyond chemical production persistence, manufacturing and WTI oil inflation, and beats a simple mean. **H3:** The effect survives 12-month block placebo, paired block bootstrap, ±25% loading perturbations, leave-one-year-out, regime splits, alternate horizons and conservative release lags. These are falsifiable hypotheses; H2/H3 fail on the observed evidence. The target is **industrial production**, not corporate fundamentals or total returns.

## 03. Industry Context

U.S. basic chemical manufacturing includes petrochemical, industrial-gas, organic and inorganic chemicals; its G.17 index is broader than the ethane/NGL-exposed petrochemical segment. U.S. DOE describes Appalachia's NGL/ethane resource and petrochemical manufacturing potential (see source register). Henry Hub measures natural gas **spot energy**, not the price of ethane feedstock; WTI measures crude oil, not each chemical producer's contracted feedstock. Relative price growth is therefore a coarse, contestable proxy. Structural capacity expansions, demand shocks, regional mix and inventory behavior can overwhelm any energy-cost signal.

## 04. Data & Source Integrity

The **201 monthly observations from January 2010 through September 2026** combine the Federal Reserve's `IPG3251S` and `IPMAN` industrial production indices (2017=100, seasonally adjusted) and EIA Henry Hub (USD/MMBtu) and WTI (USD/barrel) monthly spot averages. G.17 was released **2026-10-16**; EIA series were copied from pinned public mirrors committed **2026-10-08**. Historical original release dates for individual observations are **UNKNOWN**, and source vintages are **fixed revised snapshots**. Full A/B/C source register, exact URLs, units, dates, revisions and limitations are in [`data/source_register.csv`](data/source_register.csv), with checksums and independent row-count/sum-of-squares checks in [`data/provenance_audit.md`](data/provenance_audit.md). EIA sums were checked against the upstream GitHub file; no imputation or simulated observations.

## 05. Point-in-Time Availability

At the **end of calendar month t** (monthly dates are stored as first-of-month labels), formation uses **only source observations at t−2** to allow a conservative two-completed-month availability buffer. The target is the year-over-year log growth in chemical output at *t+6*, and a training observation formed at *j* is included only if **j+6+1 ≤ t**, reserving one further month for target publication. Every Ridge standardization is fit on the eligible training window, not on the full sample. **This prevents mechanical target overlap but does not eliminate revision lookahead:** the original G.17 monthly vintages and historical EIA publication timestamps have not been reconstructed. Accordingly this is **not a PIT backtest**.

## 06. Factor Construction

For positive level series *X*, define `YoY_X(t) = 100 × [ln(X_t) − ln(X_{t−12})]` in log percentage points. The predeclared feature is `EnergyGap_t = YoY_WTI(t−2) − YoY_HenryHub(t−2)`; the target is `Y_t = YoY_Chemical(t+6)`. A positive gap means gas price inflation was lower than oil price inflation, potentially supporting gas-based petrochemicals. The factor **does not divide USD/barrel by USD/MMBtu**, which would conflate physical units; it differences separately defined log changes. In the sensitivity experiment the gas and oil weights vary from **0.75 to 1.25**, explicitly not empirical firm exposure shares.

## 07. Exposure & Transmission

The hypothesized chain is natural-gas/NGL input economics → petrochemical operating margin → plant utilization → NAICS 3251 industrial production. [`data/exposure_map.csv`](data/exposure_map.csv) distinguishes petrochemical, industrial gas, basic organic and inorganic segments, labels the exposure weights **NOT ESTIMATED**, and records the evidence date and URL. No dated issuer-level revenue share or filing-derived exposure was obtained; **company-level exposure mapping is unverified** and no firm panel exists. A leave-one-company-out test would be meaningless; we instead compute leave-one-**year**-out influence on the macro OOS errors. This is a scope limitation, not an omitted positive test.

## 08. Outcomes & Baselines

**Primary:** chemical production YoY log growth six months ahead. **Secondary:** chemical minus aggregate-manufacturing YoY log growth six months ahead, analyzed separately and **not** interpreted as security excess return. The same 111 OOS origins are evaluated for expanding historical mean, chemical persistence, Ridge controls (chemical YoY, manufacturing YoY, WTI YoY), Ridge controls plus EnergyGap, EnergyGap-only, gas-only and oil-only ablations. Ridge penalty **alpha=12** is fixed; no hyperparameter tuning on OOS labels. The training target is purged for outcome observation and publication buffer, and only train-sample feature means/variances are used. Effective independence is less than 111 due to overlapping six-month targets.

## 09. Empirical Findings

| Forecast | OOS n | RMSE (log pp) | MAE (log pp) |
|:--|--:|--:|--:|
| Chemical persistence | 111 | **8.268** | 5.894 |
| Historical mean | 111 | **8.271** | 5.824 |
| Energy gap only | 111 | 8.420 | 5.919 |
| Macro controls | 111 | 8.971 | 6.167 |
| Gas-only controls | 111 | 8.999 | 6.206 |
| **Macro controls + energy gap** | **111** | **9.034** | **6.244** |

The challenger is **0.0625 log pp worse** than the macro controls and **0.763 log pp worse** than the historical mean. Descriptive OOS Spearman factor/target association is **0.0555** (not an independently sampled IC significance test). The secondary industry-relative outcome yields RMSE **6.694** (augmented) versus **6.703** (controls), but still loses to its mean baseline **6.327**. Full predictions, errors, tables and figures are saved under `results/` and `figures/`.

## 10. Robustness & Placebos

A **1,000-refit 12-month contiguous-block factor shuffle** yields exploratory upper-tail fraction **0.521** (not an exact permutation p-value under nonstationarity). A **2,000-draw paired circular 12-month block bootstrap** of the control-minus-augmented RMSE yields **[−0.373, 0.219] log pp** at the 95% percentile interval; zero lies inside. In **1,000 loading perturbations**, the positive-gain fraction is **0%**. Leave-one-year-out gains are negative in **8 of 10** excluded-year samples; omitting 2019 or 2021 makes the gain slightly positive, showing influence instability. Oil-only, gas-only and gap-only ablations do not beat the best naive baseline. All actual simulation draws and derived scores are committed, not just displayed summary claims.

## 11. Regime Sensitivity

The same OOS predictions show control-minus-augmented RMSE differences of **−0.299 log pp** before 2020 (36 origins), **+0.075** from 2022 onward (51 origins), and **−0.115** excluding 2020–2021 (87 origins). These are **post-hoc slices**, not independent holdouts. Horizon/lag alternatives (3, 6, 12 months; 2 or 4 months of input staleness) all yield **negative** incremental gains: the best of six is still **−0.023 log pp**. Results are sensitive to period and benchmark choice; none justify ex-post model selection.

## 12. Bias Audit & Verdict

**Historical revision leakage:** latest-revised G.17 values, not original-release vintage. **Publication lag:** a conservative proxy rather than verified per-observation timestamp. **Selection and multiple testing:** new industry/factor chosen after earlier sector studies; no familywise correction. **Survivorship:** no historical issuer universe, so equity survivorship is untested. **Overlap:** six-month forward YoY labels are serially correlated, reducing effective sample size. **Costs/capacity:** no traded asset, bid–ask spread, transaction costs, shorting or portfolio turnover. **Economic confounds:** gas and oil prices co-move with industrial demand and macro shocks; no causal identification. **Verdict: REPRODUCED RETROSPECTIVE MACRO-FACTOR FALSIFICATION; no incremental OOS gain, no verified PIT and no equity alpha.**

## 13. Reproduction

From a clean checkout inside this directory:

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m pytest -q
jupyter nbconvert --to notebook --execute research.ipynb --output research.ipynb --ExecutePreprocessor.timeout=1200
```

The analysis writes the derived panel, identical-origin OOS predictions, scorecard, 1,000 block refits, 2,000 bootstrap draws, 1,000 loading perturbations, ablations, regime/horizon diagnostics, 8 PNG figures and JSON summary. The notebook includes 15 matching substantive chapters, executable QA, re-computed OOS forecasts and saved chart/table outputs. Root layout validation: `python scripts/validate_studies.py`; this **does not certify PIT or numerical reproducibility**. Local test/execution logs are stored in `results/`.

## 14. Next-Stage Protocol

Collect archival Federal Reserve G.17 monthly release files or ALFRED vintages and timestamped EIA monthly prices to reconstruct *as-of* inputs; replace broad Henry Hub with ethane/NGL feedstock prices and validate each plant's geographic exposure. Assemble a dated historical issuer universe and segment mix from 10-Ks, independently test sales, gross margin and capacity utilization, then separately test delisting-inclusive total returns, sector-neutral portfolios, bid–ask/slippage/turnover, multiplicity-adjusted uncertainty and a forward holdout. Until then the study must remain a macro falsification, not a claimed tradeable alpha.

## 15. Sources & Artifacts

**Primary sources:** [Federal Reserve G.17 2026-10-16 release](https://www.federalreserve.gov/releases/g17/20261016/g17.pdf); [FRED IPG3251S](https://fred.stlouisfed.org/series/IPG3251S); [FRED IPMAN](https://fred.stlouisfed.org/series/IPMAN); [EIA Henry Hub monthly](https://www.eia.gov/dnav/ng/hist/rngwhhdm.htm); [EIA WTI monthly](https://www.eia.gov/dnav/pet/hist/rwtcM.htm); [DOE feedstock mechanism](https://www.energy.gov/hgeo/articles/appalachian-petrochemical-renaissance-within-reach). **Pinned source mirrors:** [natural-gas 46333b1](https://github.com/datasets/natural-gas/commit/46333b1b23502827393563e46e60210604c1fcdb) and [oil-prices 5b9f941](https://github.com/datasets/oil-prices/commit/5b9f941b232aa62263ad4798e1eb68dd1932ab3c). **Local artifacts:** `research.ipynb`, `chemicals_factor.py`, `run_analysis.py`, `requirements.txt`, `tests/`, `data/` (raw/frozen/derived, source register and exposure audit), `results/` (forecasts, 1,000+ refits, 2,000 bootstraps, robustness), `figures/` (8 computed diagnostics), and `study.json`.
