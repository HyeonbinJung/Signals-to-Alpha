import hashlib, sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import run_analysis as r

def test_frozen_source_and_spot_checks():
    d=r.load_raw()
    assert hashlib.sha256(r.RAW.read_bytes()).hexdigest()=='98ad34cabef652c021869fcfa74515a322272ddfb53c3e84dcfa65a5d9af5cc0'
    assert d.loc['2026-09-01',r.FOOD]==12393.0
    assert d.loc['2026-09-01',r.HOTEL]==1916.5
    assert d.loc['2026-06-01',r.AIR]==94921559.0
    assert np.isnan(d.loc['2026-09-01',r.AIR])

def test_lagged_features_are_not_contemporaneous():
    d=r.load_raw();p=r.build_panel(d)
    t=pd.Timestamp('2024-04-01')
    assert np.isclose(p.loc[t,'air_yoy_lag'],100*(d.loc['2023-12-01',r.AIR]/d.loc['2022-12-01',r.AIR]-1))
    assert np.isclose(p.loc[t,'food_yoy_lag'],100*(d.loc['2024-02-01',r.FOOD]/d.loc['2023-02-01',r.FOOD]-1))
    assert np.isclose(p.loc[t,'target'],100*(d.loc['2024-07-01',r.FOOD]/d.loc['2023-07-01',r.FOOD]-1))

def test_training_label_purge():
    p=r.build_panel(r.load_raw());o=r.walkforward(p)
    for _,v in o.iterrows():
        assert pd.Timestamp(v.last_train_origin)<=v.date-pd.DateOffset(months=5)
        assert v.n_train>=48

def test_factor_equation_and_weights():
    raw=r.load_raw();p=r.build_panel(raw,wa=1.1,wh=.9)
    assert np.allclose(p.tourism_gap,1.1*p.air_signal-.9*p.hotel_signal)

def test_baseline_and_reproducibility():
    p=r.build_panel(r.load_raw());o=r.walkforward(p);s=r.score(o)
    assert len(o)>50
    assert all(np.isfinite([v['rmse'],v['mae']]).all() for v in s.values())
    assert np.allclose(o.full,r.walkforward(p).full)

def test_fixed_scale_and_no_full_sample_normalization():
    p=r.build_panel(r.load_raw());assert np.all(np.abs(p.tourism_gap)<=2.0)
    x=np.array([[1.,2.],[2.,3.],[3.,4.],[4.,5.]])
    assert np.isfinite(r.ridge_predict(x,np.array([1.,2.,3.,4.]),np.array([5.,6.])))

def test_block_shuffle_reproducible():
    p=r.build_panel(r.load_raw());a=r.block_shuffle(p,np.random.default_rng(9));b=r.block_shuffle(p,np.random.default_rng(9))
    assert np.array_equal(a.tourism_gap,b.tourism_gap)
    assert np.allclose(np.sort(a.tourism_gap),np.sort(p.tourism_gap))

def test_block_bootstrap_reproducible():
    o=r.walkforward(r.build_panel(r.load_raw()));a=r.block_bootstrap(o,n=15);b=r.block_bootstrap(o,n=15)
    assert np.array_equal(a,b)

def test_saved_results_are_real_when_present():
    path=ROOT/'results/metrics.json'
    if not path.exists():pytest.skip('analysis not executed')
    import json
    m=json.loads(path.read_text());o=pd.read_csv(ROOT/'results/walk_forward_oos.csv')
    assert m['oos_n']==len(o)
    assert np.isclose(m['scores']['full']['rmse'],np.sqrt(np.mean((o.full-o.actual)**2)))
