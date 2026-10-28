# Provenance and historical point-in-time limitations

- The exact 203 observations were frozen from `statsmodels.datasets.macrodata.load_pandas()` (installed 0.14.6), not scraped from live FRED. The upstream metadata says FRED and BLS accessed 2009-12-15. The **collection date is not the original release date** for each historical quarter.
- Real consumption, real disposable income, real GDP and real investment are seasonally adjusted annual rates in **billions of chained 2005 U.S. dollars**. Chained levels should not be arithmetically added to infer industry shares.
- At formation quarter `t`, features use data no later than `t-1`, while target uses `t..t+h`; this is a conservative *observation lag*, NOT proof that the vintage used at `t` was available in `t`.
- An actual point-in-time implementation needs ALFRED/BEA vintages with first-publication timestamps, archival GDP/Income release calendars, and series-specific changes in chain-dollar bases.
- The outcome `realcons` is **all personal consumption expenditures**, including goods and services, not a retail-only, restaurant-only, or listed-company revenue series. This is a cross-sector macro demand pilot and should not be marketed as industry-specific alpha.
- NAICS mappings are illustrative 2022 classifications; no numerical firm revenue weights or historical survivorship-safe equity panel is available.
