"""Retrospective Grunfeld investment-panel forecasting; no security return claims."""
from __future__ import annotations
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

SEED = 20261027
RAW = 'data/grunfeld_statsmodels_0_14_6_frozen.csv'
FIRMS = ['American Steel','Atlantic Refining','Chrysler','Diamond Match','General Electric','General Motors','Goodyear','IBM','US Steel','Union Oil','Westinghouse']
GROUPS = {
 'American Steel':'Metals','US Steel':'Metals',
 'Atlantic Refining':'Petroleum','Union Oil':'Petroleum',
 'Chrysler':'Automotive','General Motors':'Automotive',
 'General Electric':'Electrical/industrial','Westinghouse':'Electrical/industrial',
 'Goodyear':'Tires/rubber','IBM':'Business machines','Diamond Match':'Consumer materials'
}

def load_raw(root:Path)->pd.DataFrame:
    d=pd.read_csv(root/RAW)
    assert list(d.columns)==['invest','value','capital','firm','year']
    assert d.shape==(220,5)
    assert d.firm.nunique()==11 and d.year.nunique()==20
    assert not d.duplicated(['firm','year']).any() and not d.isna().any().any()
    assert (d[['invest','value','capital']]>0).all().all()
    assert d.groupby('firm').year.agg(['min','max','count']).eq([1935,1954,20]).all().all()
    return d.sort_values(['firm','year']).reset_index(drop=True)

def prepare(raw:pd.DataFrame, lag:int=1, correct_ussteel:bool=False)->pd.DataFrame:
    d=raw.copy()
    if correct_ussteel:
        mask=(d.firm=='US Steel')&(d.year==1946)
        assert len(d[mask])==1 and np.isclose(d.loc[mask,'capital'].iloc[0],132.6)
        d.loc[mask,'capital']=232.6 # AER documentation correction, not a silent replacement
    d=d.sort_values(['firm','year']).reset_index(drop=True)
    g=d.groupby('firm',sort=False)
    d['log_invest']=np.log(d.invest)
    d['log_value']=np.log(d.value)
    d['log_capital']=np.log(d.capital)
    for col in ['log_invest','log_value','log_capital']:
        d[col+'_lag']=g[col].shift(lag)
    d['q_proxy']=d.log_value_lag-d.log_capital_lag
    d['value_momentum']=g['log_value'].shift(lag)-g['log_value'].shift(lag+1)
    d['invest_momentum']=g['log_invest'].shift(lag)-g['log_invest'].shift(lag+1)
    d['group']=d.firm.map(GROUPS)
    d['lag_year']=d.year-lag
    return d.dropna(subset=['log_invest_lag','log_capital_lag','q_proxy','value_momentum','invest_momentum']).reset_index(drop=True)

BASE=['log_invest_lag','log_capital_lag','invest_momentum']
FACTOR=['q_proxy']

def _ridge_predict(train:pd.DataFrame,test:pd.DataFrame,features:list[str],alpha:float=12.0)->np.ndarray:
    scaler=StandardScaler()
    xtrain=scaler.fit_transform(train[features]); xtest=scaler.transform(test[features])
    # Fixed firm effects; no train/test leakage: categories are predefined in the frozen universe.
    t1=np.column_stack([xtrain]+[(train.firm.to_numpy()==f).astype(float) for f in FIRMS[1:]])
    t2=np.column_stack([xtest]+[(test.firm.to_numpy()==f).astype(float) for f in FIRMS[1:]])
    return Ridge(alpha=alpha).fit(t1,train.log_invest.to_numpy()).predict(t2)

def walkforward(d:pd.DataFrame,first:int=1945,last:int=1954,embargo:int=1,
                factor:bool=True,alt_features:list[str]|None=None)->pd.DataFrame:
    records=[]
    for y in range(first,last+1):
        # Strict target purge: train target year <= y-1-embargo.
        train=d[d.year<=y-1-embargo]
        test=d[d.year==y]
        if len(test)==0 or len(train)<55:continue
        cfeatures=BASE if alt_features is None else alt_features
        full=cfeatures+FACTOR if factor else cfeatures
        control=_ridge_predict(train,test,cfeatures)
        augmented=_ridge_predict(train,test,full)
        # Firm-specific historical mean uses only training targets, not current/future years.
        fmeans=train.groupby('firm').log_invest.mean()
        global_mean=train.log_invest.mean()
        hist=test.firm.map(fmeans).fillna(global_mean).to_numpy()
        persist=test.log_invest_lag.to_numpy()
        for i,(_,row) in enumerate(test.iterrows()):
            records.append(dict(year=y,firm=row.firm,group=row.group,truth=row.log_invest,
                                control=control[i],full=augmented[i],historical_mean=hist[i],
                                persistence=persist[i],q_proxy=row.q_proxy,
                                observed_invest=row.invest,train_rows=len(train),
                                max_train_target_year=int(train.year.max()),lag_year=int(row.lag_year)))
    return pd.DataFrame(records)

