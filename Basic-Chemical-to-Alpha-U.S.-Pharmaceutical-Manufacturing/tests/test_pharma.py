from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_analysis import read_data,make_panel,walk_forward,score,improvement,shuffle_gap_blocks


def test_source_shape():
    d=read_data()
    assert len(d)==201
    assert str(d.index.min().date())=='2010-01-01'
    assert str(d.index.max().date())=='2026-09-01'
    assert d.notna().all().all()


def test_no_feature_leakage():
    raw=read_data(); p=make_panel(raw)
    d=p.index[25]; raw2=raw.copy()
    raw2.loc[d:,'CHEM']*=2
    p2=make_panel(raw2)
    assert np.isclose(p.loc[d,'gap'],p2.loc[d,'gap'])
    assert np.isclose(p.loc[d,'pharma_yoy'],p2.loc[d,'pharma_yoy'])


def test_target_horizon_and_purge():
    raw=read_data();p=make_panel(raw,horizon=6,release_lag=2)
    d=p.index[60];t=raw.index.get_loc(d)
    expected=100*np.log(raw.PHARMA.iloc[t+6]/raw.PHARMA.iloc[t-2])
    assert np.isclose(p.loc[d,'target'],expected)
    o=walk_forward(p)
    assert o.n_train.min()>=48
    assert o.index.max()<=raw.index[-7]


def test_training_cannot_see_future_labels():
    raw=read_data();p=make_panel(raw)
    o=walk_forward(p)
    d=o.index[15]
    row=p.loc[d]
    eligible=p.loc[p.origin_index<=row.origin_index-8]
    assert len(eligible)==o.loc[d,'n_train']


def test_metrics_are_computed():
    o=walk_forward(make_panel(read_data()))
    s=score(o)
    assert len(o)==111
    assert np.isfinite([v['rmse'] for v in s.values()]).all()
    assert np.isclose(improvement(o),s['macro']['rmse']-s['full']['rmse'])


def test_placebo_keeps_observation_count():
    p=make_panel(read_data()); rng=np.random.default_rng(42)
    shuffled=shuffle_gap_blocks(p,12,rng)
    assert len(shuffled)==len(p)
    assert np.array_equal(np.sort(shuffled.gap),np.sort(p.gap))


def test_weight_changes_are_not_full_sample_fit():
    p=make_panel(read_data(),gap_weights=(1.2,.8))
    assert np.isfinite(p.gap).all()
    assert (p.gap.abs()<=1).all()
