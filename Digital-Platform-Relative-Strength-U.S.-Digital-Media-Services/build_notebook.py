from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parent
readme=(ROOT/'README.md').read_text()
parts=readme.split('\n## ')[1:]
assert len(parts)==15
sections=['## '+p for p in parts]
C=lambda s:nbf.v4.new_code_cell(s.strip())
M=lambda s:nbf.v4.new_markdown_cell(s.strip())
code={
1:[
'''from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display,Markdown
from analysis import (CORE,CONTROL,EXPOSURE,load_prices,panel,walk_forward,scorecard,
                      paired_improvement,rank_diagnostics,fast_placebo,moving_block_bootstrap,
                      fast_exposure_sensitivity,regime_table,FastRefit)
ROOT=Path.cwd()
summary=json.loads((ROOT/'results'/'summary.json').read_text())
print('Snapshot:',summary['n_raw_weeks'],'weekly rows | OOS:',summary['n_oos_origins'],'origins |',summary['status'])''',
'''print('Primary OOS result: control RMSE',round(summary['control_rmse_pp'],4),
      'augmented RMSE',round(summary['augmented_rmse_pp'],4),
      'improvement',round(summary['improvement_pp'],4),'percentage points')'''],
2:[
'''hypotheses=pd.DataFrame({'hypothesis':['H1','H2','H3','Null'],
'predeclared_test':['beats mean and momentum','beats multivariate Ridge + bootstrap and block shuffle',
'leave-one-company-out, horizons, 1-week lag, exposure perturbations','no conditional incremental predictive information']})
display(hypotheses)''',
'''print('Failure standard: no OOS gain vs strongest simple baseline, bootstrap includes zero, and regime instability.');print('Selection caveat: the 2018–2019 universe was not chosen prospectively.')'''],
3:[
'''exposure=pd.read_csv(ROOT/'data'/'exposure_map.csv');display(exposure[['ticker','role','analyst_digital_exposure','filing_date']])''',
'''print('Company count:',len(exposure),'core digital-service names:',list(CORE),'comparison names:',list(CONTROL))
print('Industry market-size history: UNKNOWN — no market-size numbers inferred from this six-stock teaching sample.')'''],
4:[
'''sources=pd.read_csv(ROOT/'data'/'source_register.csv',keep_default_na=False)
display(sources[['source_id','grade','publisher','publication_date','period_start','period_end','vintage_revisions']])''',
'''prices=load_prices(ROOT/'data'/'plotly_stocks_2018_2019_frozen.csv')
print('shape:',prices.shape,'range:',prices.date.min(),prices.date.max(),
      'nulls:',int(prices.isna().sum().sum()),'weekly gaps:',prices.date.diff().dropna().dt.days.value_counts().to_dict())
print('raw SHA256:',hashlib.sha256((ROOT/'data'/'plotly_stocks_2018_2019_frozen.csv').read_bytes()).hexdigest())''',
'''fig,ax=plt.subplots(figsize=(9,3.6))
for f in CORE:ax.plot(prices.date,prices[f],label=f)
ax.set_title('Observed normalized price paths (source adjustment unknown)');ax.set_ylabel('2018-01-01=1');ax.legend(ncol=4);plt.tight_layout();plt.show()'''],
5:[
'''print('SEC 2017 filings last available:',sources.loc[sources.grade=='A','publication_date'].max())
print('Plotly historical price release/vintage:',sources.loc[sources.grade=='B','release_lag'].iloc[0])
print('UNKNOWN price adjustment and vendor: PIT claim explicitly prohibited.')''',
'''p0=panel(prices);print('First raw formation:',p0.date.min(),'first OOS evaluated formation is later; target label is 4 weeks ahead.')
assert ((p0.target_date-p0.date).dt.days==28).all()'''],
6:[
'''df=panel(prices);display(df[['date','firm','rel8','exposure','factor','y']].head(8).round(4))
print('Formula: factor_i,t = exposure_i * tanh((8-week stock log-return - 8-week comparator log-return)*100/20)')''',
'''fig,ax=plt.subplots(figsize=(9,3.6))
for f in CORE:ax.plot(df.loc[df.firm==f,'date'],df.loc[df.firm==f,'factor'],label=f)
ax.axhline(0,color='black',linewidth=.7);ax.set_title('Formation-date exposure-weighted signal');ax.legend(ncol=4);plt.tight_layout();plt.show()''',
'''print('Fixed factor scales and weights:',EXPOSURE,'; factor uses no future target or full-sample standardization.')
assert all(np.allclose(df.loc[df.firm==f,'factor'],w*np.tanh(df.loc[df.firm==f,'rel8']/20)) for f,w in EXPOSURE.items())'''],
7:[
'''display(exposure.loc[exposure.ticker.isin(CORE),['ticker','analyst_digital_exposure','filing_date','description']])''',
'''print('Fundamental outcomes (2018-2019 revenue/EPS): NOT COLLECTED. 2017 SEC filings are qualitative exposure evidence only.')
print('No exact revenue-exposure weights, no firm-level independent demand outcome, no verified security total returns.')'''],
8:[
'''print('Target: 4-week log price change of core firm minus average 4-week AAPL/MSFT log price change; unit = percentage points.')
print('Train purge: origin_train + 4 <= origin_test; train-only scaling and coefficients.');print('Raw panel rows:',len(df))''',
'''oos=walk_forward(df)
print('Model comparison observations:',oos.groupby('model').size().to_dict());print('OOS origins:',oos.t.nunique())
display(oos[['date','firm','model','train_origins','y','prediction']].head(8).round(3))''',
'''display(scorecard(oos).round(4))
print('Persistence is a direct last-4-week return forecast; momentum is raw 8-week relative return, not fitted.')'''],
9:[
'''sc=scorecard(oos);display(sc[['model','n_origins','n_predictions','rmse_pp','mae_pp','direction_accuracy']].round(4))
print('Control-minus-augmented RMSE:',round(paired_improvement(oos),6),'pp; negative = worse.')''',
'''fig,ax=plt.subplots(figsize=(9,3.5));ax.bar(sc.model,sc.rmse_pp);ax.tick_params(axis='x',rotation=35)
ax.set_title('Purged expanding-window out-of-sample RMSE');ax.set_ylabel('log price-change percentage points');plt.tight_layout();plt.show()''',
'''ic=rank_diagnostics(oos);print('Weekly mean rank IC:',round(ic.rank_ic.mean(),4),'mean top-bottom price spread:',round(ic.spread_pp.mean(),4),'pp')
display(ic[['date','rank_ic','spread_pp','long','short']].head(7).round(3))''',
'''g=oos[oos.model.isin(['control','augmented'])].groupby(['date','model']).error.apply(lambda x:np.mean(x*x)).unstack()
fig,ax=plt.subplots(figsize=(9,3.5));ax.plot(g.index,g.control.cumsum(),label='control');ax.plot(g.index,g.augmented.cumsum(),label='augmented')
ax.set_title('Cumulative average squared loss');ax.legend();plt.tight_layout();plt.show()'''],
10:[
'''place=fast_placebo(df,n=1000,seed=20261028)
archive=pd.read_csv(ROOT/'results'/'placebo.csv')
assert np.allclose(place.rmse_improvement_pp,archive.rmse_improvement_pp)
actual=paired_improvement(oos);tail=(1+(place.rmse_improvement_pp>=actual).sum())/(len(place)+1)
print('1,000 refitted four-week-block shuffles; exploratory tail fraction:',round(tail,6),'(NOT exact p-value)')''',
'''fig,ax=plt.subplots(figsize=(9,3.5));ax.hist(place.rmse_improvement_pp,bins=30);ax.axvline(actual,color='black',label='observed')
ax.set_title('Block-shuffled factor placebo: full OOS refits');ax.set_xlabel('control minus augmented RMSE (pp)');ax.legend();plt.tight_layout();plt.show()''',
'''boot=moving_block_bootstrap(oos,n=2000,block=4,seed=20261029)
assert np.allclose(boot.rmse_improvement_pp,pd.read_csv(ROOT/'results'/'bootstrap.csv').rmse_improvement_pp)
ci=np.quantile(boot.rmse_improvement_pp,[.025,.975]);print('2,000 paired moving-block draws; 95% CI:',ci)''',
'''fig,ax=plt.subplots(figsize=(9,3.5));ax.hist(boot.rmse_improvement_pp,bins=30);ax.axvline(0,color='black')
ax.set_title('Paired 4-week block bootstrap of OOS RMSE improvement');plt.tight_layout();plt.show()''',
'''expo=fast_exposure_sensitivity(df,n=1000,seed=20261030)
assert np.allclose(expo.improvement_pp,pd.read_csv(ROOT/'results'/'exposure.csv').improvement_pp)
print('1,000 exposure draws; share of RMSE improvements:',round((expo.improvement_pp>0).mean(),4))
fig,ax=plt.subplots(figsize=(9,3.5));ax.hist(expo.improvement_pp,bins=30);ax.axvline(0,color='black');ax.set_title('Fixed-prior weight perturbation');plt.tight_layout();plt.show()''',
'''leave=pd.read_csv(ROOT/'results'/'leave_one_firm.csv');display(leave.round(4))
print('Leave-one-company-out retrains on and evaluates remaining 3; it is NOT an unseen-company holdout.')''',
'''ablate=pd.read_csv(ROOT/'results'/'ablations.csv');display(ablate.round(4))
print('40-week rolling controlled-minus-augmented RMSE:',round(summary['rolling_40wk_improvement_pp'],4))'''],
11:[
'''regimes=pd.read_csv(ROOT/'results'/'regimes.csv');display(regimes.round(4))
fig,ax=plt.subplots(figsize=(8,3));ax.bar(regimes.regime,regimes.rmse_improvement_pp);ax.axhline(0,color='black')
ax.set_title('2018 vs 2019 regimes');plt.tight_layout();plt.show()''',
'''alternatives=pd.read_csv(ROOT/'results'/'alternatives.csv');display(alternatives.round(4))
fig,ax=plt.subplots(figsize=(9,3));ax.bar([f'h{r.horizon_weeks}/lag{r.signal_lag_weeks}' for r in alternatives.itertuples()],alternatives.improvement_pp)
ax.axhline(0,color='black');ax.tick_params(axis='x',rotation=40);ax.set_title('Horizon and conservative formation lag');plt.tight_layout();plt.show()'''],
12:[
'''bias=pd.DataFrame({'risk':['Historical vendor PIT','Revisions/adjustments','Selection/survivorship','Overlapping labels','Multiple testing','Costs/borrow','Independent fundamentals'],
'finding':['UNKNOWN','UNKNOWN','Six-ticker selected demonstration basket','Four-week overlap; 65 origins','No adjusted discovery claim','20bp illustration only','Not collected']})
display(bias)''',
'''gross=ic.spread_pp.mean();display(pd.DataFrame({'illustrative_roundtrip_cost_bps':[0,10,20,50,100],
'mean_top_minus_bottom_price_spread_pp':[gross-c/100 for c in [0,10,20,50,100]]}).round(3))
print('These are overlapping forecast-window spreads, NOT implementable net portfolio returns.')''',
'''print('VERDICT:',summary['status']);print('Negative OOS incremental gain and negative rank IC, no PIT or total-return claim.')'''],
13:[
'''print('Recorded artifacts:',len(list((ROOT/'figures').glob('*.png'))),'PNG figures;','1000/2000/1000 placebo/bootstrap/exposure draws')
print('Full numerical reproduction: python run_analysis.py | tests: python -m pytest -q tests | notebook: python execute_notebook.py')''',
'''r=subprocess.run([sys.executable,'-m','pytest','-q','tests'],capture_output=True,text=True,check=False)
print('Observed tests from notebook kernel:');print(r.stdout[-1200:]);assert r.returncode==0,r.stderr'''],
14:[
'''protocol=pd.DataFrame({'stage':['1 vendor tape','2 filing PIT','3 universe','4 model','5 trading audit','6 holdout'],
'deliverable':['daily prices, dividends, delistings, corporate actions','time-stamped digital ad/streaming operating metrics','all 2018 eligible public issuers','pre-registered non-price factor','market/sector total return, costs, borrow','untouched post-2019 evaluation']})
display(protocol)'''],
15:[
'''display(sources[['source_id','grade','publisher','url','publication_date','vintage_revisions']])''',
'''saved=json.loads((ROOT/'results'/'summary.json').read_text())
assert np.isclose(saved['improvement_pp'],paired_improvement(oos))
assert saved['n_oos_origins']==oos.t.nunique()
assert saved['publication_vintage']=='UNKNOWN' and saved['total_return_adjustment']=='UNKNOWN'
print('Saved outputs and current computed metrics agree. Final verdict: NEGATIVE / RETROSPECTIVE / NOT INVESTABLE.')''']
}
nb=nbf.v4.new_notebook(metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
                                  'language_info':{'name':'python'}})
nb.cells.append(M('# Digital-Platform Relative Strength — U.S. Digital Advertising & Streaming Services\n\n**Reproduced retrospective price-return pilot; NOT PIT, NOT verified total returns, NOT investable equity alpha.**\n\nIndependent paper with saved computed results; 2018–2019 Plotly six-stock frozen demonstration sample.'))
for i,s in enumerate(sections,1):
    nb.cells.append(M(s))
    for code_cell in code[i]:nb.cells.append(C(code_cell))
nbf.validate(nb)
(ROOT/'research.ipynb').write_text(nbf.writes(nb),encoding='utf-8')
print('notebook cells',len(nb.cells),'markdown',sum(c.cell_type=='markdown' for c in nb.cells),'code',sum(c.cell_type=='code' for c in nb.cells))
