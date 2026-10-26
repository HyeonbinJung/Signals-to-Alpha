from pathlib import Path
import json
import numpy as np
import pandas as pd
from run_analysis import read_data,panel_from,walk_forward,score,ridge_predict,block_bootstrap

def test_frozen_dates_and_counts():
    raw=read_data();assert len(raw)==153;assert raw.AIRRPMTSID11.count()==150
    assert raw.loc['2019-12-01','AIRRPMTSID11']==90063718
    assert raw.loc['2026-09-01','CES7072200001']==12393.0

def test_source_metadata_and_vintage():
    sources=pd.read_csv('data/source_register.csv')
    assert len(sources)==3 and set(sources.quality)=={'A'}
    assert (sources.historical_vintages_available=='NO').all()
    assert sources.source_url.str.startswith('https://fred.stlouisfed.org/data/').all()

def test_feature_no_future_values():
    raw=read_data();p=panel_from(raw)
    # Modifying any data after formation cannot change that formation's features.
    cut=pd.Timestamp('2019-08-01');before=p.loc[cut,['travel_gap','accom_signal','food_signal']].to_numpy(dtype=float)
    altered=raw.copy();altered.loc[altered.index>cut,altered.columns]*=2
    after=panel_from(altered).loc[cut,['travel_gap','accom_signal','food_signal']].to_numpy(dtype=float)
    assert np.allclose(before,after)

def test_purged_walkforward_and_counts():
    p=panel_from(read_data());o=walk_forward(p)
    assert len(p)==122 and len(o)==82
    for t,r in o.iterrows():
        train=p.loc[p.origin<=t-pd.DateOffset(months=5)]
        assert len(train)==r.n_train and len(train)>=36

def test_ridge_train_only_and_constant_feature():
    X=np.ones((40,3));y=np.arange(40.)
    assert np.isclose(ridge_predict(X,y,np.ones(3)),y.mean())

def test_baselines_and_no_claim_of_alpha():
    r=json.loads(Path('results/metrics.json').read_text())
    assert r['equity_alpha_established'] is False and r['PIT'] is False
    assert r['oos_n']==82 and r['scores']['full']['rmse']>r['scores']['mean']['rmse']

def test_block_bootstrap_reproducible():
    o=walk_forward(panel_from(read_data()));a=block_bootstrap(o,n=30,seed=19)
    b=block_bootstrap(o,n=30,seed=19)
    assert np.array_equal(a,b)

def test_all_outputs_exist_and_nonempty():
    r=json.loads(Path('results/metrics.json').read_text())
    assert r['block_shuffle_draws']>=1000 and r['block_bootstrap_draws']>=2000 and r['exposure_draws']>=1000
    assert len(list(Path('figures').glob('*.png')))>=3
    assert Path('results/walk_forward_oos.csv').stat().st_size>1000

def test_robustness_is_not_only_primary():
    r=json.loads(Path('results/metrics.json').read_text())
    assert len(r['robustness'])>=7 and len(r['leave_one_year_out'])>=5
