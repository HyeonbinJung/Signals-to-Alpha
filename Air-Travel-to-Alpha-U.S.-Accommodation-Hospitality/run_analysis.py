"""Reproducible retrospective BTS/BLS hotel-demand lead-factor falsification.

All models use latest-revised October 2026 fixed snapshots; NO historical vintages.
No equity returns, firm fundamentals, or investment alpha are estimated.
"""
from __future__ import annotations
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'/'fred_bts_bls_frozen_2026-10-26.csv'
CONTROL=['accom_signal','food_signal','accom_mom_signal']
SEED=20261026

def read_data(path=DATA):
    df=pd.read_csv(path,parse_dates=['date']).set_index('date').sort_index()
    assert df.index.is_unique and df.index.is_monotonic_increasing
    assert df.index.equals(pd.date_range('2014-01-01','2026-09-01',freq='MS'))
    assert (df.dropna() > 0).all().all()
    assert len(df)==153 and df['AIRRPMTSID11'].notna().sum()==150
    assert df.loc['2020-04-01','AIRRPMTSID11']==2877804
    assert df.loc['2026-06-01','AIRRPMTSID11']==94921559
    return df

def panel_from(raw,h=3,lag_air=4,lag_labor=2,weight=1.0):
    a=raw['AIRRPMTSID11']; y=raw['CES7072100001']; f=raw['CES7072200001']
    p=pd.DataFrame(index=raw.index)
    p['accom_yoy_l2']=100*np.log(y.shift(lag_labor)/y.shift(lag_labor+12))
    p['food_yoy_l2']=100*np.log(f.shift(lag_labor)/f.shift(lag_labor+12))
    p['accom_mom3_l2']=100*np.log(y.shift(lag_labor)/y.shift(lag_labor+3))
    p['air_yoy_l4']=100*np.log(a.shift(lag_air)/a.shift(lag_air+12))
    p['accom_signal']=np.tanh(p['accom_yoy_l2']/20.0)
    p['food_signal']=np.tanh(p['food_yoy_l2']/20.0)
    p['accom_mom_signal']=np.tanh(p['accom_mom3_l2']/10.0)
    p['travel_gap']=np.tanh((weight*p['air_yoy_l4']-(2-weight)*p['food_yoy_l2'])/20.0)
    p['air_signal']=np.tanh(p['air_yoy_l4']/20.0)
    p['target']=100*np.log(y.shift(-h)/y.shift(-h-12))
    p['origin']=p.index
    p=p.replace([np.inf,-np.inf],np.nan).dropna().copy()
    p['origin']=pd.to_datetime(p['origin'])
    return p

def ridge_predict(X,y,x,alpha=10):
    X=np.asarray(X,float);y=np.asarray(y,float);x=np.asarray(x,float)
    mu=X.mean(axis=0);sd=X.std(axis=0);sd=np.where(sd>1e-10,sd,1.0)
    Xs=(X-mu)/sd;xs=(x-mu)/sd
    ym=y.mean();coef=np.linalg.solve(Xs.T@Xs+alpha*np.eye(Xs.shape[1]),Xs.T@(y-ym))
    return float(ym+xs@coef)

def walk_forward(panel,h=3,min_train=36,full_cols=None,controls=None):
    controls=CONTROL if controls is None else controls
    full_cols=controls+['travel_gap'] if full_cols is None else full_cols
    dates=panel['origin'].to_numpy(dtype='datetime64[ns]')
    actual=panel['target'].to_numpy(dtype=float)
    xc=panel[controls].to_numpy(dtype=float)
    xf=panel[full_cols].to_numpy(dtype=float)
    persist=panel['accom_yoy_l2'].to_numpy(dtype=float)
    rows=[]
    for i in range(len(panel)):
        t=pd.Timestamp(dates[i]);cutoff=np.datetime64(t-pd.DateOffset(months=h+2))
        n=np.searchsorted(dates,cutoff,side='right')
        if n<min_train:continue
        yy=actual[:n]
        rows.append((dates[i],actual[i],n,float(yy.mean()),persist[i],
                     ridge_predict(xc[:n],yy,xc[i]),ridge_predict(xf[:n],yy,xf[i])))
    if not rows:return pd.DataFrame(columns=['origin','actual','n_train','mean','persistence','controls','full'])
    return pd.DataFrame(rows,columns=['origin','actual','n_train','mean','persistence','controls','full']).set_index('origin')

def score(oos):
    actual=oos.actual.to_numpy()
    return {name:{'rmse':float(np.sqrt(np.mean((actual-oos[name].to_numpy())**2))),
                  'mae':float(np.mean(np.abs(actual-oos[name].to_numpy())))}
            for name in ('mean','persistence','controls','full')}

