# Source and vintage QA (2026-10-27)

- Official G.17 2026-10-16 release: https://www.federalreserve.gov/releases/g17/Current/default.htm . The FRED table for IPG3361T3S reports a last-update timestamp of 2026-10-16 08:19 CDT and monthly SA 2017=100 values through September 2026.
- The 201 automobile observations are manually transcribed from https://fred.stlouisfed.org/data/IPG3361T3S on 2026-10-27; twelve spot-check rows match the displayed official table. **The remaining 189 automobile rows have not been independently machine-audited.** The inherited IPMAN series comes from the Basic Chemicals frozen study and matches the FRED table at 2010-01 and 2026-09; complete independent re-download is not available in this runtime.
- Both G.17 inputs are the **2026-10-16 revised snapshot**. Historical first-publication dates and revisions are UNKNOWN. A conservative two-month observation lag prevents simple same-month release leakage but **cannot** recreate archival PIT values.
- The source's 2020 auto index drops to 20.5804 in April 2020. This enormous pandemic production shutdown drives extreme YoY observations and warrants pre/post/exclusion robustness.
- The FRED G.17 motor-vehicle index covers NAICS 3361-3363, not global vehicle company revenue, automotive retail sales, or tradable equity returns.
- Ford and GM SEC 2025 10-K links are used **only for qualitative industry exposure**. Their 2025 business descriptions must not be backfilled as fixed historical portfolio weights.
- CSV `spot_checks.csv` records comparisons, not a programmatic remote-source audit. Reproduce official snapshots and hash them via FRED/ALFRED in a network-enabled archival environment before any PIT or investment claim.
