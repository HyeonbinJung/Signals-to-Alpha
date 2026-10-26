# Source transcription / fixed-snapshot audit — 2026-10-26

Original endpoints: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=IPG3254S`, `...id=IPG3251S`, and `...id=IPMAN`.
The machine-readable public FRED CSV response was retrieved through a browser-fetch tool and filtered to 2010-01 through 2026-09 inclusive. The three columns were aligned by identical observation months and copied to `official_snapshot.csv` without rounding beyond the source's four decimals.

| Source ID | rows | sum of published 4-decimal values | sum of squares | first | last |
|:--|--:|--:|--:|:--|:--|
| IPG3254S | 201 | 21707.4978 | 2354600.08631966 | 2010-01 119.6808 | 2026-09 124.2706 |
| IPG3251S | 201 | 19610.8607 | 1922038.71334451 | 2010-01 99.3774 | 2026-09 91.2835 |
| IPMAN | 201 | 19691.5623 | 1930809.99689063 | 2010-01 89.7715 | 2026-09 99.4361 |

The row counts, column sums and sum-of-squares match independent computations from the live source response to numerical precision. This does **not** prove each historical observation was published with the current value at the time of a past trading signal. Federal Reserve historical as-of vintages were not downloaded and remain **UNKNOWN**. This dataset is a 2026-10-26 fixed/revised snapshot, not PIT.

The G.17 October 16, 2026 release date was confirmed from the Federal Reserve's official release calendar; observation-specific original publication timestamps were not confirmed. No data were inferred, interpolated or simulated.
