from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from analysis import load_prices,compute_all,CORE,CONTROL

ROOT=Path(__file__).resolve().parent

def run():
    p=load_prices(ROOT/'data'/'plotly_stocks_2018_2019_frozen.csv')
    r=compute_all(p,heavy=True)
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'figures').mkdir(exist_ok=True)
    for k,v in r.items():
        if isinstance(v,pd.DataFrame):v.to_csv(ROOT/'results'/f'{k}.csv',index=False,float_format='%.12g')
    (ROOT/'results'/'summary.json').write_text(json.dumps(r['summary'],indent=2,ensure_ascii=False)+'\n')
    fig,ax=plt.subplots(figsize=(9,4));
    for f in CORE:ax.plot(p.date,p[f],label=f)
    ax.set(title='Normalized weekly prices (Plotly example snapshot)',ylabel='2018-01-01 = 1');ax.legend(ncol=4);fig.tight_layout();fig.savefig(ROOT/'figures'/'01_price_levels.png',dpi=130);plt.close(fig)
    x=r['panel'];fig,ax=plt.subplots(figsize=(9,4));
    for f in CORE:ax.plot(x.loc[x.firm==f,'date'],x.loc[x.firm==f,'factor'],label=f)
    ax.axhline(0,color='k',lw=.7);ax.set(title='Fixed exposure-weighted 8-week relative momentum factor',ylabel='signal');ax.legend(ncol=4);fig.tight_layout();fig.savefig(ROOT/'figures'/'02_factor.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));
    for f in CORE:ax.scatter(x.loc[x.firm==f,'factor'],x.loc[x.firm==f,'y'],alpha=.45,label=f,s=15)
    ax.axhline(0,color='k',lw=.7);ax.set(xlabel='formation signal',ylabel='next 4-week benchmark-adjusted price return (pp)',title='Exploratory signal–outcome association (overlapping labels)');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures'/'03_signal_outcome.png',dpi=130);plt.close(fig)
    sc=r['scorecard'];fig,ax=plt.subplots(figsize=(9,4));ax.bar(sc.model,sc.rmse_pp);ax.tick_params(axis='x',rotation=35);ax.set(title='Purged expanding-window OOS RMSE',ylabel='percentage points');fig.tight_layout();fig.savefig(ROOT/'figures'/'04_oos_scorecard.png',dpi=130);plt.close(fig)
    oo=r['oos'];g=oo[oo.model.isin(['control','augmented'])].groupby(['date','model']).error.apply(lambda z:np.mean(z*z)).unstack();fig,ax=plt.subplots(figsize=(9,4));ax.plot(g.index,g.control.cumsum(),label='control');ax.plot(g.index,g.augmented.cumsum(),label='augmented');ax.set(title='Cumulative mean squared prediction loss',ylabel='cumulative squared pp');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures'/'05_cumulative_loss.png',dpi=130);plt.close(fig)
    ic=r['ic'];fig,ax=plt.subplots(figsize=(9,4));ax.plot(ic.date,ic.rank_ic);ax.axhline(0,color='k',lw=.7);ax.set(title='Weekly cross-sectional rank IC (n=4 stocks)',ylabel='Spearman rho');fig.tight_layout();fig.savefig(ROOT/'figures'/'06_rank_ic.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(r['placebo'].rmse_improvement_pp,bins=35);ax.axvline(r['summary']['improvement_pp'],color='k',label='observed');ax.set(title='1,000 block-shuffled factor refits (exploratory null)',xlabel='control RMSE minus augmented RMSE (pp)');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures'/'07_placebo.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(r['bootstrap'].rmse_improvement_pp,bins=35);ax.axvline(0,color='k');ax.set(title='2,000 paired moving-block bootstrap draws',xlabel='RMSE improvement (pp)');fig.tight_layout();fig.savefig(ROOT/'figures'/'08_bootstrap.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(r['exposure'].improvement_pp,bins=35);ax.axvline(0,color='k');ax.set(title='1,000 fixed-prior exposure perturbations',xlabel='RMSE improvement (pp)');fig.tight_layout();fig.savefig(ROOT/'figures'/'09_exposure.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));alt=r['alternatives'];labels=[f'h{z.horizon_weeks}-lag{z.signal_lag_weeks}' for z in alt.itertuples()];ax.bar(labels,alt.improvement_pp);ax.axhline(0,color='k');ax.tick_params(axis='x',rotation=40);ax.set(title='Alternative horizons and formation lags',ylabel='RMSE improvement (pp)');fig.tight_layout();fig.savefig(ROOT/'figures'/'10_horizon_lag.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));rg=r['regimes'];ax.bar(rg.regime,rg.rmse_improvement_pp);ax.axhline(0,color='k');ax.set(title='Calendar-regime sensitivity',ylabel='RMSE improvement (pp)');fig.tight_layout();fig.savefig(ROOT/'figures'/'11_regimes.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));lv=r['leave_one_firm'];ax.bar(lv.excluded,lv.improvement_pp);ax.axhline(0,color='k');ax.set(title='Leave-one-company-out: remaining-universe OOS',ylabel='RMSE improvement (pp)');fig.tight_layout();fig.savefig(ROOT/'figures'/'12_leave_company.png',dpi=130);plt.close(fig)
    print(json.dumps(r['summary'],indent=2));return r
if __name__=='__main__':run()