def block_bootstrap(oos,n=2000,block=12,seed=SEED):
    rng=np.random.default_rng(seed);N=len(oos);a=oos.actual.to_numpy();b=oos.controls.to_numpy();c=oos.full.to_numpy()
    deltas=[]
    for _ in range(n):
        indices=[]
        while len(indices)<N:
            s=int(rng.integers(0,N));indices.extend((np.arange(s,s+block)%N).tolist())
        ix=np.asarray(indices[:N]);deltas.append(float(np.sqrt(np.mean((a[ix]-b[ix])**2))-np.sqrt(np.mean((a[ix]-c[ix])**2))))
    return np.asarray(deltas)

def block_shuffle_placebo(panel,n=1000,h=3,block=12,seed=SEED):
    rng=np.random.default_rng(seed);base=panel['travel_gap'].to_numpy();N=len(base)
    blocks=[base[i:i+block] for i in range(0,N,block)]
    out=[]
    for _ in range(n):
        perm=rng.permutation(len(blocks));mixed=np.concatenate([blocks[int(i)] for i in perm])
        # Different final-block lengths can alter N only if each block is concatenated: always same N.
        p=panel.copy();p['travel_gap']=mixed
        o=walk_forward(p,h=h)
        m=score(o)
        out.append(m['controls']['rmse']-m['full']['rmse'])
    return np.asarray(out)

def exposure_sensitivity(panel,n=1000,h=3,seed=SEED):
    rng=np.random.default_rng(seed);rows=[]
    for w in rng.uniform(.75,1.25,n):
        p=panel.copy();p['travel_gap']=np.tanh((w*p.air_yoy_l4-(2-w)*p.food_yoy_l2)/20)
        o=walk_forward(p,h=h);s=score(o)
        rows.append({'air_weight':w,'delta_rmse':s['controls']['rmse']-s['full']['rmse']})
    return pd.DataFrame(rows)

def robustness(raw,main_oos):
    cases={}
    for h in (1,6):
        p=panel_from(raw,h=h);o=walk_forward(p,h=h)
        if len(o):cases[f'horizon_{h}m']={'n':len(o),'scores':score(o)}
    for lag in (5,6):
        p=panel_from(raw,lag_air=lag);o=walk_forward(p)
        cases[f'air_release_lag_{lag}m']={'n':len(o),'scores':score(o)}
    p=panel_from(raw);o=walk_forward(p,full_cols=CONTROL+['air_signal'])
    cases['air_yoy_only_ablation']={'n':len(o),'scores':score(o)}
    p['travel_gap']=p.travel_gap.shift(12)
    p=p.dropna();o=walk_forward(p)
    cases['stale_12m_gap_negative_control']={'n':len(o),'scores':score(o)}
    for name,subset in [('pre_2020',main_oos.loc[main_oos.index<'2020-03-01']),
                        ('pandemic_2020_2022',main_oos.loc[(main_oos.index>='2020-03-01')&(main_oos.index<'2023-01-01')]),
                        ('post_2022',main_oos.loc[main_oos.index>='2023-01-01'])]:
        cases[name]={'n':len(subset),'scores':score(subset) if len(subset)>0 else None}
    lo=[]
    for year in sorted(main_oos.index.year.unique()):
        subset=main_oos.loc[main_oos.index.year!=year]
        s=score(subset)
        lo.append({'excluded_year':int(year),'n':len(subset),'delta_rmse':s['controls']['rmse']-s['full']['rmse']})
    return cases,pd.DataFrame(lo)

