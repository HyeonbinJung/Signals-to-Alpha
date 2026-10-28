# Network–Chip Production Balance and U.S. Computer Hardware Output

**Status:** REPRODUCED RETROSPECTIVE MACRO FALSIFICATION PILOT — **NOT POINT-IN-TIME; NOT EQUITY ALPHA**.  
**Research date:** 2026-10-28. **Outcome industry:** U.S. computer and peripheral equipment manufacturing, NAICS 3341.  
**Primary result:** the network-minus-chip production factor **worsens** 3-month-ahead computer-production YoY RMSE from **11.3479** to **11.4716 log percentage points** over 117 purged expanding-window origins; simple AR Ridge is better at **9.8988**.  
**Data provenance:** inherited, byte-verified 2011–2026 Federal Reserve G.17 fixed revised snapshot. No claim of independent data retrieval or historical release-vintage accuracy.

## 01. Abstract

**Research question:** Does the lagged U.S. communications-equipment production premium over semiconductor/electronic-component production forecast computer/peripheral equipment manufacturing output growth three months ahead, beyond its own dynamics and macro controls? This falsifiable hypothesis relates three separate NAICS production sectors rather than inferring company equity returns from a macro series. The 117-origin same-date OOS test finds **negative** incremental RMSE improvement **−0.1237 log-pp** (control 11.3479; augmented 11.4716); MAE also worsens (8.4467 to 8.7186). A 1,000-refit 12-month-block reorder gives an **exploratory** upper-tail fraction **0.4096** and a 2,000-draw paired moving-block bootstrap gives **[−0.6418, +0.1520] log-pp**; the interval crosses zero. The strongest tested AR Ridge baseline beats both. **Verdict:** negative retrospective macro factor, not a point-in-time or investable-alpha result.

## 02. Research Design & Hypotheses

The proposed transmission is a relative electronics-cycle imbalance: network-equipment production may proxy enterprise infrastructure demand, while semiconductor/electronic-component output partly captures supply and broad electronics activity. This is not a direct order-flow or supply-shortage measure; the two components can reflect common demand, outsourcing and measurement differences. **H1:** a positive lagged network-minus-chip production growth gap predicts higher next-quarter computer output YoY; **H2:** adding it to lagged computer growth/momentum, aggregate manufacturing and chip growth lowers purged OOS RMSE; **H3:** the incremental gain persists outside 2020–2021 and under lag, horizon and factor-weight changes. **Null:** the conditional incremental predictive value is zero. **Predeclared failure standard:** no robust evidence if the augmented model loses to controls or simple AR, the paired bootstrap interval contains zero, or regime/horizon effects are unstable. Counterthesis: sector production shares divergent technology cycles and measurement revisions rather than demand transmission.

## 03. Industry Context

U.S. Census NAICS 3341 covers computer and peripheral equipment manufacture (electronic computers, servers, storage and peripherals); NAICS 3342 covers communications equipment; NAICS 3344 covers semiconductors and other electronic components. These are distinct manufacturing classes. The frozen G.17 computer-production index increases from **77.1473** in January 2011 to **182.6599** in September 2026 (2017=100, SA), equivalent to approximately **5.66% annualized index growth** over that interval; this is **not** dollar market size or revenue growth. A verified historical dollar shipment market-size series was not collected, so the monetary market size is **UNKNOWN**, and no unsupported dollar estimate is supplied. The October 16, 2026 G.17 release and Census classification define the industrial scope; offshore manufacturing by U.S.-listed companies is outside this U.S. production index. See the exact publisher URLs in `data/source_register.csv`.

## 04. Data & Source Integrity

The research freezes **189 consecutive monthly rows (2011-01 through 2026-09)** from four Federal Reserve industrial-production series: `IPG3341S` (outcome), `IPG3342S` (network proxy), `IPG3344S` (chip/electronic components), `IPMAN` (aggregate manufacturing). The CSV is **byte-for-byte inherited** from the earlier semiconductor study (`Git blob 3d111120b93de0a5eb153d794772225f5dd1a6c4`; SHA-256 `6a6fca4b29755f0c2cae8ccfae1016a22648e724787cc42e726ac945583c351c`). It is not independently retrieved new data. Tests verify date uniqueness/continuity, strictly positive indices, no missing cells, correct column names and dates; independent source-row re-download and first-release validation remain incomplete. The A/B/C register identifies official sources (A), inherited frozen compilation (B), and analyst mechanism (C), with URL, publication/observation dates, revisions and rights limitations. `data/provenance_audit.md` documents failures and data reuse.

## 05. Point-in-Time Availability

