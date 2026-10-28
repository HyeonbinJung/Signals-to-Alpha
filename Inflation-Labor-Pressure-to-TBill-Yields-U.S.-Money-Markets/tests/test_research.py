import json, hashlib
import numpy as np
import pandas as pd
import pytest
from run_analysis import ROOT, RAW, ALPHA, BLOCK, load_raw, build_panel, walk_forward, scores, block_shuffle, paired_block_bootstrap, ridge_predict


def test_raw_rows_and_periods():
    d=load_raw();assert len(d)==203;assert d.period.iloc[0]=='1959Q1';assert d.period.iloc[-1]=='2009Q3'

def test_raw_provenance_hash():
    d=json.loads((ROOT/'results/metrics.json').read_text());assert hashlib.sha256(RAW.read_bytes()).hexdigest()==d['raw_sha256']

def test_panel_target_forward_only():
    d=load_raw();p=build_panel(d)
    for row in p.iloc[::11].itertuples():
        assert np.isclose(row.target,d.tbilrate.iloc[row.origin_idx+1]-d.tbilrate.iloc[row.origin_idx])

def test_factor_lag_only():
    d=load_raw();p=build_panel(d)
    for row in p.iloc[::13].itertuples():
        assert row.input_period==d.period.iloc[row.origin_idx-1]
        assert np.isclose(row.factor,d.infl.iloc[row.origin_idx-1]-.5*(d.unemp.iloc[row.origin_idx-1]-d.unemp.iloc[row.origin_idx-2]))

def test_strict_purge():
    p=walk_forward(build_panel(load_raw()));assert (p.max_train_target_idx <= p.origin_idx-1).all()

def test_train_only_scaler_invariance_to_future():
    p=build_panel(load_raw());train=p.iloc[:80];test=p.iloc[[85]]
    before=ridge_predict(train,test,['rate_l','factor']);altered=p.copy();altered.loc[100:,'factor']=1e9
    after=ridge_predict(altered.iloc[:80],altered.iloc[[85]],['rate_l','factor']);assert np.isclose(before,after)

def test_placebo_block_preserves_within_block():
    a=np.arange(32);b=block_shuffle(a,np.random.default_rng(1),8)
    assert sorted(b.tolist())==list(a)
    assert all(np.array_equal(np.sort(b[i:i+8]),np.arange(8)*(1)+8*(b[i]//8)) for i in range(0,32,8))

def test_oos_and_scores():
    p=walk_forward(build_panel(load_raw()));s=scores(p)
    assert len(p)>75 and s.n.nunique()==1 and np.isfinite(s.rmse).all()

def test_bootstrap_deterministic():
    p=walk_forward(build_panel(load_raw()));assert np.array_equal(paired_block_bootstrap(p,10,seed=44),paired_block_bootstrap(p,10,seed=44))

def test_horizon_and_lag():
    p=build_panel(load_raw(),horizon=2,lag=2)
    assert p.horizon.eq(2).all() and p.lag.eq(2).all()
    assert len(walk_forward(p))>60

def test_no_pit_claim():
    m=json.loads((ROOT/'results/metrics.json').read_text())
    assert m['source_vintage_pit_verified'] is False and m['equity_alpha_established'] is False

def test_scorecard_matches_saved_oos():
    p=pd.read_csv(ROOT/'results'/'walk_forward_oos.csv');s=scores(p).set_index('model')
    old=pd.read_csv(ROOT/'results'/'scorecard.csv').set_index('model')
    assert np.allclose(s.rmse,old.rmse,atol=1e-8)

def test_1000_and_2000_draws():
    assert len(pd.read_csv(ROOT/'results'/'block_placebo_1000.csv'))==1000
    assert len(pd.read_csv(ROOT/'results'/'paired_block_bootstrap_2000.csv'))==2000
    assert len(pd.read_csv(ROOT/'results'/'exposure_perturbation_1000.csv'))==1000
