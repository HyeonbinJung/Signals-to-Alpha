"""Reproducible fixed-snapshot macro lead test; NOT a point-in-time equity-alpha test."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RAW = ROOT/'data/frozen_observations_2026-10-26.csv'
HORIZON=6
TARGET_RELEASE_BUFFER=1
AIR_LAG=4
IP_LAG=2
MIN_TRAIN=48
RIDGE_ALPHA=10.0
SEED=20261026

def load_data():
    d=pd.read_csv(RAW,parse_dates=['date']).sort_values('date').reset_index(drop=True)
    assert len(d)==201 and d.date.is_unique and d.date.iloc[0]==pd.Timestamp('2010-01-01')
    assert (d.date.diff().dropna()==pd.Timedelta(days=31)).sum() < len(d) # calendar-month not day-based
    assert d.aerospace_ip.notna().all() and d.manufacturing_ip.notna().all()
    assert d.AIRRPMTSID11.notna().sum()==150
    assert abs(d.aerospace_ip.iloc[-1]-99.2876)<1e-9
    return d

def panel(h=HORIZON,air_lag=AIR_LAG,ip_lag=IP_LAG,air_weight=1.,mfg_weight=1.):
    d=load_data()
    for col,short in [('aerospace_ip','aero'),('manufacturing_ip','mfg'),('AIRRPMTSID11','air')]:
        d[short+'_yoy']=100*np.log(d[col]/d[col].shift(12))
    d['aero_mom']=d.aero_yoy.shift(ip_lag)
    d['mfg_mom']=d.mfg_yoy.shift(ip_lag)
    d['air_mom']=d.air_yoy.shift(air_lag)
    # Fixed ex-ante saturation, no future-sample normalization.
    d['air_gap']=30*np.tanh((air_weight*d.air_mom-mfg_weight*d.mfg_mom)/30)
    d['target']=d.aero_yoy.shift(-h)
    d['origin_month']=np.arange(len(d))
    cols=['date','origin_month','aero_mom','mfg_mom','air_mom','air_gap','target']
    return d[cols].dropna().reset_index(drop=True)

def ridge_predict(X,y,x,alpha=RIDGE_ALPHA):
    X=np.asarray(X,float); y=np.asarray(y,float); x=np.asarray(x,float)
    mu=X.mean(axis=0);sd=X.std(axis=0);sd=np.where(sd<1e-9,1,sd)
    Xs=(X-mu)/sd; xs=(x-mu)/sd
    yc=y.mean(); gram=Xs.T@Xs+alpha*np.eye(Xs.shape[1]); beta=np.linalg.solve(gram,Xs.T@(y-yc))
    return float(yc+xs@beta)

def forecast(d,min_train=MIN_TRAIN,h=HORIZON,buffer=TARGET_RELEASE_BUFFER,which='all'):
    origin=d.origin_month.to_numpy(dtype=int); actual=d.target.to_numpy(dtype=float)
    x=d[['aero_mom','mfg_mom','air_gap']].to_numpy(dtype=float)
    dates=d.date.dt.strftime('%Y-%m-%d').to_numpy()
    records=[]
    for i in range(len(d)):
        # Sorted formation months: purge any target that would not yet have been released.
        n=int(np.searchsorted(origin,origin[i]-h-buffer,side='right'))
        if n<min_train:continue
        yy=actual[:n]; xx=x[:n]; xi=x[i]
        pred={'mean':float(yy.mean()),'persistence':float(xi[0])}
        for name,idx in [('macro',[0,1]),('full',[0,1,2]),('air_only',[2]),('no_mfg',[0,2])]:
            if which!='all' and name not in ['macro',which]:continue
            pred[name]=ridge_predict(xx[:,idx],yy,xi[idx])
        records.append({'date':dates[i],'origin_month':int(origin[i]),'actual':float(actual[i]),'n_train':n,**pred})
    return pd.DataFrame.from_records(records)

def rmse(y,p):return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(p))**2)))
def mae(y,p):return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))
def scorecard(o):
    names=[x for x in ['mean','persistence','macro','full','air_only','no_mfg'] if x in o]
    return pd.DataFrame([{'model':x,'n':len(o),'rmse_pp':rmse(o.actual,o[x]),'mae_pp':mae(o.actual,o[x]),'pearson_ic':float(pd.Series(o.actual).corr(o[x]))} for x in names])

def shuffle_block(x,rng,block=12):
    blocks=[x[i:i+block] for i in range(0,len(x),block)]
    idx=rng.permutation(len(blocks))
    return np.concatenate([blocks[i] for i in idx])

def placebo(d,n=1000,seed=SEED):
    rng=np.random.default_rng(seed); base=forecast(d);base_delta=rmse(base.actual,base.macro)-rmse(base.actual,base.full)
    arr=d.air_gap.to_numpy(); out=[]
    for k in range(n):
        dd=d.copy();dd['air_gap']=shuffle_block(arr,rng)
        o=forecast(dd,which='full')
        assert len(o)==len(base)
        out.append({'draw':k,'delta_rmse_pp':rmse(o.actual,o.macro)-rmse(o.actual,o.full)})
    return pd.DataFrame(out),base_delta

def circular_block_bootstrap(o,n=2000,block=12,seed=SEED+1):
    rng=np.random.default_rng(seed); N=len(o);nblocks=int(np.ceil(N/block)); rows=[]
    for k in range(n):
        starts=rng.integers(0,N,nblocks)
        ix=np.concatenate([(np.arange(s,s+block)%N) for s in starts])[:N]
        s=o.iloc[ix]
        rows.append({'draw':k,'delta_macro_full':rmse(s.actual,s.macro)-rmse(s.actual,s.full),'delta_mean_full':rmse(s.actual,s['mean'])-rmse(s.actual,s.full)})
    return pd.DataFrame(rows)

def perturb(n=1000,seed=SEED+2):
    rng=np.random.default_rng(seed);rows=[]
    base=panel();air=base.air_mom.to_numpy();mfg=base.mfg_mom.to_numpy()
    for k in range(n):
        wa=float(rng.uniform(.8,1.2));wm=float(rng.uniform(.8,1.2))
        d=base.copy();d['air_gap']=30*np.tanh((wa*air-wm*mfg)/30)
        o=forecast(d,which='full')
        rows.append({'draw':k,'w_air':wa,'w_mfg':wm,'delta_macro_full':rmse(o.actual,o.macro)-rmse(o.actual,o.full)})
    return pd.DataFrame(rows)

def robustness(base):
    rows=[]
    for label,h,al,il in [('3-month',3,4,2),('12-month',12,4,2),('air lag 6m',6,6,2),('ip lag 3m',6,4,3)]:
        o=forecast(panel(h=h,air_lag=al,ip_lag=il),h=h)
        if len(o):rows.append({'test':label,'n':len(o),'macro_minus_full_rmse_pp':rmse(o.actual,o.macro)-rmse(o.actual,o.full),'mean_minus_full_rmse_pp':rmse(o.actual,o['mean'])-rmse(o.actual,o.full)})
    for label,mask in [('pre-2020',base.date<'2020-01-01'),('pandemic-2020-2021',base.date.between('2020-01-01','2021-12-01')),('post-2021',base.date>'2021-12-01'),('exclude-2020-2021',~base.date.between('2020-01-01','2021-12-01'))]:
        o=base[mask];rows.append({'test':label,'n':len(o),'macro_minus_full_rmse_pp':rmse(o.actual,o.macro)-rmse(o.actual,o.full),'mean_minus_full_rmse_pp':rmse(o.actual,o['mean'])-rmse(o.actual,o.full)})
    return pd.DataFrame(rows)

def plot(d,o,sc,p,b,ex,rob):
    plt.rcParams.update({'font.size':9,'figure.dpi':115})
    figs=ROOT/'figures';figs.mkdir(exist_ok=True)
    def save(name):plt.tight_layout();plt.savefig(figs/name,bbox_inches='tight');plt.close()
    raw=load_data();fig,ax=plt.subplots(figsize=(8,3.3));ax.plot(raw.date,raw.aerospace_ip,label='Aerospace IP');ax.plot(raw.date,raw.manufacturing_ip,label='Manufacturing IP',alpha=.8);ax.set_ylabel('2017=100');ax.legend();ax.set_title('01 · Industrial production, revised snapshot');save('01_industry_levels.png')
    fig,ax=plt.subplots(figsize=(8,3.3));ax.plot(d.date,d.air_mom,label='Air passenger YoY (lagged)');ax.plot(d.date,d.mfg_mom,label='Manufacturing YoY (lagged)');ax.axhline(0,color='gray',lw=.5);ax.legend();ax.set_ylabel('Log change, %');ax.set_title('02 · Formation-date inputs');save('02_input_growth.png')
    fig,ax=plt.subplots(figsize=(8,3.3));ax.plot(d.date,d.air_gap,label='Fixed tanh air-demand gap');ax.axhline(0,color='gray',lw=.5);ax.set_ylabel('Bounded signal, pp');ax.set_title('03 · Predefined factor');save('03_factor.png')
    fig,ax=plt.subplots(figsize=(8,3.3));ax.plot(o.date,o.actual,label='Realized aerospace YoY',lw=1.5);ax.plot(o.date,o.macro,label='Macro control',alpha=.8);ax.plot(o.date,o.full,label='With air factor',alpha=.8);ax.legend();ax.set_title('04 · Purged expanding-window forecasts');save('04_oos_forecasts.png')
    fig,ax=plt.subplots(figsize=(7,3.2));ax.bar(sc.model,sc.rmse_pp);ax.tick_params(axis='x',rotation=20);ax.set_ylabel('RMSE (percentage points)');ax.set_title('05 · Baseline scorecard');save('05_scorecard.png')
    fig,ax=plt.subplots(figsize=(8,3.2));ax.plot(o.date,np.cumsum((o.actual-o.macro)**2-(o.actual-o.full)**2));ax.axhline(0,color='gray',lw=.5);ax.set_title('06 · Cumulative paired squared-loss gain');ax.set_ylabel('Macro loss − full loss');save('06_loss_gain.png')
    fig,ax=plt.subplots(figsize=(7,3.2));ax.hist(p.delta_rmse_pp,bins=35,alpha=.75);ax.axvline(rmse(o.actual,o.macro)-rmse(o.actual,o.full),color='black',lw=2,label='Observed');ax.legend();ax.set_title('07 · Exploratory 12-month block-shuffle placebo');save('07_block_placebo.png')
    fig,ax=plt.subplots(figsize=(7,3.2));ax.hist(b.delta_macro_full,bins=35);ax.axvline(0,color='black',lw=1);ax.set_title('08 · Paired circular-block bootstrap');save('08_bootstrap.png')
    fig,ax=plt.subplots(figsize=(7,3.2));ax.scatter(ex.w_air,ex.delta_macro_full,s=5,alpha=.35,label='Perturbations');ax.axhline(0,color='black',lw=.8);ax.set_xlabel('Air-demand weight');ax.set_ylabel('Macro RMSE − full RMSE');ax.set_title('09 · Exposure-formula perturbations');save('09_exposure.png')
    fig,ax=plt.subplots(figsize=(8,3.3));ax.barh(rob.test,rob.macro_minus_full_rmse_pp);ax.axvline(0,color='black',lw=.8);ax.set_title('10 · Horizon, lag, and regime sensitivity');save('10_robustness.png')

def run(heavy=True):
    (ROOT/'results').mkdir(exist_ok=True)
    d=panel();o=forecast(d);sc=scorecard(o)
    assert len(o)>=45 and o.n_train.min()>=MIN_TRAIN and o.date.is_unique
    d.to_csv(ROOT/'data/derived_formation_panel.csv',index=False)
    o.to_csv(ROOT/'results/walk_forward_oos.csv',index=False);sc.to_csv(ROOT/'results/scorecard.csv',index=False)
    p,delta=placebo(d,n=1000 if heavy else 20);b=circular_block_bootstrap(o,n=2000 if heavy else 40);ex=perturb(n=1000 if heavy else 20);rob=robustness(o)
    p.to_csv(ROOT/'results/block_placebo_1000.csv',index=False);b.to_csv(ROOT/'results/bootstrap_2000.csv',index=False);ex.to_csv(ROOT/'results/exposure_1000.csv',index=False);rob.to_csv(ROOT/'results/robustness.csv',index=False)
    loo=[]
    for year in sorted(pd.to_datetime(o.date).dt.year.unique()):
        s=o[pd.to_datetime(o.date).dt.year!=year]
        loo.append({'excluded_year':int(year),'n':len(s),'delta_macro_full':rmse(s.actual,s.macro)-rmse(s.actual,s.full)})
    pd.DataFrame(loo).to_csv(ROOT/'results/leave_one_year_out.csv',index=False)
    plot(d,o,sc,p,b,ex,rob)
    metrics={'status':'REPRODUCED MACRO PILOT / NOT PIT','raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),'n_raw_months':201,'n_air_months':150,'n_formation':len(d),'n_oos':len(o),'oos_first':o.date.iloc[0],'oos_last':o.date.iloc[-1],'train_min':int(o.n_train.min()),'train_max':int(o.n_train.max()),'horizon_months':HORIZON,'target_release_buffer_months':TARGET_RELEASE_BUFFER,'signal_lag_months':AIR_LAG,'ip_lag_months':IP_LAG,'rmse':dict(zip(sc.model,sc.rmse_pp)),'mae':dict(zip(sc.model,sc.mae_pp)),'delta_macro_full_rmse_pp':delta,'block_placebo_draws':len(p),'block_placebo_tail_fraction':float((p.delta_rmse_pp>=delta).mean()),'bootstrap_draws':len(b),'bootstrap_delta_macro_full_ci95':np.quantile(b.delta_macro_full,[.025,.975]).tolist(),'exposure_draws':len(ex),'exposure_positive_fraction':float((ex.delta_macro_full>0).mean()),'company_fundamentals_tested':False,'total_returns_tested':False,'historical_pit_vintages_verified':False,'exploratory_tests_not_exact_pvalues':True}
    (ROOT/'results/metrics.json').write_text(json.dumps(metrics,indent=2))
    return metrics
if __name__=='__main__':
    m=run();print(json.dumps(m,indent=2))
