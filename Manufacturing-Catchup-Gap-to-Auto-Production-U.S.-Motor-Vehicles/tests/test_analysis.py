from pathlib import Path
import numpy as np
import pandas as pd
from analysis import load_raw,make_panel,oos,ridge_predict,block_bootstrap,score,improvement

def test_raw_months():
    d=load_raw();assert len(d)==201 and d.date.is_unique

def test_spot_checks():
    d=load_raw().set_index('date'); s=pd.read_csv(Path(__file__).parents[1]/'data/spot_checks.csv',parse_dates=['date'])
    for row in s.itertuples():assert abs(d.loc[row.date,'auto_ip']-row.official_value)<1e-8

def test_no_future_features():
    d=load_raw().set_index('date');p=make_panel()
    row=p.iloc[20];t=row.origin
    assert abs(row.auto_yoy_lag-100*np.log(d.loc[t-pd.DateOffset(months=2),'auto_ip']/d.loc[t-pd.DateOffset(months=14),'auto_ip']))<1e-8

def test_target_horizon():
    d=load_raw().set_index('date');p=make_panel();row=p.iloc[30]
    assert abs(row.target-100*np.log(d.loc[row.origin+pd.DateOffset(months=3),'auto_ip']/d.loc[row.origin-pd.DateOffset(months=9),'auto_ip']))<1e-8

def test_oos_purge():
    p=make_panel();q=oos(p)
    for row in q.itertuples():
        n=((p.target_month<=row.origin-pd.DateOffset(months=2))&(p.origin<row.origin)).sum()
        assert row.n_train==n

def test_oos_sample_size():assert len(oos(make_panel()))>=60

def test_ridge_constant():
    assert abs(ridge_predict(np.ones((10,2)),np.ones(10)*7,np.ones(2))-7)<1e-8

def test_bootstrap_reproducible():
    p=oos(make_panel());assert np.array_equal(block_bootstrap(p,20,seed=42),block_bootstrap(p,20,seed=42))

def test_score_finite():assert np.isfinite(score(oos(make_panel())).rmse).all()

def test_factor_bounded():assert make_panel().factor.abs().max()<=1

def test_outcomes_not_equity():
    import json
    x=json.loads((Path(__file__).parents[1]/'study.json').read_text());assert not x['equity_alpha_established']

def test_source_register_complete():
    s=pd.read_csv(Path(__file__).parents[1]/'data/source_register.csv');assert len(s)>=5 and s.exact_url.str.startswith('https://').all()

def test_no_missing_data():assert not make_panel()[['target','factor','auto_yoy_lag']].isna().any().any()
