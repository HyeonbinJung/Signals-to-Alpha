# Fuel-Cost Relief and U.S. Airline Passenger-Mile Growth

**Status:** REPRODUCED MACRO PILOT — retrospective fixed/revised snapshots, **NOT** historical PIT, **NOT** investable equity alpha.  
**As-of:** 2026-10-27. **Industry:** U.S. air transportation / airline passenger activity (NAICS 481). **Primary outcome:** U.S. carrier passenger miles, not airline earnings or returns.

## 01. Abstract

Can a conservative, pre-formation crude-oil cost-relief score predict U.S. airline revenue passenger miles three months ahead, beyond already observed airline and travel-service activity? Using inherited, explicitly frozen BTS/BLS and EIA monthly observations, the predeclared 70/30 annual/quarterly WTI relief score was tested in **93** target-release-purged expanding-window forecasts. The challenger returned **107.776 log-pp RMSE** versus **107.082** for macro controls and **94.303** for the historical mean; a paired 12-month circular-block bootstrap interval for the incremental RMSE gain was **[-2.032, 2.304] log-pp**. The mechanism is plausible but the observed incremental gain is negative, and pandemic-era shocks dominate the sample. **Verdict: falsified as a stable macro leading indicator on this fixed snapshot; no company-return alpha test.**

## 02. Research Design & Hypotheses

**Primary question:** Does a fixed lagged WTI fuel-cost-relief score improve 3-month-ahead year-over-year U.S. airline passenger-mile forecasts over the same-origin persistence, historical-mean and macro-control benchmarks? **H1:** oil-cost relief has positive incremental forecast information. **H2:** it beats the full controls in purged expanding-window OOS RMSE. **H3:** gains survive block-aware placebo, bootstrap, 2020–21 exclusions, alternate horizons and oil-horizon-weight perturbations. **Null:** no incremental gain. **Failure rule:** negative control-minus-challenger RMSE or fragile, baseline-inferior results reject a robust factor claim. Counterthesis: WTI is not jet fuel, travel demand dominates capacity, hedging/airfares interrupt transmission, and common macro shocks may confound oil prices and flying.

## 03. Industry Context

The airline industry is fuel-sensitive but not mechanically driven by oil. IATA's **2025-06-02** global outlook estimated fuel spending at **25.8%** of 2025 airline operating costs; this is a **global forecast**, not a measured U.S. airline-wide expense share ([IATA](https://www.iata.org/en/pressroom/2025-releases/2025-06-02-01/)). A later U.S. carrier's realized fuel bill may be hedged, lagged, and disconnected from WTI. The BTS target covers all U.S. carrier domestic/international, scheduled/unscheduled service, not a fixed panel of publicly traded firms. U.S.-specific total industry revenue for the exact BTS coverage and study window: **UNKNOWN / not used**. The signal is a cost proxy, not a jet-fuel crack-spread model or a structural demand estimate.

## 04. Data & Source Integrity

All numerical rows are inherited frozen snapshots, not newly scraped historical releases. **BTS AIRRPMTSID11** 2014-01 to 2026-06 (150 observed months, three later missing); **BLS CES7072100001/CES7072200001** 2014-01 to 2026-09; **EIA WTI and Henry Hub** 2010-01 to 2026-09 (WTI is used in the factor; Henry Hub is retained only as a prospective negative-control series). The merged source panel has **153** months. BTS's [FRED series](https://fred.stlouisfed.org/series/AIRRPMTSID11) shows **2026-06 = 94,921,559 thousand miles** and update **2026-10-01 09:01 CDT**; the [EIA monthly WTI history](https://www.eia.gov/dnav/pet/hist/rwtcm.htm) reports **2026-09 = $97.31/barrel**. The raw source SHA-256 checksums and A/B/C source hierarchy are in `data/source_register.csv` and `logs/reproduction.log`; BLS/CES and EIA historical vintage metadata are **UNKNOWN**. Source grade A means official publisher, not an assurance that frozen observations are PIT. No numeric data are inferred or interpolated.

## 05. Point-in-Time Availability

