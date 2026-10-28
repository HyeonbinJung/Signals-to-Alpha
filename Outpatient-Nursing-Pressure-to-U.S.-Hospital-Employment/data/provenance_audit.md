# Frozen CES data provenance and publication-vintage audit

- Inherited public source: `Home-Care-Pressure-to-Alpha-U.S.-Healthcare-Services/data/fred_ces_2010_2026_snapshot.csv` in `HyeonbinJung/Signals-to-Alpha`, read from GitHub `main` on 2026-10-28.
- Prior original publisher: U.S. Bureau of Labor Statistics CES, via Federal Reserve Bank of St. Louis FRED, series IDs CES6562160001, CES6562200001, CES6562300001, CES6562100001, PAYEMS. Prior study reported original retrieval 2026-10-26 and latest source release 2026-10-02.
- Data transfer: GitHub connector file content was reconstructed as integer tenths using lossless signed base-36 differences, then serialized as comma-delimited CRLF CSV; the result's SHA-256 **exactly equals** the prior study's published hash `f1d5a8ff28a55f2d1798cbdb9cac239d46db6c006b0a9e1801abae1b3b1665f6`. This verifies byte identity, not an independent BLS download.
- Sample: 201 monthly observations 2010-01 to 2026-09; all five series seasonally adjusted thousands of workers. No missing or duplicate dates; positive levels. Ambulatory minus home health positive at all dates.
- Historical publication availability: **UNKNOWN**. The 2026 snapshot is latest-revised and is not the original CES vintage at any historical forecast origin. Fixed 2-month feature buffers and 7-month target maturity reduce timing leakage but **do not eliminate revision look-ahead**.
- Issuer SEC 2025 10-Ks (HCA filed 2026-02-10, Tenet filed 2026-02-17) are **descriptive contemporary exposures only**; 2010–2025 issuer exposures are unknown, no security panel was fitted.
- Research outcome is hospital employment growth only. No patient utilization, hospital revenue prediction, security total returns, costs, or investable alpha claim.
