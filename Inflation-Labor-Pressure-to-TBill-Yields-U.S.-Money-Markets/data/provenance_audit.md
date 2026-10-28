# Frozen source and release-vintage audit — 2026-10-28

The `macrodata` CSV was copied without simulation from `statsmodels.datasets.macrodata.load_pandas().data` (installed statsmodels 0.14.6). The original compilation is explicitly attributed to FRED (St. Louis Fed) and BLS, **accessed 2009-12-15**; its 203 quarterly rows span 1959Q1–2009Q3. The data are a fixed historical package snapshot, **not** a panel of contemporaneously available quarterly vintages. Historical release dates, source-by-source original download files, and historical revisions are **UNKNOWN**. No release calendar is fabricated. CPI, unemployment, and GDP enter with a conservative one-quarter observation lag, but this does **not** establish point-in-time validity. The 3-month Treasury bill series is an interest-rate yield, not a bill total-return series; a rate forecast cannot be called investable alpha.

Official series pages used only for variable definitions, **not** as evidence that the frozen rows match their current values: TB3MS (https://fred.stlouisfed.org/series/TB3MS), CPIAUCSL (https://fred.stlouisfed.org/series/CPIAUCSL), UNRATE (https://fred.stlouisfed.org/series/UNRATE), GDPC1 (https://fred.stlouisfed.org/series/GDPC1). The package data source code is https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/macrodata/data.py and its frozen data file is https://github.com/statsmodels/statsmodels/blob/main/statsmodels/datasets/macrodata/macrodata.csv. The package compilation attribution and 2009-12-15 access date appear in `data.py`.

## QA

- Source rows: 203; unique quarter keys: 203; date span: 1959Q1–2009Q3; missing cells: 0.
- The raw SHA-256 is recorded in `results/metrics.json` and unit-tested.
- Local values can be independently cross-checked against the exact public package CSV above. This is a package-file cross-check, not a primary FRED historical-vintage audit.
- The current FRED series may differ due to benchmark revisions, seasonal adjustment, rounding, and source definitions. No unverified equality is asserted.
- Company-level exposure and issuer fundamentals are not available in this dataset; `company_exposure_map.csv` is an **unmeasured conceptual map**, not estimated company exposures.
