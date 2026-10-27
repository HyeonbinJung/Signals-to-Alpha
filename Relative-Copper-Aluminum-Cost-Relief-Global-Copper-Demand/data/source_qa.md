# Provenance, QA and publication-vintage audit

- Frozen file: `data/copper_statsmodels_0_14_6_frozen.csv`; SHA-256 `e8fc38e9f887dc696f578baf7cd240b53648002d53135708ae97d3bde1800d37`.
- Package: statsmodels 0.14.6 (`statsmodels.datasets.copper.load_pandas()`), as installed on 2026-10-27. Source attribution: Jeff Gill, *Generalized Linear Models: A Unified Approach*; the package's documentation says original author retains rights.
- The loader omits the original YEAR column and returns TIME=1..25; **year = 1950 + TIME** was reconstructed from the official package description 1951–1975. No calendar years were inferred from a regression.
- All 25 records have nonmissing, positive inputs. First and last consumption values: 3173.0 and 7157.2 thousand metric tonnes. This is a **curated historical teaching dataset**, not an independently verified official first-release series.
- Historical release timestamps for consumption, metal prices, income, and inventory: **UNKNOWN**. Historical revision chronology: **UNKNOWN**. Lagging each predictor one annual observation does not establish point-in-time availability.
- Price units are not fully described; the factor uses **differences in log changes**, so fixed unit scales cancel. No same-unit level ratio assumption enters the model.
- No independent current copper-market figures are joined to 1951–1975 observations. The ICA 2020 substitution fact is contextual, not historical evidence for the tested era.
- Dataset redistribution rights beyond the statsmodels package's express permission are not independently established. Source attribution is preserved; review rights before commercial reuse.
- Firm exposure, corporate fundamentals, equity total returns, transaction costs, and historical tradable universe: **NOT OBSERVED**.
