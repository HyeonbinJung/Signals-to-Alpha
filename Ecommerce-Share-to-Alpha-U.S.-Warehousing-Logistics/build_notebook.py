"""Builds a 15-chapter standalone research notebook with actual computed outputs."""
from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parent
nb=nbf.v4.new_notebook();cells=[]
def M(s):cells.append(nbf.v4.new_markdown_cell(s))
def C(s):cells.append(nbf.v4.new_code_cell(s))
M('''# E-Commerce Share-to-Alpha — U.S. Warehousing and Logistics
**26 October 2026 · Reproduced retrospective macro pilot · NOT historical PIT or equity alpha.**

A falsifiable industry-demand study modeled on the K-Food v3 research structure. The notebook executes from frozen official-source CSV data and computes independent descriptive tables, walk-forward forecasts, sensitivity tests and figures. Every plot below is derived from the same checked-in observations.''')
M('''## 01. Abstract
**Research question:** Does U.S. retail e-commerce share acceleration predict two-quarter-ahead warehousing employment YoY beyond warehouse persistence and national payroll growth? The primary scorecard covers 57 purged expanding-window origins. A better retrospective RMSE is not a causal or tradable alpha claim; the lack of historical release vintages is decisive.''')
C('''from pathlib import Path
import json, hashlib
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from IPython.display import display, Image
from run_analysis import ROOT, read_data, panel_for, walk_forward, metrics, block_bootstrap, block_placebo, run
raw=read_data();panel=panel_for(raw);oos=walk_forward(panel)
reported=json.loads((ROOT/'results/metrics.json').read_text())
assert len(raw)==107 and len(oos)==57
print('Data quarters:',len(raw),' | OOS origins:',len(oos),' | Date range:',raw.index.min().date(),'→',raw.index.max().date())''')
C('''display(pd.DataFrame(metrics(oos)).T.round(3))
print('Primary outcome: BLS NAICS 493 warehousing employment log YoY, two quarters ahead.')''')
M('''## 02. Research Design & Hypotheses
**H1:** increasing e-commerce share precedes greater storage/fulfillment employment. **H2:** a fixed factor adds predictive value beyond warehouse persistence and payroll. **H3:** gains withstand lag, horizon, segment and regime stress. **Null:** if simple baselines dominate or dependent-sample uncertainty includes zero, the candidate is not validated. **Counterthesis:** automation and outsourced/in-house fulfillment can break employment transmission.''')
C('''print('Formation:',oos.index.min().date(),'to',oos.index.max().date())
print('Training origins at first test:',oos.training_n.iloc[0])
print('Targets overlap: quarterly observations forecast 2Q-ahead YoY. Do not use IID t-tests.')''')
M('''## 03. Industry Context
U.S. Census retail e-commerce share rose to 17.1% in 2026Q2 from 16.3% in 2025Q2 (Census report published 18 August 2026). The employment proxy is BLS Current Employment Statistics, not fulfillment throughput or revenue. Structural online-channel growth and warehouse hiring are related but need not be proportional.''')
C('''display(raw[['ECOMPCTSA','CES4349300001','CES4349200001']].tail(9).round(2))
print('E-commerce share latest:',raw.ECOMPCTSA.dropna().iloc[-1],'%')''')
C('''display(Image(filename=str(ROOT/'figures/01_ecommerce_share.png')))
display(Image(filename=str(ROOT/'figures/02_logistics_employment.png')))''')
M('''## 04. Data & Source Integrity
**Source A:** U.S. Census Bureau (`ECOMPCTSA`) and BLS CES (`CES4349300001`, `CES4349200001`, `PAYEMS`) via FRED. Warehouse/courier/payroll monthly SA counts are converted to arithmetic quarterly means using FRED graph options; no synthetic observations. All 107 quarterly rows are frozen and source URLs/units/last known releases are recorded below. The source CSV is latest revised, not an ALFRED vintage panel.''')
C('''sources=pd.read_csv(ROOT/'data/source_register.csv')
display(sources[['series_id','publisher','units','observations','source_release_latest_known','historical_vintages','quality']])''')
C('''print('Missing observations per series:')
display(raw.isna().sum().to_frame('missing'))
assert raw.index.is_monotonic_increasing and raw.index.is_unique
assert raw.loc['2026-04-01','ECOMPCTSA']==17.1
print('Frozen CSV SHA-256:',hashlib.sha256((ROOT/'data/fred_quarterly_snapshot_2026-10-26.csv').read_bytes()).hexdigest())''')
M('''## 05. Point-in-Time Availability
At **end-of-quarter t**, features are based on quarter **t−1** or earlier, giving one full-quarter publication buffer. An origin `u` enters the training set at `t` only if `u+2+1 <= t`, reflecting two-quarter target maturity plus a one-quarter reporting buffer. **This is not genuine PIT** because original Census and BLS historical vintages were not downloaded; even old observations may have been revised years later.''')
C('''sample=oos.iloc[0]
print('First forecast origin:',oos.index[0].date(),' | matured training observations:',sample.training_n)
print('Last forecast origin:',oos.index[-1].date(),' | matured training observations:',oos.training_n.iloc[-1])
assert (panel.origin_number<=sample.origin_number-3).sum()==sample.training_n''')
C('''display(panel[['origin_number','ecom_delta','ecom_factor','known_yoy','payroll_yoy','target']].head(8).round(3))
print('The panel is an analysis snapshot; it does not assert observation-level release dates.')''')
M('''## 06. Factor Construction
Let `E` be online retail share in percentage points, `W` warehouse employment, `P` total nonfarm payroll. **Pre-fixed signal:** `F_t=tanh((E_{t−1}−E_{t−5})/2)`. **Known controls:** `100 ln(W_{t−1}/W_{t−5})` and `100 ln(P_{t−1}/P_{t−5})`. **Target:** `100 ln(W_{t+2}/W_{t−2})`. Ridge penalty 10 is fixed; all standardization is fit on the training window only. No optimized factor thresholds or whole-sample z-scores.''')
C('''display(panel[['ecom_delta','ecom_factor','known_yoy','payroll_yoy','target']].describe().round(3))
print('Factor finite:',np.isfinite(panel.ecom_factor).all(),'bounded:',panel.ecom_factor.abs().max()<=1)''')
C('''display(Image(filename=str(ROOT/'figures/03_factor_dynamics.png')))''')
M('''## 07. Exposure & Transmission
The primary outcome represents NAICS 493 warehouse employment, not a publicly traded security. A 50–100% warehouse and 0–50% courier segment mix is a **scenario** for industry-definition uncertainty; it does not represent observed historical company product/revenue weights. Dated firm-level exposure mapping is **unavailable**; firm earnings, IC, excess equity returns and transaction-cost metrics are **NOT TESTED**.''')
C('''exposure=pd.read_csv(ROOT/'data/exposure_map.csv')
display(exposure)
print('Exposure perturbation is an outcome-composition stress test, not a company portfolio backtest.')''')
M('''## 08. Outcomes & Baselines
Five expanding-window competitors are scored on **identical origins**: historical mean; warehouse persistence; warehouse persistence + payroll; both controls + e-commerce share; e-commerce alone. The earliest 2012Q1 origin has at least 41 matured training observations. Targets and training windows are purged to avoid obvious label look-ahead; revised historical observations remain a separate unresolved issue.''')
C('''scores=pd.DataFrame(metrics(oos)).T.round(4)
display(scores)
assert scores.n.nunique()==1
print('Full vs macro RMSE gain (pp):',round(scores.loc['macro','rmse']-scores.loc['full','rmse'],4))''')
C('''display(oos[['actual','mean','persistence','macro','full','training_n']].head(8).round(3))
display(oos[['actual','macro','full']].tail(8).round(3))''')
M('''## 09. Empirical Findings
In 57 forecasts, the augmented model RMSE is **5.172 pp** versus **5.869 pp** for macro controls, **5.360 pp** for persistence and **7.422 pp** for historical mean. The e-commerce-only model is substantially weaker. The macro gain is positive in this frozen retrospective exercise, but effect stability, release-vintage leakage and statistical dependence prevent an alpha conclusion.''')
C('''display(Image(filename=str(ROOT/'figures/04_oos_forecasts.png')))''')
C('''oos['loss_improvement']=(oos.macro-oos.actual)**2-(oos.full-oos.actual)**2
print('Average paired squared loss improvement:',round(oos.loss_improvement.mean(),4),'squared pp')
print('Positive loss improvement origins:',int((oos.loss_improvement>0).sum()),'/',len(oos))
display(Image(filename=str(ROOT/'figures/05_loss_difference.png')))''')
M('''## 10. Robustness & Placebos
The **1,000-refit 4-quarter block-shuffle** preserves within-block structure but does not justify an exact permutation p-value under trend/nonstationarity. The **2,000-draw 4-quarter moving-block bootstrap** resamples paired OOS errors, not individual observations. Segment-mix perturbations (1,000 draws) and horizon/lag ablations test whether the association depends on a particular specification.''')
C('''placebo=reported['placebo'];boot=reported['uncertainty'];sens=reported['exposure_sensitivity']
display(pd.DataFrame({'measure':['observed delta RMSE','block-shuffle exploratory tail','bootstrap CI lower','bootstrap CI upper','segment-mix median'],
'value':[placebo['observed_delta_rmse'],placebo['exploratory_right_tail_fraction'],*boot['delta_rmse_macro_minus_full_ci95'],sens['delta_rmse_median']]}).round(4))''')
C('''display(Image(filename=str(ROOT/'figures/06_block_placebo.png')))
print('Caution: the small exploratory block-shuffle tail fraction is NOT an exact significance level.')''')
C('''rob=pd.DataFrame(reported['robustness']).T
rob['delta_rmse_macro_minus_full']=rob.macro_rmse-rob.full_rmse
display(rob.round(3))''')
M('''## 11. Regime Sensitivity
Pre-2020 and 2020+ origins are scored separately without refitting models by regime. The candidate improves on the macro model in both subsamples, but 2020+ errors are much larger. A courier outcome check is **not a valid unaffected negative control**: delivery hiring may respond to online sales as well, so similar results imply non-specificity, not external validation.''')
C('''display(rob.loc[['pre_covid','covid_and_after','exclude_2020_2021','courier_negative_control'],['n','macro_rmse','full_rmse','delta_rmse_macro_minus_full']].round(3))''')
C('''for tag,mask in [('pre-2020',oos.index<'2020-01-01'),('2020+',oos.index>='2020-01-01')]:
 z=oos.loc[mask];print(tag, 'n=',len(z),'mean actual=',round(z.actual.mean(),3),'RMSE factor=',round(metrics(z)['full']['rmse'],3))''')
