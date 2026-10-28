# Reproduction and publication gate — 2026-10-28 UTC

Local study directory: U.S. couriers and messengers, NAICS 492. Frozen 2026-10-26 revised-data snapshot reused from an existing study; not historical point-in-time.

- `OPENBLAS_NUM_THREADS=1 PYTHONPATH=. python -m pytest -q tests`: **13 passed in 0.47s**.
- `OPENBLAS_NUM_THREADS=1 python run_analysis.py`: completed; 61 OOS origins, six model scorecards, 1,000 block-placebo refits, 2,000 paired block-bootstrap draws, 1,000 exposure-weight perturbations.
- `OPENBLAS_NUM_THREADS=1 jupyter nbconvert --to notebook --execute research.ipynb`: completed on original fully populated study; 49 cells, 32/32 code cells executed, nine embedded SVG outputs, zero error outputs.
- Clean publication simulation: copied only versioned core data, source, analysis, scorecards, nine SVGs and notebook; removed all randomization draw tables. Patched notebook generated missing draws from frozen inputs in its first code cell and completed **49 cells, 32/32 executed, nine SVGs, zero errors**.
- Independently reconstructed all 61 OOS predictions using the same expanding-window Ridge specification in a second JavaScript implementation; maximum difference from published six-model RMSE scorecard: **1.8e-15**.
- Repo-wide `python scripts/validate_studies.py`: to be checked by GitHub Actions after publishing; structural CI does not validate original-release vintages or independent security returns.

**Gate:** REPRODUCED RETROSPECTIVE MACRO PILOT, not historical PIT, not issuer fundamentals, not investable equity alpha. No claim of source-row audit or actual historical data availability. Full draw tables are generated on first notebook run and are not part of the initial committed tree.