At each hypothetical formation month **t**, the newest permitted observation is **t−2 months**, a conservative fixed buffer relative to normal monthly release scheduling. For the target at **t+h**, training origin **u** is admitted only if **u+h ≤ t−2**, avoiding forward-label leakage. Model scalers are fitted on each training window alone. The fixed 2026 revised series values for past dates may differ from actual first releases; **no ALFRED/FRASER vintage reconstruction was performed**. Hence the lag/purge discipline prevents mechanical use of future observation dates but does **not** prove historical PIT validity. Historical publication lags and revision magnitudes for each monthly observation are **UNKNOWN**.

## 06. Factor Construction

Let `g_{s,m}=100 ln(IP_{s,m}/IP_{s,m−12})` in log percentage points. The **predefined** relative production factor at formation month `t` is `F_t=g_{3342,t−2}−g_{3344,t−2}`. The computer output target is `Y_{t,h}=g_{3341,t+h}` with primary `h=3` months. Other fixed features are computer YoY `g_{3341,t−2}`, its three-month change `g_{3341,t−2}−g_{3341,t−5}`, manufacturing `g_{IPMAN,t−2}` and chip `g_{3344,t−2}`. The sign and unit weights are hypotheses, not fitted exposures; 1,000 perturbations use `F_t(k)=g_network,t−2−k*g_chip,t−2` with `k~Uniform(0.5,1.5)` and refit every origin. No full-sample normalization or ex-post factor fitting is used.

## 07. Exposure & Transmission

`data/exposure_map.csv` separates the **industry-level** mechanical mapping from **descriptive, non-tradable issuer examples**. Computer/peripheral manufacturing NAICS 3341 is the independent output, network manufacturing NAICS 3342 is the demand proxy, and chip/electronic components NAICS 3344 is the relative comparator. Dell (2025 10-K filed 2025-03-25), HP (2025 10-K filed 2025-12-10) and Cisco (2025 annual report) provide *illustrative* product associations, not a dated 2011–2026 historical issuer-weight panel. The mapping is not a company revenue exposure score, and no company-specific forward financials or stock returns are used. **Leave-one-company-out, issuer IC and long-short spreads are NOT APPLICABLE**, not counted as successful robustness tests. U.S. manufacturing output is not equivalent to globally reported issuer sales.

## 08. Outcomes & Baselines

The **only evaluated outcome** is aggregate U.S. computer/peripheral equipment **3-month-ahead 12-month log production growth**. The fixed common-origin baselines are expanding-window historical mean, stale computer YoY persistence, naive momentum extrapolation, AR Ridge on stale computer YoY/momentum, and multivariate Ridge with computer YoY/momentum + aggregate manufacturing + chip YoY. Challenger adds the network-minus-chip gap; a factor-only Ridge is also tested. All Ridge models use fixed `alpha=20`, train-only standardization, and a minimum **48** fully observed training origins. For each OOS formation date t, training labels end no later than t−2; 117 monthly OOS predictions span **2016-10 to 2026-06**. Each model shares exactly the same 117 dates. Metrics: RMSE, MAE and descriptive prediction/realization correlation; cross-sectional Rank IC/returns spreads are not meaningful without a stock universe.

## 09. Empirical Findings

| Model | OOS RMSE (log-pp) | MAE (log-pp) |
|:--|--:|--:|
| Historical mean | 13.1482 | 10.6264 |
| Computer YoY persistence | 11.7229 | 9.4970 |
| Naive momentum | 11.0615 | 9.0672 |
| **AR Ridge** | **9.8988** | **7.8444** |
| Multivariate macro control | 11.3479 | 8.4467 |
| Network-chip factor only | 13.4194 | 10.8767 |
| **Macro + network-chip factor** | **11.4716** | **8.7186** |

The observed incremental RMSE gain is `RMSE(control)−RMSE(full)=−0.1237 log-pp`, a **1.09% deterioration** relative to the control. The simple AR model outperforms the augmented model by **1.5727 log-pp**. These are actual calculations stored in `results/scorecard.csv` and `results/walk_forward_oos.csv`; no significance or trading inference is implied by the raw correlation in `results/metrics.json`. See `figures/01`–`11` for actual saved diagnostics.

## 10. Robustness & Placebos

The 1,000 **refitted** 12-month contiguous-block permutations reorder factor blocks while keeping targets and controls fixed; the observed improvement is compared to the null, giving exploratory upper-tail fraction **0.4096**. Because the block reordering does not ensure exchangeability under trends/serial dependence, this is **not** an exact randomization p-value. The 2,000 moving-block bootstrap resamples paired 117-origin prediction errors in 12-month blocks; the 95% RMSE-difference interval **[−0.6418, +0.1520]** crosses zero. Across 1,000 refitted `k∈[0.5,1.5]` chip-weight perturbations, **0%** of draws improve RMSE. A no-chip-control ablation gives RMSE **11.1930**, a no-manufacturing-control ablation **10.1973**, illustrating that feature specification matters; these were **not** preselected competitors. Leave-one-year-out evaluation reverses the RMSE sign only when **2018** is removed; it does not refit a company-level model. The 6- and 12-month horizon alternatives worsen RMSE relative to controls, with unequal sample sizes explicitly reported.

