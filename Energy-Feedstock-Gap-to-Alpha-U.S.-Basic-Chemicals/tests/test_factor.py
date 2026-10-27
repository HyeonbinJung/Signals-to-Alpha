import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import pytest
from chemicals_factor import *
ROOT=Path(__file__).resolve().parents[1]

def test_source_integrity():
    d=load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv')
    assert len(d)==201
    assert d.DATE.iloc[0]=='2010-01' and d.DATE.iloc[-1]=='2026-09'
    assert abs(d.CHEM.sum()-19610.8607)<1e-4
    assert abs(d.henry_hub_usd_mmbtu.sum()-676.72)<1e-6
    assert abs(d.wti_usd_barrel.sum()-14514.83)<1e-6

def test_source_no_missing():
    assert not load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv').isna().any().any()

def test_feature_lag():
    d=load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv');p=make_panel(d)
    assert np.isclose(p.factor.iloc[30],p.oil_yoy.iloc[28]-p.gas_yoy.iloc[28])
    assert p.feature_observation_date.iloc[30]==p.date.iloc[28]

def test_outcome_horizon():
    d=load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv');p=make_panel(d)
    assert np.isclose(p.target.iloc[50],p.chem_yoy.iloc[56])

def test_training_purge():
    p=make_panel(load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv'))
    o=walk_forward(p)
    assert len(o)>80
    assert (o.train_last_target_observation<o.date).all()
    assert (o.formation_index-o.train_n>=7).all()

def test_no_full_sample_standardization():
    train=pd.DataFrame({'x':[0,1,2,3],'target':[1,2,2,3]})
    test=pd.DataFrame({'x':[100]})
    a=ridge_predict(train,test,['x'])
    train2=train.copy();train2['x']*=2;test2=test.copy();test2['x']*=2
    assert abs(a-ridge_predict(train2,test2,['x']))<1e-9

def test_placebo_block_integrity():
    p=make_panel(load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv'))
    s=block_shuffle_factor(p,12,np.random.default_rng(42))
    assert sorted(np.round(p.factor.dropna(),7))==sorted(np.round(s.factor.dropna(),7))

def test_bootstrap_reproducibility():
    p=make_panel(load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv'))
    o=walk_forward(p)
    assert np.array_equal(block_bootstrap(o,10,seed=4),block_bootstrap(o,10,seed=4))

def test_bad_input_rejected(tmp_path):
    d=load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv')
    d.loc[4,'CHEM']=0;d.to_csv(tmp_path/'bad.csv',index=False)
    with pytest.raises(ValueError):load_snapshot(tmp_path/'bad.csv')

def test_alternate_horizon_purge():
    p=make_panel(load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv'),horizon=12)
    o=walk_forward(p,horizon=12)
    assert (o.train_last_target_observation<o.date).all()
