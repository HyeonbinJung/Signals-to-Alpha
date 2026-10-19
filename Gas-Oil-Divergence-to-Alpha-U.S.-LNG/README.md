# Gas–Oil Divergence to Alpha — U.S. LNG & Natural Gas
**Research date:** 2026-10-19 · **Data snapshot:** 2026-10-08 · **Status:** Falsification / negative factor result.

> **Verdict:** LNG infrastructure growth is a plausible fundamental industry thesis, but the energy-equivalent WTI–Henry Hub relative-price signal **does not improve** forward Henry Hub spot-price forecasts in this fixed-snapshot test. No investable equity or futures alpha has been established.

## 1. Industry outlook and hypotheses

EIA's **April 16, 2026** forecast projected U.S. LNG exports of **17.0 Bcf/d in 2026** and an additional **1.5 Bcf/d (+9%) in 2027**. Its **September 1, 2026** report put 1H26 LNG exports at **17.4 Bcf/d**, up **23% YoY**. The 2026 Annual Energy Outlook projected LNG export capacity of **27.7 Bcf/d by 2030**. Expansion could benefit exporters, liquefaction equipment, midstream gas pipelines and specialized infrastructure, but construction delays, feedgas, permitting, gas prices, global netbacks and geopolitical risk matter. Export growth is **not** equivalent to shareholder returns.

Official-source references:
- EIA April 16, 2026: https://ebs.publicnow.com/view/3450355AF1FDD5D5A4146FE59633DA460A536CA6
- EIA September 1, 2026: https://ebs.publicnow.com/view/6AF62E0FFC43478C0343A0935E6A102786C99769
- EIA Annual Energy Outlook 2026: https://www.eia.gov/outlooks/aeo/pdf/AEO_Narrative.pdf

**H1:** Oil expensive relative to natural gas on a rough energy-equivalent basis might lead gas-price normalization via demand substitution and LNG export incentives. **H2:** The spread adds out-of-sample predictive information beyond each commodity's 3/12-month momentum. **H3:** Gains survive 1/6-month targets, pre/post-2016 LNG export era, 2022 shock exclusion, and stale-spread placebo tests. **Null:** The spread adds no incremental information.

**Mechanism caveat:** WTI is not JKM/TTF/Brent LNG netback pricing. Dividing WTI USD/bbl by **6 MMBtu/bbl** is a rough energy conversion, not a frictionless arbitrage relation. LNG liquefaction/shipping and basis costs are omitted.

## 2. Source integrity and availability

The frozen `data/henry_hub_wti_monthly.csv` contains **357 monthly observations, 1997-01 to 2026-09**, aligned from **EIA-origin** public-domain monthly spot-price data:
- Henry Hub USD/MMBtu: `datasets/natural-gas`, snapshot commit `46333b1b23502827393563e46e60210604c1fcdb` (2026-10-08 05:29 UTC).
- WTI Cushing USD/barrel: `datasets/oil-prices`, snapshot commit `5b9f941b232aa62263ad4798e1eb68dd1932ab3c` (2026-10-08 06:46 UTC).

Both original data publishers are EIA; downstream CSVs are DataHub/GitHub mirrors. See `data/source_register.csv` for exact source URLs, dates, provenance, units and vintage caveats. **These are latest/frozen-vintage observations, NOT historical real-time releases.** Original publication timestamps, late revisions and ALFRED vintages have not been reconstructed. A conservative one-month input lag is imposed, but does not prove actual historical point-in-time availability.

## 3. Factor, target, and evaluation

At forecast month `t`, only observations through month `t-1` enter:
```
gas_mom3   = 100 log(G[t-1]/G[t-4])
gas_mom12  = 100 log(G[t-1]/G[t-13])
wti_mom3   = 100 log(W[t-1]/W[t-4])
wti_mom12  = 100 log(W[t-1]/W[t-13])
spread     = log((W[t-1]/6)/G[t-1])
y_h        = 100 log(G[t+h]/G[t-1])
```
`G` denotes Henry Hub spot USD/MMBtu; `W` denotes WTI USD/barrel. The primary horizon is **h=3**, implying a four-month change from last observable price to the end of t+3. This is **not** a month-t executable return; spot monthly averages cannot be filled at their published index value.

Expanding-window forecasts use a minimum **96 historical labels**, fixed Ridge penalty **alpha=10**, and **train-only** feature means/stds. The training-label purge requires **u+h ≤ t-1** for each training origin u when evaluating test origin t, preventing outcomes ending after the information cutoff. Baselines are historical mean and four commodity-momentum features; the challenger adds the oil–gas spread. Ablations use spread only, gas momentum only, and gas momentum plus spread. No full-sample normalization or optimized hyperparameter search.