def metrics(p:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for name in ['historical_mean','persistence','control','full']:
        err=p[name].to_numpy()-p.truth.to_numpy()
        rows.append(dict(model=name,n=len(err),rmse_log=float(np.sqrt(np.mean(err**2))),
                         mae_log=float(np.mean(abs(err))),
                         rmse_invest_millions_1947=float(np.sqrt(np.mean((np.exp(p[name])-p.observed_invest)**2)))))
    return pd.DataFrame(rows)

def improvement(p:pd.DataFrame)->float:
    t=p.truth.to_numpy()
    return float(np.sqrt(np.mean((p.control-t)**2))-np.sqrt(np.mean((p.full-t)**2)))

def year_block_bootstrap(p:pd.DataFrame, n:int=2000, block:int=2,seed:int=SEED)->pd.DataFrame:
    rng=np.random.default_rng(seed)
    years=np.sort(p.year.unique()); ny=len(years)
    out=[]
    for i in range(n):
        selected=[]
        while len(selected)<ny:
            start=int(rng.integers(0,ny))
            selected.extend([years[(start+j)%ny] for j in range(block)])
        sub=pd.concat([p[p.year==y] for y in selected[:ny]],ignore_index=True)
        out.append({'iteration':i+1,'rmse_improvement':improvement(sub)})
    return pd.DataFrame(out)

def block_shuffle_factor(d:pd.DataFrame,rng:np.random.Generator,block:int=3)->pd.DataFrame:
    x=d.copy()
    for f,grp in x.groupby('firm',sort=False):
        idx=grp.sort_values('year').index.to_numpy()
        vals=x.loc[idx,'q_proxy'].to_numpy()
        blocks=[vals[i:i+block] for i in range(0,len(vals),block)]
        perm=rng.permutation(len(blocks))
        # Preserve exact length; rotating blocks of unequal length can misalign, so shuffle only full blocks.
        full=len(vals)//block
        seq=np.concatenate([blocks[j] for j in rng.permutation(full)]+blocks[full:]) if full else vals
        x.loc[idx,'q_proxy']=seq
    return x

def block_placebo(d:pd.DataFrame, observed:float,n:int=1000,seed:int=SEED)->pd.DataFrame:
    rng=np.random.default_rng(seed)
    out=[]
    for i in range(n):
        p=walkforward(block_shuffle_factor(d,rng))
        out.append({'iteration':i+1,'rmse_improvement':improvement(p)})
    return pd.DataFrame(out)

def perturbations(d:pd.DataFrame,n:int=1000,seed:int=SEED)->pd.DataFrame:
    rng=np.random.default_rng(seed)
    out=[]
    for i in range(n):
        x=d.copy()
        weights={f:rng.uniform(.8,1.2) for f in FIRMS}
        x['q_proxy']=x.q_proxy*x.firm.map(weights)
        p=walkforward(x)
        out.append({'iteration':i+1,'rmse_improvement':improvement(p)})
    return pd.DataFrame(out)

def leave_one_company_out(d:pd.DataFrame)->pd.DataFrame:
    out=[]
    for f in FIRMS:
        p=walkforward(d[d.firm!=f])
        out.append({'excluded_firm':f,'n':len(p),'rmse_improvement':improvement(p),
                    'control_rmse':metrics(p).set_index('model').loc['control','rmse_log'],
                    'full_rmse':metrics(p).set_index('model').loc['full','rmse_log']})
    return pd.DataFrame(out)

def rank_diagnostics(p:pd.DataFrame)->pd.DataFrame:
    out=[]
    for y,sub in p.groupby('year'):
        delta_pred=sub.full-sub.control
        delta_actual=sub.truth-sub.control
        rho=spearmanr(delta_pred,delta_actual).statistic
        top=sub.loc[delta_pred.nlargest(3).index]
        bottom=sub.loc[delta_pred.nsmallest(3).index]
        spread=(top.truth-top.control).mean()-(bottom.truth-bottom.control).mean()
        out.append({'year':y,'n_firms':len(sub),'fundamental_residual_rank_ic':rho,
                    'top3_minus_bottom3_realized_residual_log':spread})
    return pd.DataFrame(out)

def run(root:Path,fast:bool=False)->dict:
    raw=load_raw(root)
    d=prepare(raw)
    results=root/'results';figures=root/'figures';results.mkdir(exist_ok=True);figures.mkdir(exist_ok=True)
    d.to_csv(root/'data/derived_panel.csv',index=False)
    p=walkforward(d);assert len(p)==110 and p.year.nunique()==10
    assert (p.max_train_target_year<=p.year-2).all()
    p.to_csv(results/'oos_predictions.csv',index=False)
    m=metrics(p);m.to_csv(results/'baseline_scorecard.csv',index=False)
    r=rank_diagnostics(p);r.to_csv(results/'fundamental_rank_diagnostics.csv',index=False)
    loo=leave_one_company_out(d);loo.to_csv(results/'leave_one_company_out.csv',index=False)
    variants=[]
    for lag in [1,2,3]:
        pp=walkforward(prepare(raw,lag=lag))
        variants.append({'scenario':f'feature_lag_{lag}y','n':len(pp),'rmse_improvement':improvement(pp)})
    for start,end,label in [(1945,1949,'1945_1949'),(1950,1954,'1950_1954')]:
        sub=p[p.year.between(start,end)]
        variants.append({'scenario':label,'n':len(sub),'rmse_improvement':improvement(sub)})
    corrected=walkforward(prepare(raw,correct_ussteel=True))
    variants.append({'scenario':'us_steel_1946_capital_corrected','n':len(corrected),'rmse_improvement':improvement(corrected)})
    for feature_set,label in [(['log_invest_lag','log_capital_lag'],'no_invest_momentum'),
                              (['log_invest_lag','invest_momentum'],'no_capital'),
                              (['log_capital_lag','invest_momentum'],'no_invest_level')]:
        pp=walkforward(d,alt_features=feature_set)
        variants.append({'scenario':label,'n':len(pp),'rmse_improvement':improvement(pp)})
    variants=pd.DataFrame(variants);variants.to_csv(results/'robustness_scenarios.csv',index=False)
    bootstrap=year_block_bootstrap(p,n=200 if fast else 2000)
    bootstrap.to_csv(results/'bootstrap_year_blocks.csv',index=False)
    placebo=block_placebo(d,improvement(p),n=100 if fast else 1000)
    placebo.to_csv(results/'block_shuffle_placebo.csv',index=False)
    pert=perturbations(d,n=100 if fast else 1000)
    pert.to_csv(results/'exposure_perturbations.csv',index=False)
    summary={
      'dataset':'statsmodels.datasets.grunfeld', 'data_observations':len(raw),
      'n_firms':int(raw.firm.nunique()),'years':[int(raw.year.min()),int(raw.year.max())],
      'oos_years':[int(p.year.min()),int(p.year.max())], 'oos_firm_years':len(p),
      'minimum_train_rows':int(p.train_rows.min()),'max_train_target_year_leq_test_minus_2':bool((p.max_train_target_year<=p.year-2).all()),
      'control_minus_full_rmse':improvement(p),
      'bootstrap_ci_95':np.quantile(bootstrap.rmse_improvement,[.025,.975]).tolist(),
      'placebo_exploratory_upper_tail_fraction':float((1+(placebo.rmse_improvement>=improvement(p)).sum())/(1+len(placebo))),
      'perturbation_positive_fraction':float((pert.rmse_improvement>0).mean()),
      'fundamental_residual_rank_ic_mean':float(r.fundamental_residual_rank_ic.mean()),
      'fundamental_residual_top_bottom_spread_mean':float(r.top3_minus_bottom3_realized_residual_log.mean()),
      'no_pit':True,'no_equity_returns':True,'full_repetitions':not fast
    }
    import json
    (results/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
