"""Retrospective U.S. courier-employment lead-factor falsification.

Inputs are frozen latest-revised quarterly snapshots inherited from an earlier
study, not reconstructed point-in-time vintage data. No equity returns.
"""
from pathlib import Path
import numpy as np
import pandas as pd

COLS=['courier_yoy','payroll_yoy','warehouse_yoy']
ALPHA=10.0
H=2
PUB_BUFFER=1
MIN_TRAIN=36

def prepare(raw):
    d=raw.copy().sort_values('observation_date').reset_index(drop=True)
    # The 2026Q3 row has only July employment and no Q3 e-commerce share.
    # Exclude this incomplete quarter from both features and labels.
    d=d[d.observation_date<='2026-04-01'].reset_index(drop=True)
    d['date']=pd.to_datetime(d['observation_date'])
    assert len(d)==106 and d['date'].is_unique and (d['date'].diff().dropna().dt.days.between(89,93)).all()
    for k in ['CES4349200001','CES4349300001','PAYEMS']:
        assert (d[k]>0).all()
        d[k+'_yoy']=100*np.log(d[k]/d[k].shift(4))
    # All information used for origin t is from quarter t-1 or earlier.
    d['courier_yoy']=d['CES4349200001_yoy'].shift(1)
    d['warehouse_yoy']=d['CES4349300001_yoy'].shift(1)
    d['payroll_yoy']=d['PAYEMS_yoy'].shift(1)
    d['share_yoy_pp']=(d['ECOMPCTSA']-d['ECOMPCTSA'].shift(4)).shift(1)
    d['capacity_premium']=d['warehouse_yoy']-d['payroll_yoy']
    d['factor']=d['share_yoy_pp']-0.10*d['capacity_premium']
    d['target']=d['CES4349200001_yoy'].shift(-H)
    d['target_date']=d['date'].shift(-H)
    d['formation_date']=d['date']+pd.offsets.QuarterEnd(0)
    d['last_signal_observation']=d['date'].shift(1)
    d['target_known_after']=d['date'].shift(-(H+PUB_BUFFER))
    return d

def ridge(x,y,xp,alpha=ALPHA):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float);xp=np.asarray(xp,dtype=float)
    mu=x.mean(0);sd=x.std(0);sd[sd<1e-9]=1.
    z=(x-mu)/sd; zp=(xp-mu)/sd
    yc=y-y.mean()
    coef=np.linalg.solve(z.T@z+alpha*np.eye(z.shape[1]),z.T@yc)
    return float(y.mean()+zp@coef)

def walkforward(panel, factor='factor', horizon=H, min_train=MIN_TRAIN, extra=None, ablate=None):
    """Train only on outcomes released by formation t (j+h+1<=t)."""
    d=panel.copy()
    if horizon!=H:
        d['target']=d['CES4349200001_yoy'].shift(-horizon)
    if extra is not None:
        d['factor']=extra
    if ablate=='no_ecommerce':d['factor']=-0.10*d['capacity_premium']
    if ablate=='no_capacity':d['factor']=d['share_yoy_pp']
    names={'mean':[], 'persistence':['courier_yoy'],
           'macro':['courier_yoy','payroll_yoy'],
           'warehouse_control':['courier_yoy','payroll_yoy','warehouse_yoy'],
           'factor_only':['factor'],
           'full':['courier_yoy','payroll_yoy','factor']}
    rows=[]
    for t in range(len(d)-horizon):
        if not np.isfinite(d.loc[t,'target']):continue
        train=d.iloc[:max(0,t-horizon-PUB_BUFFER+1)].copy()
        train=train.dropna(subset=['target','courier_yoy','payroll_yoy','warehouse_yoy','factor'])
        if len(train)<min_train:continue
        row=d.iloc[t]
        if not np.isfinite(row[['courier_yoy','payroll_yoy','warehouse_yoy','factor']].to_numpy(dtype=float)).all():continue
        out={'t':t,'date':row['date'],'target_date':row['target_date'],'actual':row['target'],'n_train':len(train),'last_training_target_date':train.iloc[-1]['target_date']}
        for name,features in names.items():
            out[name]=float(train.target.mean()) if not features else ridge(train[features].to_numpy(),train.target.to_numpy(),row[features].to_numpy())
        rows.append(out)
    return pd.DataFrame(rows)

