# Active Ownership → Market-Wide Information: Research Study

> **Status: SYNTHETIC SOFTWARE TEST ONLY — EMPIRICAL ALPHA NOT ESTABLISHED.** This is a paper-inspired implementation; its synthetic Sharpe ratio must not be confused with a market result. See [technical notes](DETAILS.md) and [synthetic scorecard](results_synthetic/RESULTS.md).

## 01. Abstract

Chen and Yin (2026) report that return spreads across stocks with high versus low active-manager ownership forecast next-day S&P 500 futures/ETF returns, with market-timing Sharpe near one. We implement the idea with point-in-time (PIT) holdings, a Newey–West forecast test and next-open intraday execution with trading costs. Seven unit tests pass; a deliberately predictive **synthetic** process yields a net Sharpe of 2.8902 and HAC t-statistic 7.1924, which merely validates computational functionality. **Verdict: reproducible software validation, not paper replication or investable equity alpha.**

## 02. Research Design & Hypotheses

Question: Does a day-*t* ownership-weighted cross-sectional return spread forecast market return on *t+1*, and is any gain tradable after next-open costs? H1: the signal predicts next-day market close-to-close returns. H2: a precommitted signal threshold generates positive next-open-to-close returns after costs. H3: investor-group and sector-neutral variations survive. Null/failure: non-significant incremental prediction or lack of positive after-cost holdout performance. No real historical PIT data were available here to test these economic hypotheses.

## 03. Industry Context

This is an asset-pricing and fund-management study, not a particular NAICS industry. Specialized active managers may impound common information in stock prices before slower-moving index capital adjusts; this mechanism remains a *hypothesis*. Relevant instruments: U.S. listed common stocks and S&P 500 ETF/futures. Market size, growth and firm-level industry transmission estimates are **UNKNOWN** in this code-validation stage.

## 04. Data & Source Integrity

Real replication requires historical delisting-inclusive total returns (e.g. CRSP), published ownership with manager-level historical active/passive classifications (SEC 13F or LSEG s34) and precise ETF open, close and distributions. [Source register](data_sources.csv). Input `prices.csv`: `date,security_id,ret` plus optional `sector,market_cap,eligible`; input `holdings.csv`: `security_id,report_date,available_date,owner_type,active_ownership` (fraction, including zero owners); input `market.csv`: `date,cc_return,oc_return` (decimal returns). The committed synthetic generator embeds predictive association intentionally, using seed 42; data are not authentic market observations.

## 05. Point-in-Time Availability

SEC 13F is generally due within 45 days of quarter end, but each manager's **actual filing timestamp** is required for PIT work. The join requires `available_date < signal_date`; same-day filings are conservatively excluded, stale snapshots over 200 days are invalid, and t-close signals cannot be filled before t+1 open. A real-data version also needs amendments, historical CUSIP↔PERMNO links, historical active/passive classifications, zero-holding coverage and a survivor-free universe. Using quarter-end holdings on quarter-end trading dates is a forbidden look-ahead.

## 06. Factor Construction

Define `S[t] = mean(return of top-20% ownership stocks at t) − mean(return of bottom-20% at t)`; `Z[t] = (S[t] − trailing 126-day mean through t−1) / trailing 126-day standard deviation through t−1`. Position after t close: +1 if `Z[t] ≥ 0.25`, −1 if `Z[t] ≤ −0.25`, otherwise flat. Positions execute **only** at open(t+1) and close at close(t+1). The weights, thresholds and quintile choices are ours, **not verified as the paper's exact construction**. Baseline equal weighting; optional value-weighted or sector-neutral variants.

## 07. Exposure & Transmission

Individual stock research produces firm-specific and market-wide information. If information-rich stocks respond earlier than index capital, their return spreads may forecast future market adjustment. The model intuition uses specialized managers and slow-moving capital, but regression results alone do not prove that mechanism. Market beta, liquidity, factor exposure, sector imbalance and funding conditions remain competing hypotheses.

## 08. Outcomes & Baselines

Forecast `market cc_return[t+1]` on `S[t]`, with Newey–West HAC(5) coefficient, t-statistic, p-value and R²; also control for same-day market return. Trade next-open to same-close using ETF `oc_return[t+1]`, subtract 2 bps **per side** by default and optional short borrow. Report gross/net cumulative growth, CAGR, Sharpe, Sortino, max drawdown, hit rate, 95% moving-block-bootstrap Sharpe interval and chronological 70/30 descriptive split. Compare with an always-long intraday ETF reference and a separately labeled market close-close benchmark (different holding windows).

