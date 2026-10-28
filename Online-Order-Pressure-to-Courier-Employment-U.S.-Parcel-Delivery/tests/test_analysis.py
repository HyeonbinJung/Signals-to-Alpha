from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from analysis import prepare,walkforward,score,gain,block_shuffle_factor,ridge
R=Path(__file__).resolve().parents[1]
d=prepare(pd.read_csv(R/'data/frozen_quarterly_courier_ecommerce_2026-10-26.csv'))
o=walkforward(d)
def test_raw_count():assert len(d)==106
def test_oos_count():assert len(o)>45
def test_purge():assert ((pd.to_datetime(o.date).dt.to_period('Q')-pd.to_datetime(o.last_training_target_date).dt.to_period('Q')).apply(lambda q:q.n)>=1).all()
def test_signal_lag():assert (d.loc[5:,'last_signal_observation']<d.loc[5:,'formation_date']).all()
def test_target_horizon():assert (pd.to_datetime(o.target_date).dt.to_period('Q')-pd.to_datetime(o.date).dt.to_period('Q')).apply(lambda x:x.n).eq(2).all()

def test_no_future_last_signal():assert (d.loc[5:,'last_signal_observation']==d.date.shift(1).loc[5:]).all()
def test_ridge_constant():assert np.isfinite(ridge(np.ones((10,2)),np.arange(10),np.ones(2)))
def test_model_count():assert len(score(o))==6
def test_no_missing_preds():assert np.isfinite(o[['mean','persistence','macro','warehouse_control','factor_only','full']].to_numpy()).all()
def test_factor_equation():assert np.allclose(d.factor.dropna(),(d.share_yoy_pp-.1*d.capacity_premium).dropna())
def test_block_shuffle():
 z=block_shuffle_factor(d,np.random.default_rng(42));assert np.array_equal(np.sort(z[np.isfinite(z)]),np.sort(d.factor.dropna().to_numpy()))
def test_same_origins():assert len(walkforward(d,ablate='no_capacity'))==len(o)
def test_score():assert np.isfinite(gain(o))
