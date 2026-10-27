import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_analysis as a

def test_raw_provenance():
    d=a.load_data()
    assert len(d)==201 and d.AIRRPMTSID11.notna().sum()==150
    assert np.isclose(d.loc[d.date.eq('2020-04-01'),'aerospace_ip'].iloc[0],54.3996)

def test_lagged_features_not_contemporaneous():
    d=a.load_data();p=a.panel();origin=p.iloc[15]
    t=d.index[d.date.eq(origin.date)][0]
    expected=100*np.log(d.AIRRPMTSID11.iloc[t-4]/d.AIRRPMTSID11.iloc[t-16])
    assert np.isclose(origin.air_mom,expected)

def test_training_purged():
    p=a.panel();o=a.forecast(p)
    for row in o.itertuples():
        assert (p.origin_month.iloc[row.n_train-1]+a.HORIZON+a.TARGET_RELEASE_BUFFER)<=row.origin_month
        if row.n_train<len(p):
            assert (p.origin_month.iloc[row.n_train]+a.HORIZON+a.TARGET_RELEASE_BUFFER)>row.origin_month

def test_no_forward_fill():
    d=a.load_data();assert d.loc[d.date.eq('2026-09-01'),'AIRRPMTSID11'].isna().all()

def test_target_horizon():
    d=a.load_data();p=a.panel();row=p.iloc[30];t=d.index[d.date.eq(row.date)][0]
    expected=100*np.log(d.aerospace_ip.iloc[t+6]/d.aerospace_ip.iloc[t-6]);assert np.isclose(row.target,expected)

def test_train_only_scaling():
    X=np.array([[1.,3.],[2.,5.],[3.,9.]])
    v=a.ridge_predict(X,np.array([1.,2.,3.]),np.array([2.,4.]))
    X2=np.vstack([X,[99999.,99999.]])
    assert np.isfinite(v) and v!=a.ridge_predict(X2,np.array([1.,2.,3.,99999.]),np.array([2.,4.]))

def test_placebo_length_and_block_preservation():
    x=np.arange(48);s=a.shuffle_block(x,np.random.default_rng(42),12)
    assert len(s)==48 and sorted(s)==list(x)
    for j in range(0,48,12):assert np.all(np.diff(s[j:j+12])==1)

def test_saved_oos_reproduction():
    a1=a.forecast(a.panel());a2=pd.read_csv(a.ROOT/'results/walk_forward_oos.csv')
    assert len(a1)==len(a2) and np.allclose(a1[['mean','persistence','macro','full','air_only','no_mfg']],a2[['mean','persistence','macro','full','air_only','no_mfg']])

def test_falsification_draw_counts():
    assert len(pd.read_csv(a.ROOT/'results/block_placebo_1000.csv'))==1000
    assert len(pd.read_csv(a.ROOT/'results/bootstrap_2000.csv'))==2000
    assert len(pd.read_csv(a.ROOT/'results/exposure_1000.csv'))==1000

def test_no_equity_claim():
    import json
    m=json.loads((a.ROOT/'results/metrics.json').read_text())
    assert m['company_fundamentals_tested'] is False and m['total_returns_tested'] is False
    assert m['historical_pit_vintages_verified'] is False

def test_rmse_identity():
    o=a.forecast(a.panel());s=a.scorecard(o)
    assert np.isclose(s.loc[s.model.eq('full'),'rmse_pp'].iloc[0],a.rmse(o.actual,o.full))

def test_horizon_and_regime_robustness():
    r=pd.read_csv(a.ROOT/'results/robustness.csv');assert {'3-month','12-month','exclude-2020-2021'}<=set(r.test)