def figures(raw,panel,oos,placebo,boot,weights,robust,root=ROOT):
    folder=root/'figures';folder.mkdir(exist_ok=True)
    def save(name):plt.tight_layout();plt.savefig(folder/name,dpi=125);plt.close()
    ax=raw[['AIRRPMTSID11']].plot(figsize=(10,3),title='BTS air revenue passenger miles (SA, latest-revised)');ax.set_ylabel('Thousands of passenger-miles');save('01_air_passenger_miles.png')
    ax=raw[['CES7072100001','CES7072200001']].plot(figsize=(10,3),title='BLS accommodation vs restaurant payroll (different scales)');ax.set_ylabel('Thousands of employees');save('02_hospitality_employment.png')
    ax=panel[['travel_gap']].plot(figsize=(10,3),title='Predefined air–restaurant demand divergence factor');ax.axhline(0,color='black',lw=.7);save('03_travel_gap_factor.png')
    ax=oos[['actual','persistence','controls','full']].plot(figsize=(11,4),title='Purged OOS: accommodation YoY target and predictions');ax.set_ylabel('Log YoY (%)');save('04_oos_forecasts.png')
    scores=score(oos);fig,ax=plt.subplots(figsize=(7,3));ax.bar(list(scores),[v['rmse'] for v in scores.values()]);ax.set_title('Same-origin OOS RMSE (percentage points)');save('05_baseline_scorecard.png')
    d=(oos.actual-oos.controls)**2-(oos.actual-oos.full)**2
    fig,ax=plt.subplots(figsize=(10,3));ax.plot(d.index,d.cumsum());ax.axhline(0,color='black',lw=.8);ax.set_title('Cumulative squared-error improvement: controls minus factor');save('06_cumulative_loss.png')
    fig,ax=plt.subplots(figsize=(8,3));ax.hist(placebo,bins=35,alpha=.8);ax.axvline(scores['controls']['rmse']-scores['full']['rmse'],color='black',lw=2);ax.set_title('Exploratory 12-month block-shuffle null');save('07_block_placebo.png')
    fig,ax=plt.subplots(figsize=(8,3));ax.scatter(weights.air_weight,weights.delta_rmse,s=5,alpha=.25);ax.axhline(0,color='black',lw=.8);ax.set_title('Air-exposure weight sensitivity');save('08_exposure_sensitivity.png')
    fig,ax=plt.subplots(figsize=(8,3));ax.hist(boot,bins=40);ax.axvline(0,color='black',lw=.8);ax.set_title('Moving-block bootstrap: control minus full RMSE');save('09_bootstrap_uncertainty.png')

def run(write=True,permutations=1000,bootstraps=2000,sensitivities=1000):
    raw=read_data();panel=panel_from(raw);oos=walk_forward(panel);assert len(oos)>25
    scores=score(oos);delta=scores['controls']['rmse']-scores['full']['rmse']
    placebo=block_shuffle_placebo(panel,n=permutations)
    boot=block_bootstrap(oos,n=bootstraps)
    weights=exposure_sensitivity(panel,n=sensitivities)
    robust,loyo=robustness(raw,oos)
    report={'industry':'U.S. accommodation / travel hospitality','evidence':'retrospective revised-snapshot macro forecast only',
       'raw_rows':len(raw),'raw_range':[str(raw.index.min().date()),str(raw.index.max().date())],
       'panel_rows':len(panel),'oos_n':len(oos),'oos_start':str(oos.index.min().date()),'oos_end':str(oos.index.max().date()),
       'scores':scores,'delta_rmse_controls_minus_full':delta,
       'block_shuffle_draws':len(placebo),'block_shuffle_exploratory_upper_tail':float((1+(placebo>=delta).sum())/(1+len(placebo))),
       'block_bootstrap_draws':len(boot),'block_bootstrap_ci95':np.quantile(boot,[.025,.975]).tolist(),
       'exposure_draws':len(weights),'exposure_positive_share':float((weights.delta_rmse>0).mean()),
       'robustness':robust,'leave_one_year_out':loyo.to_dict('records'),
       'PIT':False,'equity_alpha_established':False,
       'source_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest()}
    if write:
        (ROOT/'results').mkdir(exist_ok=True)
        panel.drop(columns='origin').to_csv(ROOT/'data'/'derived_formation_panel.csv',float_format='%.9g')
        oos.to_csv(ROOT/'results'/'walk_forward_oos.csv',float_format='%.9g')
        pd.DataFrame(scores).T.to_csv(ROOT/'results'/'scorecard.csv',float_format='%.9g')
        pd.DataFrame({'null_delta_rmse':placebo}).to_csv(ROOT/'results'/'block_placebo_null.csv',index=False)
        pd.DataFrame({'bootstrap_delta_rmse':boot}).to_csv(ROOT/'results'/'bootstrap_deltas.csv',index=False)
        weights.to_csv(ROOT/'results'/'exposure_sensitivity.csv',index=False)
        loyo.to_csv(ROOT/'results'/'leave_one_year_out.csv',index=False)
        (ROOT/'results'/'metrics.json').write_text(json.dumps(report,indent=2,allow_nan=False))
        figures(raw,panel,oos,placebo,boot,weights,robust)
        (ROOT/'results'/'run_log.txt').write_text('Executed analysis; all requested calculations completed without exception.\n'+json.dumps({k:report[k] for k in ('oos_n','scores','delta_rmse_controls_minus_full','block_shuffle_exploratory_upper_tail','block_bootstrap_ci95')},indent=2))
    return report,raw,panel,oos,placebo,boot,weights

if __name__=='__main__':
    report,*_=run()
    print(json.dumps({k:report[k] for k in ('raw_rows','panel_rows','oos_n','scores','delta_rmse_controls_minus_full','block_shuffle_exploratory_upper_tail','block_bootstrap_ci95','exposure_positive_share')},indent=2))
