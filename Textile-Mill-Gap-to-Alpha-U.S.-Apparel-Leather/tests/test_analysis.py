import json
import numpy as np
import pandas as pd
from run_analysis import (read_data,panelize,walk_forward,metrics,delta,
    fast_augmented_predictions,block_permute,paired_bootstrap,leave_one_year_out,ROOT)

def test_source_integrity():
    d=read_data()
    assert len(d)==201 and np.isclose(d.iloc[-1]['IPG313A4S'],75.231)
    assert np.isclose(d.sum()['IPG315A6S'],20494.6714)

def test_formula_fixed_and_no_future_features():
    d=read_data();p=panelize(d)
    origin=pd.Timestamp('2018-06-01')
    g=100*np.log(d.loc['2018-04-01','IPG313A4S']/d.loc['2017-04-01','IPG313A4S'])
    gm=100*np.log(d.loc['2018-04-01','IPMAN']/d.loc['2017-04-01','IPMAN'])
    assert np.isclose(p.loc[origin,'factor'],np.tanh((g-gm)/10))
    assert p.factor.between(-1,1).all()

def test_label_purge():
    p=panelize(read_data());o=walk_forward(p)
    assert len(o)==111
    assert (o.last_training_origin+pd.DateOffset(months=8)<=o.index).all()
    assert (o.latest_feature_month==o.index-pd.DateOffset(months=2)).all()

def test_oos_model_predictions_and_metrics():
    p=panelize(read_data());o=walk_forward(p)
    assert np.allclose(o.full,fast_augmented_predictions(p,p.factor))
    stored=json.loads((ROOT/'results/metrics.json').read_text())
    assert np.isclose(delta(o),stored['delta_macro_minus_full_rmse'])
    assert metrics(o)['full']['rmse']>metrics(o)['macro']['rmse']

def test_block_permutation_preserves_values():
    rng=np.random.default_rng(123)
    x=np.arange(181)
    shuffled=block_permute(x,12,rng)
    assert len(shuffled)==len(x) and np.array_equal(np.sort(shuffled),x)

def test_bootstrap_is_reproducible():
    o=walk_forward(panelize(read_data()))
    a=paired_bootstrap(o,n=30,seed=15);b=paired_bootstrap(o,n=30,seed=15)
    assert np.array_equal(a,b) and np.isfinite(a).all()

def test_leave_one_year():
    o=walk_forward(panelize(read_data()))
    out=leave_one_year_out(o)
    assert len(out)==10 and (out.n<111).all()

def test_pit_and_equity_honesty():
    j=json.loads((ROOT/'study.json').read_text())
    assert j['equity_alpha_established'] is False
    assert 'NOT PIT' in j['evidence_level']

def test_heavy_saved_sample_counts():
    for path,n in [('results/block_placebo_1000.csv',1000),('results/bootstrap_2000.csv',2000),('results/exposure_1000.csv',1000)]:
        assert len(pd.read_csv(ROOT/path))==n

def test_source_qa_dates():
    r=pd.read_csv(ROOT/'data/source_register.csv')
    assert set(r.grade)=={'A','B'}
    assert all(r.exact_url.str.startswith('https://'))
