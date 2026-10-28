# Frozen-data provenance and quality audit — 2026-10-28

- Input: Plotly 6.5.2 `plotly.express.data.stocks()`, **105** weekly rows from **2018-01-01** to **2019-12-30**, six columns of normalized positive prices.
- Raw frozen CSV SHA-256: `b80a2e38aa02076ad977f89f9595853f5e69a0bd1e1d5726b761977101009a9e`.
- Plotly documentation: https://plotly.com/python-api-reference/generated/plotly.express.data.html .
- Exact packaged dataset URL: https://github.com/plotly/plotly.py/blob/v6.5.2/plotly/package_data/datasets/stocks.csv.gz .
- Original exchange/vendor, publication date, corporate-action adjustment, dividend treatment and per-week availability: **UNKNOWN**. This is **not** a verified PIT tape, not certified total-return data, and cannot support an investable-alpha claim.
- Rows checked for nonmissing, unique monotonic dates, exact 7-day spacing, positive prices, and base value 1.0. No external vendor cross-check was possible in this execution environment.
- Source grade: B for developer-distributed snapshot, C for its unverified upstream provenance. SEC 2017 10-K filings are grade A and used only for qualitative business exposure mapping.
- Selection: all four chosen digital-platform/media names were selected retrospectively from a six-ticker demo basket, introducing survivorship/selection risk. AAPL/MSFT are **not** an investable broad-market benchmark.
- Formation after 2018-02-06 means all four selected 2017 10-K filing dates precede evaluated OOS origins; historical weekly price availability still **unverified**.

- **Trading-calendar anomaly:** 2018-01-01 is a U.S. market holiday, yet the example uses it as the initial weekly label. Thus dates are sample grid labels, **not independently verified exchange closing timestamps**. No executable weekly-close strategy is inferred.
