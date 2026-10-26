# Data provenance and independent checks

- Frozen input: `frozen_g17_2010_2026.csv`, SHA256 `e468485f066f10711bb20d5dead47f44e4edf03a1d33d15fa59eacb6046a0f30`.
- Data copied from GitHub `rektosaure/financial-dataset` at immutable commit `21323f93cece664b4e052213b0a78a38e1c22b4b` (committed 2026-10-26 17:00:15 UTC). GitHub blob SHA `4eccf0081cdcf4a57f1a665beeafe1cc8dc63e0d`.
- Original publisher: Federal Reserve Board G.17. Mirror is **grade B numeric source**, not an official direct download.
- Exactly 201 continuous monthly observations, 2010-01 to 2026-09, three positive numeric series, no missing or duplicate dates.
- Exact extracted column sums: textile `19349.8960`, apparel/leather `20494.6714`, manufacturing `19691.5623`.
- Latest official FRED G.17 table (2026-10-16) matches Sep 2026 textile 75.2310, apparel/leather 79.4959, IPMAN 99.4361 and Aug 2026 75.6765, 79.3947, 99.1776.
- Earlier rows were **not independently reconciled** against historical Federal Reserve releases; old as-of vintages are **UNKNOWN**.
- PIT status: NOT VERIFIED. Lagging by two months does not repair revision look-ahead.
