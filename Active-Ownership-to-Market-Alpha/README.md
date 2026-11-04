# Active Ownership → Market-Wide Information: Research Study

> **Status: REAL PUBLIC-DATA EXPLORATORY PILOT FAILED TO FIND ALPHA.** The selected-manager breadth **proxy** is not the paper's exact Active Ownership variable. In the 272-session 2023–2024 pilot, net Sharpe = **−1.052**, net return = **−8.77%** and predictive HAC p = **0.803**. The earlier synthetic Sharpe 2.8902 is only a software test; never treat it as live-market evidence. [Real-data pilot](outputs/real_2024_pilot/REAL_PILOT_RESULTS.md) · [source audit](outputs/real_2024_pilot/audit.json).

## 01. Abstract

Chen and Yin (2026) report that return spreads across stocks with high versus low active-manager ownership forecast next-day S&P 500 futures/ETF returns, with market-timing Sharpe near one. Our original software validation on deliberately predictive synthetic data reported Sharpe 2.8902. **The new public-data experiment instead uses 127 actual SEC Form 13F filings from 26 selected managers and historical equities/ETF prices:** this restricted proxy has net Sharpe **−1.052**, 272 sessions, HAC p **0.803**. These are two distinct experiments; **neither replicates the original paper's precise Active Ownership construction**. No investable alpha is established.

## 02. Research Design & Hypotheses

Question: Does a day-*t* ownership-weighted cross-sectional return spread forecast market return on *t+1*, and is any gain tradable after next-open costs? H1: the signal predicts next-day market close-to-close returns. H2: a precommitted signal threshold generates positive next-open-to-close returns after costs. H3: investor-group and sector-neutral variations survive. Null/failure: non-significant incremental prediction or lack of positive after-cost holdout performance. The 2024 **real-data breadth proxy** rejects neither null; it is not sufficient to confirm or reject the original paper.

## 03. Industry Context

This is an asset-pricing and fund-management study, not a particular NAICS industry. Specialized active managers may impound common information in stock prices before slower-moving index capital adjusts; this mechanism remains a *hypothesis*. Relevant instruments: U.S. listed common stocks and S&P 500 ETF/futures. Market size, growth and firm-level industry transmission estimates are **UNKNOWN** in this code-validation stage.

## 04. Data & Source Integrity

