import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis import load_raw,build_panel,walk_forward,scorecard,rmse,block_shuffle,ridge_prediction

@pytest.fixture(scope='module')
def raw():return load_raw()
@pytest.fixture(scope='module')
def panel(raw):return build_panel(raw)
@pytest.fixture(scope='module')
def pred(panel):return walk_forward(panel)

def test_raw_length(raw):assert len(raw)==203
def test_raw_dates(raw):assert raw.date.iloc[0]=='1959Q1' and raw.date.iloc[-1]=='2009Q3'
def test_raw_no_missing(raw):assert not raw.isna().any().any()
def test_positive_levels(raw):assert (raw[['realcons','realdpi','realgdp']]>0).all().all()
def test_factor_definition(raw,panel):
    i=int(panel.origin.iloc[10]);want=100*np.log(raw.realdpi.iloc[i-1]/raw.realdpi.iloc[i-5])-100*np.log(raw.realcons.iloc[i-1]/raw.realcons.iloc[i-5]);assert np.isclose(want,panel.factor.iloc[10])
def test_target_definition(raw,panel):
    i=int(panel.origin.iloc[12]);assert np.isclose(panel.target.iloc[12],100*np.log(raw.realcons.iloc[i+4]/raw.realcons.iloc[i]))
def test_strict_lag(raw):
    a=build_panel(raw);b=raw.copy();b.loc[120,'realdpi']*=100
    c=build_panel(b)
    assert np.allclose(a.loc[a.origin<121,'factor'],c.loc[c.origin<121,'factor'])
def test_purge(pred):assert (pred.train_last_origin+4<=pred.origin).all()
def test_oos_sample(pred):assert len(pred)>100
def test_no_train_full_sample(pred):assert (pred.train_n<203).all()
def test_models(pred):assert {'historical_mean','consumption_persistence','ar_ridge','macro_controls','macro_plus_factor'}.issubset(pred.columns)
def test_finite_scores(pred):assert np.isfinite(scorecard(pred).rmse_log_pp).all()
def test_rmse_nonnegative():assert rmse([1,2],[1,2])==0

def test_block_shuffle_preserves_values():
    x=np.arange(23);y=block_shuffle(x,np.random.default_rng(42),block=8);assert sorted(x)==sorted(y)
def test_ridge_constant_feature():assert np.isfinite(ridge_prediction(np.ones((20,2)),np.arange(20),np.ones(2)))
def test_horizon_robustness(raw):
    for h in [1,2,4]:
        p=build_panel(raw,horizon=h);q=walk_forward(p,horizon=h);assert (q.train_last_origin+h<=q.origin).all()
def test_lag_robustness(raw):
    for lag in [1,2,3]:assert len(build_panel(raw,lag=lag))>100

def test_stored_scorecard(pred):
    path=Path(__file__).resolve().parents[1]/'results'/'scorecard.csv'
    if not path.exists():pytest.skip('Run analysis first')
    expected=pd.read_csv(path).set_index('model').rmse_log_pp
    observed=scorecard(pred).set_index('model').rmse_log_pp
    assert np.allclose(expected.loc[observed.index],observed,atol=1e-10)