At formation month **t**, only observations dated **t−2 or earlier** enter features; the training label from formation **s** is permitted only if **s + horizon + 2 months ≤ t**. This target-release purge is conservative but does **not** verify each historical publication timestamp, BTS seasonal revisions, CES benchmark revisions or EIA mirror history. Publication lag is a modeling assumption, not a verified release-vintage panel. The current FRED update dates do not establish the vintage available at historical origins. **PIT status: NOT VERIFIED; retrospective association/falsification only.** The 2025 airline filings in the exposure map were unavailable at earlier formation dates and never enter the model.

## 06. Factor Construction

Let \(P_t\) be the positive EIA WTI monthly average. Define \(g^{12}_t=100\ln(P_{t-2}/P_{t-14})\) and \(g^{3}_t=100\ln(P_{t-2}/P_{t-5})\). The predeclared **fuel-cost relief score** is \(F_t=-[0.70g^{12}_t+0.30g^{3}_t]\), in log percentage points; higher means falling oil prices. No full-sample normalization, future mean or target-tuned exposure weight is used. Sensitivity refits vary the annual weight uniformly between 0.30 and 0.90 **without selecting a winner**. The outcome is \(Y_{t+3}=100\ln(RPM_{t+3}/RPM_{t-9})\). The lagged persistence baseline is \(100\ln(RPM_{t-2}/RPM_{t-14})\).

## 07. Exposure & Transmission

The channel is **WTI → (imperfect) jet-fuel costs → capacity, ticket pricing and passenger demand → passenger miles**. `data/company_exposure_map.csv` records dated qualitative evidence for **DAL** (2025 fuel costs 17% of operating expense, disclosed 2026), **UAL** (2025 aircraft fuel $11,396m vs operating expenses $54,356m, disclosed 2026), and **LUV** (2024 Brent-linked hedging disclosure, 2025 filing). These are **not historical exposure weights**, and the U.S. BTS aggregate cannot be decomposed into these issuers from the frozen inputs. The 70/30 factor blend is an analyst-defined *temporal horizon weight*, not a company revenue or fuel-cost share. Leave-one-company-out is **not applicable**; leave-one-formation-year-out is supplied instead. No unsupported issuer-level performance inference is made.

## 08. Outcomes & Baselines

Five **same-origin** 3-month-ahead airline YoY log-growth forecasts: (1) expanding historical mean of released labels; (2) last available airline YoY persistence; (3) Ridge controls (airline persistence, lodging employment YoY, foodservice employment YoY); (4) those controls plus oil relief; (5) oil relief alone. Ridge uses **fixed alpha=15**, training-only feature centering/scaling, predeclared z clipping at ±6, and a release-purged expanding window with at least **36** eligible training origins. Model choice and factor weight were not optimized on returns. Main metric is RMSE; MAE and signed bias are secondary. IC/long-short spread are **not defined** for this single macro target; no company financial outcome or security total-return benchmark was available.

## 09. Empirical Findings

| Forecast | OOS n | RMSE (log-pp) | MAE (log-pp) |
|---|---:|---:|---:|
| Historical mean | 93 | 94.303 | 45.955 |
| Airline persistence | 93 | 111.133 | 53.811 |
| Macro controls | 93 | 107.082 | 53.197 |
| **Oil relief + macro controls** | **93** | **107.776** | **53.544** |
| Oil relief only | 93 | 93.117 | 44.704 |

The **predeclared incremental comparison** is control minus augmented RMSE **−0.694 log-pp**. Although oil-only beats the mean by **1.186 log-pp**, that secondary comparison is neither a controlled incremental result nor robust evidence: it remains exposed to pandemic shocks and was not the registered primary success criterion. There are 93 OOS origins, the smallest released-label training set contains 36 origins, and the final formation is 2026-03. See computed `results/scorecard.csv`, `results/oos_predictions.csv`, and diagnostic figures.

## 10. Robustness & Placebos

The **1,000-refit non-overlapping 12-month block-order shuffle** gives an exploratory upper-tail fraction **0.615** for control-minus-augmented RMSE; the exchangeability assumptions are not established, so this is **not an exact permutation p-value**. A **2,000-draw paired circular 12-month block bootstrap** produces a 95% percentile interval **[−2.032, 2.304] log-pp**, including zero. Across **1,000** oil-horizon-weight perturbations (annual weight 0.30–0.90), **0%** beat the control RMSE. Ablation of foodservice controls flips the gain to **+0.175**, a sign of specification fragility rather than proof. Alternative horizons (1/3/6 months) and lags (2/3/4 months) vary in sign; see `results/horizon_lag_sensitivity.csv`. Leave-one-year-out is a diagnostic on the same OOS predictions, not independent refitting on a new holdout.

