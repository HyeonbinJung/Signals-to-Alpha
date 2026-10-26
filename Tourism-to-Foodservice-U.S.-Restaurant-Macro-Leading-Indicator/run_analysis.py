"""Tourism-to-foodservice lead indicator; retrospective fixed-revision snapshot ONLY.

All predictors are lagged by explicit assumed release buffers; this is NOT
historical point-in-time because underlying BTS/BLS observations are revised.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'data/bts_bls_snapshot_2026-10-26.csv'
SEED=20261026
AIR='AIRRPMTSID11'; HOTEL='CES7072100001'; FOOD='CES7072200001'


def load_raw():
    df=pd.read_csv(RAW,parse_dates=['date']).set_index('date').sort_index()
    assert len(df)==153 and df.index.min()==pd.Timestamp('2014-01-01') and df.index.max()==pd.Timestamp('2026-09-01')
    assert df.index.is_unique and df.index.equals(pd.date_range(df.index.min(),df.index.max(),freq='MS'))
    assert df[FOOD].notna().all() and df[HOTEL].notna().all() and df[AIR].notna().sum()==150
    assert df[[FOOD,HOTEL]].gt(0).all().all() and df[AIR].dropna().gt(0).all()
    return df


def growth(df, col, months=12):
    return 100*(df[col]/df[col].shift(months)-1)


def build_panel(raw,horizon=3,air_lag=4,bls_lag=2,wa=1.0,wh=1.0):
    # Formation month t: 4m-old BTS and 2m-old BLS observations.
    air_yoy=growth(raw,AIR).shift(air_lag)
    hotel_yoy=growth(raw,HOTEL).shift(bls_lag)
    food_yoy=growth(raw,FOOD).shift(bls_lag)
    food_mom3=growth(raw,FOOD,3).shift(bls_lag)
    panel=pd.DataFrame(index=raw.index)
    panel['air_yoy_lag']=air_yoy
    panel['hotel_yoy_lag']=hotel_yoy
    panel['food_yoy_lag']=food_yoy
    panel['food_mom3_lag']=food_mom3
    panel['air_signal']=np.tanh(air_yoy/20)
    panel['hotel_signal']=np.tanh(hotel_yoy/20)
    panel['tourism_gap']=wa*panel['air_signal']-wh*panel['hotel_signal']
    # Target is year-over-year foodservice employment at t+h (not a return).
    panel['target']=growth(raw,FOOD).shift(-horizon)
    return panel.dropna().copy()


def ridge_predict(X,y,x0,alpha=10.0):
    X=np.asarray(X,float);y=np.asarray(y,float);x0=np.asarray(x0,float)
    mu=X.mean(axis=0);scale=X.std(axis=0);scale[scale<1e-8]=1
    Z=(X-mu)/scale;z0=(x0-mu)/scale
    ymu=y.mean();yc=y-ymu
    # Intercept not penalized; fixed ridge strength, no tuning on OOS.
    beta=np.linalg.solve(Z.T@Z+alpha*np.eye(Z.shape[1]),Z.T@yc)
    return float(ymu+z0@beta)


def walkforward(panel,horizon=3,min_train=48,eval_start='2019-01-01',eval_end='2025-06-01',label_lag=2):
    features={
      'mean':[], 'persistence':['food_yoy_lag'],
      'controls':['food_yoy_lag','food_mom3_lag','hotel_yoy_lag'],
      'full':['food_yoy_lag','food_mom3_lag','hotel_yoy_lag','tourism_gap'],
      'factor_only':['tourism_gap']}
    # Pre-extract arrays: avoids repeated DataFrame copies in 1000-draw refits.
    dates=panel.index.to_numpy(dtype='datetime64[ns]');y=panel['target'].to_numpy()
    matrices={k:panel[v].to_numpy() if v else None for k,v in features.items()}
    out=[]
    for i,date in enumerate(panel.index):
        if not(pd.Timestamp(eval_start)<=date<=pd.Timestamp(eval_end)):continue
        cut=np.datetime64(date-pd.DateOffset(months=horizon+label_lag))
        n=int(np.searchsorted(dates,cut,side='right'))
        if n<min_train:continue
        pred={'date':date,'actual':float(y[i]),'n_train':n,'last_train_origin':str(panel.index[n-1].date())}
        for key,X in matrices.items():
            pred[key]=(float(y[:n].mean()) if X is None else ridge_predict(X[:n],y[:n],X[i]))
        out.append(pred)
    return pd.DataFrame(out)


def score(oos):
    a=oos['actual'].to_numpy()
    return {k:{'rmse':float(np.sqrt(np.mean((oos[k].to_numpy()-a)**2))),
               'mae':float(np.mean(np.abs(oos[k].to_numpy()-a))),
               'n':len(oos)}
            for k in ['mean','persistence','controls','full','factor_only']}


def gap(oos):return score(oos)['controls']['rmse']-score(oos)['full']['rmse']


def block_shuffle(panel,rng,block=12):
    # Permutes nonoverlapping 12-month signal blocks, preserving within-block
    # serial structure; this is exploratory, not an exact exchangeable null.
    p=panel.copy();v=p['tourism_gap'].to_numpy();blocks=[v[i:i+block] for i in range(0,len(v),block)]
    order=rng.permutation(len(blocks))
    p['tourism_gap']=np.concatenate([blocks[i] for i in order])
    return p


def block_bootstrap(oos,n=2000,block=12,seed=SEED):
    rng=np.random.default_rng(seed);a=oos['actual'].to_numpy()
    c=oos['controls'].to_numpy();f=oos['full'].to_numpy();m=len(oos)
    vals=[]
    for _ in range(n):
        ids=[]
        while len(ids)<m:
            start=int(rng.integers(0,m))
            ids.extend((start+np.arange(block))%m)
        ix=np.asarray(ids[:m],int)
        vals.append(float(np.sqrt(np.mean((c[ix]-a[ix])**2))-np.sqrt(np.mean((f[ix]-a[ix])**2))))
    return np.array(vals)


def robust_variant(raw,**kwargs):
    horizon=kwargs.pop('horizon',3)
    panel=build_panel(raw,horizon=horizon,**kwargs)
    oos=walkforward(panel,horizon=horizon)
    return {'n':len(oos),'scores':score(oos),'delta_controls_minus_full':gap(oos)}


def plot_results(raw,panel,oos,scorecard,placebo,boot,sensitivity):
    plt.rcParams.update({'figure.figsize':(9,4.3),'font.size':10})
    figs=ROOT/'figures';figs.mkdir(exist_ok=True)
    def save(name):plt.tight_layout();plt.savefig(figs/name,dpi=110);plt.close()
    raw[[AIR]].plot(title='BTS seasonally adjusted revenue passenger miles (thousands)');plt.ylabel('Thousands');save('01_air_traffic.png')
    raw[[HOTEL,FOOD]].plot(title='BLS sector employment (thousands, SA)');plt.ylabel('Thousands of workers');save('02_sector_employment.png')
    panel[['air_signal','hotel_signal','tourism_gap']].plot(title='Lagged, fixed-scale tourism gap and components');plt.axhline(0,color='grey',lw=.6);save('03_signal_components.png')
    d=oos.set_index('date');d[['actual','mean','controls','full']].plot(title='Purged OOS: 3m-ahead foodservice employment YoY');plt.ylabel('Percent');save('04_oos_predictions.png')
    scorecard.set_index('model')['rmse'].plot(kind='bar',title='Identical-origin OOS RMSE');plt.ylabel('Percentage points');save('05_baselines.png')
    a=oos.actual.to_numpy();dif=(oos.controls.to_numpy()-a)**2-(oos.full.to_numpy()-a)**2
    plt.plot(oos.date,np.cumsum(dif));plt.axhline(0,color='grey',lw=.6);plt.title('Cumulative squared-error advantage: controls minus full');plt.ylabel('Cumulative pp²');save('06_loss_difference.png')
    plt.hist(placebo,bins=35,alpha=.75);plt.axvline(gap(oos),color='red',ls='--',label='Observed');plt.legend();plt.title('12-month block-shuffle null (exploratory)');plt.xlabel('Control-minus-full RMSE (pp)');save('07_block_shuffle.png')
    plt.hist(boot,bins=40,alpha=.75);plt.axvline(0,color='red',ls='--');plt.title('Moving-block bootstrap paired RMSE difference');plt.xlabel('Control-minus-full RMSE (pp)');save('08_bootstrap.png')
    plt.scatter(sensitivity[:,0],sensitivity[:,2],s=5,alpha=.25,label='Air weight');plt.axhline(0,color='red',ls='--');plt.title('Exposure perturbation: air weight vs OOS gain');plt.xlabel('Air weight');plt.ylabel('Control-minus-full RMSE (pp)');save('09_exposure_perturbation.png')


def main(n_placebo=1000,n_bootstrap=2000,n_exposure=1000):
    raw=load_raw();panel=build_panel(raw);oos=walkforward(panel)
    if len(oos)<30:raise RuntimeError('Insufficient OOS origins')
    rng=np.random.default_rng(SEED)
    placebo=[]
    for _ in range(n_placebo):
        alt=walkforward(block_shuffle(panel,rng))
        placebo.append(gap(alt))
    placebo=np.asarray(placebo)
    boot=block_bootstrap(oos,n_bootstrap)
    sensitivity=[]
    for _ in range(n_exposure):
        wa,wh=rng.uniform(.7,1.3,size=2)
        alt=walkforward(build_panel(raw,wa=wa,wh=wh))
        sensitivity.append([wa,wh,gap(alt)])
    sensitivity=np.asarray(sensitivity)
    robust={
      'horizon_1m':robust_variant(raw,horizon=1),
      'horizon_6m':robust_variant(raw,horizon=6),
      'air_release_lag_5m':robust_variant(raw,air_lag=5),
      'air_release_lag_6m':robust_variant(raw,air_lag=6),
      'bls_release_lag_3m':robust_variant(raw,bls_lag=3),
    }
    leave_year=[]
    for yr in sorted(oos.date.dt.year.unique()):
        subset=oos[oos.date.dt.year!=yr]
        leave_year.append({'excluded_year':int(yr),'n':len(subset),'delta_rmse':gap(subset)})
    regimes={}
    for label,mask in [('pre_2020',oos.date<'2020-01-01'),('pandemic_2020_2022',(oos.date>='2020-01-01')&(oos.date<'2023-01-01')),('post_2022',oos.date>='2023-01-01'),('excluding_2020',oos.date.dt.year!=2020)]:
        s=oos[mask];regimes[label]={'n':len(s),'delta_rmse':gap(s) if len(s)>0 else None,'scores':score(s) if len(s)>0 else None}
    scores=score(oos)
    sc=pd.DataFrame([{'model':k,**v} for k,v in scores.items()])
    results=ROOT/'results';results.mkdir(exist_ok=True)
    panel.reset_index().to_csv(ROOT/'data/derived_formation_panel.csv',index=False)
    oos.to_csv(results/'walk_forward_oos.csv',index=False)
    sc.to_csv(results/'scorecard.csv',index=False)
    pd.DataFrame({'control_minus_full_rmse':placebo}).to_csv(results/'block_shuffle_1000.csv',index=False)
    pd.DataFrame({'control_minus_full_rmse':boot}).to_csv(results/'bootstrap_2000.csv',index=False)
    pd.DataFrame(sensitivity,columns=['air_weight','hotel_weight','delta_rmse']).to_csv(results/'exposure_1000.csv',index=False)
    pd.DataFrame(leave_year).to_csv(results/'leave_one_year_out.csv',index=False)
    pd.DataFrame([{'experiment':k,'n':v['n'],'delta_rmse':v['delta_controls_minus_full']} for k,v in robust.items()]).to_csv(results/'robustness.csv',index=False)
    plot_results(raw,panel,oos,sc,placebo,boot,sensitivity)
    observed=gap(oos)
    metrics={'industry':'U.S. food services and drinking places (NAICS 722)',
      'claim':'retrospective fixed-revision macro forecast; NOT PIT or equity alpha',
      'raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
      'raw_rows':len(raw),'raw_range':[str(raw.index.min().date()),str(raw.index.max().date())],
      'panel_rows':len(panel),'oos_n':len(oos),'oos_range':[str(oos.date.min().date()),str(oos.date.max().date())],
      'scores':scores,'delta_controls_minus_full':observed,
      'placebo_draws':n_placebo,'placebo_exploratory_upper_tail':float((1+(placebo>=observed).sum())/(n_placebo+1)),
      'bootstrap_draws':n_bootstrap,'bootstrap_ci95':np.quantile(boot,[.025,.975]).tolist(),
      'exposure_draws':n_exposure,'exposure_positive_fraction':float((sensitivity[:,2]>0).mean()),
      'robustness':robust,'regimes':regimes,'leave_one_year_out':leave_year,
      'effective_sample_warning':'Overlapping 3-month-ahead YoY targets and monthly origins; nominal N overstates independence',
      'data_vintage':'Single manually transcribed latest-revised 2026-10-26 snapshot; release buffers assumptions, NOT PIT',
      'fundamentals_tested':False,'equity_returns_tested':False}
    (results/'metrics.json').write_text(json.dumps(metrics,indent=2,allow_nan=False))
    (results/'execution.log').write_text(f"Analysis executed with seed {SEED}; raw rows {len(raw)}; OOS {len(oos)}; placebo {n_placebo}; bootstrap {n_bootstrap}; exposure {n_exposure}; full RMSE {scores['full']['rmse']:.6f}; control RMSE {scores['controls']['rmse']:.6f}\n")
    print(json.dumps({k:metrics[k] for k in ['oos_n','scores','delta_controls_minus_full','placebo_exploratory_upper_tail','bootstrap_ci95','exposure_positive_fraction']},indent=2))
    return metrics

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--placebo',type=int,default=1000);parser.add_argument('--bootstrap',type=int,default=2000);parser.add_argument('--exposure',type=int,default=1000)
    a=parser.parse_args();main(a.placebo,a.bootstrap,a.exposure)
