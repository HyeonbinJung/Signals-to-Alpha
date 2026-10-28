#!/usr/bin/env python3
"""U.S. communications-equipment production macro lead-factor falsification.
Frozen historical G.17 snapshot; NOT a point-in-time trading strategy.
"""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'data/raw_g17_inherited_2026-10-19.csv'
EXPECTED_GIT_BLOB='3d111120b93de0a5eb153d794772225f5dd1a6c4'
SEED=20261028
HORIZON=3
LAG=2
MIN_TRAIN=48
ALPHA=10.0

def git_blob_sha(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()

def load_raw()->pd.DataFrame:
    assert git_blob_sha(RAW.read_bytes())==EXPECTED_GIT_BLOB,'Inherited source bytes do not match GitHub upstream blob'
    df=pd.read_csv(RAW,parse_dates=['date']).sort_values('date').reset_index(drop=True)
    assert len(df)==189 and df.date.iloc[0]==pd.Timestamp('2011-01-01') and df.date.iloc[-1]==pd.Timestamp('2026-09-01')
    assert df.date.is_unique and (df.date.dt.to_period('M').diff().dropna().apply(lambda v:v.n)==1).all()
    assert df.drop(columns='date').notna().all().all() and (df.drop(columns='date')>0).all().all()
    assert len(df.columns)==5
    return df

def build_panel(df:pd.DataFrame,lag:int=LAG,horizon:int=HORIZON,weight:float=1.0)->pd.DataFrame:
    """Every X(t) uses G.17 observation at t-lag, y(t)=g_comm(t+horizon).
    weight 1.0 is predeclared sem-only; sensitivity 0.8-1.0 mixes computer output.
    """
    assert lag>=1 and horizon>=1 and 0<=weight<=1
    p=pd.DataFrame({'date':df.date})
    for col,nm in [('IPG3344S','sem'),('IPG3341S','computer'),('IPG3342S','comm'),('IPMAN','man')]:
        p[nm]=100*np.log(df[col]/df[col].shift(12))
    for nm in ['sem','computer','comm','man']:
        p[nm+'_available']=p[nm].shift(lag)
    p['momentum']=p['comm_available']-p['comm'].shift(lag+3)
    p['factor_raw']=weight*p['sem_available']+(1-weight)*p['computer_available']-p['man_available']
    p['factor']=np.tanh(p['factor_raw']/15.0)
    p['target']=p['comm'].shift(-horizon)
    p['origin_index']=np.arange(len(p))
    return p.dropna(subset=['comm_available','man_available','computer_available','sem_available','momentum','factor','target']).reset_index(drop=True)

def ridge_predict(X:np.ndarray,y:np.ndarray,x:np.ndarray,alpha:float=ALPHA)->float:
    """Train-only standardization, intercept unpenalized, fixed ridge alpha."""
    if X.shape[1]==0:return float(np.mean(y))
    mu=X.mean(axis=0); sd=X.std(axis=0); sd=np.where(sd<1e-9,1.0,sd)
    z=(X-mu)/sd
    ym=y.mean()
    beta=np.linalg.solve(z.T@z+alpha*np.eye(X.shape[1]),z.T@(y-ym))
    return float(ym+((x-mu)/sd)@beta)

def walk_forward(panel:pd.DataFrame,horizon:int=HORIZON,lag:int=LAG,start_origin:int=76,shuffle_factor:np.ndarray|None=None,models:tuple[str,...]=('mean','persistence','momentum','macro','full','factor_only')) ->pd.DataFrame:
    """Purged expanding window, NumPy implementation for reproducible 1,000-refit null."""
    cols=['comm_available','momentum','man_available','computer_available','factor']
    arr=panel[cols].to_numpy(dtype=float).copy()
    if shuffle_factor is not None:arr[:,4]=shuffle_factor
    y=panel.target.to_numpy(dtype=float)
    origins=panel.origin_index.to_numpy(dtype=int)
    spec={'mean':[],'persistence':[0],'momentum':[0,1],'macro':[0,1,2,3],'full':[0,1,2,3,4],'factor_only':[4]}
    out=[]
    for i,t in enumerate(origins):
        if t<start_origin:continue
        n=int(np.searchsorted(origins,t-lag-horizon,side='right'))
        if n<MIN_TRAIN:continue
        item={'date':panel.date.iloc[i],'origin_index':int(t),'target':float(y[i]),'n_train':n,'last_train_origin':int(origins[n-1]),'max_train_label_observation':int(origins[n-1])+horizon,'latest_usable_observation':int(t)-lag}
        for name in models:
            cc=spec[name]
            item[name]=ridge_predict(arr[:n,cc],y[:n],arr[i,cc]) if cc else float(y[:n].mean())
        out.append(item)
    return pd.DataFrame(out)

def rmse(y,p):return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(p))**2)))
def mae(y,p):return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))
def metrics(o:pd.DataFrame)->pd.DataFrame:
    models=['mean','persistence','momentum','macro','full','factor_only']
    return pd.DataFrame([{'model':m,'n':len(o),'rmse_log_pp':rmse(o.target,o[m]),'mae_log_pp':mae(o.target,o[m])} for m in models])

