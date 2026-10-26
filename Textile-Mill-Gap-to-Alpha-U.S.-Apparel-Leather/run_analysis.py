"""Retrospective textile-input → apparel/leather output falsification.

Uses frozen revised Federal Reserve G.17 series redistributed in a public GitHub
CSV. NOT a historical-vintage/PIT study and NOT a security-return study.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data/frozen_g17_2010_2026.csv'


def read_data(path=DATA):
    df = pd.read_csv(path, parse_dates=['DATE']).set_index('DATE').sort_index()
    assert list(df.columns) == ['IPG313A4S','IPG315A6S','IPMAN']
    assert len(df) == 201 and df.index.is_unique and df.notna().all().all()
    assert (df > 0).all().all()
    assert df.index.equals(pd.date_range('2010-01-01','2026-09-01',freq='MS'))
    return df


def panelize(df, lag=2, horizon=6, textile_weight=1., macro_weight=1., stale=0):
    """Formation origin t: latest presumed known month t-lag.
    Outcome = log apparel(t+horizon)/apparel(t-lag). Note the 8-month span.
    """
    p = pd.DataFrame(index=df.index)
    a, t, m = (np.log(df[x]) for x in ['IPG315A6S','IPG313A4S','IPMAN'])
    p['apparel_yoy'] = 100*(a.shift(lag)-a.shift(lag+12))
    p['apparel_3m'] = 100*(a.shift(lag)-a.shift(lag+3))
    p['manufacturing_yoy'] = 100*(m.shift(lag)-m.shift(lag+12))
    p['textile_yoy'] = 100*(t.shift(lag+stale)-t.shift(lag+stale+12))
    p['factor'] = np.tanh((textile_weight*p['textile_yoy']-macro_weight*p['manufacturing_yoy'])/10)
    p['target'] = 100*(a.shift(-horizon)-a.shift(lag))
    p = p.dropna().copy()
    p.index.name='origin'
    return p


def ridge_predict(train, row, features, alpha=20.):
    """Train-only z-score with unpenalized intercept, fixed ridge alpha."""
    X=train[features].to_numpy(dtype=float)
    x=row[features].to_numpy(dtype=float)
    y=train['target'].to_numpy(dtype=float)
    mu=X.mean(0); sd=X.std(0,ddof=0)
    sd=np.where(sd<1e-10,1.,sd)
    Z=(X-mu)/sd
    beta=np.linalg.solve(Z.T@Z+alpha*np.eye(len(features)),Z.T@(y-y.mean()))
    return float(y.mean()+((x-mu)/sd)@beta)


def walk_forward(panel, horizon=6, lag=2, start='2017-01-01', min_train=48, window=None):
    names={
        'mean':[], 'persistence':['apparel_yoy','apparel_3m'],
        'macro':['apparel_yoy','apparel_3m','manufacturing_yoy'],
        'full':['apparel_yoy','apparel_3m','manufacturing_yoy','factor'],
        'factor_only':['factor']}
    records=[]
    for i,(origin,row) in enumerate(panel.iterrows()):
        if origin < pd.Timestamp(start):continue
        # Original outcomes t+h are released only after an additional lag months.
        train=panel.iloc[:max(0,i-horizon-lag)]
        if window is not None:train=train.tail(window)
        if len(train)<min_train:continue
        result={'origin':origin,'target':float(row['target']),'train_n':len(train),
                'latest_feature_month':origin-pd.DateOffset(months=lag),
                'last_training_origin':train.index[-1]}
        for name, features in names.items():
            result[name]=float(train['target'].mean()) if not features else ridge_predict(train,row,features)
        records.append(result)
    return pd.DataFrame(records).set_index('origin')


def metrics(oos):
    actual=oos['target'].to_numpy()
    return {k:{'rmse':float(np.sqrt(np.mean((oos[k]-actual)**2))),
               'mae':float(np.mean(np.abs(oos[k]-actual)))}
            for k in ['mean','persistence','macro','full','factor_only']}


def delta(oos):
    m=metrics(oos)
    return m['macro']['rmse']-m['full']['rmse']


def paired_bootstrap(oos, n=2000, block=12, seed=20261026):
    rng=np.random.default_rng(seed); N=len(oos)
    e0=(oos['macro']-oos['target']).to_numpy()**2
    e1=(oos['full']-oos['target']).to_numpy()**2
    out=np.empty(n)
    for i in range(n):
        starts=rng.integers(0,N,size=int(np.ceil(N/block)))
        ids=np.concatenate([(np.arange(s,s+block)%N) for s in starts])[:N]
        out[i]=np.sqrt(e0[ids].mean())-np.sqrt(e1[ids].mean())
    return out


def fast_augmented_predictions(panel, factor, horizon=6, lag=2, start='2017-01-01', min_train=48, window=None):
    """NumPy-only full-model OOS refits for block shuffles / weight sweeps."""
    base=panel[['apparel_yoy','apparel_3m','manufacturing_yoy']].to_numpy()
    y=panel['target'].to_numpy()
    origins=panel.index
    z=np.asarray(factor,dtype=float)
    preds=[]
    for i,origin in enumerate(origins):
        if origin<pd.Timestamp(start):continue
        end=max(0,i-horizon-lag)
        lo=0 if window is None else max(0,end-window)
        if end-lo<min_train:continue
        X=np.column_stack([base[lo:end],z[lo:end]])
        x=np.r_[base[i],z[i]]
        yy=y[lo:end]
        mu=X.mean(0); sd=X.std(0)
        sd=np.where(sd<1e-10,1.,sd)
        zz=(X-mu)/sd
        beta=np.linalg.solve(zz.T@zz+20.*np.eye(4),zz.T@(yy-yy.mean()))
        preds.append(float(yy.mean()+((x-mu)/sd)@beta))
    return np.array(preds)


def block_permute(x, block=12, rng=None):
    rng=np.random.default_rng(0) if rng is None else rng
    blocks=[x[i:i+block] for i in range(0,len(x),block)]
    # Move complete blocks; short terminal block remains short.
    order=rng.permutation(len(blocks))
    return np.concatenate([blocks[j] for j in order])


def placebo(panel, actual_delta, n=1000, block=12, seed=113):
    rng=np.random.default_rng(seed); out=[]
    baseline=walk_forward(panel)
    for i in range(n):
        factor=block_permute(panel['factor'].to_numpy(),block,rng)
        pred=fast_augmented_predictions(panel,factor)
        oos_baseline=baseline
        out.append(float(np.sqrt(np.mean((oos_baseline['macro']-oos_baseline['target'])**2))-
                         np.sqrt(np.mean((pred-oos_baseline['target'].to_numpy())**2))))
    out=np.asarray(out)
    return out,float((np.sum(out>=actual_delta)+1)/(n+1))


def exposure(panel_source, n=1000, seed=781):
    rng=np.random.default_rng(seed); out=[]
    p=panelize(panel_source)
    baseline=walk_forward(p)
    target=baseline['target'].to_numpy(); base=baseline['macro'].to_numpy()
    base_rmse=float(np.sqrt(np.mean((base-target)**2)))
    for _ in range(n):
        w1,w2=rng.uniform(.5,1.5,size=2)
        factor=np.tanh((w1*p['textile_yoy'].to_numpy()-w2*p['manufacturing_yoy'].to_numpy())/10)
        pred=fast_augmented_predictions(p,factor)
        out.append((w1,w2,base_rmse-float(np.sqrt(np.mean((pred-target)**2)))))
    return pd.DataFrame(out,columns=['textile_weight','macro_weight','delta_rmse'])


def regime_scores(oos):
    masks={'pre_2020':oos.index<'2020-01-01',
           'pandemic_2020_21':(oos.index>='2020-01-01')&(oos.index<'2022-01-01'),
           'post_2022':oos.index>='2022-01-01',
           'excluding_2020_21':(oos.index<'2020-01-01')|(oos.index>='2022-01-01')}
    return {k:{'n':int(sum(mask)),'delta_rmse':delta(oos.loc[mask])} for k,mask in masks.items() if sum(mask)>5}


def sensitivities(df):
    scenarios={'horizon_3m':(2,3,0,None),'horizon_9m':(2,9,0,None),
               'lag_3m':(3,6,0,None),'stale_textile_12m':(2,6,12,None),
               'rolling_72m':(2,6,0,72)}
    res={}
    for name,(lag,h,stale,window) in scenarios.items():
        pred=walk_forward(panelize(df,lag,h,stale=stale),h,lag,window=window)
        res[name]={'n':len(pred),'delta_rmse':delta(pred)}
    return res


def leave_one_year_out(oos):
    out=[]
    for year in sorted(set(oos.index.year)):
        keep=oos[oos.index.year!=year]
        out.append({'excluded_year':int(year),'n':len(keep),'delta_rmse':delta(keep)})
    return pd.DataFrame(out)


def run(heavy=True):
    df=read_data(); p=panelize(df); oos=walk_forward(p)
    ROOT.joinpath('results').mkdir(exist_ok=True)
    p.to_csv(ROOT/'data/derived_panel.csv',float_format='%.9f')
    oos.to_csv(ROOT/'results/oos_forecasts.csv',float_format='%.9f')
    score=metrics(oos); d=delta(oos)
    result={'source_n':len(df),'source_start':str(df.index.min().date()),'source_end':str(df.index.max().date()),
            'panel_n':len(p),'oos_n':len(oos),'oos_start':str(oos.index.min().date()),
            'oos_end':str(oos.index.max().date()),'scores':score,'delta_macro_minus_full_rmse':d,
            'regimes':regime_scores(oos),'sensitivity':sensitivities(df),
            'leave_one_year_out':leave_one_year_out(oos).to_dict('records'),
            'PIT_verified':False,'equity_alpha_established':False}
    if heavy:
        boot=paired_bootstrap(oos)
        np.savetxt(ROOT/'results/bootstrap_2000.csv',boot,delimiter=',',header='delta_rmse',comments='')
        null,tail=placebo(p,d)
        np.savetxt(ROOT/'results/block_placebo_1000.csv',null,delimiter=',',header='delta_rmse',comments='')
        ex=exposure(df);ex.to_csv(ROOT/'results/exposure_1000.csv',index=False)
        result.update({'bootstrap_95pct':np.quantile(boot,[.025,.975]).tolist(),
                       'placebo_exploratory_tail_fraction':tail,
                       'exposure_positive_fraction':float((ex.delta_rmse>0).mean()),
                       'exposure_95pct':ex.delta_rmse.quantile([.025,.975]).tolist()})
    (ROOT/'results/metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    leave_one_year_out(oos).to_csv(ROOT/'results/leave_one_year_out.csv',index=False)
    return result

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
