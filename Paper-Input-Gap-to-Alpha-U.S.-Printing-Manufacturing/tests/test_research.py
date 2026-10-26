import numpy as np
import pandas as pd
import pytest
from run_analysis import read_official_transcription,make_panel,walk_forward,metrics,ridge_predict,moving_block_bootstrap,block_permutation_factor

def test_frozen_source_201_months():
    d=read_official_transcription();assert len(d)==201
    assert str(d.index.min().date())=='2010-01-01'
    assert str(d.index.max().date())=='2026-09-01'
    assert d.notna().all().all()

def test_source_spot_checks():
    d=read_official_transcription()
    assert d.loc['2026-09-01','printing_ip']==74.0432
    assert d.loc['2020-04-01','paper_ip']==95.7202

def test_future_labels_are_not_features():
    d=read_official_transcription();p=make_panel(d)
    assert p.loc['2018-01-01','print_momentum']==pytest.approx(100*np.log(d.loc['2017-12-01','printing_ip']/d.loc['2016-12-01','printing_ip']))
    assert p.loc['2018-01-01','target']==pytest.approx(100*np.log(d.loc['2018-04-01','printing_ip']/d.loc['2017-04-01','printing_ip']))

def test_training_labels_purged():
    o=walk_forward(make_panel(read_official_transcription()))
    assert (o.last_train_outcome_date<o.origin).all()
    assert (o.n_train>=36).all()
    assert (o.outcome_date>o.origin).all()

def test_baselines_same_origins():
    o=walk_forward(make_panel(read_official_transcription()))
    m=metrics(o)
    assert len({v['n'] for v in m.values()})==1
    assert np.isfinite([v['rmse'] for v in m.values()]).all()

def test_ridge_intercept_no_future_fit():
    X=np.arange(10).reshape(-1,1).astype(float)
    assert ridge_predict(X,np.ones(10)*4,np.array([999.]))==pytest.approx(4.)

def test_paper_weight_changes_factor_only():
    d=read_official_transcription();a=make_panel(d,paper_weight=1);b=make_panel(d,paper_weight=1.2)
    assert np.allclose(a.target,b.target)
    assert not np.allclose(a.factor,b.factor)

def test_invalid_release_buffer():
    with pytest.raises(ValueError):make_panel(read_official_transcription(),lag=0)

def test_block_bootstrap_deterministic():
    o=walk_forward(make_panel(read_official_transcription()))
    assert np.allclose(moving_block_bootstrap(o,draws=10,seed=2),moving_block_bootstrap(o,draws=10,seed=2))

def test_placebo_length_and_finite():
    p=make_panel(read_official_transcription());rng=np.random.default_rng(2)
    z=block_permutation_factor(p,rng)
    assert len(z)==len(p) and np.isfinite(z).all()

def test_fast_full_matches_reference():
    from run_analysis import fast_full_predictions
    p=make_panel(read_official_transcription())
    o=walk_forward(p)
    fast=fast_full_predictions(p,p.factor.to_numpy())
    assert np.allclose(fast,o.full.to_numpy(),rtol=0,atol=1e-9)

def test_2026_observations_are_not_full_year():
    raw=read_official_transcription()
    assert len(raw.loc['2026'])==9
