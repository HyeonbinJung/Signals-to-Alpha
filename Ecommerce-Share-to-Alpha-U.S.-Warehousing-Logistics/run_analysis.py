"""Reproducible retrospective macro lead-factor falsification for U.S. warehousing.

Not a point-in-time backtest: downloaded FRED CSV is latest revised as of 2026-10-26.
Only pandas, numpy and matplotlib required. All features use t-1 quarter or earlier.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
SEED=20261026

def read_data(path=None):
    p=Path(path) if path else ROOT/'data/fred_quarterly_snapshot_2026-10-26.csv'
    d=pd.read_csv(p,parse_dates=['observation_date']).set_index('observation_date').sort_index()
    assert len(d)==107 and d.index.is_unique and (d.index.to_series().diff().dropna().dt.days.between(89,92)).all()
    assert d['ECOMPCTSA'].notna().sum()==106
    assert d[['CES4349300001','CES4349200001','PAYEMS']].notna().all().all()
    assert (d.dropna()>0).all().all()
    return d

def panel_for(d,horizon=2, ecom_lag=1, exposure=1.0):
    """Quarter t: predictors observed at t-ecom_lag (>=1); target YoY at t+h.

    exposure mixes NAICS 493 (warehousing) and 492 (couriers) outcomes as a
    *scenario* only; it is NOT a firm-revenue or portfolio exposure estimate.
    """
    assert horizon in (1,2,4) and ecom_lag>=1 and 0<=exposure<=1
    x=d.copy()
    x['segment_mix']=exposure*x['CES4349300001']+(1-exposure)*x['CES4349200001']
    # The primary outcome is NAICS 493 employment; 492 is sensitivity/negative-control.
    yoy=lambda s: 100*np.log(s/s.shift(4))
    x['target']=yoy(x['segment_mix']).shift(-horizon)
    x['known_yoy']=yoy(x['segment_mix']).shift(1)
    x['payroll_yoy']=yoy(x['PAYEMS']).shift(1)
    x['courier_yoy']=yoy(x['CES4349200001']).shift(1)
    # E-commerce share acceleration, in percentage points over the last 4 quarters.
    x['ecom_delta']=x['ECOMPCTSA'].shift(ecom_lag)-x['ECOMPCTSA'].shift(ecom_lag+4)
    x['ecom_factor']=np.tanh(x['ecom_delta']/2.0)
    x['origin_number']=np.arange(len(x))
    x=x[['origin_number','target','known_yoy','payroll_yoy','courier_yoy','ecom_delta','ecom_factor']].dropna()
    return x

def ridge_fit_predict(train_x,train_y,test_x,alpha=10.0):
    X=np.asarray(train_x,dtype=float);y=np.asarray(train_y,dtype=float)
    z=np.asarray(test_x,dtype=float)
    mu=X.mean(axis=0);sigma=X.std(axis=0);sigma=np.where(sigma<1e-9,1.0,sigma)
    X=(X-mu)/sigma; z=(z-mu)/sigma
    yy=y.mean(); beta=np.linalg.solve(X.T@X+alpha*np.eye(X.shape[1]),X.T@(y-yy))
    return float(yy+z@beta)

def walk_forward(panel,horizon=2,start='2012-01-01',end=None,signal=None):
    p=panel.copy()
    if signal is not None: p['ecom_factor']=np.asarray(signal,dtype=float)
    X=p[['known_yoy','payroll_yoy','ecom_factor']].to_numpy(dtype=float)
    y=p['target'].to_numpy(dtype=float)
    ids=p['origin_number'].to_numpy(dtype=int)
    dates=p.index.to_numpy()
    rows=[]
    startdate=np.datetime64(start)
    enddate=np.datetime64(end) if end else np.datetime64('2100-01-01')
    for i in range(len(p)):
        if dates[i]<startdate or dates[i]>enddate:continue
        mask=ids<=ids[i]-(horizon+1)
        if mask.sum()<32:continue
        yy=y[mask];xx=X[mask];z=X[i]
        # Intercept-only, AR, AR+payroll, AR+payroll+e-commerce, e-commerce-only.
        pred=[float(yy.mean())]
        for cols in ([0],[0,1],[0,1,2],[2]):
            pred.append(ridge_fit_predict(xx[:,cols],yy,z[cols]))
        rows.append([pd.Timestamp(dates[i]),float(y[i]),int(ids[i]),int(mask.sum()),*pred])
    return pd.DataFrame(rows,columns=['origin','actual','origin_number','training_n','mean','persistence','macro','full','ecom_only']).set_index('origin')

def metrics(oos):
    y=oos['actual'].values
    return {c:{'rmse':float(np.sqrt(np.mean((oos[c].values-y)**2))),
               'mae':float(np.mean(np.abs(oos[c].values-y))),
               'n':len(oos)} for c in ('mean','persistence','macro','full','ecom_only')}

def block_bootstrap(oos,n=2000,block=4,seed=SEED):
    rng=np.random.default_rng(seed);N=len(oos);y=oos.actual.to_numpy();
    a=(oos.macro.to_numpy()-y)**2;b=(oos.full.to_numpy()-y)**2
    deltas=[]
    for _ in range(n):
        ids=np.concatenate([np.arange(s,s+block)%N for s in rng.integers(0,N,size=(N+block-1)//block)])[:N]
        deltas.append(np.sqrt(np.mean(a[ids]))-np.sqrt(np.mean(b[ids])))
    return {'draws':n,'block_quarters':block,'delta_rmse_macro_minus_full_ci95':list(map(float,np.quantile(deltas,[.025,.975]))),
            'prob_improvement_exploratory':float(np.mean(np.array(deltas)>0))}

def block_placebo(panel,observed,n=1000,block=4,seed=SEED):
    """Shuffle contiguous 4-quarter signal blocks; exploratory, NOT an exact p-value.

    Retains local within-block serial correlation but disrupts cross-block alignment.
    Refit the entire purged expanding-window forecast on every draw.
    """
    rng=np.random.default_rng(seed+7);x=panel.ecom_factor.to_numpy();N=len(x)
    blocks=[x[i:i+block] for i in range(0,N,block)]
    actual=metrics(observed)
    delta=actual['macro']['rmse']-actual['full']['rmse']
    null=[]
    for _ in range(n):
        perm=rng.permutation(len(blocks))
        shuf=np.concatenate([blocks[i] for i in perm])
        test=walk_forward(panel,signal=shuf)
        score=metrics(test)
        null.append(score['macro']['rmse']-score['full']['rmse'])
    null=np.array(null)
    return {'draws':n,'block_quarters':block,'observed_delta_rmse':float(delta),
            'null_median':float(np.median(null)),
            'exploratory_right_tail_fraction':float((1+(null>=delta).sum())/(n+1)),
            'null_ci95':list(map(float,np.quantile(null,[.025,.975]))),'null_draws':null}

def exposure_sensitivity(d, n=1000,seed=SEED):
    rng=np.random.default_rng(seed+8);w=rng.uniform(.5,1.0,n);vals=[]
    for weight in w:
        p=panel_for(d,exposure=float(weight));o=walk_forward(p)
        m=metrics(o);vals.append(m['macro']['rmse']-m['full']['rmse'])
    return {'draws':n,'warehouse_weight_range':[.5,1.0],
            'delta_rmse_median':float(np.median(vals)),
            'delta_rmse_ci90':list(map(float,np.quantile(vals,[.05,.95]))),
            'fraction_positive':float(np.mean(np.array(vals)>0))}

def run(write=True,permutations=1000,exposure_draws=1000):
    d=read_data();p=panel_for(d);o=walk_forward(p);m=metrics(o)
    pb=block_placebo(p,o,n=permutations);bs=block_bootstrap(o)
    ex=exposure_sensitivity(d,n=exposure_draws)
    robust={}
    for h in (1,4):
        x=walk_forward(panel_for(d,horizon=h),horizon=h)
        a=metrics(x);robust[f'horizon_{h}q']={'n':len(x),'macro_rmse':a['macro']['rmse'],'full_rmse':a['full']['rmse']}
    for lag in (2,3):
        x=walk_forward(panel_for(d,ecom_lag=lag))
        a=metrics(x);robust[f'lag_{lag}q']={'n':len(x),'macro_rmse':a['macro']['rmse'],'full_rmse':a['full']['rmse']}
    for name,cond in [('pre_covid',o.index<'2020-01-01'),('covid_and_after',o.index>='2020-01-01'),
                      ('exclude_2020_2021',~o.index.year.isin([2020,2021]))]:
        z=o.loc[cond];a=metrics(z)
        robust[name]={'n':len(z),'macro_rmse':a['macro']['rmse'],'full_rmse':a['full']['rmse']}
    courier=walk_forward(panel_for(d,exposure=0.0));mc=metrics(courier)
    robust['courier_negative_control']={'n':len(courier),'macro_rmse':mc['macro']['rmse'],'full_rmse':mc['full']['rmse']}
    results={
        'as_of':'2026-10-26','scope':'RETROSPECTIVE LATEST-REVISED MACRO PILOT; NOT PIT OR EQUITY ALPHA',
        'data':{'quarters':len(d),'ecommerce_nonmissing':int(d.ECOMPCTSA.notna().sum()),
                'first':str(d.index.min().date()),'last':str(d.index.max().date())},
        'primary':{'n_oos':len(o),'first_origin':str(o.index.min().date()),'last_origin':str(o.index.max().date()),
                   'minimum_train_n':int(o.training_n.min()),'horizon_quarters':2,'formation_lag_quarters':1,
                   'maturity_purge_quarters':3,'metrics':m,
                   'delta_rmse_macro_minus_full':m['macro']['rmse']-m['full']['rmse']},
        'uncertainty':bs,'placebo':{k:v for k,v in pb.items() if k!='null_draws'},
        'exposure_sensitivity':ex,'robustness':robust,
        'warnings':['No ALFRED/Census/BLS historical vintages: one-quarter lag is conservative assumption, not PIT proof.',
                    'Macro employment is not firm fundamentals or adjusted security returns.',
                    'Overlapping two-quarter forecast targets induce dependent errors.',
                    'Block-shuffle null is exploratory, not an exact permutation test.',
                    'Data collection snapshot contains 2026 Q3 employment but e-commerce only through Q2.']}
    if write:
        (ROOT/'results').mkdir(exist_ok=True);(ROOT/'figures').mkdir(exist_ok=True)
        p.to_csv(ROOT/'data/derived_factor_panel.csv',float_format='%.9f')
        o.to_csv(ROOT/'results/walk_forward_oos.csv',float_format='%.9f')
        pd.DataFrame(m).T.to_csv(ROOT/'results/scorecard.csv',float_format='%.8f')
        pd.DataFrame([{'check':k,**v} for k,v in robust.items()]).to_csv(ROOT/'results/robustness.csv',index=False)
        pd.DataFrame({'delta_rmse_macro_minus_full':pb['null_draws']}).to_csv(ROOT/'results/block_placebo_null.csv',index=False)
        (ROOT/'results/metrics.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
        plt.rcParams.update({'figure.dpi':125,'axes.grid':True,'grid.alpha':.2})
        fig,ax=plt.subplots(figsize=(10,4));ax.plot(d.index,d.ECOMPCTSA);ax.set(title='U.S. e-commerce share of retail sales (revised FRED snapshot)',ylabel='Percent');fig.tight_layout();fig.savefig(ROOT/'figures/01_ecommerce_share.png');plt.close(fig)
        fig,ax=plt.subplots(figsize=(10,4));ax.plot(d.index,d.CES4349300001,label='Warehousing & storage');ax.plot(d.index,d.CES4349200001,label='Couriers & messengers');ax.set(title='U.S. logistics employment (quarterly mean, thousands)',ylabel='Thousand persons');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/02_logistics_employment.png');plt.close(fig)
        fig,ax=plt.subplots(figsize=(10,4));ax.plot(p.index,p.ecom_factor,label='E-commerce share acceleration factor');ax.plot(p.index,p.known_yoy/20,label='Known warehouse YoY / 20');ax.set(title='Lagged factor and employment dynamics (different scales)');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/03_factor_dynamics.png');plt.close(fig)
        fig,ax=plt.subplots(figsize=(11,4));ax.plot(o.index,o.actual,label='Realized');ax.plot(o.index,o.macro,label='Macro controls',alpha=.85);ax.plot(o.index,o.full,label='With e-commerce factor',alpha=.8);ax.set(title='Purged expanding-window 2Q-ahead warehouse YoY predictions',ylabel='Log YoY, percentage points');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/04_oos_forecasts.png');plt.close(fig)
        fig,ax=plt.subplots(figsize=(10,4));ax.plot(o.index,(o.macro-o.actual)**2-(o.full-o.actual)**2);ax.axhline(0,color='black',linewidth=.8);ax.set(title='Paired squared-loss improvement: positive favors factor',ylabel='Squared pp');fig.tight_layout();fig.savefig(ROOT/'figures/05_loss_difference.png');plt.close(fig)
        fig,ax=plt.subplots(figsize=(9,4));ax.hist(pb['null_draws'],bins=35);ax.axvline(results['primary']['delta_rmse_macro_minus_full'],color='black',label='Observed');ax.set(title='Exploratory 1,000-refit four-quarter block-shuffle placebo',xlabel='Macro RMSE minus factor RMSE (pp)');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/06_block_placebo.png');plt.close(fig)
    return results

if __name__=='__main__':
    res=run();print(json.dumps({k:res[k] for k in ('primary','uncertainty','placebo','exposure_sensitivity','robustness')},indent=2))
