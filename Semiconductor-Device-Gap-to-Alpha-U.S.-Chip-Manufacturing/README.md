# Device-Gap-to-Alpha — U.S. Semiconductors

> **Status:** Executed fixed-snapshot macro falsification; no equity alpha  
> **Research date:** 2026-10-19  
> **Scope:** Downstream device production as lead for chip/component output  
> **Study ID:** `semiconductor` · [Quality standard](../RESEARCH_QUALITY_STANDARD.md) · [Machine-readable manifest](study.json)

## 01. Abstract

This study is part of **Signals to Alpha**, which treats real-economy data as *candidate* research signals and separates observable economic relationships from investable returns. Downstream computer and communications-equipment output may lead chip production, but the global semiconductor demand story alone is not a predictive factor. In **108** expanding-window forecasts the device gap produced RMSE **4.746 pp**, worse than macro controls (**4.713 pp**) and semiconductor persistence (**4.468 pp**). A moving-block bootstrap interval straddles zero and an exploratory block-placebo (**p≈0.796**) offers no support; data are latest-revised snapshots. **Verdict:** no robust incremental production predictor and no tested equity alpha.

## 02. Research Design & Hypotheses

Does U.S. downstream computer and communications-equipment output forecast future domestic semiconductor/component production? H1: a device-versus-chip growth gap leads output; H2: it beats persistence and manufacturing controls; H3: it survives placebo, ablations, perturbations and regimes.

## 03. Industry Context

AI/memory demand is a relevant global industry driver, but a U.S. downstream-versus-upstream manufacturing gap is vulnerable to imports, geographic fragmentation and inventory cycles. WSTS 2026 industry projections are contextual, not historical factor inputs.

## 04. Data & Source Integrity

Official Federal Reserve G.17 / FRED monthly index snapshot from 2011-01 to 2026-09 (189 observations per series); `source_register.csv` identifies series, updates and vintage limitations. Analysis uses actual index data, not synthetic firm financial histories.

## 05. Point-in-Time Availability

At formation *t*, features use source month *t−2* or earlier; training origins must have mature labels. Because all past values come from a single revised 2026 snapshot, the result is **not** an archival point-in-time exercise.

## 06. Factor Construction

Define `g[j,s]=100 ln(IP[j,s]/IP[j,s−12])`; `gap[t]=tanh((0.5*g[computer,t−2]+0.5*g[communications,t−2]−g[semiconductor,t−2])/15)`. Fixed weight 0.5 and scale 15; train-fold standardized Ridge `α=10`.

## 07. Exposure & Transmission

IPG3341S computers and IPG3342S communications feed the downstream proxy; IPG3344S chips is the target; IPMAN provides cycle control. No stock universe, issuer product exposure or earnings panel is present.

## 08. Outcomes & Baselines

Target: `g[semiconductor,t+3]` (future 3-month-ahead YoY output). 108 purged expanding forecasts compare historical mean, persistence, macro+momentum controls, and those controls plus device gap.

## 09. Empirical Findings

Primary RMSE mean **5.222 pp**, persistence **4.468 pp**, macro **4.713 pp**, augmented **4.746 pp**. The factor fails the main macro-control comparison; it does not represent an equity signal.

## 10. Robustness & Placebos

Six-month moving-block bootstrap interval of incremental RMSE improvement **[−0.149, 0.077] pp** includes zero. Exploratory 2,000-replicate block-permutation (**p≈0.796**) does not establish improvement; see `results/metrics.json`.

## 11. Regime Sensitivity

Possible structural dependence on 2022+, US/global manufacturing geography, sourcing changes and serially overlapping horizons cautions against single-regime claims.

## 12. Bias Audit & Verdict

Release/revision vintages, geographic mismatch, firm selection, absent securities data and overlapping forecast errors remain open. **Conclusion:** no confirmed downstream-device lead factor; no investable alpha studied.

## 13. Reproduction

From this directory: `python -m pip install -r requirements.txt`; `python semiconductor_alpha.py`; `python -m pytest -q tests/test_semiconductor_alpha.py`; inspect `research.ipynb`. Deterministic results and SVG plots are stored under `results/` and `figures/`.

## 14. Next-Stage Protocol

Reconstruct historic G.17 vintages and period-correct WSTS/shipments/inventory; date issuer-level exposure and filings, then test forward fundamentals and survivorship-free returns with conservative costs, controls and untouched validation.

## 15. Sources & Artifacts

References: Federal Reserve G.17 and FRED IPG3344S, IPG3341S, IPG3342S, IPMAN; WSTS Spring 2026 outlook (context only). See [research notes](DETAILS.md) and `source_register.csv` for exact citations.