## 4. Primary quantitative results

**242 expanding-window OOS forecasts, 2006-05 through 2026-06.** Errors are percentage points of log gas-price change.

| Model | RMSE (pp) | MAE (pp) | Direction hit |
|---|---:|---:|---:|
| Historical mean | **30.825** | 23.660 | 39.3% |
| Gas/WTI momentum controls | 30.911 | **23.312** | 58.7% |
| Controls + spread | **32.707** | 25.040 | 55.8% |
| Spread only | 32.682 | 25.360 | 47.1% |
| Gas momentum only | 31.170 | 23.775 | 52.1% |
| Gas momentum + spread | 33.267 | 25.362 | 49.6% |

**Incremental ΔRMSE (control − full) = −1.796 pp**: the spread makes the forecast worse. Directional hit rate does not account for prices, trading costs, futures roll or statistical dependence.

## 5. Robustness and negative controls

| Evaluation | n | Control RMSE | Full RMSE | ΔRMSE |
|---|---:|---:|---:|---:|
| 1-month target | 246 | 22.026 | 22.665 | −0.639 |
| 6-month target | 236 | 40.438 | 44.517 | −4.079 |
| Before 2016 | 116 | 25.642 | 29.908 | −4.266 |
| Since 2016 | 126 | 35.070 | 35.087 | −0.017 |
| Since 2020 | 78 | 41.899 | 41.907 | −0.007 |
| Excluding 2022 test origins | 230 | 29.300 | 31.288 | −1.988 |
| Placebo: spread 12 months staler | 230 | 31.466 | 32.071 | −0.605 |
| Placebo: spread 24 months staler | 218 | 32.272 | 33.151 | −0.880 |
| Placebo: spread 36 months staler | 206 | 31.287 | 32.427 | −1.140 |

The placebos replace the signal with older observations, **not** shuffled future data. Each placebo is compared with controls on its **own matched sample**, because the starting dates differ. This is a falsification/ablation battery, not a formal permutation p-value. For primary paired OOS forecast errors, a 12-month moving-block bootstrap with 1,000 replications gives an **approximate 95% interval [−3.540, −0.274] pp** for control-minus-full RMSE (seed 20261019, xorshift32 in initial cross-check; Python uses NumPy PCG64 and may yield a slightly different interval). Serial correlation, overlapping outcomes, structural breaks and researcher degrees of freedom prevent strong significance claims.

## 6. Bias audit

| Risk | Control | Residual risk |
|---|---|---|
| Input look-ahead | t−1 monthly input cutoff | Historical EIA release dates and vintages unaudited |
| Outcome leakage | u+h ≤ t−1 purge | Revised historical target levels |
| Scaling leakage | Train-only mean/std | Fixed hyperparameter chosen for this pilot |
| Survivorship | National commodity benchmarks, no selected stocks | Mirror and data-revision bias |
| Overfitting | Historical-mean and momentum baselines; negative controls | Exploratory factor design, no untouched post-publication test |
| Overlap | Moving-block bootstrap | Block length and regime shifts are approximations |
| Nontradable spot | Explicitly label spot target | No NYMEX contracts, rolls, slippage, basis, collateral, fees |
| Wrong industry exposure | LNG thesis kept separate from price-factor test | No company earnings, export volumes, or equity return link |
| Data license | EIA public-domain provenance | Mirror transformations not separately verified |

## 7. Next research

1. Audit **ALFRED/EIA historical vintages** and exact monthly release timestamps.
2. Add time-stamped **LNG exports, feedgas flow, terminal utilization, gas storage surprises, heating/cooling degree days** and global **JKM/TTF–Henry Hub netbacks**.
3. Run roll-aware **NYMEX futures** backtests with term structure, financing, trading costs and realistic execution.
4. Link factor to **LNG operator and midstream company earnings revisions / total shareholder returns** using dated exposure matrices and survivorship-safe universes.
5. Reserve a true post-publication holdout before feature/model selection.

## Reproduce

```bash
python -m pip install -r requirements.txt
python run_analysis.py --write
python -m unittest discover -s tests -v
jupyter notebook research.ipynb
```

Files: frozen data and source register in `data/`; executable `run_analysis.py`; reproducible `research.ipynb`; `tests/` sanity checks; script-generated `results/oos_predictions.csv` and `results/metrics.json`. **No equity alpha, strategy Sharpe or investment recommendation is claimed.**