def score(o):
    return pd.DataFrame([{'model':k,'n':len(o),'rmse':float(np.sqrt(np.mean((o.actual-o[k])**2))),'mae':float(np.mean(np.abs(o.actual-o[k]))),'bias':float(np.mean(o[k]-o.actual))} for k in ['mean','persistence','macro','warehouse_control','factor_only','full']])

def gain(o,control='macro'):
    return float(np.sqrt(np.mean((o.actual-o[control])**2))-np.sqrt(np.mean((o.actual-o.full)**2)))

def fast_factor_predictions(d, origins, signal):
    """Numerically identical full-model refits without per-origin pandas slicing."""
    yy=d.target.to_numpy(dtype=float)
    base=d[['courier_yoy','payroll_yoy']].to_numpy(dtype=float)
    signal=np.asarray(signal,dtype=float)
    x=np.column_stack([base,signal])
    finite=np.isfinite(x).all(1)&np.isfinite(yy)
    out=[]
    for t in origins:
        t=int(t)
        train=np.flatnonzero(finite[:max(0,t-H-PUB_BUFFER+1)])
        if len(train)<MIN_TRAIN or not np.isfinite(x[t]).all():
            raise ValueError('Changed OOS origin support')
        out.append(ridge(x[train],yy[train],x[t]))
    return np.asarray(out)

def gain_from_pred(o,pred,control='macro'):
    return float(np.sqrt(np.mean((o.actual-o[control])**2))-np.sqrt(np.mean((o.actual.to_numpy()-pred)**2)))

def block_shuffle_factor(d,rng,block=4):
    v=d['factor'].to_numpy().copy(); valid=np.flatnonzero(np.isfinite(v))
    # Randomly permute contiguous chronological 4-quarter blocks, preserving
    # within-block dependence but not the full original joint chronology.
    chunks=[v[valid[i:i+block]] for i in range(0,len(valid),block)]
    perm=rng.permutation(len(chunks)); out=v.copy()
    out[valid]=np.concatenate([chunks[j] for j in perm])
    return out

def placebo(d,observed,n=1000,seed=271027):
    rng=np.random.default_rng(seed);arr=[]
    for i in range(n):
        pred=fast_factor_predictions(d,observed.t,block_shuffle_factor(d,rng))
        arr.append({'draw':i+1,'gain_macro':gain_from_pred(observed,pred),'gain_warehouse':gain_from_pred(observed,pred,'warehouse_control')})
    return pd.DataFrame(arr)

def paired_block_bootstrap(o,n=2000,block=4,seed=271028):
    rng=np.random.default_rng(seed);m=len(o);a=[]
    for i in range(n):
        idx=[]
        while len(idx)<m:
            start=int(rng.integers(m));idx.extend((start+np.arange(block))%m)
        b=o.iloc[idx[:m]]
        a.append({'draw':i+1,'gain_macro':gain(b),'gain_warehouse':gain(b,'warehouse_control')})
    return pd.DataFrame(a)

def perturb(d,n=1000,seed=271029):
    rng=np.random.default_rng(seed);a=[]
    baseline=walkforward(d);origins=baseline.t
    for i in range(n):
        w=float(rng.uniform(0,0.3))
        pred=fast_factor_predictions(d,origins,d.share_yoy_pp-w*d.capacity_premium)
        a.append({'draw':i+1,'warehouse_weight':w,'gain_macro':gain_from_pred(baseline,pred),'gain_warehouse':gain_from_pred(baseline,pred,'warehouse_control')})
    return pd.DataFrame(a)

def rank_ic(o,signal):
    # Single aggregate time series; this is time-series Spearman, NOT cross-sectional stock IC.
    return float(pd.Series(o.actual).corr(pd.Series(signal.loc[o.t].to_numpy()),method='spearman'))
