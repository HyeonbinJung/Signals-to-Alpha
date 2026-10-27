# Source audit and leakage register (2026-10-26)

This study **does not download new vintage data**. It combines two **previously frozen public-data snapshots** already in the repository, independently checks the EIA mirror's 201 monthly records against the frozen copy, and preserves the upstream dates/URLs. No interpolation or extrapolation was performed. The research target (U.S. basic chemicals manufacturing) is different from the earlier pharmaceutical target and natural-gas price target; the input snapshots are explicitly reused.

## Numeric QA

- Federal Reserve `IPG3251S`: 201 observations, 2010-01 to 2026-09, sum `19610.8607`, first `99.3774`, last `91.2835` (matched the earlier fixed snapshot source QA).
- Federal Reserve `IPMAN`: 201 observations, sum `19691.5623`, first `89.7715`, last `99.4361`.
- EIA Henry Hub: 201 observations, sum `676.72`, sum of squares `2593.6076`, first `5.83`, last `2.95` (cross-checked against GitHub original file in the existing LNG study).
- EIA WTI: 201 observations, sum `14514.83`, sum of squares `1133694.1403`, first `78.33`, last `97.31` (same cross-check).

These aggregate checks reduce transcription risk but do not prove every historical record was the value available at its past forecast date. G.17 original-release vintages were not reconstructed; EIA mirror commit date is not the original monthly publication date. The explicit 2-month feature delay and 1-month target delay are **conservative assumptions**, not historical PIT certification. Source code, results and numerical data are frozen here; prospective research must collect ALFRED / G.17 historical vintages and archival EIA files.
