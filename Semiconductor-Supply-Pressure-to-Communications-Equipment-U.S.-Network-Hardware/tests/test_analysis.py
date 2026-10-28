import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import run_analysis as r

def test_exact_inherited_source_blob():
    assert r.git_blob_sha(r.RAW.read_bytes())==r.EXPECTED_GIT_BLOB

def test_raw_integrity():
    assert r.load_raw().shape==(189,5)

def test_factor_equation():
    d=r.load_raw();p=r.build_panel(d)
    x=p.iloc[0]
    assert np.isclose(x.factor,np.tanh((x.sem_available-x.man_available)/15))

def test_no_future_features():
    d=r.load_raw();p=r.build_panel(d)
    x=p.iloc[0]; t=int(x.origin_index)
    assert np.isclose(x.sem_available,100*np.log(d.IPG3344S.iloc[t-2]/d.IPG3344S.iloc[t-14]))
    assert np.isclose(x.target,100*np.log(d.IPG3342S.iloc[t+3]/d.IPG3342S.iloc[t-9]))

def test_expanding_purge():
    p=r.build_panel(r.load_raw());o=r.walk_forward(p)
    assert (o.max_train_label_observation<=o.latest_usable_observation).all()
    assert o.n_train.is_monotonic_increasing

def test_perturbation_no_lookahead():
    d=r.load_raw();a=r.build_panel(d,weight=.9);b=r.build_panel(d,weight=1)
    assert np.allclose(a.target,b.target)
    assert np.allclose(a.factor_raw,.9*a.sem_available+.1*a.computer_available-a.man_available)

def test_rolling_blocks_are_valid():
    idx=r.block_indices(81,np.random.default_rng(123),12)
    assert len(idx)==81 and idx.min()>=0 and idx.max()<81

def test_placebo_preserves_multiset():
    x=np.arange(101);z=r.block_shuffle(x,np.random.default_rng(12))
    assert sorted(x)==sorted(z)

def test_no_unverified_alpha_claim():
    import json
    m=json.loads((r.ROOT/'study.json').read_text())
    assert m['equity_alpha_established'] is False
    assert m['point_in_time_verified'] is False

def test_result_provenance():
    import json
    x=json.loads((r.ROOT/'results/summary.json').read_text())
    assert x['n_raw']==189 and x['block_shuffle_draws']>=1000 and x['bootstrap_draws']>=2000

def test_notebook_executed_no_errors():
    import nbformat
    nb=nbformat.read(r.ROOT/'research.ipynb',as_version=4)
    assert len(nb.cells)>=36
    codes=[c for c in nb.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in codes)
    assert not any(out.output_type=='error' for c in codes for out in c.outputs)
    assert sum(any(o.output_type=='display_data' and 'image/png' in o.data for o in c.outputs) for c in codes)>=3
