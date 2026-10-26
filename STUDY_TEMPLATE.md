# New study template — canonical 15-section format

Create `<Signal>-to-Alpha-<Region>-<Industry>/` containing `README.md`, `study.json`, `research.ipynb`, `run_analysis.py`, `requirements.txt`, `data/source_register.csv`, frozen raw/derived inputs, `results/` computed tables, `figures/` at least three real diagnostics and `tests/` checks.

Use the **same 15 section titles**, in order, in the study README. Develop the notebook using the K-Food v3 research design: abstract, H1–H3/null, company/industry mechanism, source grades, publication timestamp and vintage, fixed formula, exposure map, separated macro/fundamental/return outcomes, baselines, purged OOS, uncertainty, placebo, ablations, sensitivities, bias audit, verdict and prospective plan.

## 01. Abstract

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 02. Research Design & Hypotheses

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 03. Industry Context

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 04. Data & Source Integrity

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 05. Point-in-Time Availability

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 06. Factor Construction

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 07. Exposure & Transmission

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 08. Outcomes & Baselines

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 09. Empirical Findings

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 10. Robustness & Placebos

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 11. Regime Sensitivity

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 12. Bias Audit & Verdict

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 13. Reproduction

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 14. Next-Stage Protocol

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->

## 15. Sources & Artifacts

<!-- Add substantiated, study-specific content. State UNKNOWN when source release dates, vintages or results cannot be verified. -->


## Publication checklist

- [ ] Real source URLs, as-of collection dates, units, allowed-use provenance and a publication/revision register
- [ ] Predeclared signal, target, baselines and no look-ahead/survivorship leakage
- [ ] Fully executed independent notebook with saved plots/tables (not generated-looking placeholders)
- [ ] Reproducibility commands and tests from a fresh checkout, with observed pass evidence
- [ ] At least three justified falsification/sensitivity checks, or explicit incomplete-draft status
- [ ] Independent fundamental and security-return evidence before any investable-alpha claim
- [ ] Exactly 3–4 meaningful sentences appended to root README Research Summaries
- [ ] New manifest `study.json` with actual file paths and `equity_alpha_established: false` unless conclusively demonstrated
- [ ] `python scripts/validate_studies.py` passes and GitHub Action results checked
