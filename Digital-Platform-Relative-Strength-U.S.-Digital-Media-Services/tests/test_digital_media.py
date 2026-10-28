import json
import hashlib
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from analysis import (load_prices,panel,walk_forward,scorecard,paired_improvement,FastRefit,
                      fast_placebo,fast_exposure_sensitivity,moving_block_bootstrap,
                      CORE,CONTROL,EXPOSURE,rank_diagnostics,feature_matrix,ridge_fit_predict)

@pytest.fixture(scope='module')
def prices():return load_prices(ROOT/'data'/'plotly_stocks_2018_2019_frozen.csv')
@pytest.fixture(scope='module')
def df(prices):return panel(prices)
@pytest.fixture(scope='module')
def oos(df):return walk_forward(df)

def test_frozen_sha():
    p=ROOT/'data'/'plotly_stocks_2018_2019_frozen.csv'
    assert hashlib.sha256(p.read_bytes()).hexdigest()=='b80a2e38aa02076ad977f89f9595853f5e69a0bd1e1d5726b761977101009a9e'

def test_observations_and_time(prices):
    assert len(prices)==105 and prices.date.iloc[0]==pd.Timestamp('2018-01-01')
    assert prices.date.iloc[-1]==pd.Timestamp('2019-12-30')
    assert np.allclose(prices[list(CORE+CONTROL)].iloc[0],1)

def test_panel_structure(df):
    assert len(df)==372 and df.t.nunique()==93 and df.firm.nunique()==4
    assert ((df.target_date-df.date).dt.days==28).all()
    assert df[['y','factor','lag4','lag1','vol4','bench8']].notna().all().all()

def test_exposure_not_fitted(df):
    for f,w in EXPOSURE.items():
        g=df[df.firm==f]
        assert np.allclose(g.factor,w*np.tanh(g.rel8/20))

def test_no_future_feature_leak(prices,df):
    modified=prices.copy()
    modified.loc[modified.index>=70,list(CORE+CONTROL)]*=1.77
    d=panel(modified)
    old=df.loc[df.t<=65,['t','firm','factor','lag4','lag1','vol4','bench8']].reset_index(drop=True)
    new=d.loc[d.t<=65,['t','firm','factor','lag4','lag1','vol4','bench8']].reset_index(drop=True)
    pd.testing.assert_frame_equal(old,new)

def test_training_labels_purged(oos):
    assert oos.t.nunique()==65
    assert oos.groupby(['t','firm']).model.nunique().eq(6).all()
    assert (oos.train_origins>=25).all()
    assert (oos.train_rows>=100).all()
    assert (oos.target_date>oos.date).all()

def test_baselines_and_improvement(oos):
    s=scorecard(oos).set_index('model')
    assert set(s.index)=={'mean','persistence','momentum','factor_only','control','augmented'}
    assert np.isclose(s.loc['control','rmse_pp'],6.943659225438157)
    assert np.isclose(paired_improvement(oos),-0.07059382327363029)

def test_fast_exact_reproduction(df,oos):
    r=FastRefit(df)
    p=r.augmented_predictions(r.df.factor.to_numpy())
    assert np.allclose(p,oos.loc[oos.model=='augmented','prediction'].to_numpy(),atol=1e-10)

def test_train_only_standardization():
    x=np.array([[1.,1.],[2.,2.],[3.,3.]])
    y=np.array([0.,1.,2.]);new=np.array([[1000.,1000.]])
    assert np.isfinite(ridge_fit_predict(x,y,new)).all()
    assert np.isclose(ridge_fit_predict(x,y,np.array([[2.,2.]]))[0],1.)

def test_placebo_reproducible(df):
    a=fast_placebo(df,n=12,seed=13);b=fast_placebo(df,n=12,seed=13)
    pd.testing.assert_frame_equal(a,b)
    assert a.rmse_improvement_pp.std()>0

def test_bootstrap_block_reproducible(oos):
    a=moving_block_bootstrap(oos,n=15,seed=17);b=moving_block_bootstrap(oos,n=15,seed=17)
    pd.testing.assert_frame_equal(a,b)
    assert a.rmse_improvement_pp.std()>0

def test_exposure_reproducible(df):
    a=fast_exposure_sensitivity(df,n=12,seed=19)
    b=fast_exposure_sensitivity(df,n=12,seed=19)
    pd.testing.assert_frame_equal(a,b)
    assert a[list(CORE)].ge(0).all().all() and a[list(CORE)].le(1).all().all()

def test_ic_spread_is_cross_sectional(oos):
    d=rank_diagnostics(oos)
    assert len(d)==65 and d.rank_ic.between(-1,1).all()
    assert d.spread_pp.notna().all()

def test_source_qa_and_release_dates(oos):
    s=pd.read_csv(ROOT/'data'/'source_register.csv')
    assert set(s.grade)=={'A','B','C'}
    assert (s[s.grade=='A'].publication_date<'2018-03-01').all()
    assert oos.date.min()>=pd.Timestamp('2018-03-01')
    assert s[s.grade=='B'].publication_date.iloc[0]=='UNKNOWN'

def test_reported_artifacts_and_counts():
    j=json.loads((ROOT/'results'/'summary.json').read_text())
    assert j['n_oos_predictions_per_model']==260
    assert j['n_oos_origins']==65
    assert len(pd.read_csv(ROOT/'results'/'placebo.csv'))==1000
    assert len(pd.read_csv(ROOT/'results'/'bootstrap.csv'))==2000
    assert len(pd.read_csv(ROOT/'results'/'exposure.csv'))==1000
    assert len(list((ROOT/'figures').glob('*.png')))>=12
    assert j['publication_vintage']=='UNKNOWN' and j['total_return_adjustment']=='UNKNOWN'

def test_lookahead_not_claimed():
    txt=(ROOT/'data'/'source_qa.md').read_text()
    assert 'UNKNOWN' in txt and 'not' in txt.lower()
