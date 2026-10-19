"""U.S. semiconductor production lead-indicator falsification.

All source observations are revised G.17 snapshots (downloaded 2026-10-19),
NOT archival point-in-time vintages. Nothing here establishes tradable equity alpha.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
COLS = ['IPG3344S','IPG3341S','IPG3342S','IPMAN']
SEED = 20261019


def load_data(path=ROOT/'data'/'fred_g17_snapshot_2011_2026.csv'):
    d = pd.read_csv(path, parse_dates=['date']).set_index('date').sort_index()
    assert list(d.columns)==COLS, f'Unexpected columns: {list(d.columns)}'
    assert not d.isna().any().any(), 'Missing source observation'
    assert (d>0).all().all(), 'Index levels must be positive'
    assert d.index.is_unique and d.index.equals(pd.date_range(d.index.min(), d.index.max(), freq='MS'))
    return d


def make_panel(d, horizon=3, lag=2, weight=.5):
    """Origin t: features dated t-lag; label is semiconductor YoY at t+horizon."""
    if not 0<=weight<=1: raise ValueError('weight outside [0,1]')
    if lag<1 or horizon<1: raise ValueError('positive lag and horizon required')
    growth=100*np.log(d/d.shift(12))
    s=growth.shift(lag)
    out=pd.DataFrame(index=d.index)
    out['semi_yoy']=s['IPG3344S']
    out['computer_yoy']=s['IPG3341S']
    out['communications_yoy']=s['IPG3342S']
    out['manufacturing_yoy']=s['IPMAN']
    out['demand_yoy']=weight*out['computer_yoy']+(1-weight)*out['communications_yoy']
    out['gap']=np.tanh((out['demand_yoy']-out['semi_yoy'])/15)
    out['breadth']=((out['computer_yoy']>0).astype(float)+(out['communications_yoy']>0).astype(float))/2
    out['semi_3m']=100*np.log(d['IPG3344S']/d['IPG3344S'].shift(3)).shift(lag)
    out['y']=growth['IPG3344S'].shift(-horizon)
    out=out.dropna()
    out.index.name='formation_month'
    return out

FEATURES={
 'persistence':['semi_yoy'],
 'macro':['semi_yoy','manufacturing_yoy','semi_3m'],
 'full':['semi_yoy','manufacturing_yoy','semi_3m','gap'],
 'computer_only':['semi_yoy','manufacturing_yoy','semi_3m','computer_yoy'],
 'communications_only':['semi_yoy','manufacturing_yoy','semi_3m','communications_yoy'],
 'breadth':['semi_yoy','manufacturing_yoy','semi_3m','breadth'],
}


def fit_predict(train, test, columns, alpha=10):
    scaler=StandardScaler().fit(train[columns].to_numpy())
    X=scaler.transform(train[columns].to_numpy())
    x=scaler.transform(test[columns].to_numpy())
    m=Ridge(alpha=alpha).fit(X,train.y.to_numpy())
    return m.predict(x)


def walk_forward(panel, horizon=3, lag=2, min_train=60, start='2017-01-01', end=None):
    """Purged expanding walk-forward. For t, training label u+h <= t-lag."""
    rows=[]
    for t in panel.index:
        if t<pd.Timestamp(start) or (end is not None and t>pd.Timestamp(end)): continue
        cutoff=t-pd.DateOffset(months=horizon+lag)
        train=panel.loc[panel.index<=cutoff]
        if len(train)<min_train: continue
        test=panel.loc[[t]]
        row={'formation_month':t,'actual':float(test.y.iloc[0]),'n_train':len(train),
             'last_training_origin':train.index.max().strftime('%Y-%m')}
        row['mean']=float(train.y.mean())
        for key,features in FEATURES.items():row[key]=float(fit_predict(train,test,features)[0])
        rows.append(row)
    if not rows: raise ValueError('No OOS observations')
    return pd.DataFrame(rows).set_index('formation_month')


def metrics(pred):
    y=pred.actual.to_numpy();result={}
    for key in ['mean',*FEATURES]:
        v=pred[key].to_numpy();e=v-y
        ic=spearmanr(v,y).statistic if np.std(v)>0 else np.nan
        result[key]={'n':len(y),'rmse':float(np.sqrt(np.mean(e**2))),
                     'mae':float(np.mean(np.abs(e))),
                     'spearman_time_rank_corr_descriptive':float(ic)}
    result['delta_rmse_macro_minus_full']=result['macro']['rmse']-result['full']['rmse']
    result['delta_rmse_mean_minus_full']=result['mean']['rmse']-result['full']['rmse']
    return result


def moving_block_bootstrap(pred, n=2000, block=6, seed=SEED):
    """CI for RMSE(macro)-RMSE(full), block resampling OOS errors."""
    rng=np.random.default_rng(seed)
    err_a=(pred.macro-pred.actual).to_numpy()
    err_b=(pred.full-pred.actual).to_numpy()
    N=len(err_a);out=np.empty(n)
    for k in range(n):
        starts=rng.integers(0,max(1,N-block+1),size=int(np.ceil(N/block)))
        ix=np.concatenate([np.arange(i,min(i+block,N)) for i in starts])[:N]
        out[k]=np.sqrt(np.mean(err_a[ix]**2))-np.sqrt(np.mean(err_b[ix]**2))
    return {'n':n,'block':block,'ci95':np.quantile(out,[.025,.975]).tolist(),
            'probability_delta_positive_descriptive':float((out>0).mean())}


def fixed_holdout_placebo(panel, n=2000, block=6, seed=SEED, split='2022-01-01', horizon=3, lag=2):
    """Fixed pre-2022 fit, block-permute post-2022 labels only.

    Exploratory alignment null, not an exact test of a refitted walk-forward model.
    """
    cut=pd.Timestamp(split)-pd.DateOffset(months=horizon+lag)
    train=panel.loc[panel.index<=cut]
    test=panel.loc[panel.index>=pd.Timestamp(split)]
    if len(train)<60 or len(test)<2*block:raise ValueError('Insufficient holdout')
    a=fit_predict(train,test,FEATURES['macro']);b=fit_predict(train,test,FEATURES['full'])
    y=test.y.to_numpy();rng=np.random.default_rng(seed)
    def improvement(y):return float(np.sqrt(np.mean((a-y)**2))-np.sqrt(np.mean((b-y)**2)))
    observed=improvement(y)
    blocks=[y[i:i+block] for i in range(0,len(y),block)]
    null=[]
    for _ in range(n):
        perm=rng.permutation(len(blocks))
        yy=np.concatenate([blocks[i] for i in perm]);null.append(improvement(yy))
    null=np.asarray(null)
    return {'n_permutations':n,'n_holdout':len(y),'split':split,'observed_delta_rmse':observed,
            'p_one_sided_exploratory':float((1+np.sum(null>=observed))/(n+1)),
            'null_95_interval':np.quantile(null,[.025,.975]).tolist()}


def exposure_weight_sensitivity(d, n=1000, horizon=3, lag=2, seed=SEED):
    """1000 fixed training / holdout fits under alternative demand mix priors."""
    rng=np.random.default_rng(seed);out=[]
    for weight in rng.uniform(.2,.8,size=n):
        panel=make_panel(d,horizon=horizon,lag=lag,weight=float(weight))
        cutoff=pd.Timestamp('2022-01-01')-pd.DateOffset(months=horizon+lag)
        train=panel.loc[panel.index<=cutoff];test=panel.loc[panel.index>='2022-01-01']
        a=fit_predict(train,test,FEATURES['macro']);b=fit_predict(train,test,FEATURES['full'])
        y=test.y.to_numpy()
        out.append(float(np.sqrt(np.mean((a-y)**2))-np.sqrt(np.mean((b-y)**2))))
    return {'n':n,'weight_range':[.2,.8],'holdout_delta_rmse_median':float(np.median(out)),
            'delta_rmse_5_95':np.quantile(out,[.05,.95]).tolist(),
            'fraction_positive':float(np.mean(np.asarray(out)>0))}


def evaluate(d, horizon=3, lag=2):
    panel=make_panel(d,horizon,lag)
    pred=walk_forward(panel,horizon,lag)
    return panel,pred,metrics(pred)


def run(root=ROOT, simulations=2000):
    root=Path(root);(root/'results').mkdir(exist_ok=True)
    d=load_data(root/'data'/'fred_g17_snapshot_2011_2026.csv')
    panel,pred,main=evaluate(d)
    h6=evaluate(d,horizon=6)[2]
    lag3=evaluate(d,lag=3)[2]
    post=pred.loc[pred.index>='2022-01-01']
    precovid=pred.loc[pred.index<'2020-01-01']
    stats={'source_snapshot':'2026-10-19','data_rows':len(d),'data_first':str(d.index.min().date()),
           'data_last':str(d.index.max().date()),'formation_n':len(panel),
           'oos_first':str(pred.index.min().date()),'oos_last':str(pred.index.max().date()),
           'main':main,'horizon_6m':h6,'publication_lag_3m':lag3,
           'post_2022':metrics(post) if len(post)>10 else None,
           'pre_2020':metrics(precovid) if len(precovid)>10 else None,
           'block_bootstrap':moving_block_bootstrap(pred,n=simulations),
           'fixed_holdout_block_placebo':fixed_holdout_placebo(panel,n=simulations),
           'exposure_weight_perturbation':exposure_weight_sensitivity(d,n=1000),
           'bias_warning':'Latest-revised G.17 snapshot; no archival vintages, no company fundamentals, no stock returns; NOT investable alpha.'}
    pred.to_csv(root/'results'/'walk_forward_oos.csv',float_format='%.8f')
    panel.to_csv(root/'data'/'derived_formation_panel.csv',float_format='%.8f')
    (root/'results'/'metrics.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False))
    return d,panel,pred,stats

if __name__=='__main__':
    _,_,_,s=run()
    print(json.dumps({'oos_n':s['main']['full']['n'],'rmse':{k:round(s['main'][k]['rmse'],3) for k in ['mean','persistence','macro','full']},
                      'block_ci':s['block_bootstrap']['ci95'],'placebo_p':s['fixed_holdout_block_placebo']['p_one_sided_exploratory']},indent=2))
