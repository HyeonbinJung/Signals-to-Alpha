from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_analysis import read_data,panel_for,walk_forward,metrics,block_bootstrap,block_placebo

def test_source_dates_and_values():
    d=read_data();assert len(d)==107 and d.ECOMPCTSA.notna().sum()==106
    assert d.loc['2026-04-01','ECOMPCTSA']==17.1
    assert d.loc['2026-07-01','CES4349300001']==1835.4

def test_feature_is_past_only():
    d=read_data();p=panel_for(d)
    t=p.index[0];idx=d.index.get_loc(t)
    expected=np.tanh((d.ECOMPCTSA.iloc[idx-1]-d.ECOMPCTSA.iloc[idx-5])/2)
    assert np.isclose(p.iloc[0].ecom_factor,expected)

def test_purge_and_no_future_labels():
    p=panel_for(read_data());o=walk_forward(p)
    assert len(o)==57 and o.index[0].year==2012
    for t,row in o.iterrows():
        assert (p.origin_number<=row.origin_number-3).sum()==row.training_n

def test_baseline_identical_origins():
    o=walk_forward(panel_for(read_data()));m=metrics(o)
    assert all(x['n']==len(o) for x in m.values())
    assert np.isfinite(o[['mean','persistence','macro','full']]).all().all()

def test_placebo_deterministic():
    p=panel_for(read_data());o=walk_forward(p)
    a=block_placebo(p,o,n=20);b=block_placebo(p,o,n=20)
    assert a['exploratory_right_tail_fraction']==b['exploratory_right_tail_fraction']

def test_bootstrap_deterministic():
    o=walk_forward(panel_for(read_data()));a=block_bootstrap(o,n=20);b=block_bootstrap(o,n=20)
    assert a==b

def test_exposure_bounds():
    d=read_data()
    for w in (0.,.5,1.):
        p=panel_for(d,exposure=w)
        assert len(p)>90
