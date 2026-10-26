<div align="center">

# Signals to Alpha

**Open research on real-economy signals, falsifiable industry factors and the limits of predictive alpha.**

[Research index](#research-index) · [Findings](#research-summaries) · [Standard](RESEARCH_QUALITY_STANDARD.md) · [Contributing](#contributing-a-study)

</div>

---

## Purpose

Signals to Alpha tests whether observable shifts in consumption, production, construction and commodity markets anticipate measurable outcomes. The reference model is the [Consumption-to-Alpha K-Food study](Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/): explicit hypotheses, source provenance, fixed factor rules, independent outcomes, out-of-sample baselines, falsification and a frank verdict.

**Important distinction:** industrial-output forecasts, corporate fundamental associations and investable equity alpha are three different claims. A negative result is useful evidence. Fixed, revised data snapshots are not automatically point-in-time datasets.

## Research Index

| Study | Signal → outcome | Current evidence | Notebook |
|:--|:--|:--|:--|
| [Consumption-to-Alpha — U.S. K-Food Demand](Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/) | K-Food category demand → firm sales / equity excess returns | Fundamental lead plausible; equity alpha unproven | [Open](Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/kfood_research_grade_alpha_v3.ipynb) |
| [Grid-Capex-to-Alpha — U.S. Electrical Equipment](Grid-Capex-to-Alpha-U.S.-Electric-Equipment/) | Power output gap → electrical-equipment output | Fails mean baseline | [Open](Grid-Capex-to-Alpha-U.S.-Electric-Equipment/grid_capex_alpha_research.ipynb) |
| [Housing-Permits-to-Alpha — U.S. Building Materials](Housing-Permits-to-Alpha-U.S.-Building-Materials/) | Housing permits / starts → materials output | Fails mean and macro baselines | [Open](Housing-Permits-to-Alpha-U.S.-Building-Materials/housing_permits_alpha_research.ipynb) |
| [Gas–Oil Divergence-to-Alpha — U.S. LNG](Gas-Oil-Divergence-to-Alpha-U.S.-LNG/) | WTI–Henry Hub divergence → natural-gas spot movement | Fails mean and momentum baselines | [Open](Gas-Oil-Divergence-to-Alpha-U.S.-LNG/research.ipynb) |
| [Device-Gap-to-Alpha — U.S. Semiconductors](Semiconductor-Device-Gap-to-Alpha-U.S.-Chip-Manufacturing/) | Downstream devices → semiconductor output | Fails persistence / macro baselines | [Open](Semiconductor-Device-Gap-to-Alpha-U.S.-Chip-Manufacturing/research.ipynb) |
| [Charging-to-Adoption — Global EV Infrastructure](Charging-to-Adoption-Global-EV-Infrastructure/) | Public charging growth → next-year national EV sales-share change | Negligible incremental OOS gain; fails momentum | [Open](Charging-to-Adoption-Global-EV-Infrastructure/research.ipynb) |

| [E-Commerce Share-to-Alpha — U.S. Warehousing & Logistics](Ecommerce-Share-to-Alpha-U.S.-Warehousing-Logistics/) | E-commerce share acceleration → 2Q-ahead warehouse employment YoY | Positive retrospective OOS gain; uncertain PIT and bootstrap | [Open](Ecommerce-Share-to-Alpha-U.S.-Warehousing-Logistics/research.ipynb) |

## Research Summaries

### [Consumption-to-Alpha — U.S. K-Food Demand](Consumption-to-Alpha-A-U.S.-K-Food-Alternative-Data-Factor-Model/)

Annual K-Food demand and company category exposure show an economically plausible relationship with subsequent sales growth, but the equity signal is unstable. The five-year test's mean Rank IC is weak and the apparent return spread depends heavily on Samyang Foods. Exposure perturbations, company exclusions, regime splits and a within-year permutation placebo do not establish sector-wide investable alpha. **Verdict:** a useful demand-nowcasting hypothesis, not a validated trading strategy.

### [Grid-Capex-to-Alpha — U.S. Electrical Equipment](Grid-Capex-to-Alpha-U.S.-Electric-Equipment/)

Electricity demand and infrastructure investment provide a strong economic thesis, but a macro lead factor must still beat predictive baselines. The grid-output gap achieved six-month RMSE **4.124 pp** versus **4.228 pp** for momentum controls, yet lagged the historical-mean forecast (**3.524 pp**). An exploratory time-shift placebo (**p≈0.32**) did not support robust incremental value, and source vintages were not reconstructed. **Verdict:** useful structural context, but neither a verified point-in-time factor nor tested equity alpha.

### [Housing-Permits-to-Alpha — U.S. Building Materials](Housing-Permits-to-Alpha-U.S.-Building-Materials/)

Housing permits and starts are plausible precursors to construction-material demand but do not automatically forecast producer output. In **98** six-month-ahead expanding-window origins, housing-augmented Ridge had RMSE **5.109 pp**, worse than macro controls (**4.874 pp**) and a historical mean (**4.808 pp**). Alternative horizons, wood-products outcomes, regime splits and lag-only placebos did not establish consistent incremental value; historic vintages remain unaudited. **Verdict:** an informative negative macro-factor result, with no tested equity alpha.

### [Gas–Oil Divergence-to-Alpha — U.S. LNG](Gas-Oil-Divergence-to-Alpha-U.S.-LNG/)

Global LNG capacity expansion is a credible sector story, but relative oil–gas prices are not automatically a repeatable return signal. In **242** monthly expanding-window forecasts, the divergence model's RMSE was **32.707 pp** versus **30.911 pp** for momentum controls and **30.825 pp** for the historical mean. Alternative horizons, LNG-era splits, 2022 exclusion and stale-spread checks did not rescue the factor, and the data are not archival vintages. **Verdict:** failed natural-gas spot-price predictor; futures and equity alpha were not tested.

### [Device-Gap-to-Alpha — U.S. Semiconductors](Semiconductor-Device-Gap-to-Alpha-U.S.-Chip-Manufacturing/)

Downstream computer and communications-equipment output may lead chip production, but the global semiconductor demand story alone is not a predictive factor. In **108** expanding-window forecasts the device gap produced RMSE **4.746 pp**, worse than macro controls (**4.713 pp**) and semiconductor persistence (**4.468 pp**). A moving-block bootstrap interval straddles zero and an exploratory block-placebo (**p≈0.796**) offers no support; data are latest-revised snapshots. **Verdict:** no robust incremental production predictor and no tested equity alpha.

### [Charging-to-Adoption — Global EV Infrastructure](Charging-to-Adoption-Global-EV-Infrastructure/)

Across 16 selected national markets, 180 country-year observations from the IEA 2024 snapshot support 96 expanding-window EV sales-share forecasts for 2018–2023. Charging-augmented Ridge improves control-model RMSE only from **4.483** to **4.468 pp** and trails simple momentum at **4.416 pp**. A 1,000-refit within-year shuffle yields exploratory **p≈0.132** and a 2,000-draw year-block bootstrap interval **[−0.017, 0.052] pp** includes zero, with effects changing sign across regimes. **Verdict:** charging is a plausible infrastructure theme, but retrospective vintages, ex-post country selection and absent company returns prevent any validated point-in-time or equity-alpha claim.

### [E-Commerce Share-to-Alpha — U.S. Warehousing & Logistics](Ecommerce-Share-to-Alpha-U.S.-Warehousing-Logistics/)

E-commerce share acceleration has an economically plausible transmission channel into U.S. warehousing employment, but this is a revised-data retrospective study rather than a point-in-time trading strategy. Across 57 purged expanding-window two-quarter-ahead forecasts, the augmented model reduced RMSE to **5.172 pp**, compared with **5.869 pp** for payroll/persistence controls and **5.360 pp** for warehouse persistence alone. A 2,000-draw moving-block bootstrap interval for the macro-control improvement **[−1.486, 2.572] pp** crosses zero, while the 1,000-refit block-shuffle is exploratory and does not repair historical-vintage leakage. **Verdict:** a potentially useful macro lead-factor candidate, but historical release-vintage validity, corporate fundamentals and investable equity alpha remain unverified.

## Common Research Format

Every study README follows the same **15 sections**: Abstract; Research Design; Industry Context; Data & Source Integrity; Point-in-Time Availability; Factor Construction; Exposure & Transmission; Outcomes & Baselines; Empirical Findings; Robustness & Placebos; Regime Sensitivity; Bias Audit & Verdict; Reproduction; Next-Stage Protocol; Sources & Artifacts.

Each study also has `study.json` with a notebook path, source register, artifacts, tests and honest evidence level. Previously published detailed source notes remain in `DETAILS.md` where applicable. Existing executed notebooks and numeric data have **not** been rewritten merely for consistent formatting.

The [research quality standard](RESEARCH_QUALITY_STANDARD.md) and [new-study template](STUDY_TEMPLATE.md) define the publication gate. Validate documentation integrity locally:

```bash
python scripts/validate_studies.py
```

## Reproducing a Study

1. Open the individual study README and inspect its data source register, vintage caveat and analysis target.
2. Install the listed dependencies, use the study-specific reproduction command, and run its tests.
3. Inspect the notebook, original data files and recorded results. Cross-check any newly computed numbers against the published snapshot before citing them.
4. Treat archived, mixed-vintage forecasts as retrospective evidence only until original publication vintages are verified.

**All published results are research-only and not investment advice.** No currently indexed study establishes a fully point-in-time, transaction-cost-aware equity-alpha strategy.

## Contributing a Study

Follow [STUDY_TEMPLATE.md](STUDY_TEMPLATE.md); add an industry directory with `README.md`, `study.json`, a stand-alone executed notebook, primary-source register, frozen inputs, reproducible analysis code, tests, and computed figures/results. Write a 3–4-sentence summary into this index and identify negative findings without dilution. A new run is accepted only after evidence and execution gates pass; otherwise keep it as a draft and report the blocker.

Automated deep-research batches are managed separately from GitHub Actions. The repository's Actions check research layout and existing executable notebooks; the CI workflow does **not** autonomously generate new industry studies.

---

<sub>Maintained by [Hyeonbin Jung](https://github.com/HyeonbinJung). Source credibility, research reproducibility and falsifiable claims come before backtest headline numbers.</sub>
