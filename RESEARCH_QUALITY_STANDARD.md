# Signals-to-Alpha Research Quality Standard (v1)

**Reference benchmark:** [Consumption-to-Alpha v3](Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/kfood_research_grade_alpha_v3.ipynb) is the *minimum narrative and analytical depth*, not a guarantee of statistical significance. Size alone is **never** sufficient; 25–40+ cells are a presentation target, not an evidence criterion.

## Publication gate

A study is **NOT READY** for a research-grade claim until all relevant conditions pass:

1. **Question and falsifiability:** 1-sentence primary research question; explicit H1–H3, null, economic mechanism, failure standard, counterthesis and industry size/growth with dated citations.
2. **Sources and reproducibility:** include original-source URL, publisher, instrument/series, units, collection date, observed dates, original publication delay (if known), update/revision policy, usage role, A/B/C reliability and raw/derived CSV. If a field is not known, mark **UNKNOWN**; never invent a release timestamp.
3. **Point-in-time rigor:** all formation-date inputs must have publication availability documented. Fixed lags on latest-revised data do **not** prove PIT availability. A mixed-vintage exercise is expressly a *fixed-snapshot association / falsification pilot*.
4. **Predefined transparent features:** equations, scaling, units, exposure construction, fixed vs fitted parameters and precise target definition. No future data in preprocessing, normalization, exposure weights, model tuning or selection.
5. **Independent outcomes:** separate industrial demand/production from firm-level sales/EPS and **tradable total-return alpha**. If company-level adjusted prices are missing, do not title a study as proven equity alpha.
6. **Out-of-sample comparison:** same origins for baseline and challenger, expanding/rolling training, target-release purge, train-only transformations, explicit observations and horizon; compare to historical mean and plausible AR/momentum/multivariate baseline.
7. **Effect size and uncertainty:** show primary metrics (RMSE/MAE, IC/LS only where security returns exist), paired loss differences, directional robustness, effective sample size and uncertainty appropriate to serial dependence.
8. **Falsifications:** document at least three relevant tests such as ablation, leave-one-security-out, exposure perturbations, regime split, conservative time shift, alternative horizon, macro controls, block-aware placebo, 1,000+ permutation/randomization draws *when valid*. Never call stale-lag checks or circular shifts exact permutation p-values.
9. **Bias register:** publication and historical revision leakage; survivorship/security universe; targeting/selection; temporal overlap; multiple testing; nonstationarity; execution, transaction costs and capacity.
10. **Readable, complete notebook:** abstract, sectioned equations and interpretations, **at least three nonredundant computed diagnostic figures**, descriptive tables, baseline scorecards, negative controls, verdict, next-stage protocol and citations. A 5-cell wrapper importing Python modules is not an acceptable notebook deliverable.
11. **Execution proof:** every published notebook must run from a clean checkout with declared dependencies; executed table and figure outputs must be persisted in the committed `.ipynb`. Run unit tests and check no cell has an error output. Never claim **verified** if a test/CI job was not observed to pass.
12. **Summary hygiene:** add exactly 3–4 substantive sentences to README Research Summaries reporting **actual** findings, crucial limitations and categorical verdict; keep the prior work intact.

## Release statuses

- **DRAFT / UNEXECUTED** — source and prose present; newly modified notebook not run through clean-environment validation.
- **REPRODUCED MACRO PILOT** — source and notebook execute successfully, but vintage audit and/or security-level data missing.
- **REPRODUCED PIT FUNDAMENTAL LEAD TEST** — feature releases and filing dates checked and independent corporate outcomes tested.
- **REPRODUCED INVESTABLE ALPHA TEST** — above plus historical-universe total returns, sector controls, execution/cost sensitivity, clean holdout, and honest false-discovery adjustment.

**No study should be labeled `investable alpha` without passing the final gate.** Failure of a hypothesis is a legitimate, publishable research outcome.

## Existing 2026-10-19 remedial pass

The Grid, Housing and Gas–Oil notebooks were expanded from 12/10/8 cells to **35/34/35** cells respectively. The new narrative explicitly covers formulas, source classifications, outcome definition, baselines, graphical error diagnostics, robustness limitations and bias audits. This is a **presentation and reviewability improvement**, not new evidence; original fixed-snapshot numerical results remain unchanged. Newly appended code outputs are not considered validated until [the research notebook execution workflow](.github/workflows/research-notebook-validation.yml) successfully runs and commits them.

## Routine for each four-hour research run

1. Inspect the latest repository before selecting an **unresearched** industry.
2. Evaluate source quality and historical PIT feasibility **before** claiming alpha.
3. Conduct the study and independently re-run analysis + notebook from a fresh working directory.
4. Pass tests and quality gate before committing the published result.
5. Commit notebook outputs, data, source register and README summary in the same auditable contribution; include a CI/reproduction reference.
6. If any mandatory prerequisite is unavailable, **do not fabricate it**. Publish only honestly scoped pilot findings or retain a draft until the gate passes.
