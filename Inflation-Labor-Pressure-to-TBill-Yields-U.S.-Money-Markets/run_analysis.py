"""Historical U.S. Treasury-bill rate forecasting: deterministic retrospective pilot.

Never interprets the 2009 fixed snapshot as historical point-in-time availability.
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
RAW=ROOT/'data'/'macrodata_statsmodels_2009_snapshot.csv'
ALPHA=12.0
BLOCK=8
SEED=20261028


def load_raw():
    df=pd.read_csv(RAW)
    assert len(df)==203 and df[['year','quarter']].drop_duplicates().shape[0]==203
    assert not df.isna().any().any()
    assert list(df[['year','quarter']].iloc[0])==[1959,1]
    assert list(df[['year','quarter']].iloc[-1])==[2009,3]
    assert df['tbilrate'].between(0,25).all()
    df['period']=[f'{int(y)}Q{int(q)}' for y,q in zip(df.year,df.quarter)]
    return df


def build_panel(df,horizon=1,lag=1,weight=.5):
    """Decision at quarter t end; all macro inputs use t-lag, outcome rate[t+h]-rate[t]."""
    records=[]
    for t in range(max(lag+4,6),len(df)-horizon):
        i=t-lag
        records.append(dict(origin_idx=t, origin=df.period.iloc[t],target_period=df.period.iloc[t+horizon],
            input_period=df.period.iloc[i], horizon=horizon,lag=lag,
            target=float(df.tbilrate.iloc[t+horizon]-df.tbilrate.iloc[t]),
            rate_l=float(df.tbilrate.iloc[i]),
            rate_momentum=float(df.tbilrate.iloc[i]-df.tbilrate.iloc[i-1]),
            unemp_l=float(df.unemp.iloc[i]),
            unemployment_change=float(df.unemp.iloc[i]-df.unemp.iloc[i-1]),
            inflation_l=float(df.infl.iloc[i]),
            gdp_yoy=float(100*np.log(df.realgdp.iloc[i]/df.realgdp.iloc[i-4])),
            factor=float(df.infl.iloc[i]-weight*(df.unemp.iloc[i]-df.unemp.iloc[i-1]))))
    panel=pd.DataFrame(records)
    assert panel.notna().all().all()
    return panel


def ridge_predict(train, test, columns, alpha=ALPHA):
    """Train-only standardized ridge; intercept unpenalized; no tuning on OOS."""
    X=train[columns].to_numpy(float); x=test[columns].to_numpy(float)
    mean=X.mean(axis=0); sd=X.std(axis=0); sd=np.where(sd<1e-9,1.,sd)
    Z=(X-mean)/sd; z=(x-mean)/sd
    y=train.target.to_numpy(float); ym=y.mean()
    beta=np.linalg.solve(Z.T@Z+alpha*np.eye(len(columns)),Z.T@(y-ym))
    return float((ym+z@beta)[0])


def walk_forward(panel, min_train=80, feature_override=None):
    """Fast expanding OOS with target-release purge and train-only standardization."""
    work=panel.copy()
    if feature_override is not None:
        assert len(feature_override)==len(work)
        work['factor']=np.asarray(feature_override,float)
    features=work[['rate_l','rate_momentum','unemp_l','gdp_yoy','factor']].to_numpy(float)
    y=work.target.to_numpy(float)
    origins=work.origin_idx.to_numpy(int)
    horizon=work.horizon.to_numpy(int)
    records=[]
    def fit(X,xx,yy):
        mu=X.mean(0); sd=np.where(X.std(0)<1e-9,1,X.std(0))
        z=(X-mu)/sd; zt=(xx-mu)/sd
        beta=np.linalg.solve(z.T@z+ALPHA*np.eye(z.shape[1]),z.T@(yy-yy.mean()))
        return float(yy.mean()+zt@beta)
    for k,t in enumerate(origins):
        end=int(np.searchsorted(origins,t-1-horizon[k],side='right'))
        if end<min_train:continue
        X=features[:end]; yy=y[:end]; xx=features[k]
        records.append((k,int(t),end,int(np.max(origins[:end]+horizon[:end])),float(y[k]),
                        float(yy.mean()),0.,float(xx[1]),fit(X[:,:2],xx[:2],yy),
                        fit(X[:,:4],xx[:4],yy),fit(X[:,4:5],xx[4:5],yy),fit(X,xx,yy)))
    rows=[]
    for k,t,n,mx,yt,mean,pers,mom,ar,ctrl,fac,full in records:
        rows.append(dict(origin=work.origin.iloc[k],origin_idx=t,target_period=work.target_period.iloc[k],
            target=yt,n_train=n,max_train_target_idx=mx,mean=mean,persistence=pers,momentum=mom,
            ar_ridge=ar,control=ctrl,factor_only=fac,full=full))
    return pd.DataFrame(rows)


def scores(oos):
    rows=[]
    for name in ['mean','persistence','momentum','ar_ridge','control','factor_only','full']:
        e=oos[name]-oos.target
        rows.append(dict(model=name,n=len(e),rmse=float(np.sqrt(np.mean(e**2))),mae=float(np.mean(abs(e))),
                         sign_accuracy=float(np.mean(np.sign(oos[name])==np.sign(oos.target)))))
    return pd.DataFrame(rows)


def block_shuffle(values,rng,block=BLOCK):
    """Reorder non-overlapping contiguous blocks; no IID shuffling."""
    vals=np.asarray(values)
    chunks=[vals[i:i+block] for i in range(0,len(vals),block)]
    return np.concatenate([chunks[i] for i in rng.permutation(len(chunks))])


def paired_block_bootstrap(oos,n=2000,block=BLOCK,seed=SEED+1):
    rng=np.random.default_rng(seed); m=len(oos)
    ec=(oos.control.to_numpy()-oos.target.to_numpy())**2
    ef=(oos.full.to_numpy()-oos.target.to_numpy())**2
    out=[]
    for _ in range(n):
        idx=[]
        for s in rng.integers(0,m,size=math.ceil(m/block)):
            idx.extend((s+np.arange(block))%m)
        idx=np.asarray(idx[:m],int)
        out.append(float(np.sqrt(ec[idx].mean())-np.sqrt(ef[idx].mean())))
    return np.array(out)


def subset_gain(oos,mask):
    d=oos.loc[mask]
    if len(d)<5:return dict(n=len(d),delta_rmse=np.nan)
    sc=scores(d).set_index('model').rmse
    return dict(n=len(d),delta_rmse=float(sc['control']-sc['full']),full_rmse=float(sc['full']),control_rmse=float(sc['control']))


def compute(n_placebo=1000,n_bootstrap=2000,n_exposure=1000):
    df=load_raw(); panel=build_panel(df)
    panel.to_csv(ROOT/'data'/'derived_formation_panel.csv',index=False)
    oos=walk_forward(panel)
    assert len(oos)>=75 and (oos.max_train_target_idx <= oos.origin_idx-1).all()
    sc=scores(oos)
    sc.to_csv(ROOT/'results'/'scorecard.csv',index=False,float_format='%.10g')
    oos.to_csv(ROOT/'results'/'walk_forward_oos.csv',index=False,float_format='%.10g')
    main_gain=float(sc.set_index('model').loc['control','rmse']-sc.set_index('model').loc['full','rmse'])
    rng=np.random.default_rng(SEED)
    placebo=[]
    for i in range(n_placebo):
        fake=block_shuffle(panel.factor.to_numpy(),rng)
        p=walk_forward(panel,feature_override=fake)
        s=scores(p).set_index('model').rmse
        placebo.append(dict(draw=i,delta_rmse=float(s['control']-s['full'])))
    placebo=pd.DataFrame(placebo)
    placebo.to_csv(ROOT/'results'/'block_placebo_1000.csv',index=False,float_format='%.10g')
    bootstrap=paired_block_bootstrap(oos,n_bootstrap)
    pd.DataFrame({'draw':np.arange(n_bootstrap),'delta_rmse':bootstrap}).to_csv(ROOT/'results'/'paired_block_bootstrap_2000.csv',index=False,float_format='%.10g')
    weights=np.random.default_rng(SEED+2).uniform(0.1,1.0,size=n_exposure)
    exposures=[]
    for i,w in enumerate(weights):
        factor=panel.inflation_l-w*panel.unemployment_change
        p=walk_forward(panel,feature_override=factor)
        s=scores(p).set_index('model').rmse
        exposures.append(dict(draw=i,weight=float(w),delta_rmse=float(s['control']-s['full'])))
    exposures=pd.DataFrame(exposures)
    exposures.to_csv(ROOT/'results'/'exposure_perturbation_1000.csv',index=False,float_format='%.10g')
    checks=[]
    for horizon,lag in [(1,2),(2,1),(3,1),(2,2)]:
        p=walk_forward(build_panel(df,horizon=horizon,lag=lag))
        s=scores(p).set_index('model').rmse
        checks.append(dict(horizon=horizon,lag=lag,n=len(p),delta_rmse=float(s['control']-s['full'])))
    pd.DataFrame(checks).to_csv(ROOT/'results'/'horizon_lag_robustness.csv',index=False)
    regimes=[]
    year=oos.origin.str[:4].astype(int)
    for label,mask in [('1980s',year.between(1980,1989)),('1990s',year.between(1990,1999)),('2000s',year.between(2000,2009)),
                       ('exclude_2008_2009',year<2008),('exclude_1980s',~year.between(1980,1989))]:
        regimes.append(dict(regime=label,**subset_gain(oos,mask)))
    pd.DataFrame(regimes).to_csv(ROOT/'results'/'regime_sensitivity.csv',index=False)
    loo=[]
    for decade in sorted((year//10*10).unique()):
        loo.append(dict(omitted_decade=int(decade),**subset_gain(oos,(year//10*10)!=decade)))
    pd.DataFrame(loo).to_csv(ROOT/'results'/'leave_one_decade_out.csv',index=False)
    ablations=[]
    for label,feat in [('inflation_only',panel.inflation_l),('unemployment_change_only',-panel.unemployment_change),
                       ('opposite_sign',-panel.factor)]:
        p=walk_forward(panel,feature_override=feat)
        s=scores(p).set_index('model').rmse
        ablations.append(dict(ablation=label,n=len(p),delta_rmse=float(s['control']-s['full'])))
    pd.DataFrame(ablations).to_csv(ROOT/'results'/'ablations.csv',index=False)
    factor_corr=float(panel[['factor','target']].corr().iloc[0,1])
    pd.DataFrame([{'n':len(panel),'pearson_factor_target':factor_corr,'spearman_factor_target':float(panel[['factor','target']].corr(method='spearman').iloc[0,1])}]).to_csv(ROOT/'results'/'factor_association.csv',index=False)
    metrics=dict(factor_target_pearson=factor_corr, dataset_rows=len(df),formation_rows=len(panel),oos_n=len(oos),first_oos=oos.origin.iloc[0],last_oos=oos.origin.iloc[-1],
                 main_gain_rmse_pp=main_gain,rmse={r.model:r.rmse for r in sc.itertuples()},
                 placebo_draws=n_placebo,placebo_upper_tail_fraction=float((1+np.sum(placebo.delta_rmse>=main_gain))/(n_placebo+1)),
                 bootstrap_draws=n_bootstrap,bootstrap_ci_95=list(map(float,np.quantile(bootstrap,[.025,.975]))),
                 exposure_draws=n_exposure,exposure_positive_share=float(np.mean(exposures.delta_rmse>0)),
                 source_vintage_pit_verified=False,equity_alpha_established=False,
                 raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest())
    (ROOT/'results'/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    make_figures(df,panel,oos,sc,placebo,bootstrap,exposures)
    return metrics


def make_figures(df,panel,oos,sc,placebo,bootstrap,exposures):
    plt.rcParams.update({'font.size':10,'figure.figsize':(9,4.5),'axes.spines.top':False,'axes.spines.right':False})
    dates=pd.PeriodIndex(df.period,freq='Q').to_timestamp(); f=ROOT/'figures'
    def save(name):
        plt.tight_layout();plt.savefig(f/name,dpi=115);plt.close()
    fig,ax=plt.subplots();ax.plot(dates,df.tbilrate,label='3m T-bill rate (%)');ax.plot(dates,df.infl,alpha=.65,label='annualized quarterly CPI inflation (%)');ax.set_ylabel('Annualized percent');ax.legend();save('01_rate_and_inflation.png')
    fig,ax=plt.subplots();ax.plot(panel.origin_idx,panel.factor,label='predeclared pressure factor');ax.plot(panel.origin_idx,panel.target,label='future rate change',alpha=.55);ax.set_ylabel('Percentage points');ax.legend();save('02_factor_and_target.png')
    fig,ax=plt.subplots();ax.scatter(panel.factor,panel.target,s=13,alpha=.6);ax.axhline(0,color='gray',lw=.8);ax.set(xlabel='Lagged pressure (pp)',ylabel='Future 1Q rate change (pp)');save('03_factor_scatter.png')
    fig,ax=plt.subplots();ax.bar(sc.model,sc.rmse);ax.tick_params(axis='x',rotation=40);ax.set_ylabel('OOS RMSE (percentage points)');save('04_baseline_scorecard.png')
    fig,ax=plt.subplots();ax.plot(oos.origin_idx,oos.target,label='actual',lw=1.5);ax.plot(oos.origin_idx,oos.control,label='control',alpha=.8);ax.plot(oos.origin_idx,oos.full,label='full',alpha=.8);ax.legend();ax.set_ylabel('Next-quarter rate change (pp)');save('05_oos_forecasts.png')
    fig,ax=plt.subplots();loss=(oos.control-oos.target)**2-(oos.full-oos.target)**2;ax.plot(oos.origin_idx,np.cumsum(loss));ax.axhline(0,color='gray');ax.set_ylabel('Cumulative control - full squared error');save('06_cumulative_loss.png')
    fig,ax=plt.subplots();ax.hist(placebo.delta_rmse,bins=35);ax.axvline(float(np.sqrt(np.mean((oos.control-oos.target)**2))-np.sqrt(np.mean((oos.full-oos.target)**2))),color='black',lw=2,label='observed');ax.legend();ax.set_xlabel('Control minus full RMSE (pp)');save('07_block_placebo.png')
    fig,ax=plt.subplots();ax.hist(bootstrap,bins=35);ax.axvline(0,color='black');ax.set_xlabel('Paired block-bootstrap RMSE improvement (pp)');save('08_bootstrap.png')
    fig,ax=plt.subplots();ax.scatter(exposures.weight,exposures.delta_rmse,s=9,alpha=.5);ax.axhline(0,color='black');ax.set(xlabel='Unemployment-change weight',ylabel='Control minus full RMSE (pp)');save('09_exposure_weights.png')
    year=oos.origin.str[:4].astype(int);fig,ax=plt.subplots();ax.scatter(year,loss,s=12,alpha=.65);ax.axhline(0,color='gray');ax.set(xlabel='Origin year',ylabel='Control minus full squared error');save('10_regime_losses.png')

if __name__=='__main__':
    print(json.dumps(compute(),indent=2))