def block_shuffle(x:np.ndarray,rng:np.random.Generator,block:int=12)->np.ndarray:
    # Contiguous source blocks are permuted, preserving within-block order.
    blocks=[x[i:i+block] for i in range(0,len(x),block)]
    return np.concatenate([blocks[j] for j in rng.permutation(len(blocks))])

def block_indices(n:int,rng:np.random.Generator,block:int=12)->np.ndarray:
    starts=rng.integers(0,n,size=math.ceil(n/block))
    return np.concatenate([(s+np.arange(block))%n for s in starts])[:n]

def compute_all(n_placebo:int=1000,n_boot:int=2000,n_exposure:int=1000):
    for p in ['results','figures']:(ROOT/p).mkdir(exist_ok=True)
    raw=load_raw(); panel=build_panel(raw)
    panel.to_csv(ROOT/'data/derived_formation_panel.csv',index=False,float_format='%.10g')
    o=walk_forward(panel)
    assert len(o)>=70 and (o.max_train_label_observation<=o.latest_usable_observation).all()
    o.to_csv(ROOT/'results/walk_forward_oos.csv',index=False,float_format='%.10g')
    score=metrics(o);score.to_csv(ROOT/'results/scorecard.csv',index=False,float_format='%.10g')
    base=float(score.set_index('model').loc['macro','rmse_log_pp']); full=float(score.set_index('model').loc['full','rmse_log_pp'])
    observed=base-full
    rng=np.random.default_rng(SEED)
    placebo=[]
    for b in range(n_placebo):
        shuffled=block_shuffle(panel.factor.to_numpy(),rng)
        z=walk_forward(panel,shuffle_factor=shuffled,models=('full',))
        assert np.array_equal(o.origin_index,z.origin_index)
        placebo.append({'draw':b,'delta_rmse':base-rmse(z.target,z.full)})
    pl=pd.DataFrame(placebo);pl.to_csv(ROOT/'results/block_placebo_1000.csv',index=False,float_format='%.10g')
    rng=np.random.default_rng(SEED+1)
    boot=[]
    for b in range(n_boot):
        idx=block_indices(len(o),rng)
        sub=o.iloc[idx]
        boot.append({'draw':b,'delta_rmse':rmse(sub.target,sub.macro)-rmse(sub.target,sub.full)})
    bs=pd.DataFrame(boot);bs.to_csv(ROOT/'results/block_bootstrap_2000.csv',index=False,float_format='%.10g')
    rng=np.random.default_rng(SEED+2)
    exposure=[]
    for b in range(n_exposure):
        w=float(rng.uniform(0.8,1.0))
        p=panel.copy()
        p['factor']=np.tanh((w*p.sem_available+(1-w)*p.computer_available-p.man_available)/15.0)
        z=walk_forward(p,models=('full',))
        exposure.append({'draw':b,'sem_weight':w,'delta_rmse':base-rmse(z.target,z.full)})
    ex=pd.DataFrame(exposure);ex.to_csv(ROOT/'results/exposure_perturbation_1000.csv',index=False,float_format='%.10g')
    regimes=[]
    for name,mask in [('pre2020',o.date<'2020-01-01'),('pandemic2020_2021',(o.date>='2020-01-01')&(o.date<'2022-01-01')),('post2021',o.date>='2022-01-01')]:
        d=o.loc[mask]
        if len(d):regimes.append({'regime':name,'n':len(d),'delta_rmse':rmse(d.target,d.macro)-rmse(d.target,d.full),'rmse_mean':rmse(d.target,d['mean']),'rmse_full':rmse(d.target,d.full)})
    pd.DataFrame(regimes).to_csv(ROOT/'results/regimes.csv',index=False,float_format='%.10g')
    loyo=[]
    for year in sorted(o.date.dt.year.unique()):
        d=o[o.date.dt.year!=year]
        loyo.append({'excluded_year':int(year),'n':len(d),'delta_rmse':rmse(d.target,d.macro)-rmse(d.target,d.full)})
    pd.DataFrame(loyo).to_csv(ROOT/'results/leave_one_year_out.csv',index=False,float_format='%.10g')
    sens=[]
    for lag in [1,2,3,4]:
      for horizon in [1,3,6]:
        p=build_panel(raw,lag=lag,horizon=horizon)
        z=walk_forward(p,horizon=horizon,lag=lag)
        if len(z):sens.append({'lag_months':lag,'horizon_months':horizon,'n':len(z),'delta_rmse':rmse(z.target,z.macro)-rmse(z.target,z.full),'mean_rmse':rmse(z.target,z['mean'])})
    pd.DataFrame(sens).to_csv(ROOT/'results/horizon_lag.csv',index=False,float_format='%.10g')
    abl=[]
    for typ in ['no_momentum','no_computer','no_manufacturing']:
        cols={'no_momentum':['comm_available','man_available','computer_available','factor'],'no_computer':['comm_available','momentum','man_available','factor'],'no_manufacturing':['comm_available','momentum','computer_available','factor']}[typ]
        rows=[]
        for _,r in o.iterrows():
            t=int(r.origin_index); train=panel.loc[panel.origin_index+HORIZON<=t-LAG]
            now=panel.loc[panel.origin_index==t].iloc[0]
            rows.append(ridge_predict(train[cols].to_numpy(float),train.target.to_numpy(float),now[cols].to_numpy(float)))
        abl.append({'ablation':typ,'rmse':rmse(o.target,rows),'delta_vs_macro':base-rmse(o.target,rows)})
    pd.DataFrame(abl).to_csv(ROOT/'results/ablations.csv',index=False,float_format='%.10g')
    q=pd.qcut(o['target'],5,duplicates='drop')
    association={'factor_target_pearson_full':float(panel[['factor','target']].corr().iloc[0,1]),'oos_factor_target_spearman':float(pd.Series(o.factor_only).corr(pd.Series(o.target),method='spearman')),'oos_n':len(o)}
    summary={'study':'semiconductor-supply-to-us-communications-equipment-2026-10-28','n_raw':len(raw),'n_panel':len(panel),'n_oos':len(o),'oos_start':str(o.date.min().date()),'oos_end':str(o.date.max().date()),'primary_horizon_months':HORIZON,'lag_months':LAG,'primary_delta_rmse_log_pp':observed,'rmse_macro':base,'rmse_full':full,'rmse_mean':float(score.set_index('model').loc['mean','rmse_log_pp']),'rmse_persistence':float(score.set_index('model').loc['persistence','rmse_log_pp']),'block_shuffle_draws':n_placebo,'exploratory_block_shuffle_tail_fraction':float((1+(pl.delta_rmse>=observed).sum())/(1+n_placebo)),'bootstrap_draws':n_boot,'bootstrap_95pct_delta_rmse':[float(v) for v in np.quantile(bs.delta_rmse,[.025,.975])],'exposure_draws':n_exposure,'exposure_positive_fraction':float((ex.delta_rmse>0).mean()),'pre2020_delta':next((r['delta_rmse'] for r in regimes if r['regime']=='pre2020'),None),'post2021_delta':next((r['delta_rmse'] for r in regimes if r['regime']=='post2021'),None),'source_git_blob_sha':EXPECTED_GIT_BLOB,'point_in_time_verified':False,'firm_fundamentals_tested':False,'equity_total_returns_tested':False,'exploratory_many_hypotheses':True,**association}
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    make_figures(raw,panel,o,score,pl,bs,ex,regimes)
    return summary

