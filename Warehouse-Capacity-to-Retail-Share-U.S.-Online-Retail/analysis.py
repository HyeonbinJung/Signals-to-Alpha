"""Retrospective U.S. online-retail-share lead-factor falsification.

No historical-vintage reconstruction: this is a frozen revised-data macro pilot.
All OOS folds are expanding with three-quarter target-publication purge.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data/fred_quarterly_snapshot_2026-10-26.csv'
ALPHA = 8.0
HORIZON = 2
PURGE = 3
MIN_TRAIN = 40
SEED = 20261027
CONTROLS = ['share_level','share_mom2','payroll_yoy_l1','courier_yoy_l1']


def read_raw(path=RAW):
    df = pd.read_csv(path, parse_dates=['observation_date'])
    assert len(df) == 107 and df.observation_date.is_unique
    assert df.observation_date.is_monotonic_increasing
    assert df.observation_date.diff().dropna().dt.days.between(89,92).all()
    assert df['ECOMPCTSA'].isna().sum() == 1
    assert (df[['CES4349300001','CES4349200001','PAYEMS']] > 0).all().all()
    assert df.ECOMPCTSA.dropna().between(0,100).all()
    return df


def make_panel(df, horizon=HORIZON, lag=1, warehouse_weight=1.0, courier_weight=0.0):
    d=df.copy()
    d['share_level']=d.ECOMPCTSA
    d['share_mom2']=d.ECOMPCTSA-d.ECOMPCTSA.shift(2)
    for col,name in [('CES4349300001','warehouse'),('CES4349200001','courier'),('PAYEMS','payroll')]:
        d[name+'_yoy_l1']=(100*np.log(d[col]/d[col].shift(4))).shift(lag)
    d['factor']=warehouse_weight*d.warehouse_yoy_l1+courier_weight*d.courier_yoy_l1-d.payroll_yoy_l1
    d['target']=d.ECOMPCTSA.shift(-horizon)-d.ECOMPCTSA
    d['origin_index']=np.arange(len(d))
    d['year']=d.observation_date.dt.year
    return d.dropna(subset=CONTROLS+['factor','target']).reset_index(drop=True)


def ridge_predict(train, test, features, alpha=ALPHA):
    x=train[features].to_numpy(dtype=float)
    y=train.target.to_numpy(dtype=float)
    xt=test[features].to_numpy(dtype=float)
    mu=x.mean(axis=0)
    sd=x.std(axis=0,ddof=0)
    sd=np.where(sd>1e-12,sd,1.)
    z=(x-mu)/sd
    zt=(xt-mu)/sd
    yy=y-y.mean()
    gram=z.T@z+alpha*np.eye(len(features))
    beta=np.linalg.solve(gram,z.T@yy)
    return float(y.mean()+zt@beta)


def walk_forward(panel, min_train=MIN_TRAIN, purge=PURGE, features=None):
    features=features or {'mean':[], 'persistence':['share_mom2'], 'controls':CONTROLS, 'augmented':CONTROLS+['factor'], 'factor_only':['factor']}
    y=panel.target.to_numpy(dtype=float)
    origins=panel.origin_index.to_numpy(dtype=int)
    matrices={name:panel[cols].to_numpy(dtype=float) for name,cols in features.items() if cols}
    rows=[]
    for i,origin in enumerate(origins):
        ntrain=int(np.searchsorted(origins,origin-purge,side='right'))
        if ntrain<min_train:continue
        yt=y[:ntrain]
        row={'origin_index':int(origin),'date':str(panel.observation_date.iloc[i].date()),'year':int(panel.year.iloc[i]),'actual':float(y[i]),'train_n':ntrain,'train_last_origin':int(origins[ntrain-1])}
        for name,cols in features.items():
            if not cols:row[name]=float(yt.mean());continue
            xx=matrices[name]
            x=xx[:ntrain]
            mu=x.mean(axis=0);sd=x.std(axis=0)
            sd=np.where(sd>1e-12,sd,1.)
            z=(x-mu)/sd
            zt=(xx[i]-mu)/sd
            beta=np.linalg.solve(z.T@z+ALPHA*np.eye(len(cols)),z.T@(yt-yt.mean()))
            row[name]=float(yt.mean()+zt@beta)
        rows.append(row)
    return pd.DataFrame(rows)


def score(pred):
    actual=pred.actual.to_numpy(dtype=float)
    out=[]
    for model in ['mean','persistence','controls','augmented','factor_only']:
        if model not in pred.columns: continue
        err=pred[model].to_numpy()-actual
        out.append({'model':model,'n_oos':len(err),'rmse_pp':float(np.sqrt(np.mean(err**2))),'mae_pp':float(np.mean(abs(err))),'bias_pp':float(np.mean(err))})
    return pd.DataFrame(out)


def delta(pred):
    a=pred.actual.to_numpy()
    return float(np.sqrt(np.mean((a-pred.controls.to_numpy())**2))-np.sqrt(np.mean((a-pred.augmented.to_numpy())**2)))


def circular_bootstrap(pred, n=2000, block=4, seed=SEED):
    rng=np.random.default_rng(seed)
    m=len(pred)
    a=pred.actual.to_numpy()
    c=pred.controls.to_numpy()
    f=pred.augmented.to_numpy()
    out=np.empty(n)
    for j in range(n):
        starts=rng.integers(0,m,size=int(np.ceil(m/block)))
        ix=np.concatenate([(np.arange(s,s+block)%m) for s in starts])[:m]
        out[j]=np.sqrt(np.mean((a[ix]-c[ix])**2))-np.sqrt(np.mean((a[ix]-f[ix])**2))
    return out


def block_permute_factor(panel, n=1000, block=4, seed=SEED):
    rng=np.random.default_rng(seed)
    arr=panel.factor.to_numpy()
    chunks=[arr[i:i+block] for i in range(0,len(arr),block)]
    null=np.empty(n)
    for j in range(n):
        # Shuffle whole blocks; a shorter terminal block may be relocated.
        shuffled=np.concatenate([chunks[k] for k in rng.permutation(len(chunks))])
        pp=panel.copy()
        pp['factor']=shuffled
        pred=walk_forward(pp,features={'controls':CONTROLS,'augmented':CONTROLS+['factor']})
        null[j]=delta(pred)
    return null


def exposure_perturb(df, n=1000, seed=SEED):
    rng=np.random.default_rng(seed)
    out=[]
    for j in range(n):
        w=float(rng.uniform(.5,1.))
        pp=make_panel(df,warehouse_weight=w,courier_weight=1-w)
        pr=walk_forward(pp,features={'controls':CONTROLS,'augmented':CONTROLS+['factor']})
        out.append({'draw':j,'warehouse_weight':w,'courier_weight':1-w,'delta_rmse_pp':delta(pr)})
    return pd.DataFrame(out)


def regimes(pred):
    masks={'pre_2020':pred.year<2020,'2020_2021':pred.year.between(2020,2021),'post_2021':pred.year>=2022,'exclude_2020_2021':~pred.year.between(2020,2021)}
    rows=[]
    for name,mask in masks.items():
        sub=pred[mask]
        if len(sub)>2:
            rows.append({'regime':name,'n':len(sub),'delta_rmse_pp':delta(sub),'rmse_controls':score(sub).set_index('model').loc['controls','rmse_pp'],'rmse_augmented':score(sub).set_index('model').loc['augmented','rmse_pp']})
    return pd.DataFrame(rows)


def leave_one_year_out(pred):
    return pd.DataFrame([{'excluded_year':int(y),'n_remaining':len(pred[pred.year!=y]),'delta_rmse_pp':delta(pred[pred.year!=y])} for y in sorted(pred.year.unique())])


def run(root=ROOT, n_perm=1000, n_boot=2000, n_pert=1000):
    root=Path(root)
    for d in ['results','figures','logs','data']:(root/d).mkdir(parents=True,exist_ok=True)
    df=read_raw(root/'data/fred_quarterly_snapshot_2026-10-26.csv')
    panel=make_panel(df)
    pred=walk_forward(panel)
    assert len(pred)>=35
    assert (pred.train_last_origin<=pred.origin_index-PURGE).all()
    assert pred.origin_index.is_unique
    sc=score(pred)
    obs=delta(pred)
    boot=circular_bootstrap(pred,n=n_boot)
    null=block_permute_factor(panel,n=n_perm)
    perturb=exposure_perturb(df,n=n_pert)
    reg=regimes(pred)
    loo=leave_one_year_out(pred)
    horizon_rows=[]
    for h in [1,2,4]:
        pp=make_panel(df,horizon=h)
        ppred=walk_forward(pp,purge=h+1)
        horizon_rows.append({'horizon_quarters':h,'n_oos':len(ppred),'delta_rmse_pp':delta(ppred)})
    lag_rows=[]
    for l in [1,2,3]:
        pp=make_panel(df,lag=l)
        ppred=walk_forward(pp)
        lag_rows.append({'payroll_lag_quarters':l,'n_oos':len(ppred),'delta_rmse_pp':delta(ppred)})
    ablation=[]
    for name,cols in [('no_share_level',['share_mom2','payroll_yoy_l1','courier_yoy_l1']),('no_courier',['share_level','share_mom2','payroll_yoy_l1']),('no_macro',['share_level','share_mom2'])]:
        pp=walk_forward(panel,features={'controls':cols,'augmented':cols+['factor']})
        ablation.append({'ablation':name,'n_oos':len(pp),'delta_rmse_pp':delta(pp)})
    # A contemporaneous correlation is descriptive, not a lead/alpha test.
    ic=float(spearmanr(panel.factor,panel.target).statistic)
    summary={
      'research_status':'REPRODUCED MACRO PILOT; HISTORICAL VINTAGES UNAVAILABLE; NOT EQUITY ALPHA',
      'raw_rows':len(df),'formation_rows':len(panel),'oos_rows':len(pred),'oos_first':pred.date.iloc[0],'oos_last':pred.date.iloc[-1],
      'observed_delta_rmse_pp':obs,'rank_ic_fullsample_descriptive_not_oos':ic,
      'permutation_draws':n_perm,'permutation_exploratory_tail_fraction':float((1+np.sum(null>=obs))/(n_perm+1)),
      'bootstrap_draws':n_boot,'bootstrap_95pct_delta_rmse_pp':[float(x) for x in np.quantile(boot,[.025,.975])],
      'exposure_draws':n_pert,'exposure_positive_fraction':float(np.mean(perturb.delta_rmse_pp>0)),
      'source_snapshot_sha256':hashlib.sha256((root/'data/fred_quarterly_snapshot_2026-10-26.csv').read_bytes()).hexdigest(),
      'PIT_verified':False,'firm_fundamentals_tested':False,'equity_returns_tested':False,
      'selection_note':'Retail outcome was selected as a new industry; no trading claim or causal inference.'}
    panel.to_csv(root/'data/derived_formation_panel.csv',index=False)
    for name,x in [('oos_predictions',pred),('model_scorecard',sc),('regime_scores',reg),('leave_one_year_out',loo),('exposure_perturbations',perturb),('alternative_horizons',pd.DataFrame(horizon_rows)),('alternative_lags',pd.DataFrame(lag_rows)),('ablations',pd.DataFrame(ablation))]:x.to_csv(root/f'results/{name}.csv',index=False)
    pd.DataFrame({'null_delta_rmse_pp':null}).to_csv(root/'results/block_permutation.csv',index=False)
    pd.DataFrame({'bootstrap_delta_rmse_pp':boot}).to_csv(root/'results/block_bootstrap.csv',index=False)
    (root/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return {'raw':df,'panel':panel,'pred':pred,'scorecard':sc,'null':null,'bootstrap':boot,'perturb':perturb,'regimes':reg,'loo':loo,'summary':summary,'horizons':pd.DataFrame(horizon_rows),'lags':pd.DataFrame(lag_rows),'ablations':pd.DataFrame(ablation)}

if __name__=='__main__':
    result=run()
    print(json.dumps(result['summary'],indent=2))
    print(result['scorecard'].to_string(index=False))
