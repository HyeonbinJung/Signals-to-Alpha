# Supplementary Technical Notes — Active Ownership PIT Backtest

> **Status: IMPLEMENTATION COMPLETE / EMPIRICAL REPLICATION PENDING DATA.**
> This is a research-grade, **paper-inspired** implementation and validation harness, **not** a reproduction of the authors' Sharpe ≈ 1. The bundled run uses deliberately synthetic data and must not be used as evidence of financial alpha.

Based on *Between the Bells: Active Management and the Aggregation of Market-Wide Information* (Shuaiyu Chen and Cynthia Yin, 2026), [SSRN](https://ssrn.com/abstract=7367200).

## 1. Executive summary

Chen and Yin report that the daily return spread between stocks with high and low active-manager ownership forecasts next-day S&P 500 futures and ETF returns, with market-timing Sharpe ratios near one. They attribute the pattern to information produced by specialized active managers aggregating into a common signal, while index capital moves slowly. Their structural model associates approximately 20% of stock-level signal variance in high-active-ownership stocks with market-wide information. This repository tests the **observable prediction** with strict point-in-time alignment; it does **not** estimate their structural model. The authors' precise full-paper empirical specification is not established from the publicly accessible abstract.

## 2. Research question

Do high-minus-low active-ownership stock return spreads observed by the end of trading day *t* predict the market's close-to-close return on *t+1*? More importantly, does a position entered at the **next day's opening print** earn positive **after-cost intraday** returns? These are **different estimands**.

## 3. Hypotheses

- **H1 — predictive signal:** the cross-sectional return spread forecasts next-day market return (Newey–West HAC predictive regression).
- **H2 — tradability:** a precommitted threshold rule applied at day *t* close profits from *t+1* open-to-close after realistic entry/exit costs.
- **H3 — active-manager heterogeneity:** hedge-fund versus active-mutual-fund ownership groupings provide different signal strengths.
- **H4 — robustness:** signals survive ownership-threshold changes, sector neutrality and trading-cost stress.

## 4. Information-set and data design

Data are expected as three **long-format CSVs**; no account credentials are stored in the repository.

### `prices.csv`

| Column | Type | Description |
| --- | --- | --- |
| `date` | YYYY-MM-DD | Security return trading date |
| `security_id` | string | **Stable historical** security ID, not a reused ticker |
| `ret` | float | Decimal **total** daily stock return, including delisting when applicable |
| `sector` | string (optional) | Point-in-time sector classification |
| `market_cap` | float (optional) | Point-in-time capitalization for value weighting |
| `eligible` | boolean (optional) | Historical, precommitted universe membership |

### `holdings.csv`

| Column | Type | Description |
| --- | --- | --- |
| `security_id` | string | Same stable security ID as price input |
| `report_date` | YYYY-MM-DD | Date **of** the reported holdings (often quarter-end) |
| `available_date` | YYYY-MM-DD | Earliest date the aggregate ownership measure was **actually public** |
| `owner_type` | string | e.g., `all_active`, `hedge_fund`, `active_mutual_fund` |
| `active_ownership` | float | Fraction of shares outstanding, **0 to 1**, with complete zero rows |

Ownership must already be aggregated correctly across managers and reconciled for positions reported in amendments. The pipeline cannot infer active/passive classifications from a raw 13F filing. **A manager-level point-in-time classification table is necessary** for credible empirical replication. Every eligible security must have a value, including *zero*, not only positive holdings; omission would bias low-ownership groups. Portfolio holdings reported at quarter-end are **not** available until the actual filing release date.

### `market.csv`

| Column | Type | Description |
| --- | --- | --- |
| `date` | YYYY-MM-DD | Market trading date |
| `cc_return` | float | Decimal close-to-close index/ETF **total return** (predictive target) |
| `oc_return` | float | Decimal **next-session open-to-close** tradable ETF return |

The desired index, ETF, futures contract specifications, roll adjustments, distributions, session boundaries, and transaction-cost model must be fixed before comparing to the paper. Market `oc_return` is a separate payoff, **not** the paper's reported close-to-close estimate.

### Required publication-time safeguards

1. `available_date` must come from a verifiable filing/release timestamp, not the quarter-end reference date. Form 13F is generally due within 45 days of quarter end; filing timing is not identical across managers.
2. The as-of join uses `available_date < signal_date`, conservatively disallowing same-day releases.
3. Historical CUSIP↔PERMNO mappings must be time-aware; ticker matching is **not enough**.
4. Include delisted and formerly index-eligible securities, dividends and split adjustments, avoiding survivorship and corporate-action bias.
5. Preserve raw filing, revision and normalization provenance separately from the final ownership panel.
6. An initial pre-sample lookback for ownership is necessary; do not backfill a future-known holdings ratio.

## 5. Model & formulas

For trading day *t*, sort eligible equities by the latest published ownership fraction `AO_i,t`. With upper/lower fraction `q`:

```text
S[t] = mean_return(highest-q AO stocks, t) - mean_return(lowest-q AO stocks, t)
Z[t] = (S[t] - mean(S[t-126:t-1])) / stdev(S[t-126:t-1])
decision[t] = +1 if Z[t] >= 0.25, -1 if Z[t] <= -0.25, else 0
position_at_open[t+1] = decision[t]
gross[t+1] = position_at_open[t+1] * ETF_open_to_close_return[t+1]
net[t+1] = gross[t+1] - abs(position)*2*side_cost_bps/10000 - short_borrow_cost
```

`Z[t]` uses only historical signal observations through **t−1** to estimate its mean and standard deviation; the day-t signal itself is known only at the close. The rule is not fitted to future labels. The implementation uses equal-weight return spreads by default; optional value weighting and sector-neutral spreads are available. This is **our** implementation, not a claim about the authors' exact specification.

## 6. Prediction test ≠ trading return

- **Prediction:** regress `market cc_return[t+1]` on `signal[t]`; report coefficient, `t` and `p` with Newey–West (5 lags), R² and observations. A second regression controls for contemporaneous market close-to-close returns.
- **Trading:** enter at `open[t+1]`, exit at `close[t+1]`. This gives up overnight return deliberately. A day-t close fill would be improperly optimistic unless close-auction order timing is modeled.
- **Costs:** default **2 bps each way**, plus configurable per-short-day borrow fee. Execute one round trip per active day. Equity curves include an always-long intraday reference **and** a distinct close-to-close market benchmark; they are not identical exposure windows.
- **Risk:** annualized Sharpe/Sortino, CAGR, cumulative return, max drawdown, hit rate, gross vs net, and 5-day moving-block-bootstrap Sharpe interval.

## 7. Installation

```bash
cd Active-Ownership-to-Market-Alpha
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Windows PowerShell users can use identical `python` commands from the repository folder.

## 8. Reproduce the SYNTHETIC software test

```bash
python make_synthetic_fixture.py --out data/synthetic
python backtest.py \
  --prices data/synthetic/prices.csv \
  --holdings data/synthetic/holdings.csv \
  --market data/synthetic/market.csv \
  --source-label synthetic \
  --out outputs/synthetic
python robustness.py \
  --prices data/synthetic/prices.csv \
  --holdings data/synthetic/holdings.csv \
  --market data/synthetic/market.csv \
  --out outputs/synthetic/robustness.csv
```

Outputs: `daily.csv`, `metrics.json`, `equity.png`, `RESULTS.md`, `config.json`, `provenance.json`, `robustness.csv`.

**Synthetic generation deliberately injects an information-transfer effect and normal noise.** Synthetic Sharpe, regression significance, and positive profitability are **engineering assertions**, **not** replicated research results. No synthetic performance figure should be quoted without its synthetic label.

## 9. Real-data backtest

Once licensed PIT CRSP or equivalent survivor-free daily security returns, historically classified 13F ownership and ETF/index market data are available:

```bash
python backtest.py \
  --prices data/private/crsp_daily.csv \
  --holdings data/private/active_ownership_pit.csv \
  --market data/private/spy_daily.csv \
  --source-label licensed --out outputs/crsp_pit
```

Do not upload licensed data. Document universe, sample, vendor, extraction time, 13F classification and amended-filing policy in a separate reproducibility manifest. If only free public prices are used, label them separately and disclose missing delistings and adjusted-dividend limitations. The CLI does **not** currently collect raw SEC filings: its input is a **validated, already-normalized ownership panel**.

## 10. Robustness grid

`robustness.py` runs:

- Ownership tail fractions: 10%, 20%, 30%.
- Per-side costs: 1, 2, 5, 10 bps.
- Ownership groups present in file (e.g. hedge funds, active mutual funds).
- Optional sector-neutral signal; equal sector contributions.
- First 70% / last 30% descriptive chronological performance.

**Caution:** these are sensitivity checks, **not** selection of the best Sharpe post hoc. A true holdout requires freezing parameters before reviewing its outcome. Multiple testing correction or a reality check is necessary before declaring discovered alpha.

## 11. Economic objections & identification

1. **Factor risk masquerading as information:** momentum, size, liquidity, sector, market beta, and contemporaneous risk-on trading can cause the spread. The included same-day market control/sector-neutral variants are partial defenses, not exhaustive factor attribution.
2. **Ownership endogeneity:** managers choose stocks for characteristics that independently predict returns. Ownership may proxy for liquidity/analyst coverage rather than private information.
3. **Slow-moving index capital vs fast index futures:** demonstrate that the price discovery delay survives controls for overnight gaps, funding liquidity and futures execution timing.
4. **Publication lag:** quarterly holdings are not real-time trades; no reconstructed daily portfolio may use postdated 13F data.
5. **Survivorship:** index constituents today are an invalid historical test universe.
6. **Market impact / capacity:** a cost-only simulator does not estimate real limit-order liquidity, financing, constraints or slippage across economic regimes.

## 12. What would qualify as a paper replication?

This project must satisfy **all** conditions before status can change from `IMPLEMENTED_NOT_REPLICATED_DATA_PENDING`:

- Full 82-page paper reviewed; exact ownership definition, filters, sample period, daily return construction, horizons and portfolio weights coded.
- Point-in-time ownership/splits/returns, including historical managers and missing zero owners, independently audited.
- CRSP or equivalent survivor-free panel, complete with delisting distributions, crosswalks and corporate actions.
- Exact forecasting tests and comparable HAC specifications reproduced, ideally with reported coefficients and standard errors.
- Unadjusted, factor-adjusted, sector-neutral and placebo results, plus out-of-sample 1/3 split and stress periods.
- Risk-free rate, leverage, liquidity, borrow assumptions and open/close execution documented.
- A reconciliation table against the original paper's table numbers and definitions.

## 13. Reproducibility and file map

```text
Active-Ownership-to-Market-Alpha/
├── README.md                  # Research question, methodology, cautions
├── backtest.py                # PIT merge, spread, Newey-West, costs, charts
├── robustness.py              # Parameter/cost/investor-type stress tests
├── make_synthetic_fixture.py  # Data generation, explicitly fictional
├── tests/test_backtest.py     # Seven unit checks, including lookahead timing
├── study.json                 # Machine-readable study status
├── data_sources.csv           # Source registry
├── results_synthetic/        # Committed illustrative fixture output
└── requirements.txt
```

Run generated private outputs in `outputs/` (ignored by git). The small committed `results_synthetic/` artifact carries its evidence warning.

## 14. References

- Chen, Shuaiyu, and Cynthia Yin (2026), *Between the Bells: Active Management and the Aggregation of Market-Wide Information*. [SSRN](https://ssrn.com/abstract=7367200).
- [SEC 13F Data Sets](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets).
- [Investor.gov: Form 13F reporting](https://www.investor.gov/introduction-investing/investing-basics/glossary/form-13f-reports-filed-institutional-investment).
- [WRDS Research Data Overview](https://wrds-www.wharton.upenn.edu/).

## 15. Honest conclusion

**The code can be run and audited now; the empirical strategy cannot be claimed validated until real, historical point-in-time ownership and price data are provided.** A claimed annual Sharpe ratio of 1.0 based on synthetic records would be misleading. We preserve that separation by design.