## 09. Empirical Findings

**No empirical real-price findings yet.** The synthetic fixture contains 850 daily observations and is constructed to generate predictability. Its net Sharpe **2.8902**, net CAGR **52.70%**, max drawdown **−12.32%** and predictive HAC t-statistic **7.1924** only check the pipeline. [Exact synthetic results](results_synthetic/RESULTS.md) · [JSON](results_synthetic/metrics.json) · [Plot](results_synthetic/equity.png) · [Executed notebook](research.ipynb). The authors' Sharpe near 1 and model-implied 20% market-information share remain **unreplicated**.

## 10. Robustness & Placebos

[`robustness.py`](robustness.py) tests tail groups 10%/20%/30%, costs 1/2/5/10 bps per side, investor-type alternatives and a sector-neutral variant. In the artificial data, net Sharpe for the 20% signal falls from 3.1348 at 1 bps to 0.9125 at 10 bps per side. In the generator, hedge-fund and active-mutual-fund ownership rank stocks in the same order **by construction**, so their equal synthetic results do not validate any manager heterogeneity. Placebo time shifts, equity factor residualization, beta matching and false-discovery adjustments remain necessary with real data. [Sensitivity CSV](results_synthetic/robustness.csv).

## 11. Regime Sensitivity

The paper abstract reports stronger effects in recession/high-uncertainty periods and longer persistence under tight funding. This synthetic simulator has no legitimate NBER, VIX, funding-spread or international-regime series. Current real-market regime sensitivity is **UNKNOWN**. Required extensions: prespecified historical state masks, available-at-time indicator vintages and well-powered subsamples.

## 12. Bias Audit & Verdict

Threats: 13F release delay/amendments, long-only disclosures hiding shorts, manager-classification revisions, unstable CUSIP mappings, survivor bias, delisting omissions, risk factor exposure, high-turnover ETF costs, borrowing, market impact, repeated model selection and mechanism non-identification. The predictive **close-close** target is not an executable strategy return; only t+1 **open-close** is credited in the implementation. **Verdict: code validated on synthetic data; genuine empirical and investable-alpha claims withheld.**

## 13. Reproduction

```bash
cd Active-Ownership-to-Market-Alpha
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python make_synthetic_fixture.py --out data/synthetic
python backtest.py --prices data/synthetic/prices.csv --holdings data/synthetic/holdings.csv --market data/synthetic/market.csv --source-label synthetic --out outputs/synthetic
python robustness.py --prices data/synthetic/prices.csv --holdings data/synthetic/holdings.csv --market data/synthetic/market.csv --out outputs/synthetic/robustness.csv
```

Open `research.ipynb` from the study directory for a narrative and executed charts. Private or licensed empirical inputs go under the git-ignored `data/private/`. The committed results contain seed-42 **synthetic** outputs only.

## 14. Next-Stage Protocol

1. Obtain manager type plus true filing dates, amended 13F ownership and historical shares-outstanding; document how manager positions are aggregated.
2. Obtain CRSP PIT security universe/delisting adjusted returns, time-varying identifiers, index/ETF open-close total returns and a risk-free series.
3. Read the complete Chen–Yin draft and reconcile exact portfolio formation rules, universes, horizons and numbered result tables.
4. Freeze parameters on a training sample and test an untouched chronological holdout, factor controls, bootstrap/placebo, regime and trading-cost sensitivity.
5. Publish actual signed real-data findings, including negative results, only after the [repository research quality gate](../RESEARCH_QUALITY_STANDARD.md) passes.

## 15. Sources & Artifacts

- Chen & Yin (2026), [*Between the Bells: Active Management and the Aggregation of Market-Wide Information*](https://ssrn.com/abstract=7367200).
- [SEC 13F data](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets) · [Investor.gov filing rule](https://www.investor.gov/introduction-investing/investing-basics/glossary/form-13f-reports-filed-institutional-investment) · [WRDS](https://wrds-www.wharton.upenn.edu/).
- [Data sources](data_sources.csv) · [Technical notes](DETAILS.md) · [Backtester](backtest.py) · [Sensitivity script](robustness.py) · [Executed notebook](research.ipynb) · [Tests](tests/test_backtest.py).
- [Synthetic scorecard](results_synthetic/RESULTS.md) · [Equity curve](results_synthetic/equity.png) · [Robustness grid](results_synthetic/robustness.csv) · [Study manifest](study.json).
