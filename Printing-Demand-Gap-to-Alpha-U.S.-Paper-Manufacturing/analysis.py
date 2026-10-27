"""Paper demand-pressure retrospective falsification; NO historical PIT or equity alpha claim.
All parameters for primary test are fixed, and training targets are purged by outcome availability.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw_g17_paper_printing_2026-10-26.csv'
HORIZON = 3
LAG = 2
MIN_TRAIN = 60
ALPHA = 10.0
BLOCK = 12
SEED = 20261027


def load_data(path=RAW):
    df = pd.read_csv(path, parse_dates=['date']).sort_values('date').reset_index(drop=True)
    assert len(df)==201 and df.date.iloc[0]==pd.Timestamp('2010-01-01') and df.date.iloc[-1]==pd.Timestamp('2026-09-01')
    assert df.date.is_unique and (df.date.diff().dropna().dt.days.between(28,31)).all()
    assert set(['paper_ip','printing_ip','manufacturing_ip']).issubset(df.columns)
    assert df[['paper_ip','printing_ip','manufacturing_ip']].notna().all().all()
    assert (df[['paper_ip','printing_ip','manufacturing_ip']]>0).all().all()
    return df


def build_panel(raw, horizon=HORIZON, lag=LAG, printing_weight=1., manufacturing_weight=1.):
    """Formation t: all predictors observed at t-lag, label paper growth at t+h.
    This is only an assumed conservative release buffer on revised-snapshot data.
    """
    d = raw[['date','paper_ip','printing_ip','manufacturing_ip']].copy()
    for s in ['paper','printing','manufacturing']:
        d[f'{s}_yoy']=100*(np.log(d[f'{s}_ip'])-np.log(d[f'{s}_ip'].shift(12)))
        d[f'{s}_lag']=d[f'{s}_yoy'].shift(lag)
    d['factor']=printing_weight*d.printing_lag-manufacturing_weight*d.manufacturing_lag
    d['target']=d.paper_yoy.shift(-horizon)
    d['target_month']=d.date.shift(-horizon)
    d['feature_month']=d.date.shift(lag)
    d['horizon']=horizon
    d['release_buffer_months']=lag
    return d.dropna(subset=['paper_lag','printing_lag','manufacturing_lag','factor','target']).reset_index(drop=True)


def fit_predict(train, test, cols):
    if not cols: return float(train.target.mean())
    scaler=StandardScaler().fit(train[cols].to_numpy())
    X=scaler.transform(train[cols].to_numpy());x=scaler.transform(test[cols].to_numpy())
    model=Ridge(alpha=ALPHA,fit_intercept=True).fit(X,train.target.to_numpy())
    return float(model.predict(x)[0])


def walk_forward(panel, horizon=HORIZON, lag=LAG, min_train=MIN_TRAIN):
    """Training sample j label is available only if j+h+lag <= formation origin t.
    The extra lag is a conservative release delay, NOT vintage verification.
    """
    models={'mean':[], 'persistence':['paper_lag'],
            'macro_controls':['paper_lag','manufacturing_lag'],
            'factor_only':['factor'],
            'augmented':['paper_lag','manufacturing_lag','factor']}
    rows=[]
    for i in range(len(panel)):
        t=panel.date.iloc[i]
        train=panel.loc[panel.target_month <= t-pd.DateOffset(months=lag)]
        # target_month refers to the outcome's observation month, and is conservatively lagged.
        if len(train)<min_train: continue
        test=panel.iloc[[i]]
        row={'origin':t,'target_month':panel.target_month.iloc[i],
             'actual':float(panel.target.iloc[i]),'factor':float(panel.factor.iloc[i]),
             'train_n':len(train),'train_last_target_month':train.target_month.max()}
        for name,cols in models.items():row[name]=fit_predict(train,test,cols)
        rows.append(row)
    return pd.DataFrame(rows)


def score(pred):
    actual=pred.actual.to_numpy()
    rows=[]
    for name in ['mean','persistence','macro_controls','factor_only','augmented']:
        y=pred[name].to_numpy()
        rmse=float(np.sqrt(np.mean((actual-y)**2)))
        mae=float(np.mean(np.abs(actual-y)))
        ic=float(pearsonr(actual,y).statistic) if np.std(y)>1e-9 else np.nan
        rows.append({'model':name,'n':len(actual),'rmse_log_pp':rmse,'mae_log_pp':mae,'temporal_pearson_ic':ic})
    return pd.DataFrame(rows)


def rmse_improvement(pred):
    a=pred.actual.to_numpy()
    return float(np.sqrt(np.mean((a-pred.macro_controls)**2))-np.sqrt(np.mean((a-pred.augmented)**2)))


def block_bootstrap(pred, draws=2000, block=BLOCK, seed=SEED):
    rng=np.random.default_rng(seed);n=len(pred);a=pred.actual.to_numpy()
    c=pred.macro_controls.to_numpy();f=pred.augmented.to_numpy()
    out=np.empty(draws)
    for b in range(draws):
        idx=np.concatenate([(np.arange(s,s+block)%n) for s in rng.integers(0,n,size=(n+block-1)//block)])[:n]
        out[b]=np.sqrt(np.mean((a[idx]-c[idx])**2))-np.sqrt(np.mean((a[idx]-f[idx])**2))
    return out


def shuffle_blocks(x, block, rng):
    """Shuffle nonoverlapping contiguous blocks; preserves within-block serial structure."""
    chunks=[x[i:i+block] for i in range(0,len(x),block)]
    order=rng.permutation(len(chunks))
    return np.concatenate([chunks[j] for j in order])


def _fast_augmented(panel, lag=LAG, min_train=MIN_TRAIN):
    """Numerically equivalent train-only standardization and closed-form Ridge.
    This avoids repeated pandas/sklearn overhead during Monte Carlo refits.
    """
    X=panel[['paper_lag','manufacturing_lag','factor']].to_numpy(dtype=float)
    y=panel.target.to_numpy(dtype=float)
    dates=panel.date.to_numpy(dtype='datetime64[M]')
    label_dates=panel.target_month.to_numpy(dtype='datetime64[M]')
    preds=[]
    for i in range(len(panel)):
        count=int(np.searchsorted(label_dates,dates[i]-np.timedelta64(lag,'M'),side='right'))
        if count<min_train:continue
        tr=X[:count];target=y[:count];mu=tr.mean(axis=0);std=tr.std(axis=0)
        std[std==0]=1.
        z=(tr-mu)/std
        beta=np.linalg.solve(z.T@z+ALPHA*np.eye(3),z.T@(target-target.mean()))
        preds.append(target.mean()+((X[i]-mu)/std)@beta)
    return np.asarray(preds)


def placebo(panel, original_gain, draws=1000, seed=SEED, block=BLOCK):
    rng=np.random.default_rng(seed);base=panel.factor.to_numpy();results=[]
    baseline=walk_forward(panel)
    a=baseline.actual.to_numpy();c=baseline.macro_controls.to_numpy()
    baseline_rmse=np.sqrt(np.mean((a-c)**2))
    for b in range(draws):
        p=panel.copy();p['factor']=shuffle_blocks(base,block,rng)
        f=_fast_augmented(p)
        assert len(f)==len(a)
        results.append(baseline_rmse-np.sqrt(np.mean((a-f)**2)))
    gains=np.asarray(results)
    return gains, float((np.sum(gains>=original_gain)+1)/(len(gains)+1))


def exposure_perturbations(raw, draws=1000, seed=SEED):
    rng=np.random.default_rng(seed);rows=[]
    p=build_panel(raw);pred=walk_forward(p)
    a=pred.actual.to_numpy();control_rmse=np.sqrt(np.mean((a-pred.macro_controls.to_numpy())**2))
    for i in range(draws):
        w_print=rng.uniform(.8,1.2);w_manuf=rng.uniform(.8,1.2)
        q=p.copy();q['factor']=w_print*q.printing_lag-w_manuf*q.manufacturing_lag
        f=_fast_augmented(q)
        rows.append({'iteration':i,'printing_weight':w_print,'manufacturing_weight':w_manuf,
                     'control_minus_augmented_rmse':control_rmse-np.sqrt(np.mean((a-f)**2))})
    return pd.DataFrame(rows)

def regime_scores(pred):
    regimes={'pre_2020':pred.origin<'2020-01-01',
             '2020_2021':pred.origin.between('2020-01-01','2021-12-31'),
             'post_2021':pred.origin>='2022-01-01',
             'exclude_2020_2021':~pred.origin.between('2020-01-01','2021-12-31')}
    rows=[]
    for k,mask in regimes.items():
        p=pred.loc[mask]
        if len(p)>=5:rows.append({'regime':k,'n':len(p),'gain_log_pp':rmse_improvement(p),
                                  'mean_rmse':score(p).set_index('model').loc['mean','rmse_log_pp']})
    return pd.DataFrame(rows)


def leave_one_year_out(pred):
    rows=[]
    for y in sorted(pred.origin.dt.year.unique()):
        p=pred.loc[pred.origin.dt.year!=y]
        rows.append({'excluded_year':int(y),'n':len(p),'gain_log_pp':rmse_improvement(p)})
    return pd.DataFrame(rows)


def rank_spread(pred):
    # This is macro conditional growth, not a long-short portfolio or equity return spread.
    q=pd.qcut(pred.factor,5,labels=False,duplicates='drop')
    s=pred.assign(factor_quintile=q).groupby('factor_quintile').actual.agg(['mean','count'])
    return s, float(s['mean'].iloc[-1]-s['mean'].iloc[0])
