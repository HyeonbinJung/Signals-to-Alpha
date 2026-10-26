# Frozen data provenance and transcription audit

These are **manual transcriptions** of three FRED official display tables retrieved 2026-10-26; no external CSV downloader or API key was available in the execution environment. The complete 2014-01 through 2026-09 monthly calendar is frozen in `fred_bts_bls_frozen_2026-10-26.csv`. AIRRPMTSID11 ends 2026-06; the last three cells are missing, **not filled**. Values are BTS/BLS official government series, **latest-revised snapshots**, and should not be described as original publication vintages.

| Series | Original table | Reported last update | Spot checks against displayed rows |
|:--|:--|:--|:--|
| AIRRPMTSID11 | https://fred.stlouisfed.org/data/AIRRPMTSID11 | 2026-10-01 09:01 CDT | 2019-12 90063718; 2020-04 2877804; 2026-06 94921559 |
| CES7072100001 | https://fred.stlouisfed.org/data/CES7072100001 | 2026-10-02 08:26 CDT | 2019-12 2118.2; 2020-04 1199.1; 2026-09 1916.5 |
| CES7072200001 | https://fred.stlouisfed.org/data/CES7072200001 | 2026-10-02 08:26 CDT | 2019-12 12217.9; 2020-04 6317.3; 2026-09 12393.0 |

`build_frozen_inputs.py` preserves the month-by-month transcribed values so errors can be audited and corrected. The source CSV SHA-256 is recorded in `results/metrics.json`. Spot-checks do **not** independently verify every transcribed row; a direct BTS/BLS bulk download and checksum comparison is required before stronger provenance claims. The four-month BTS and two-month BLS feature delays are conservative modeling assumptions, not certified historical release timestamps. Historical revisions/seasonal re-estimation remain a look-ahead vulnerability.