M('''## 12. Bias Audit & Verdict
**Unresolved vintage/revision leakage** is the most consequential weakness. A conservative t−1 buffer does not recover the historical data actually visible at each formation date. Additional limitations: nonstationarity and COVID structural break, multiple exploratory variants, overlapping targets, national-level selection, no independent firm sample, no delisting-adjusted total returns, no trading costs, and invalid exact-exchangeability assumptions for the block shuffle. **Verdict:** promising *retrospective macro lead-factor candidate*, not verified PIT and not equity alpha.''')
C('''for i,w in enumerate(reported['warnings'],1):print(f'{i}. {w}')
assert boot['delta_rmse_macro_minus_full_ci95'][0]<0<boot['delta_rmse_macro_minus_full_ci95'][1]
print('Inference gate: bootstrap interval includes zero; no reliable positive alpha claim.')''')
M('''## 13. Reproduction
From a clean checkout, install `requirements.txt`, run `python run_analysis.py`, `pytest -q tests`, and execute this notebook with `jupyter nbconvert --to notebook --execute research.ipynb`. From repository root run `python scripts/validate_studies.py`. Frozen raw inputs, derived panel, all OOS forecasts, uncertainty tables and six calculated diagnostic figures are committed; no network request is needed for reproduction.''')
C('''print('Saved artifact checks:')
for p in [ROOT/'data/derived_factor_panel.csv',ROOT/'results/walk_forward_oos.csv',ROOT/'results/metrics.json',ROOT/'figures/06_block_placebo.png']:
 print(p.relative_to(ROOT),p.exists(),p.stat().st_size if p.exists() else None)
assert all(p.exists() for p in (ROOT/'figures').glob('*.png'))''')
C('''from run_analysis import ridge_fit_predict
z=np.array([[1.],[2.],[3.],[4.]])
assert np.isfinite(ridge_fit_predict(z,np.array([1.,2.,3.,4.]),np.array([2.5])))
print('Closed-form train-only ridge smoke test passed.')''')
M('''## 14. Next-Stage Protocol
Obtain archived quarter-specific Census releases and BLS vintage files, rebuild the panel using actual release timestamps, and rerun with a locked 2022–2027 holdout. Add independently dated warehouse capacity, automation capex, shipment volumes and company segment financials; only then examine historical-universe adjusted total returns with costs and multiple-testing controls. Prefer a genuinely prospective test over tuning the same retrospective sample.''')
C('''print('Next gate: source-vintage verification -> independent firm fundamentals -> security total returns -> costs.')
print('No historical PIT evidence or company-level investable alpha is present in this study.')''')
M('''## 15. Sources & Artifacts
Primary publishers: U.S. Census Bureau and U.S. Bureau of Labor Statistics, via the Federal Reserve Bank of St. Louis. Official series: [ECOMPCTSA](https://fred.stlouisfed.org/series/ECOMPCTSA), [CES4349300001](https://fred.stlouisfed.org/series/CES4349300001), [CES4349200001](https://fred.stlouisfed.org/series/CES4349200001), [PAYEMS](https://fred.stlouisfed.org/series/PAYEMS). Latest e-commerce release: 2026-08-18; latest BLS CES release: 2026-10-02. **Historical observation release timestamps: UNKNOWN.** See `data/source_register.csv`, `data/fred_quarterly_snapshot_2026-10-26.csv`, `results/`, `figures/`, `tests/` and `README.md`.''')
C('''print('Official source URLs:')
for u in sources.source_url:print(' •',u)
print('End of research notebook. Evidence level: reproduced retrospective macro pilot.')''')
nb.cells=cells;nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}
nbf.write(nb,ROOT/'research.ipynb')
print('Notebook cells:',len(cells),'code:',sum(c.cell_type=='code' for c in cells))
