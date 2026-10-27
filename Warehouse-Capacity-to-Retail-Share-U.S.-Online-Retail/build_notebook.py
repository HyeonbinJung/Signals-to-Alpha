"""Generate a self-contained, narrative-first 15-chapter executed notebook."""
import nbformat as nbf
from pathlib import Path
ROOT=Path(__file__).resolve().parent
nb=nbf.v4.new_notebook();cells=[]
def md(s):cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s):cells.append(nbf.v4.new_code_cell(s.strip()))
md('''# Warehouse Hiring → U.S. Online Retail Share
### A falsifiable retrospective macro lead-factor study · 2026-10-27

**Evidence class:** REPRODUCED MACRO PILOT — latest-revised data; historical publication vintages **UNKNOWN**; **not investable equity alpha**.

**Abstract.** Does the excess hiring of U.S. warehousing employees over economy-wide payroll growth forecast a two-quarter increase in the e-commerce share of retail sales? We compare a predeclared lagged signal against historical mean, share persistence, multivariate macro controls, and a signal-only model using 57 purged expanding-window OOS forecasts. We include 1,000 block-aware shuffle refits, 2,000 paired block-bootstrap draws, 1,000 exposure mixtures, multiple horizons, lag shifts, regime splits and leave-one-year-out diagnostics. Data are frozen from an existing official-source snapshot and are not reconstructed historical vintages. **The augmented model fails the historical mean benchmark; any control-relative gain is pandemic-sensitive.**''')
md('''## 01. Abstract

The unit of analysis is a U.S. calendar quarter, 2000Q1–2026Q3. The target is the **two-quarter change in the Census seasonally adjusted online retail share**, not revenue or stock returns. Our 57 OOS origins run from 2011Q4 to 2025Q4; the training target-availability purge is three quarters. We deliberately retain negative findings and make the fixed-vintage limitation visible.''')
code('''from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, SVG
from scipy.stats import spearmanr
from analysis import ROOT, read_raw, make_panel, walk_forward, score, delta, run, ALPHA, PURGE, HORIZON, CONTROLS
from run_analysis import charts
pd.set_option('display.max_columns', 20)
print('Study root:', ROOT)
print('Fixed Ridge alpha:', ALPHA, '| target horizon:', HORIZON, '| purge:', PURGE)''')
code('''raw = read_raw()
print('Raw rows:',len(raw),'| Date range:',raw.observation_date.min().date(),'to',raw.observation_date.max().date())
display(raw.head(4))
display(raw.tail(4))''')
md('''## 02. Research Design & Hypotheses

**H1 (direction):** warehouse hiring premium is positively associated with future e-commerce retail-share expansion. **H2 (incremental):** warehouse signal lowers OOS RMSE versus the multivariate control and the historical mean. **H3 (stability):** effect survives exclusion of 2020–2021, alternative horizons, lag buffers, and exposure scenarios.

**Counterthesis:** warehouse staffing is a lagging response to online retail rather than a leading capacity constraint. **Failure rule:** losing to the mean, zero-crossing block uncertainty, or regime sign reversal defeats a robust-factor claim. This retrospective design is not a prospective preregistration.''')
code('''print('Observed e-commerce retail share (%):')
display(raw[['observation_date','ECOMPCTSA']].iloc[[0,20,40,60,80,100,105]])''')
md('''## 03. Industry Context

Retail trade (NAICS 44–45) includes omnichannel and online transactions. Census ECOMPCTSA was **17.1% in 2026Q2**, released **2026-08-18**. Warehouse employment (NAICS 493) and courier employment (NAICS 492) can proxy for fulfillment capacity, but outsourcing, automation, delivery density, and returns can disconnect staffing from retail sales. The 2020–2021 pandemic creates a powerful nonstationarity test.

Official release references: [Census e-commerce share](https://fred.stlouisfed.org/series/ECOMPCTSA), [BLS warehousing payroll](https://fred.stlouisfed.org/series/CES4349300001), [couriers](https://fred.stlouisfed.org/series/CES4349200001).''')
code('''display(pd.read_csv(ROOT/'data/exposure_map.csv'))''')
md('''## 04. Data & Source Integrity

**Grade A:** Census and BLS original series via FRED. **Grade B:** this byte-identical copied quarterly snapshot, whose historical release values were **not** independently audited. **Grade C:** unverified narrative claims, not used in numerical analysis. The dataset is **not** a collection of original as-published vintages. One 2026Q3 retail-share value is missing and is never imputed. The 2025 Census benchmark change is an important definition/revision caveat.''')
code('''source_register=pd.read_csv(ROOT/'data/source_register.csv')
display(source_register[['source_id','grade','original_release_date_latest','observed_start','observed_end','historical_vintages','role']])''')
code('''snapshot_sha=hashlib.sha256((ROOT/'data/fred_quarterly_snapshot_2026-10-26.csv').read_bytes()).hexdigest()
print('Frozen raw SHA256:',snapshot_sha)
print('Rows / missing counts:',len(raw),raw.isna().sum().to_dict())
assert snapshot_sha=='17b99d105505b7c4ef7741012cf65d916bac0b907403474f18cffedcc4a99b2d' ''')
md('''## 05. Point-in-Time Availability

At origin *t*, use a hypothetical decision time at **end of t+1**. The observed share at *t* has one full-quarter publication buffer; employment inputs stop at *t−1*. Predict share[t+2]−share[t], which becomes public in *t+3*. Train only on rows with origin `i≤t−3`, so their target release is no later than *t*. **This is a conservative timing convention on revised data, NOT actual-vintage PIT validation.**''')
code('''panel=make_panel(raw)
print('Usable formation rows:',len(panel),'| First:',panel.observation_date.min().date(),'| Last:',panel.observation_date.max().date())
display(panel[['observation_date','origin_index','share_level','share_mom2','factor','target']].head(5))''')
code('''pred_check=walk_forward(panel)
assert (pred_check.train_last_origin<=pred_check.origin_index-PURGE).all()
display(pred_check[['date','origin_index','train_n','train_last_origin','actual']].iloc[[0,1,-2,-1]])
print('Purged OOS origins:',len(pred_check))''')
md('''## 06. Factor Construction

For warehouse payroll `W`, courier payroll `C` and aggregate payroll `P`, define `g(X,t)=100·ln(X[t]/X[t−4])` in log-percentage points. The **predefined signal** is `F[t]=g(W,t−1)−g(P,t−1)`. Target: `Y[t]=S[t+2]−S[t]` (retail share percentage points). Alternative exposure `F[t;w]=w·g(W,t−1)+(1−w)·g(C,t−1)−g(P,t−1)`, `w∈[0.5,1]`. No future-fitted feature scaling: Ridge uses train-fold-only means/standard deviations.''')
code('''ix=int(panel.origin_index.iloc[12]);row=panel.iloc[12]
manual=100*np.log(raw.CES4349300001.iloc[ix-1]/raw.CES4349300001.iloc[ix-5])-100*np.log(raw.PAYEMS.iloc[ix-1]/raw.PAYEMS.iloc[ix-5])
print('Manual signal:',round(manual,6),'| implemented:',round(row.factor,6))
assert np.isclose(manual,row.factor)''')
code('''plt.figure(figsize=(8,3));plt.plot(panel.observation_date,panel.factor);plt.axhline(0,color='black',lw=.7);plt.title('One-quarter-stale warehouse hiring premium');plt.ylabel('Log percentage points');plt.show()''')
md('''## 07. Exposure & Transmission

The baseline factor assigns weight 1.0 to warehousing (NAICS 493) and 0.0 to couriers (NAICS 492), relative to total payroll. This is an **industry transmission scenario**, not an issuer-level revenue weight. Company-specific historical online-sales shares, geographic fulfillment allocations and dated filing evidence are **UNKNOWN**; no issuer names are scored. We test 1,000 alternative sector mixtures, and substitute leave-one-year-out for the inapplicable leave-one-company-out.''')
code('''exposure=pd.read_csv(ROOT/'data/exposure_map.csv')
display(exposure[['segment','NAICS','base_weight','scenario_weight_range','exact_historical_company_share']])''')
md('''## 08. Outcomes & Baselines

All forecasts use the same 57 origin dates. Baselines: expanding historical mean, share persistence (`S[t]−S[t−2]`), fixed Ridge controls (`share level`, `two-quarter share momentum`, lagged macro payroll YoY, lagged courier YoY), augmented Ridge (+ warehouse premium), and signal-only Ridge. Ridge `alpha=8` is fixed, never optimized on test outcomes; minimum train count is 40, and three-quarter purge prevents future target-release overlap.''')
code('''r=run(n_perm=1000,n_boot=2000,n_pert=1000)
charts(r)
print('Computed OOS rows:',len(r['pred']))
print('Saved figures:',len(list((ROOT/'figures').glob('*.svg'))))''')
code('''display(r['scorecard'].round(5))
print('Control minus augmented RMSE:',round(r['summary']['observed_delta_rmse_pp'],6),'pp')''')
md('''## 09. Empirical Findings

The augmented model achieves **1.2803 pp RMSE** versus **1.3233 pp** for the controls (improvement **0.0430 pp**), but the historical mean achieves **0.8223 pp** and is substantially better. Augmented MAE (**0.5947**) is slightly worse than controls (**0.5889**). The full-panel factor/target Spearman correlation is only a descriptive association, not a security-return IC.''')
code('''display(r['pred'][['date','actual','mean','persistence','controls','augmented','factor_only']].head(8).round(4))
print('Full-panel descriptive Spearman:',round(r['summary']['rank_ic_fullsample_descriptive_not_oos'],4))''')
code('''plt.figure(figsize=(9,3.5));x=pd.to_datetime(r['pred'].date);plt.plot(x,r['pred'].actual,label='Actual');plt.plot(x,r['pred']['mean'],label='Mean');plt.plot(x,r['pred'].augmented,label='Augmented');plt.legend();plt.title('Real OOS forecasts: observed vs models');plt.show()''')
code('''display(SVG(filename=str(ROOT/'figures/05_scorecard.svg')))''')
md('''## 10. Robustness & Placebos

The **1,000-refit 4-quarter block shuffle** preserves within-block signal structure but not a valid exact exchangeable null; report an **exploratory tail fraction**, never an exact p-value. The **2,000-draw paired circular-block bootstrap** retains local serial dependence in OOS error pairs; its interval is descriptive and sensitive to block length and small effective sample. The 1,000 exposure perturbations test a plausible NAICS 493/492 blend, not precise issuer revenue weights.''')
code('''print('Block shuffle draws:',len(r['null']),'| exploratory tail fraction:',r['summary']['permutation_exploratory_tail_fraction'])
print('Paired bootstrap draws:',len(r['bootstrap']),'| 95% interval:',r['summary']['bootstrap_95pct_delta_rmse_pp'])
print('Exposure draws:',len(r['perturb']),'| control-relative positive fraction:',r['summary']['exposure_positive_fraction'])''')
code('''display(SVG(filename=str(ROOT/'figures/06_block_placebo.svg')))''')
code('''display(SVG(filename=str(ROOT/'figures/07_bootstrap.svg')))''')
code('''display(SVG(filename=str(ROOT/'figures/08_exposure.svg')))''')
code('''display(r['ablations'].round(5))
display(r['horizons'].round(5))
display(r['lags'].round(5))''')
md('''## 11. Regime Sensitivity

The positive aggregate control-relative RMSE gain is concentrated in **2020–2021**. Before 2020, after 2021 and after excluding 2020–2021, the incremental gain is **negative**. Pandemic shocks and the 2025 Census definition/benchmark change prevent treating the full-sample coefficient as stationary.''')
code('''display(r['regimes'].round(5))
assert r['regimes'].set_index('regime').loc['exclude_2020_2021','delta_rmse_pp']<0''')
code('''display(SVG(filename=str(ROOT/'figures/09_regimes.svg')))''')
code('''display(r['loo'].round(5))''')
code('''display(SVG(filename=str(ROOT/'figures/10_leave_one_year_out.svg')))''')
md('''## 12. Bias Audit & Verdict

**PIT/revisions:** exact historical Census/BLS vintages not retrieved; lagged revised snapshots remain non-PIT. **Lookahead:** no future feature values or full-sample scaling in the model, and three-origin purge applies. **Selection:** reverse-direction hypothesis is not independent of prior warehousing research; no preregistered prospective holdout. **Survivorship:** no issuer sample, but the national survey has coverage/definition changes. **Overlap:** two-quarter targets and serial errors make IID inference invalid. **Multiple testing:** exploratory robustness does not license selecting the best horizon after seeing the outcomes. **Costs:** no tradable securities, corporate fundamentals, benchmark-adjusted returns or execution costs. **Verdict:** negative/unstable macro factor, no investable alpha.''')
code('''s=r['summary']
checks={'loses_to_mean':float(r['scorecard'].set_index('model').loc['augmented','rmse_pp'])>float(r['scorecard'].set_index('model').loc['mean','rmse_pp']),
'bootstrap_crosses_zero':s['bootstrap_95pct_delta_rmse_pp'][0]<0<s['bootstrap_95pct_delta_rmse_pp'][1],
'nonpandemic_negative':float(r['regimes'].set_index('regime').loc['exclude_2020_2021','delta_rmse_pp'])<0,
'PIT_unverified':not s['PIT_verified'],'equity_unverified':not s['equity_returns_tested']}
display(pd.Series(checks,name='Audit result'))
assert all(checks.values())''')
md('''## 13. Reproduction

Reproduction from a clean directory: `pip install -r requirements.txt`; `OPENBLAS_NUM_THREADS=1 python run_analysis.py`; `PYTHONPATH=. OPENBLAS_NUM_THREADS=1 pytest -q tests`; `jupyter nbconvert --to notebook --execute research.ipynb --output reproduced.ipynb`. The original 107-row raw file is immutable and hash checked. All model tables, 1,000 permutations, 2,000 bootstrap draws and 1,000 exposure mixtures are recomputed from it. The root repository's `scripts/validate_studies.py` is a **layout** check, not a numerical CI run.''')
code('''print('Frozen SHA:',s['source_snapshot_sha256'])
print('Observed rows:',s['raw_rows'],'| formation rows:',s['formation_rows'],'| OOS:',s['oos_rows'])
print('Figure files:',sorted(x.name for x in (ROOT/'figures').glob('*.svg')))''')
md('''## 14. Next-Stage Protocol

Acquire true 2000–2026 Census quarterly vintages and BLS monthly release histories (ALFRED or official archived releases); reproduce the historical 2025 methodology break; source independently dated U.S. retailer digital sales and 10-Q/10-K disclosures. Establish issuer-level exposures before any leave-one-company-out test. Only then preregister a 2027-forward holdout with dividend-adjusted total returns, industry controls, realistic publication dates, transaction costs, and multiple-testing correction. **Do not relabel this macro pilot as equity alpha.**''')
code('''pending=pd.DataFrame({'required_next_stage':['Census/BLS historical release vintages','2025 Census definition bridge','Issuer-level dated e-commerce sales','Delisted-inclusive total-return panel','Costs and execution model'], 'status':['NOT RETRIEVED']*5})
display(pending)''')
md('''## 15. Sources & Artifacts

**Official data:** [ECOMPCTSA](https://fred.stlouisfed.org/series/ECOMPCTSA), [CES4349300001](https://fred.stlouisfed.org/series/CES4349300001), [CES4349200001](https://fred.stlouisfed.org/series/CES4349200001), [PAYEMS](https://fred.stlouisfed.org/series/PAYEMS); see `data/source_register.csv` for source grades, release dates, observation ranges, revision caveats, and exact URLs. **Artifacts:** raw snapshot, derived panel, source and exposure registers, 11 computed result files, 10 SVG diagnostics, Python modules, tests and logs. **No claim of issuer-level equity returns or actual-vintage point-in-time availability.**''')
code('''print('Verdict: FAIL as robust incremental retail-share predictor; reproduced retrospective macro pilot only.')
print('PIT:',s['PIT_verified'],'| issuer fundamentals:',s['firm_fundamentals_tested'],'| equity returns:',s['equity_returns_tested'])''')
nb.cells=cells
nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'},'study_status':'REPRODUCED MACRO PILOT; NOT PIT; NO EQUITY ALPHA'}
nbf.write(nb,ROOT/'research.ipynb')
print('Generated',len(cells),'cells;',sum(x.cell_type=='code' for x in cells),'code cells')
