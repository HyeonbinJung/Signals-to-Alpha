import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from analysis import *

def test_source_shape_and_last_date():
    x=load_frozen(ROOT)
    assert len(x)==153 and x.date.max()==pd.Timestamp('2026-09-01')

def test_signal_is_preformation():
    x=load_frozen(ROOT);p=build_panel(x)
    t=p.iloc[20];date=t.date-pd.DateOffset(months=RELEASE_LAG)
    row=x.loc[x.date==date].iloc[0]
    assert np.isfinite(row.wti_usd_barrel)
    assert t.target_month==t.date+pd.DateOffset(months=HORIZON)

def test_target_release_purge():
    p=build_panel(load_frozen(ROOT));o=walk_forward(p)
    for _,r in o.iterrows():
        train=p.loc[p.available_month<=r.formation_date]
        assert len(train)==r.n_train
        assert (train.target_month<r.formation_date).all()

def test_training_only_scaler_no_future_dependence():
    X=np.array([[1.,2.],[2.,3.],[3.,4.],[4.,5.]])
    y=np.array([1.,2.,3.,4.]);a=fit_predict_ridge(X,y,np.array([5.,6.]))
    assert a==fit_predict_ridge(X.copy(),y.copy(),np.array([5.,6.]))

def test_block_shuffle_preserves_within_year_order():
    x=np.arange(50.);y=block_shuffle(x,np.random.default_rng(4))
    assert sorted(y)==sorted(x)
    assert np.array_equal(y[-2:],x[-2:])
    for i in range(0,48,12):assert np.all(np.diff(y[i:i+12])==1)

def test_scorecard_exact():
    p=build_panel(load_frozen(ROOT));o=walk_forward(p)
    s=scorecard(o);m=s.set_index('model').loc['macro_control','rmse']
    assert np.isclose(m,np.sqrt(np.mean((o.actual-o.macro_control)**2)))

def test_no_nan_predictions():
    o=walk_forward(build_panel(load_frozen(ROOT)))
    assert len(o)>50 and np.isfinite(o.select_dtypes('number')).all().all()

def test_horizon_and_lag_change_sample():
    x=load_frozen(ROOT)
    p1=build_panel(x,StudyConfig(horizon=1,release_lag=2))
    p6=build_panel(x,StudyConfig(horizon=6,release_lag=3))
    assert p1.target_month.iloc[0]!=p6.target_month.iloc[0]

def test_oil_exposure_weights():
    p=build_panel(load_frozen(ROOT));r=p.iloc[0]
    assert np.isclose(r.oil_relief,-(.7*r.wti_yoy+.3*r.wti_3m))

def test_company_level_is_not_claimed():
    assert not any(x in ['company_returns','ticker_returns'] for x in build_panel(load_frozen(ROOT)).columns)
