"""Reproducible retrospective computer-hardware manufacturing factor falsification.

All indices are revised fixed snapshots; no historical PIT claim. No company alpha.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

RAW = ['IPG3341S', 'IPG3342S', 'IPG3344S', 'IPMAN']
HORIZON = 3
RELEASE_BUFFER = 2
MIN_TRAIN = 48
ALPHA = 20.0


def load_and_qa(path):
    df = pd.read_csv(path, parse_dates=['date']).sort_values('date').reset_index(drop=True)
    assert list(df.columns) == ['date', 'IPG3344S', 'IPG3341S', 'IPG3342S', 'IPMAN']
    assert len(df) == 189
    assert df['date'].is_unique and df['date'].notna().all()
    assert df['date'].dt.to_period('M').astype(int).diff().dropna().eq(1).all()
    assert df[RAW].notna().all().all() and (df[RAW] > 0).all().all()
    assert df['date'].iloc[0] == pd.Timestamp('2011-01-01')
    assert df['date'].iloc[-1] == pd.Timestamp('2026-09-01')
    return df


def make_panel(raw, h=HORIZON, buffer=RELEASE_BUFFER, k=1.0):
    """Origin t uses only observations <= t-buffer; outcome at t+h.

    Each training row u is usable at t only if u+h <= t-buffer.
    """
    df = raw[['date']].copy()
    for col, short in [('IPG3341S','computer'),('IPG3342S','network'),('IPG3344S','chip'),('IPMAN','manufacturing')]:
        g = 100 * np.log(raw[col] / raw[col].shift(12))
        df[f'{short}_yoy'] = g
        df[f'{short}_stale'] = g.shift(buffer)
    df['computer_momentum'] = df['computer_stale'] - df['computer_yoy'].shift(buffer+3)
    df['network_momentum'] = df['network_stale'] - df['network_yoy'].shift(buffer+3)
    df['factor'] = df['network_stale'] - k * df['chip_stale']
    df['target'] = df['computer_yoy'].shift(-h)
    df['target_month'] = raw['date'].shift(-h)
    df['latest_input_month'] = raw['date'].shift(buffer)
    df['formation_month'] = raw['date']
    df['horizon'] = h
    df['buffer'] = buffer
    return df


FEATURES = {
    'ar_ridge': ['computer_stale','computer_momentum'],
    'macro_control': ['computer_stale','computer_momentum','manufacturing_stale','chip_stale'],
    'network_factor_only': ['factor'],
    'full_network_balance': ['computer_stale','computer_momentum','manufacturing_stale','chip_stale','factor'],
}


def fit_predict(train, row, columns):
    """Closed-form ridge, identical objective to sklearn Ridge(alpha=20).

    Intercept and standardization are fitted on each training window only.
    """
    X = train[columns].to_numpy(dtype=float)
    x = row[columns].to_numpy(dtype=float).reshape(1,-1)
    mu=X.mean(axis=0); sigma=X.std(axis=0); sigma[sigma==0]=1.0
    z=(X-mu)/sigma
    y=train['target'].to_numpy(dtype=float)
    beta=np.linalg.solve(z.T@z + ALPHA*np.eye(len(columns)), z.T@(y-y.mean()))
    return float(y.mean()+((x-mu)/sigma@beta)[0])


def oos(panel, h=HORIZON, buffer=RELEASE_BUFFER, min_train=MIN_TRAIN, factor_values=None, feature_sets=None):
    p = panel.copy()
    if factor_values is not None:
        assert len(factor_values) == len(p)
        p['factor'] = factor_values
    models = FEATURES if feature_sets is None else feature_sets
    required = sorted(set(sum(models.values(), [])) | {'target', 'computer_stale', 'computer_momentum'})
    origins = np.flatnonzero(p[required].notna().all(axis=1))
    cols = sorted(set(sum(models.values(), [])))
    x_all = p[cols].to_numpy(dtype=float)
    target=p['target'].to_numpy(dtype=float)
    col_idx={c:i for i,c in enumerate(cols)}
    out=[]
    for t in origins:
        if t+h >= len(p): continue
        train_ids=origins[(origins+h <= t-buffer) & (origins<t)]
        if len(train_ids)<min_train: continue
        ytrain=target[train_ids]
        rec={'date':p.at[t,'date'],'target_month':p.at[t,'target_month'],
             'latest_input_month':p.at[t,'latest_input_month'],'origin_index':int(t),
             'n_train':int(len(train_ids)),'y':float(target[t]),
             'historical_mean':float(ytrain.mean()),
             'persistence':float(p.at[t,'computer_stale']),
             'momentum':float(p.at[t,'computer_stale']+0.5*p.at[t,'computer_momentum'])}
        for name,model_cols in models.items():
            ix=[col_idx[c] for c in model_cols]
            X=x_all[np.ix_(train_ids,ix)]
            xx=x_all[t,ix]
            mu=X.mean(axis=0); sd=X.std(axis=0); sd[sd==0]=1.0
            z=(X-mu)/sd
            beta=np.linalg.solve(z.T@z+ALPHA*np.eye(len(ix)),z.T@(ytrain-ytrain.mean()))
            rec[name]=float(ytrain.mean()+((xx-mu)/sd)@beta)
        out.append(rec)
    return pd.DataFrame(out)

def rmse(y, pred):
    return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(pred))**2)))


def mae(y, pred):
    return float(np.mean(np.abs(np.asarray(y)-np.asarray(pred))))


def scorecard(oos_df):
    models = ['historical_mean','persistence','momentum']+list(FEATURES)
    return pd.DataFrame([{'model':m,'n':len(oos_df),'rmse_log_pp':rmse(oos_df.y,oos_df[m]),
                          'mae_log_pp':mae(oos_df.y,oos_df[m]),
                          'correlation':float(np.corrcoef(oos_df.y,oos_df[m])[0,1])}
                         for m in models])


def moving_block_indices(n, block, rng):
    """Moving-block bootstrap sample indices; contiguous, no circular wrap."""
    assert 1 <= block <= n
    starts = rng.integers(0, n-block+1, size=int(np.ceil(n/block)))
    return np.concatenate([np.arange(s,s+block) for s in starts])[:n]


def bootstrap_paired(o, draws=2000, block=12, seed=20261028):
    rng=np.random.default_rng(seed)
    y=o.y.to_numpy(); a=o.macro_control.to_numpy(); b=o.full_network_balance.to_numpy()
    return pd.DataFrame({'draw':np.arange(draws),'delta_rmse_log_pp':[
        rmse(y[idx],a[idx])-rmse(y[idx],b[idx])
        for idx in (moving_block_indices(len(o),min(block,len(o)),rng) for _ in range(draws))]})


def block_permute_factor(panel, block, rng):
    """Reorder nonoverlapping chronological blocks; within-block order preserved.

    This is a diagnostic null, not an exact randomization distribution.
    """
    vals=panel['factor'].to_numpy().copy()
    good=np.flatnonzero(np.isfinite(vals))
    blocks=[good[i:i+block] for i in range(0,len(good),block)]
    perm=rng.permutation(len(blocks))
    shuffled=np.concatenate([vals[blocks[i]] for i in perm])
    vals[good]=shuffled
    return vals


def block_placebo(panel, observed_gain, draws=1000, block=12, seed=20261029):
    rng=np.random.default_rng(seed)
    gains=[]
    for i in range(draws):
        vals=block_permute_factor(panel,block,rng)
        o=oos(panel,factor_values=vals,feature_sets={'macro_control':FEATURES['macro_control'],
                                                    'full_network_balance':FEATURES['full_network_balance']})
        gains.append(rmse(o.y,o.macro_control)-rmse(o.y,o.full_network_balance))
    null=np.asarray(gains)
    return pd.DataFrame({'draw':np.arange(draws),'null_delta_rmse_log_pp':null}),float((1+np.sum(null>=observed_gain))/(draws+1))


def exposure_perturbation(raw, draws=1000, seed=20261030):
    rng=np.random.default_rng(seed)
    weights=rng.uniform(0.5,1.5,draws)
    rec=[]
    for i,k in enumerate(weights):
        panel=make_panel(raw,k=float(k))
        o=oos(panel,feature_sets={'macro_control':FEATURES['macro_control'],
                                   'full_network_balance':FEATURES['full_network_balance']})
        rec.append({'draw':i,'chip_subtraction_weight':k,
                    'delta_rmse_log_pp':rmse(o.y,o.macro_control)-rmse(o.y,o.full_network_balance)})
    return pd.DataFrame(rec)


def subset_gain(o):
    return rmse(o.y,o.macro_control)-rmse(o.y,o.full_network_balance)
