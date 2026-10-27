"""Reproducible fixed-snapshot U.S. basic-chemical manufacturing macro-factor test.

The dataset is NOT an archived publication-vintage panel. The code enforces a
conservative two-completed-month input lag and one-month outcome publication
buffer, but cannot repair historical revisions.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

HORIZON = 6
FEATURE_LAG = 2
OUTCOME_LAG = 1
ALPHA = 12.0
SEED = 2601026


def load_snapshot(path):
    d = pd.read_csv(path)
    required = ['DATE', 'CHEM', 'MANUF', 'henry_hub_usd_mmbtu', 'wti_usd_barrel']
    if not set(required).issubset(d.columns):
        raise ValueError('Missing required columns')
    d['date'] = pd.to_datetime(d['DATE'] + '-01')
    if d['date'].duplicated().any() or not d['date'].is_monotonic_increasing:
        raise ValueError('Dates not unique or sorted')
    expected = pd.date_range(d['date'].iloc[0], d['date'].iloc[-1], freq='MS')
    if len(d) != len(expected) or not d['date'].reset_index(drop=True).equals(pd.Series(expected)):
        raise ValueError('Monthly continuity violated')
    if not np.isfinite(d[required[1:]].to_numpy(dtype=float)).all() or (d[required[1:]] <= 0).any().any():
        raise ValueError('Nonpositive/nonfinite source value')
    return d


def make_panel(d, horizon=HORIZON, feature_lag=FEATURE_LAG, gas_weight=1.0, oil_weight=1.0):
    if horizon < 1 or feature_lag < 1:
        raise ValueError('Horizon and feature lag must be positive')
    p = pd.DataFrame({'date': d['date']})
    # date is a first-of-month LABEL; the hypothetical decision occurs at that month-end.
    p['formation_asof_month_end'] = p['date'] + pd.offsets.MonthEnd(0)
    logs = {key: np.log(d[col].astype(float)) for key,col in [('chem','CHEM'),('manuf','MANUF'),('gas','henry_hub_usd_mmbtu'),('oil','wti_usd_barrel')]}
    for key, v in logs.items():
        p[f'{key}_yoy'] = 100*(v - v.shift(12))
    p['chem_yoy_available'] = p['chem_yoy'].shift(feature_lag)
    p['manuf_yoy_available'] = p['manuf_yoy'].shift(feature_lag)
    p['oil_yoy_available'] = p['oil_yoy'].shift(feature_lag)
    p['gas_yoy_available'] = p['gas_yoy'].shift(feature_lag)
    p['factor'] = oil_weight*p['oil_yoy_available'] - gas_weight*p['gas_yoy_available']
    p['target'] = p['chem_yoy'].shift(-horizon)
    p['relative_target'] = (p['chem_yoy']-p['manuf_yoy']).shift(-horizon)
    p['target_observation_date'] = p['date'].shift(-horizon)
    p['target_release_proxy'] = p['date'].shift(-(horizon + OUTCOME_LAG))
    p['feature_observation_date'] = p['date'].shift(feature_lag)
    p['year'] = p['date'].dt.year
    p['formation_index'] = np.arange(len(p))
    return p


def ridge_predict(train, test, cols, alpha=ALPHA, target='target'):
    x = train[list(cols)].to_numpy(dtype=float)
    y = train[target].to_numpy(dtype=float)
    xt = test[list(cols)].to_numpy(dtype=float)
    mu = x.mean(axis=0)
    sd = x.std(axis=0, ddof=0)
    sd = np.where(sd < 1e-9, 1.0, sd)
    z = (x-mu)/sd
    zt = (xt-mu)/sd
    yc = y.mean()
    coef = np.linalg.solve(z.T@z + alpha*np.eye(z.shape[1]), z.T@(y-yc))
    return float(yc + (zt@coef).item())


MODELS = {
    'historical_mean': [],
    'chemical_persistence': ['chem_yoy_available'],
    'macro_controls': ['chem_yoy_available','manuf_yoy_available','oil_yoy_available'],
    'energy_gap_augmented': ['chem_yoy_available','manuf_yoy_available','oil_yoy_available','factor'],
    'energy_gap_only': ['factor'],
    'gas_only': ['chem_yoy_available','manuf_yoy_available','gas_yoy_available'],
    'oil_only': ['chem_yoy_available','manuf_yoy_available','oil_yoy_available'],
}


def walk_forward(panel, models=None, start='2017-01-01', target='target', horizon=HORIZON, min_train=48):
    models = MODELS if models is None else models
    needed = sorted(set([target]+[c for v in models.values() for c in v]))
    p = panel.dropna(subset=needed).copy().reset_index(drop=True)
    feature_columns = sorted(set(c for cols in models.values() for c in cols))
    x = p[feature_columns].to_numpy(dtype=float)
    y = p[target].to_numpy(dtype=float)
    indices = p.formation_index.to_numpy(dtype=int)
    date = p.date.to_numpy()
    feature_index = {col:i for i,col in enumerate(feature_columns)}
    out = []
    for i in range(len(p)):
        if date[i] < np.datetime64(start):
            continue
        # Target j+h must have passed the extra one-month release buffer.
        ntrain=int(np.searchsorted(indices, indices[i]-horizon-OUTCOME_LAG,side='right'))
        if ntrain < min_train:
            continue
        if indices[ntrain-1]+horizon+OUTCOME_LAG>indices[i]:
            raise AssertionError('Target release purge failure')
        obs = {'date':p.date.iloc[i],'year':int(p.year.iloc[i]),'formation_index':int(indices[i]),
               'train_n':ntrain,'train_last_date':p.date.iloc[ntrain-1],
               'train_last_target_observation':p.target_observation_date.iloc[ntrain-1],
               'actual':float(y[i]),'factor':float(p.factor.iloc[i])}
        for name, cols in models.items():
            if not cols:
                obs[name]=float(y[:ntrain].mean())
                continue
            select=[feature_index[c] for c in cols]
            xt=x[:ntrain][:,select]
            mu=xt.mean(axis=0);sd=np.where(xt.std(axis=0)<1e-9,1.,xt.std(axis=0))
            z=(xt-mu)/sd;yt=y[:ntrain];yc=yt.mean()
            coef=np.linalg.solve(z.T@z+ALPHA*np.eye(len(select)),z.T@(yt-yc))
            obs[name]=float(yc+((x[i,select]-mu)/sd)@coef)
        out.append(obs)
    if not out:
        raise ValueError('No OOS predictions')
    return pd.DataFrame(out)


def rmse(actual,pred):
    return float(np.sqrt(np.mean((np.asarray(actual,dtype=float)-np.asarray(pred,dtype=float))**2)))


def mae(actual,pred):
    return float(np.mean(np.abs(np.asarray(actual,dtype=float)-np.asarray(pred,dtype=float))))


def scorecard(oos, models=MODELS):
    return pd.DataFrame([{'model':m,'n_oos':len(oos),'rmse_log_pp':rmse(oos.actual,oos[m]),'mae_log_pp':mae(oos.actual,oos[m]),'mean_error':float((oos[m]-oos.actual).mean())} for m in models]).sort_values('rmse_log_pp')


def block_bootstrap(oos, draws=2000, block=12, seed=SEED):
    rng=np.random.default_rng(seed)
    a=oos.actual.to_numpy(float);c=oos.macro_controls.to_numpy(float);f=oos.energy_gap_augmented.to_numpy(float)
    n=len(a); vals=np.empty(draws)
    for i in range(draws):
        indices=[]
        while len(indices)<n:
            st=int(rng.integers(0,n));indices.extend((st+np.arange(block))%n)
        ix=np.asarray(indices[:n],dtype=int)
        vals[i]=rmse(a[ix],c[ix])-rmse(a[ix],f[ix])
    return vals


def block_shuffle_factor(panel, block=12, rng=None):
    rng=np.random.default_rng() if rng is None else rng
    p=panel.copy()
    ix=np.flatnonzero(p.factor.notna().to_numpy())
    vals=p.loc[ix,'factor'].to_numpy(float)
    blocks=[vals[i:i+block] for i in range(0,len(vals),block)]
    # Rotate contiguous 12m blocks, preserve within-block order, not an exact exchangeability null.
    order=rng.permutation(len(blocks))
    shuffled=np.concatenate([blocks[i] for i in order])
    p.loc[ix,'factor']=shuffled
    return p


def placebo(panel, baseline_oos, draws=1000, seed=SEED, block=12):
    rng=np.random.default_rng(seed)
    actual_gain=rmse(baseline_oos.actual,baseline_oos.macro_controls)-rmse(baseline_oos.actual,baseline_oos.energy_gap_augmented)
    vals=np.empty(draws)
    models={'macro_controls':MODELS['macro_controls'],'energy_gap_augmented':MODELS['energy_gap_augmented']}
    for k in range(draws):
        perm=walk_forward(block_shuffle_factor(panel,block,rng),models=models)
        if len(perm)!=len(baseline_oos) or not np.array_equal(perm.date,baseline_oos.date):
            raise AssertionError('Placebo origins not aligned')
        vals[k]=rmse(perm.actual,perm.macro_controls)-rmse(perm.actual,perm.energy_gap_augmented)
    # Empirical upper tail is exploratory, NOT an exact p-value for serially dependent data.
    tail=(1+int((vals>=actual_gain).sum()))/(draws+1)
    return vals,tail,actual_gain


def exposure_perturbation(panel, draws=1000, seed=SEED):
    rng=np.random.default_rng(seed+17)
    base=walk_forward(panel,models={'macro_controls':MODELS['macro_controls']})
    base_rmse=rmse(base.actual,base.macro_controls)
    rows=[]
    for _ in range(draws):
        wg=float(rng.uniform(.75,1.25));wo=float(rng.uniform(.75,1.25))
        p=panel.copy()
        p['factor']=wo*p.oil_yoy_available-wg*p.gas_yoy_available
        oos=walk_forward(p,models={'energy_gap_augmented':MODELS['energy_gap_augmented']})
        rows.append({'gas_weight':wg,'oil_weight':wo,'improvement':base_rmse-rmse(oos.actual,oos.energy_gap_augmented)})
    return pd.DataFrame(rows)


def block_ic(oos):
    # Descriptive rank correlation across OOS origins; overlapping labels invalidate iid t-stat.
    return float(pd.Series(oos.factor).corr(pd.Series(oos.actual),method='spearman'))