def make_figures(raw,p,o,score,pl,bs,ex,regimes):
    def fig(name,title,xlabel,ylabel,draw):
        plt.figure(figsize=(9,4.8));draw();plt.title(title);plt.xlabel(xlabel);plt.ylabel(ylabel);plt.tight_layout();plt.savefig(ROOT/'figures'/name,dpi=125);plt.close()
    fig('01_output_levels.png','G.17 manufacturing output indexes','Month','2017=100',lambda:(plt.plot(raw.date,raw.IPG3342S,label='Communications'),plt.plot(raw.date,raw.IPG3344S,label='Semiconductors'),plt.plot(raw.date,raw.IPMAN,label='Manufacturing'),plt.legend()))
    fig('02_yoy_growth.png','Observed annual output growth','Month','YoY log percentage points',lambda:(plt.plot(p.date,p.comm,label='Communications'),plt.plot(p.date,p['sem'],label='Semiconductors'),plt.legend()))
    fig('03_signal_and_target.png','Predeclared stale upstream pressure and future output','Formation month','Factor / scaled target',lambda:(plt.plot(p.date,p.factor,label='Factor'),plt.plot(p.date,p.target/25,label='Future communications YoY /25'),plt.legend()))
    fig('04_oos_forecasts.png','Purged expanding-window OOS forecasts','Origin month','3m-ahead YoY log pp',lambda:(plt.plot(o.date,o.target,label='Realized'),plt.plot(o.date,o['mean'],label='Historical mean'),plt.plot(o.date,o.full,label='Augmented ridge'),plt.legend()))
    fig('05_rmse_scorecard.png','Same-origin OOS baseline comparison','RMSE (log pp)','Model',lambda:plt.barh(score.model,score.rmse_log_pp))
    fig('06_cumulative_paired_loss.png','Cumulative squared-loss difference (macro minus full)','Origin month','Cumulative squared log-pp',lambda:plt.plot(o.date,((o.target-o.macro)**2-(o.target-o.full)**2).cumsum()))
    fig('07_block_placebo.png','1,000 refit block-shuffle placebo (exploratory)','RMSE gain vs macro','Count',lambda:(plt.hist(pl.delta_rmse,bins=35),plt.axvline(float(score.set_index('model').loc['macro','rmse_log_pp']-score.set_index('model').loc['full','rmse_log_pp']),ls='--',label='Observed'),plt.legend()))
    fig('08_bootstrap.png','2,000 paired moving-block bootstrap draws','RMSE gain vs macro','Count',lambda:(plt.hist(bs.delta_rmse,bins=35),plt.axvline(0,ls='--')))
    fig('09_exposure_perturbation.png','1,000 bounded upstream exposure weights','Semiconductor weight','RMSE gain vs macro',lambda:(plt.scatter(ex.sem_weight,ex.delta_rmse,s=5,alpha=.25),plt.axhline(0,ls='--')))
    fig('10_regime_sensitivity.png','Regime-specific OOS incremental RMSE gain','Regime','RMSE gain (log pp)',lambda:plt.bar([r['regime'] for r in regimes],[r['delta_rmse'] for r in regimes]))

if __name__=='__main__':
    print(json.dumps(compute_all(),indent=2))