The exploratory experiment combines five **official SEC Form 13F bulk ZIPs** for filing dates in October 2023–November 2024, a **third-party historical S&P 500 price/index-membership dataset** from [Johnbrick123/sp500-data](https://github.com/Johnbrick123/sp500-data), and a **retrospective, not point-in-time CUSIP–ticker crosswalk** from [ReAXET/Stock_Data](https://github.com/ReAXET/Stock_Data). The 26-manager list is hand-picked. The signal is *manager holding breadth*, not shares owned / shares outstanding. Source file SHA256 hashes, names, filings and coverage appear in [audit.json](outputs/real_2024_pilot/audit.json). For exact original-paper replication, historical active/passive classification, definitive manager-parent aggregation, dated security IDs and historical shares outstanding are still needed. The separate synthetic generator remains a functionality test only.

## 05. Point-in-Time Availability

SEC 13F is generally due within 45 days of quarter end. In the actual pilot, the *specific* SEC filing date updates each manager's holdings; the join requires `available_date < signal_date`, with same-day filings excluded. Stale snapshots over 200 days are invalid; positions fill no earlier than next open. 13F-HR initial reports only; amendments and confidential treatment are not reconstructed. The third-party index membership uses historical intervals, but ticker/CUSIP resolution remains retrospective and therefore introduces possible identifier look-ahead. No quarter-end holdings are made tradable at quarter end.

## 06. Factor Construction

General engine: `S[t] = mean(return of high-ownership stocks at t) − mean(return of low-ownership stocks at t)`. The public-data pilot specifically defines breadth as `number of the 26 currently reporting selected managers holding a ticker / number of currently reporting managers` and applies inclusive 20th/80th percentile groups, avoiding arbitrary alphabetical tie-breaking of zero-breadth stocks. It uses a **63-session rolling z-score** with the mean/std ending *t−1*, minimum 40 prior signals. Position after t close: +1 if `Z[t] ≥ 0.25`, −1 if `Z[t] ≤ −0.25`, otherwise flat. Positions execute only at open(t+1) and close(t+1); 2 bps per side. The previous synthetic engine defaults to a distinct 126-session lookback. Both are **our unverified specifications**, not attributed to the authors.

## 07. Exposure & Transmission

Individual stock research produces firm-specific and market-wide information. If information-rich stocks respond earlier than index capital, their return spreads may forecast future market adjustment. The model intuition uses specialized managers and slow-moving capital, but regression results alone do not prove that mechanism. Market beta, liquidity, factor exposure, sector imbalance and funding conditions remain competing hypotheses.

## 08. Outcomes & Baselines

Forecast `market cc_return[t+1]` on `S[t]`, with Newey–West HAC(5) coefficient, t-statistic, p-value and R²; also control for same-day market return. Trade next-open to same-close using ETF `oc_return[t+1]`, subtract 2 bps **per side** by default and optional short borrow. Report gross/net cumulative growth, CAGR, Sharpe, Sortino, max drawdown, hit rate, 95% moving-block-bootstrap Sharpe interval and chronological 70/30 descriptive split. Compare with an always-long intraday ETF reference and a separately labeled market close-close benchmark (different holding windows).

## 09. Empirical Findings

**REAL 2023-11–2024-11 EXPLORATORY PILOT:** 26 SEC 13F managers, 127 reports, 481 mapped price/membership-eligible names, 272 SPY sessions, 262 signal days and 186 active trading days. **Net cumulative return −8.77%, net CAGR −8.16%, net Sharpe −1.052, max drawdown −13.79%, gross return −1.73%; HAC t = −0.249 and p = 0.803 (n=261).** SPY close–close buy-and-hold gained 46.04% in this particular period, but is an **incommensurate holding window** to our intraday trade. Last 30%-of-sessions strategy return −11.68% (descriptive, not untouched OOS). See [full real results](outputs/real_2024_pilot/RESULTS.md), [metrics](outputs/real_2024_pilot/metrics.json) and [daily trade audit](outputs/real_2024_pilot/daily.csv). **SYNTHETIC SOFTWARE TEST:** 850 artificial sessions with planted alpha, net Sharpe 2.8902 and HAC t 7.1924; [separate results](results_synthetic/RESULTS.md). The original paper's Sharpe and structural market-information share remain **unreplicated**.

## 10. Robustness & Placebos

[`real_robustness.py`](real_robustness.py) mechanically varies round-trip costs on **exactly the same pre-fixed 2024 actual-price trades** and exports [real-data cost stress](outputs/real_2024_pilot/cost_sensitivity.csv), without selecting a better threshold after inspecting returns. Separately, [`robustness.py`](robustness.py) tests tail groups, cost sensitivity and investor type on **artificial data only**; those high synthetic scores are not empirical evidence. Still required: a multi-year historical active/passive fund panel, factor residualization, placebo, multiple-testing adjustment and holdout.

## 11. Regime Sensitivity

The paper abstract reports stronger effects in recession/high-uncertainty periods and longer persistence under tight funding. This synthetic simulator has no legitimate NBER, VIX, funding-spread or international-regime series. Current real-market regime sensitivity is **UNKNOWN**. Required extensions: prespecified historical state masks, available-at-time indicator vintages and well-powered subsamples.

## 12. Bias Audit & Verdict

Threats: manager-selection discretion, related managers counted separately, 13F delay and amendments, undisclosed shorts/confidential holdings, no historical active/passive fund classification, retrospective CUSIP mappings, survivorship/delisting errors in third-party sources, factor exposures, 2-bps-per-side assumption, borrow/financing, market impact, repeated model selection and unidentified mechanisms. Regression close–close targets are **not executable payoffs**; only t+1 open–close is credited. **Verdict: real-data proxy yielded negative net returns and no significant predictability. This does not refute or reproduce the paper's thesis.**

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

**Re-run actual 2024 public-data proxy (downloads ~600 MB; source assets may update):**

```bash
python -m pip install -r requirements-real.txt
export SEC_USER_AGENT='Your Name your-real-email@example.org'
python download_real_data.py --out data/public-2024
python real_data_pilot.py --source-dir data/public-2024 --out outputs/real_2024_pilot
python real_robustness.py --daily outputs/real_2024_pilot/daily.csv --out outputs/real_2024_pilot/cost_sensitivity.csv
```

Check SHA256 against [the committed source audit](outputs/real_2024_pilot/audit.json) before interpreting differences: the dataset maintainer updates its Parquet release; no raw vendor dataset is checked in. Real-data code/results and the synthetic fixtures are deliberately kept separate.

## 14. Next-Stage Protocol

1. Obtain manager type plus true filing dates, amended 13F ownership and historical shares-outstanding; document how manager positions are aggregated.
2. Obtain CRSP PIT security universe/delisting adjusted returns, time-varying identifiers, index/ETF open-close total returns and a risk-free series.
3. Read the complete Chen–Yin draft and reconcile exact portfolio formation rules, universes, horizons and numbered result tables.
4. Freeze parameters on a training sample and test an untouched chronological holdout, factor controls, bootstrap/placebo, regime and trading-cost sensitivity.
5. Publish actual signed real-data findings, including negative results, only after the [repository research quality gate](../RESEARCH_QUALITY_STANDARD.md) passes.

## 15. Sources & Artifacts

- Chen & Yin (2026), [*Between the Bells: Active Management and the Aggregation of Market-Wide Information*](https://ssrn.com/abstract=7367200).
- [SEC 13F data](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets) · [Investor.gov filing rule](https://www.investor.gov/introduction-investing/investing-basics/glossary/form-13f-reports-filed-institutional-investment) · [WRDS](https://wrds-www.wharton.upenn.edu/).
- [Historical S&P500 membership/prices](https://github.com/Johnbrick123/sp500-data) · [CUSIP crosswalk](https://github.com/ReAXET/Stock_Data) · [Actual 2024 pilot](outputs/real_2024_pilot/REAL_PILOT_RESULTS.md) · [Actual daily CSV](outputs/real_2024_pilot/daily.csv) · [Real-price equity curve](outputs/real_2024_pilot/equity.png).
- [Data sources](data_sources.csv) · [Technical notes](DETAILS.md) · [Backtester](backtest.py) · [Sensitivity script](robustness.py) · [Executed notebook](research.ipynb) · [Tests](tests/test_backtest.py).
- [Synthetic scorecard](results_synthetic/RESULTS.md) · [Equity curve](results_synthetic/equity.png) · [Robustness grid](results_synthetic/robustness.csv) · [Study manifest](study.json).
