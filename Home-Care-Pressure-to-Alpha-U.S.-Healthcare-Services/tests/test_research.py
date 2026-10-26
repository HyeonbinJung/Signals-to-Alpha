from pathlib import Path
import numpy as np
import pandas as pd
from run_analysis import load_data, make_panel, walk_forward, fast_full_predictions, score, shuffle_blocks


def test_source_snapshot_shape_and_endpoints():
    d=load_data();assert d.shape==(201,5)
    assert d.loc['2026-09-01','home']==1894.2
    assert d.loc['2026-09-01','hospital']==5797.8
    assert d.loc['2026-09-01','nursing']==3489.4


def test_target_correct_yoy_at_forward_month():
    d=load_data();p=make_panel(d,horizon=6,lag=2)
    t=pd.Timestamp('2018-06-01');expected=100*np.log(d.loc['2018-12-01','nursing']/d.loc['2017-12-01','nursing'])
    assert np.isclose(p.loc[t,'target'],expected)


def test_factor_uses_only_two_month_lagged_inputs():
    d=load_data();p=make_panel(d)
    t=pd.Timestamp('2019-05-01')
    expected=np.tanh((100*np.log(d.loc['2019-03-01','home']/d.loc['2018-03-01','home'])-100*np.log(d.loc['2019-03-01','hospital']/d.loc['2018-03-01','hospital']))/5)
    assert np.isclose(p.loc[t,'factor'],expected)


def test_no_target_leakage_from_future_data_into_factor():
    d=load_data();p=make_panel(d)
    mutated=d.copy();mutated.loc['2026-09-01','nursing']*=2
    p2=make_panel(mutated)
    assert np.isclose(p.loc['2024-01-01','factor'],p2.loc['2024-01-01','factor'])


def test_train_label_purge_and_minimum_history():
    p=make_panel(load_data());o=walk_forward(p)
    assert len(o)==99 and o.index[0]==pd.Timestamp('2018-01-01')
    assert o.index[-1]==pd.Timestamp('2026-03-01')
    assert o.train_n.min()>=60
    # Earliest eligible label at origin 2018-01 is from origin 2017-06 or earlier.
    assert o.iloc[0].train_n==(p.index<=pd.Timestamp('2017-06-01')).sum()


def test_fast_placebo_refit_matches_main_walkforward():
    p=make_panel(load_data());o=walk_forward(p)
    assert np.allclose(fast_full_predictions(p),o.full.to_numpy(),rtol=1e-10,atol=1e-10)


def test_block_shuffle_preserves_multiset():
    x=np.arange(101);z=shuffle_blocks(x,12,np.random.default_rng(9))
    assert sorted(x)==sorted(z) and len(x)==len(z)


def test_negative_primary_result_is_computed_not_asserted_constant():
    p=make_panel(load_data());o=walk_forward(p);s=score(o)
    assert s['full']['rmse']>s['macro']['rmse']
    assert s['full']['rmse']>s['persistence']['rmse']


def test_frozen_source_checksum_matches_manifest():
    import hashlib,json
    root=Path(__file__).resolve().parents[1]
    m=json.loads((root/'results/metrics.json').read_text())
    assert hashlib.sha256((root/'data/fred_ces_2010_2026_snapshot.csv').read_bytes()).hexdigest()==m['source_sha256']
