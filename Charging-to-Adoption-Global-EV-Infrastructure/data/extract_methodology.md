# Frozen extract methodology

Upstream: IEA Global EV Data 2024, mirrored at
https://github.com/WRicd/IEA-Data-Project/blob/main/data/raw/IEA-EV-Data-2024.csv
(checked 2026-10-19). Original IEA release date: 2024-04-23.

Filter `category == Historical` and retain three exact fields:

- `parameter == EV sales share`, `mode == Cars`, `powertrain == EV`, `unit == percent`.
- `parameter == EV charging points`, `mode == EV`, `powertrain == Publicly available fast`, `unit == charging points`.
- `parameter == EV charging points`, `mode == EV`, `powertrain == Publicly available slow`, `unit == charging points`.

Inner-join on country/year. Preserve 16 explicitly named countries with enough joint coverage: Belgium, Canada, China, Denmark, Finland, France, Germany, Italy, Netherlands, Norway, Portugal, Spain, United Kingdom, USA, Korea, Japan. Exclude aggregates (World, EU27, Europe). Filter 2011–2023. The result has 180 complete country-years. `ev_sales_share_pct` rounded to at most 5 decimals, charging points to 2 decimals. This is a derived extract, not the full raw IEA CSV; source URLs and exact filters are supplied so a reviewer can obtain the original independently. Data were not generated or interpolated.

**Critical:** The repository's 2024 dataset is not proven to be an immutable copy of the IEA's April 2024 release; nor is there a collection of 2011–2023 as-of vintages. Historical lead tests using this file are retrospective and cannot establish a tradeable point-in-time signal. Missing countries and potential source revisions may bias estimates.

`fetch_source.py` optionally downloads the full upstream mirror, prints its SHA256, applies the exact filters, and compares its current extract with the frozen 180-row panel. This script was **not** executed in the offline validation environment. The upstream mirror may change, so mismatches must be audited rather than silently replacing the frozen observations.
