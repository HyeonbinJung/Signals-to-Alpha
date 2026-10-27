from pathlib import Path
import nbformat as nbf
from build_docs import sections
ROOT=Path(__file__).resolve().parent
nb=nbf.v4.new_notebook()
nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}
cells=[]
def md(t):cells.append(nbf.v4.new_markdown_cell(t))
def code(t):cells.append(nbf.v4.new_code_cell(t.strip()))
md('# Historical Copper–Aluminum Relative Prices and World Copper Demand\n\n**Reproducible retrospective demand-factor falsification, 1951–1975.** Original release vintages UNKNOWN; not equity alpha. The 15 sections follow `STUDY_TEMPLATE.md`. All plotted values and tables are computed from frozen observations and saved OOS tests.')
for h,body in sections.items():
    md('## '+h)
    md(body)
    if h.startswith('01.'):
        code('''from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt, json
from IPython.display import display
from analysis import (read_raw, make_panel, walk_forward, score, improvement,
                      block_bootstrap, block_shuffle_placebo, exposure_sensitivity,
                      ridge_forecast, CONTROLS, run_all)
from make_figures import main as make_figures
ROOT=Path.cwd()
summary=json.loads((ROOT/'results/summary.json').read_text())
print('Source observations:',summary['n_raw'],'OOS origins:',summary['n_oos'])
print('Primary gain (log-pp):',round(summary['rmse_gain_controls_minus_full'],6))''')
        code('''assert summary['not_pit'] and not summary['equity_returns_tested']
print('Research status: RETROSPECTIVE MACRO PILOT; PIT and equity alpha NOT established')''')
    elif h.startswith('02.'):
        code('''hypotheses=pd.DataFrame({'hypothesis':['H1 substitution','H2 incremental','H3 stability'],
'operational_test':['lagged relative-price signal versus forward consumption','full versus control OOS RMSE','horizon, lag, regimes, block placebo and perturbations'],
'failure_criterion':['sign/association not robust','RMSE gain <=0 or uncertain','gain reverses across credible specifications']})
display(hypotheses)''')
        code('''print('Predeclared fixed rules: lag=1 annual observation; horizon=1 year; Ridge alpha=8; first OOS formation=1965')''')
    elif h.startswith('03.'):
        code('''raw=read_raw()
print('Historical consumption first/last (1000 metric tonnes):',raw.iloc[0].WORLDCONSUMPTION,raw.iloc[-1].WORLDCONSUMPTION)
print('Historical growth multiple:',round(raw.iloc[-1].WORLDCONSUMPTION/raw.iloc[0].WORLDCONSUMPTION,3))
display(raw[['year','WORLDCONSUMPTION','COPPERPRICE','ALUMPRICE']].head())''')
        code('''fig,ax=plt.subplots(figsize=(8,3.3));ax.plot(raw.year,raw.WORLDCONSUMPTION,marker='.',label='Copper consumption');ax.set(xlabel='Year',ylabel='Thousand metric tonnes',title='Observed world copper consumption, 1951–1975');ax.grid(alpha=.2);plt.show()''')
    elif h.startswith('04.'):
        code('''assert len(raw)==25 and raw.year.is_unique and raw.notna().all().all()
assert np.allclose(raw.TIME,raw.year-1950)
print('QA PASS: 25 complete consecutive years, TIME mapping, positive levels')
register=pd.read_csv('data/source_register.csv')
display(register[['grade','publisher','series','source_publication_date','revisions_vintage']])''')
        code('''import hashlib
f=Path('data/copper_statsmodels_0_14_6_frozen.csv')
print('Frozen source SHA256:',hashlib.sha256(f.read_bytes()).hexdigest())''')
    elif h.startswith('05.'):
        code('''panel=make_panel(raw)
assert (panel.observed_through==panel.formation_year-1).all()
oos=walk_forward(panel)
assert (oos.last_train_target_year<=oos.formation_year-1).all()
display(oos[['formation_year','observed_through','target_year','last_train_target_year','n_train']])''')
        code('''print('First admissible feature year:',int(panel.observed_through.min()))
print('First OOS target year:',int(oos.target_year.min()))
print('Unknown: historical original-release timestamps; fixed lag is NOT proof of PIT')''')
    elif h.startswith('06.'):
        code('''assert np.allclose(panel.relative_cost_relief,-panel.lag_copper_price_growth+panel.lag_aluminum_price_growth)
display(panel[['formation_year','relative_cost_relief','lag_demand_growth','lag_income_growth','y_growth']].head())''')
        code('''fig,ax=plt.subplots(figsize=(8,3.3));ax.plot(panel.formation_year,panel.relative_cost_relief,label='Lagged relative-cost relief');ax.plot(panel.formation_year,panel.y_growth,label='Next-year demand growth');ax.legend();ax.grid(alpha=.2);ax.set(xlabel='Formation year',ylabel='100 x log change',title='Ex-ante factor rule versus outcome');plt.show()''')
    elif h.startswith('07.'):
        code('''exposure=pd.read_csv('data/exposure_map.csv');display(exposure)
print('Firm-level exposure estimates: NOT AVAILABLE; leave-one-company-out: NOT APPLICABLE')''')
        code('''print('Substitution hypothesis sign: copper price growth enters with -1, aluminum price growth enters with +1')''')
    elif h.startswith('08.'):
        code('''sc=score(oos)
display(sc)
assert sc.n_oos.nunique()==1 and sc.n_oos.iloc[0]==10''')
        code('''t=1965;train=panel[panel.target_year<=t-1];test=panel[panel.formation_year==t]
print('1965 origin, last allowed training label:',int(train.target_year.max()))
print('Control model prediction:',round(ridge_forecast(train,test,CONTROLS),5))
print('Augmented prediction:',round(ridge_forecast(train,test,CONTROLS+['relative_cost_relief']),5))''')
    elif h.startswith('09.'):
        code('''print('Observed control-minus-full RMSE gain:',improvement(oos))
display(oos[['formation_year','actual','mean','persistence','controls','full','factor_only']])''')
        code('''fig,ax=plt.subplots(figsize=(8,3.3));ax.plot(oos.formation_year,oos.actual,'k-o',label='Actual');ax.plot(oos.formation_year,oos.controls,'--',label='Controls');ax.plot(oos.formation_year,oos.full,':',label='Full');ax.legend();ax.grid(alpha=.2);ax.set(xlabel='Formation year',ylabel='Log-pp',title='Expanding-window out-of-sample forecasts');plt.show()''')
        code('''paired_loss=(oos.actual-oos.controls)**2-(oos.actual-oos.full)**2
print('Mean paired squared-error gain:',paired_loss.mean(),'n=',len(paired_loss))
fig,ax=plt.subplots(figsize=(8,3));ax.bar(oos.formation_year,paired_loss);ax.axhline(0,color='black',lw=.8);ax.set(title='Per-origin paired squared-error differences',xlabel='Year',ylabel='Control error² - full error²');plt.show()''')
    elif h.startswith('10.'):
        code('''placebo=pd.read_csv('results/block_shuffle_1000.csv');boot=pd.read_csv('results/block_bootstrap_2000.csv')
assert len(placebo)==1000 and len(boot)==2000
p_tail=(1+(placebo.rmse_gain>=improvement(oos)).sum())/(len(placebo)+1)
print('Exploratory block-reordering tail fraction:',p_tail)
print('Paired block-bootstrap 95% percentiles:',np.quantile(boot.rmse_gain,[.025,.975]))''')
        code('''fig,ax=plt.subplots(figsize=(8,3));ax.hist(placebo.rmse_gain,bins=35);ax.axvline(improvement(oos),color='red',label='Observed');ax.legend();ax.set(title='1,000 block-reordered refit gains (not exact p)',xlabel='RMSE gain');plt.show()''')
        code('''fig,ax=plt.subplots(figsize=(8,3));ax.hist(boot.rmse_gain,bins=35);ax.axvline(0,color='red');ax.set(title='2,000 paired circular-block bootstrap gains',xlabel='RMSE gain');plt.show()''')
        code('''expo=pd.read_csv('results/exposure_perturbations_1000.csv')
assert len(expo)==1000
print('Positive gain under ±25% independent weights:',round(100*(expo.rmse_gain>0).mean(),1),'%')
display(pd.read_csv('results/leave_one_year_out.csv'))''')
    elif h.startswith('11.'):
        code('''regimes=pd.read_csv('results/regime_sensitivity.csv');robust=pd.read_csv('results/robustness.csv')
display(regimes);display(robust)''')
        code('''fig,ax=plt.subplots(figsize=(8,3));ax.bar(regimes.regime,regimes.rmse_gain);ax.axhline(0,color='black',lw=.8);ax.set(title='Tiny historical regime splits; descriptive only',ylabel='RMSE gain');plt.show()''')
    elif h.startswith('12.'):
        code('''audit=pd.DataFrame({'risk':['Original release-vintage leakage','Demand/price simultaneity','Single historical series','Small and serially correlated OOS','Multiple-testing / subgroup selection','Survivorship and costs'],
'assessment':['UNVERIFIED','HIGH','HIGH','HIGH','HIGH','NOT APPLICABLE to untested equities']})
display(audit)''')
        code('''assert np.quantile(boot.rmse_gain,.025)<0<np.quantile(boot.rmse_gain,.975)
assert robust.loc[robust.scenario=='h2','rmse_gain'].iloc[0]<0
print('VERDICT: No stable, modern or investable alpha established.')''')
    elif h.startswith('13.'):
        code('''import importlib.metadata as meta
print('Environment:',{p:meta.version(p) for p in ['numpy','pandas','matplotlib','statsmodels']})
print('Reproduction command: OPENBLAS_NUM_THREADS=1 python run_analysis.py')''')
        code('''# Independently reconstruct one OOS row without reading saved prediction columns.
origin=1967;tr=panel[panel.target_year<=origin-1];te=panel[panel.formation_year==origin]
pred=ridge_forecast(tr,te,CONTROLS+['relative_cost_relief'])
stored=oos.loc[oos.formation_year==origin,'full'].iloc[0]
assert np.isclose(pred,stored,atol=1e-10)
print('Independent 1967 OOS recomputation matches saved table:',pred)''')
    elif h.startswith('14.'):
        code('''protocol=pd.DataFrame({'next_data':['ICSG first-release monthly usage','Dated metal prices/futures','Original vintage income & inventory','Contemporaneous firm filings and security total returns'],
'required_check':['release archive & revisions','price date and units','timestamp and no lookahead','historical universe, delistings and costs']})
display(protocol)''')
        code('''print('Pre-registration required before modern study; this 25-year teaching panel cannot justify live deployment.')''')
    elif h.startswith('15.'):
        code('''print('Frozen raw data:',Path('data/copper_statsmodels_0_14_6_frozen.csv').stat().st_size,'bytes')
print('Computed figures:',len(list(Path('figures').glob('*.svg'))))
print('Placebo rows:',len(placebo),'Bootstrap rows:',len(boot),'Perturbation rows:',len(expo))
print('Source register entries:',len(register))''')
        code('''display(register[['grade','publisher','url','observation_period','release_lag']])
print('Explicit limitation: not point-in-time; no issuer fundamentals or equity total returns.')''')
nb.cells=cells
nbf.validate(nb)
nbf.write(nb,ROOT/'research.ipynb')
print('Created',len(cells),'cells, code',sum(c.cell_type=='code' for c in cells))
