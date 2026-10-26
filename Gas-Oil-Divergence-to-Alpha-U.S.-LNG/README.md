# Gas–Oil Divergence-to-Alpha — U.S. LNG

> **Status:** Reproduced fixed-snapshot price-factor falsification; no equity alpha  
> **Research date:** 2026-10-19  
> **Scope:** WTI/Henry Hub divergence as a lead for natural-gas spot-price changes  
> **Study ID:** `lng` · [Quality standard](../RESEARCH_QUALITY_STANDARD.md) · [Machine-readable manifest](study.json)

## 01. Abstract

This study is part of **Signals to Alpha**, which treats real-economy data as *candidate* research signals and separates observable economic relationships from investable returns. Global LNG capacity expansion is a credible sector story, but relative oil–gas prices are not automatically a repeatable return signal. In **242** monthly expanding-window forecasts, the divergence model's RMSE was **32.707 pp** versus **30.911 pp** for momentum controls and **30.825 pp** for the historical mean. Alternative horizons, LNG-era splits, 2022 exclusion and stale-spread checks did not rescue the factor, and the data are not archival vintages. **Verdict:** failed natural-gas spot-price predictor; futures and equity alpha were not tested.

## 02. Research Design & Hypotheses

Can the oil-versus-gas price divergence predict subsequent natural-gas spot-price growth better than mean or momentum controls? H1: spread mean reversion helps; H2: an out-of-sample augmented model beats simple alternatives; H3: it survives LNG-era, horizon and placebo tests.

## 03. Industry Context

U.S. liquefaction capacity, feedgas needs and international LNG netbacks are economically relevant. EIA's industry capacity outlook is structural context; the observed price spread alone cannot prove a tradeable futures or equity edge.

## 04. Data & Source Integrity

Monthly Henry Hub and WTI series are snapshotted in `data/henry_hub_wti_monthly.csv`, with publisher, timing and units tracked in `data/source_register.csv`. Values reflect accessible historical data, not independently reconstructed real-time vintages.

## 05. Point-in-Time Availability

Release-date precision and historical data revisions are not established. Lagged features and purged expanding forecasts reduce some leakage risks but are insufficient to claim historical trade feasibility.

## 06. Factor Construction

Predefined factor compares WTI and Henry Hub relative prices using a stable transformation; implementation, scaling and horizons are in `run_analysis.py` and `research.ipynb`. Recalculation must use only data available at each formation origin.

## 07. Exposure & Transmission

This is a commodity-level time series, not an issuer exposure design. A firm-level LNG profitability thesis would require separately timestamped terminal capacity, feedgas, contract, company and currency exposures.

## 08. Outcomes & Baselines

The outcome is future natural-gas **spot-price change**, not total-return futures P&L or equity returns. Mean and momentum baselines are evaluated over the same 242 expanding-window OOS origins.

## 09. Empirical Findings

Primary RMSE: divergence model **32.707 pp**, momentum **30.911 pp**, historical mean **30.825 pp**. The candidate worsens errors, so a positive sector narrative does not imply signal validity.

## 10. Robustness & Placebos

One- and six-month lead targets, post-LNG-era samples, exclusion of 2022 and stale-spread placebos do not produce stable predictive advantage. These controls are exploratory and should not be advertised as proof of significance.

## 11. Regime Sensitivity

Natural-gas spot dynamics change with storage, weather, pipeline constraints and world LNG demand. Subperiod failures caution against extrapolation.

## 12. Bias Audit & Verdict

Latest-revised/unknown vintages, serial dependence, data-snooping, omitted futures roll/transaction costs, absent security fundamentals and survivorship controls remain. **Conclusion:** candidate factor rejected for current scope.

## 13. Reproduction

From this directory: `python -m pip install -r requirements.txt`; `python run_analysis.py --write`; `python -m unittest discover -s tests -v`; open `research.ipynb`. Snapshots and result JSON allow a consistent local reproduction attempt.

## 14. Next-Stage Protocol

Add historically timestamped LNG exports, feedgas, gas storage surprises, weather, global netbacks; then test roll-aware futures and issuer-level earnings/industry-adjusted returns with clean holdouts.

## 15. Sources & Artifacts

Primary sources are registered in `data/source_register.csv`. See [research notes](DETAILS.md) for original methodology, full tables and source links.
