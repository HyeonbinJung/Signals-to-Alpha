import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis import (read_raw,make_panel,walk_forward,score,improvement,_ridge_numpy,
                      block_bootstrap,block_shuffle_placebo,exposure_sensitivity,scenario)

def test_source_length_years():
    r=read_raw();assert len(r)==25 and r.year.min()==1951 and r.year.max()==1975

def test_source_observation_spotchecks():
    r=read_raw();assert r.iloc[0].WORLDCONSUMPTION==3173 and r.iloc[-1].WORLDCONSUMPTION==7157.2

def test_no_null_or_duplicate_year():
    r=read_raw();assert r.notna().all().all() and r.year.is_unique

def test_fixed_factor_formula():
    p=make_panel(read_raw());np.testing.assert_allclose(p.relative_cost_relief,-p.lag_copper_price_growth+p.lag_aluminum_price_growth)

def test_stale_formation():
    p=make_panel(read_raw());assert (p.observed_through==p.formation_year-1).all()

def test_target_is_forward_log_growth():
    r=read_raw().set_index('year');p=make_panel(read_raw());t=int(p.iloc[0].formation_year)
    assert np.isclose(p.iloc[0].y_growth,100*np.log(r.at[t+1,'WORLDCONSUMPTION']/r.at[t,'WORLDCONSUMPTION']))

def test_purged_training():
    o=walk_forward(make_panel(read_raw()));assert (o.last_train_target_year<=o.formation_year-1).all()

def test_oos_ten_origins():
    o=walk_forward(make_panel(read_raw()));assert o.formation_year.tolist()==list(range(1965,1975))

def test_ridge_train_only_scaling():
    X=np.array([[1.],[2.],[3.],[4.],[5.],[6.]]);y=np.arange(6.)
    assert np.isfinite(_ridge_numpy(X,y,np.array([[8.]]),8.)).all()

def test_scorecard_consistency():
    o=walk_forward(make_panel(read_raw()));s=score(o);assert np.isclose(improvement(o),float(s.set_index('model').loc['controls','rmse']-s.set_index('model').loc['full','rmse']))

def test_block_bootstrap_deterministic():
    o=walk_forward(make_panel(read_raw()));a=block_bootstrap(o,draws=10);b=block_bootstrap(o,draws=10)
    pd.testing.assert_frame_equal(a,b)

def test_placebo_deterministic():
    p=make_panel(read_raw());pd.testing.assert_frame_equal(block_shuffle_placebo(p,0,draws=5),block_shuffle_placebo(p,0,draws=5))

def test_exposure_deterministic():
    r=read_raw();pd.testing.assert_frame_equal(exposure_sensitivity(r,draws=5),exposure_sensitivity(r,draws=5))

def test_alternative_horizon_does_not_use_future():
    r=read_raw();p=make_panel(r,horizon=2);o=walk_forward(p);assert (o.last_train_target_year<=o.formation_year-1).all()

def test_no_equity_claim():
    import json
    d=json.loads((Path(__file__).resolve().parents[1]/'study.json').read_text());assert d['equity_alpha_established'] is False