## 11. Regime Sensitivity

The same 93 OOS predictions produce control-minus-augmented RMSE gain **−0.694** overall, **+2.289** after excluding 2020–21 target years (69 origins), **−0.098** before 2020 (15 origins), **+2.589** for 2022+ (54 origins), and **−0.929** for 2024+ (30 origins). These are **post hoc diagnostic slices**, not independent confirmations. The COVID collapse and rebound dominate target scale and error; a change of sign under regime selection makes a stable industry predictor claim untenable. Regime sample sizes are reported in `results/regime_sensitivity.csv`.

## 12. Bias Audit & Verdict

**Lookahead:** features and labels are lagged/purged, but historical revisions remain uncorrected. **Selection:** U.S. airline target and inherited source files were selected after prior sector work; external holdout absent. **Survivorship:** aggregate BTS series is not an issuer universe; issuer filings shown only for mechanism. **Multiple testing:** horizon/lag/ablation/regime searches are diagnostics, not adjusted discoveries. **Transaction costs/capacity:** not applicable without a security portfolio, so no tradability claim. **WTI proxy bias:** crude is not jet fuel, and crack spreads/hedges/airfare pass-through are unobserved. **Verdict: negative retrospective macro lead-factor falsification, not PIT, not an equity-alpha study.**

## 13. Reproduction

From this directory: `python -m pip install -r requirements.txt`, then `python run_analysis.py`, `python -m pytest -q tests`, and `jupyter nbconvert --to notebook --execute --inplace research.ipynb` (or `python -m nbclient` via the provided notebook execution command in `logs/reproduction.log`). `run_analysis.py` deterministically writes derived CSV, OOS predictions, 1,000 block-refit nulls, 2,000 block-bootstrap draws, 1,000 oil-weight refits, ablations, horizon/lag/regime checks and nine SVG figures. All numerical results are computed from frozen CSVs; no network or API key is required. The committed notebook retains executed outputs, not placeholder plots. `python scripts/validate_studies.py` must also pass from the repository root before publication; it is structural validation only.

## 14. Next-Stage Protocol

Collect **actual historical BTS, EIA and CES release-vintage archives** with release timestamps and audit t-2 availability. Replace WTI with an archived U.S. jet-fuel spot index plus refinery crack spread, airport-level traffic, capacity and airfares; obtain carrier-quarter fuel gallons, hedging disclosures and operating margins with dated SEC filings. Define issuer universe without survivorship, use split-adjusted total returns and an airline/market benchmark with borrow, turnover and transaction-cost sensitivity, and preregister a holdout before parameter selection. Run blocked multiple-hypothesis adjustments, crisis exclusion and independent post-2026 validation before considering an investable-alpha label.

## 15. Sources & Artifacts

**Primary:** [BTS AIRRPMTSID11](https://fred.stlouisfed.org/series/AIRRPMTSID11), [EIA monthly WTI](https://www.eia.gov/dnav/pet/hist/rwtcm.htm), [BLS accommodation CES](https://fred.stlouisfed.org/series/CES7072100001), [BLS foodservice CES](https://fred.stlouisfed.org/series/CES7072200001). **Industry/issuer context:** [IATA 2025-06-02](https://www.iata.org/en/pressroom/2025-releases/2025-06-02-01/), [DAL FY2025 10-K](https://www.sec.gov/Archives/edgar/data/27904/000002790426000013/dal-20251231.htm), [UAL FY2025 10-K](https://www.sec.gov/Archives/edgar/data/100517/000010051726000023/ual-20251231.htm), [LUV FY2024 10-K](https://investors.southwest.com/sec-filings/all-sec-filings/content/0000092380-25-000024/luv-20241231.htm). Full grade, dates, coverage, limitations, usage role, revision policy and assumed lags are in `data/source_register.csv`. Raw inputs: `data/bts_bls_frozen_2026-10-26.csv`, `data/eia_energy_frozen_2026-10-08.csv`; computed panel: `data/derived_formation_panel.csv`; reproducible code: `analysis.py`, `run_analysis.py`, `tests/`; nine computed SVG figures and all statistical tables: `figures/`, `results/`; observed logs: `logs/`. **No security-return data, no invented performance metrics.**