## 11. Regime Sensitivity

| Formation dates | OOS n | RMSE control | RMSE full | Gain (control−full) |
|:--|--:|--:|--:|--:|
| Before 2020 | 39 | 12.3991 | 12.8901 | **−0.4910** |
| 2020–2021 | 24 | 17.1729 | 16.9351 | **+0.2377** |
| 2022 onward | 54 | 6.0751 | 6.1366 | **−0.0615** |

The only positive regime is 2020–2021, when electronics supply and demand faced exceptional disruptions. Regime observations overlap through YoY targets; these partitions are descriptive rather than independent confirmatory holdouts. A different sign outside the pandemic violates H3. The historical panel is short relative to technology-cycle structural change.

## 12. Bias Audit & Verdict

**Lookahead:** label purge and train-only scaling are enforced; historical revisions remain unresolved. **Selection:** the factor and industry were chosen after many repository studies, so multiple testing and data reuse can bias the research agenda. **Survivorship:** aggregate official production is not a security universe; issuer-level delisting/mergers cannot be audited. **Publication:** t−2 buffer does not reconstruct first release values. **Serial dependence:** YoY overlap makes naive iid confidence intervals inappropriate. **Costs and capacity:** no prices, dividends, slippage, liquidity or trading strategy exist; costs cannot be estimated. **Economic confounds:** chip production, communications output and computer manufacturing share common technology cycles, globalization and measurement changes. **Verdict:** **H1 inconclusive; H2 fails OOS; H3 fails regime/horizon/weight robustness**. This is a reproducible retrospective *macro falsification*, **not** a validated PIT factor or equity alpha.

## 13. Reproduction

From this directory in a fresh checkout, using Python 3.11+ and an environment with the pinned-range requirements:

```bash
python -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python run_analysis.py
OPENBLAS_NUM_THREADS=1 python -m pytest -q tests
OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute --inplace research.ipynb --ExecutePreprocessor.timeout=900
# from the repository root:
python scripts/validate_studies.py
```

`run_analysis.py` writes derived inputs, 11 diagnostic figures, and scorecards; the three Monte Carlo stages run as separate processes for stability. The notebook recomputes primary OOS estimates and visualizations and verifies stored Monte Carlo outputs. `results/analysis_execution.log`, `results/test_execution.log`, and `results/notebook_execution.log` are execution evidence **only when the corresponding commands have actually completed**. Re-running with a different package version may change plot hashes and minor floating-point digits; no claim of universal bitwise reproducibility. The structural validator is not a statistical test.

## 14. Next-Stage Protocol

Obtain true monthly first-release vintages from ALFRED/FRASER and the Federal Reserve G.17 archives, with date-stamped formation availability and revision deltas; re-run the 2016–2026 OOS evaluation using actual available vintages. Expand the factor with order backlog, server shipments, capex announcements and supplier lead times, but pre-register features and hold out an untouched subsequent period. Build company-specific historical segment-revenue exposures from contemporaneous 10-K filings with report publication dates, including delisted firms; test sales/EPS before securities. Only then evaluate sector-neutral **total returns** with dividends, execution costs, capacity, cross-sectional IC, portfolio spreads and multiple-testing adjustment. A prospective holdout should be a requirement before promoting any macro hypothesis to equity alpha.

## 15. Sources & Artifacts

Primary official sources: Federal Reserve G.17 release dated **2026-10-16** (`https://www.federalreserve.gov/releases/g17/20261016/default.htm`); FRED `IPG3341S`, `IPG3342S`, `IPG3344S`, `IPMAN` (`https://fred.stlouisfed.org/series/IPG3341S` and corresponding series URLs); Census NAICS 2017 definitions (`https://www.census.gov/naics/2017NAICS/2017_Definition_File.pdf`); Dell 2025 10-K (`https://www.sec.gov/Archives/edgar/data/1571996/000157199625000034/dell-20250131.htm`), HP 2025 10-K (`https://www.sec.gov/Archives/edgar/data/47217/000004721725000071/hpq-20251031.htm`), Cisco 2025 annual reports (`https://www.cisco.com/c/en/us/about/annual-reports.html`). The byte-identical inherited source is the earlier semiconductor study's G.17 CSV; see `data/source_register.csv` and `data/provenance_audit.md` for A/B/C grades, observation dates, unknown vintages and rights. Computed artifacts: `data/derived_formation_panel.csv`, `results/metrics.json`, `results/scorecard.csv`, `results/walk_forward_oos.csv`, 1,000/2,000-draw Monte Carlo CSVs, regime/horizon/ablation/leave-year tables, 11 PNG charts, 15-section `research.ipynb`, `computer_factor.py`, `compute_draws.py`, `run_analysis.py`, tests and execution logs. **No corporate returns, corporate OOS fundamentals, PIT source vintages, or investable alpha evidence are included.**
