import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from analysis import *

def test_raw_integrity():
    d=load_data();assert len(d)==201 and d.date.is_unique

def test_target_horizon():
    raw=load_data();p=build_panel(raw)
    row=p.iloc[0]; t=raw.set_index('date')
    assert np.isclose(row.target,100*np.log(t.loc[row.target_month,'paper_ip']/t.loc[row.target_month-pd.DateOffset(months=12),'paper_ip']))

def test_no_current_input():
    p=build_panel(load_data());assert ((p.date.dt.to_period('M')-p.feature_month.dt.to_period('M')).apply(lambda x:x.n)==2).all()

def test_purge():
    p=walk_forward(build_panel(load_data()));assert (p.train_last_target_month<=p.origin-pd.DateOffset(months=2)).all()

def test_oos_sample():
    p=walk_forward(build_panel(load_data()));assert len(p)>60 and p.origin.is_monotonic_increasing

def test_baseline_not_future():
    raw=load_data();p=build_panel(raw);pr=walk_forward(p);r=pr.iloc[0]
    train=p.loc[p.target_month<=r.origin-pd.DateOffset(months=2)]
    assert np.isclose(r['mean'],train.target.mean())

def test_score_consistency():
    p=walk_forward(build_panel(load_data()));s=score(p).set_index('model')
    assert np.isclose(s.loc['augmented','rmse_log_pp'],np.sqrt(np.mean((p.actual-p.augmented)**2)))

def test_block_shuffle_permutation():
    x=np.arange(123);rng=np.random.default_rng(1);y=shuffle_blocks(x,12,rng)
    assert len(y)==len(x) and set(x)==set(y)

def test_bootstrap_count():
    p=walk_forward(build_panel(load_data()));a=block_bootstrap(p,draws=17);assert len(a)==17 and np.isfinite(a).all()

def test_rank_spread_not_returns():
    p=walk_forward(build_panel(load_data()));q,s=rank_spread(p);assert q['count'].sum()==len(p) and np.isfinite(s)

def test_lag_sensitivity_distinct():
    raw=load_data();p1=build_panel(raw,lag=1);p3=build_panel(raw,lag=3)
    assert not np.isclose(p1.factor.iloc[-1],p3.factor.iloc[-1])

def test_revised_snapshot_flag():
    import json
    s=ROOT/'results/summary.json'
    if s.exists():assert json.loads(s.read_text())['historical_vintages_verified'] is False

def test_ten_official_spot_checks():
    raw=load_data().set_index('date')
    checks=pd.read_csv(ROOT/'data/official_spot_checks_2026-10-27.csv',parse_dates=['date'])
    assert len(checks)==10
    for row in checks.itertuples():
        assert np.isclose(raw.loc[row.date,row.series],row.official_value,rtol=0,atol=1e-8)
