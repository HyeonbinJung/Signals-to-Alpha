"""Regression, point-in-time proxy, randomization and reproducibility checks."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import run_analysis as r


def test_raw_schema():assert r.load_raw().shape==(960,8)
def test_raw_dates_unique():assert r.load_raw().date.is_unique
def test_raw_no_future():assert r.load_raw().date.max()==pd.Timestamp('2023-12-01')
def test_positive_weights():assert (r.load_raw()[['beef','pork','broilers','turkey']].dropna()>0).all().all()
def test_poultry_start():assert r.load_raw().broilers.first_valid_index()==192

def test_signal_formula():
    raw=r.load_raw();p=r.make_panel(raw);row=p.iloc[100]
    exp=np.tanh((.5*row.beef_yoy_lag2+.5*row.pork_yoy_lag2-row.turkey_yoy_lag2)/20)
    assert abs(row.factor-exp)<1e-12

def test_signal_uses_only_lagged_data():
    raw=r.load_raw();p=r.make_panel(raw);date=p.date.iloc[150]
    modified=raw.copy();modified.loc[modified.date==date,'beef']*=100
    q=r.make_panel(modified)
    assert abs(q.loc[q.date==date,'factor'].iloc[0]-p.loc[p.date==date,'factor'].iloc[0])<1e-12

def test_release_cutoff():
    p=r.make_panel(r.load_raw());pred=r.walkforward(p)
    assert (pred.max_training_label_available<=pred.date).all()
    assert (pred.max_training_target_date+pd.DateOffset(months=2)<=pred.date).all()

def test_oos_start_and_count():
    pred=r.walkforward(r.make_panel(r.load_raw()))
    assert len(pred)==165 and pred.date.min()==pd.Timestamp('2010-01-01')

def test_oos_end():
    pred=r.walkforward(r.make_panel(r.load_raw()))
    assert pred.date.max()==pd.Timestamp('2023-09-01')

def test_fast_equivalence():
    p=r.make_panel(r.load_raw());pr=r.walkforward(p,models=['macro_control','augmented'])
    assert np.allclose(r._fast_augmented_forecasts(p),pr.augmented,rtol=0,atol=1e-9)

def test_scorecard_n():
    pr=r.walkforward(r.make_panel(r.load_raw()));s=r.scorecard(pr)
    assert s.n_oos.eq(len(pr)).all() and len(s)==7

def test_block_reorder_preserves_values():
    x=np.arange(120);z=r.block_reorder_factor(x,np.random.default_rng(1),12)
    assert np.array_equal(np.sort(x),np.sort(z))

def test_block_reorder_preserves_internal_order():
    x=np.arange(120);z=r.block_reorder_factor(x,np.random.default_rng(1),12)
    assert np.all(np.diff(z.reshape(-1,12),axis=1)==1)

def test_bootstrap_reproducible():
    p=r.walkforward(r.make_panel(r.load_raw()));a=r.block_bootstrap_gain(p,30);b=r.block_bootstrap_gain(p,30)
    assert np.array_equal(a,b)

def test_weights_sum_one():
    w=r.weight_sensitivity(r.load_raw(),0,draws=10)
    assert np.allclose(w.beef_weight+w.pork_weight,1)

def test_no_alpha_label():
    import json
    j=json.loads((r.RESULTS/'summary.json').read_text())
    assert j['equity_alpha_established'] is False and j['pit_verified'] is False

def test_figures_exist():
    assert len(list(r.FIGURES.glob('*.svg')))>=3

def test_placebo_draw_count():
    assert len(pd.read_csv(r.RESULTS/'placebo_draws.csv'))==1000

def test_bootstrap_draw_count():
    assert len(pd.read_csv(r.RESULTS/'bootstrap_draws.csv'))==2000

def test_no_company_return_data():
    import json
    j=json.loads((r.RESULTS/'summary.json').read_text())
    assert j['company_fundamentals_tested'] is False and j['security_total_returns_tested'] is False
