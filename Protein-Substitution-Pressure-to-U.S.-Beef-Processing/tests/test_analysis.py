import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_analysis as a

@pytest.fixture(scope='module')
def raw():return a.load_raw()

@pytest.fixture(scope='module')
def panel(raw):return a.make_panel(raw)

@pytest.fixture(scope='module')
def preds(panel):return a.walkforward(panel)

def test_schema(raw):assert raw.columns.tolist()==['date','beef','veal','pork','lamb_and_mutton','broilers','other_chicken','turkey']
def test_n(raw):assert len(raw)==960
def test_window(raw):assert (raw.date.min(),raw.date.max())==(pd.Timestamp('1944-01-01'),pd.Timestamp('2023-12-01'))
def test_poultry_missingness(raw):assert raw.broilers.notna().sum()==768 and raw.turkey.notna().sum()==768
def test_no_duplicate_dates(raw):assert raw.date.is_unique
def test_panel_nonmissing(panel):assert not panel.isna().any().any()
def test_panel_target_future(panel):assert (panel.target_date>panel.date).all()
def test_label_lag(panel):assert ((panel.label_available.dt.to_period('M')-panel.target_date.dt.to_period('M')).apply(lambda x:x.n)==a.LAG).all()
def test_factor_formula(panel):assert np.allclose(panel.factor,np.tanh(panel.factor_raw/20.))
def test_factor_excludes_beef(panel):assert np.allclose(panel.factor_raw,.7*panel.broiler_yoy_lag2+.3*panel.turkey_yoy_lag2-panel.pork_yoy_lag2)
def test_oos_count(preds):assert len(preds)==186
def test_purge(preds):assert (preds.max_training_label_available<=preds.date).all()
def test_oos_start(preds):assert preds.date.min()==pd.Timestamp('2008-01-01')
def test_oos_end(preds):assert preds.date.max()==pd.Timestamp('2023-06-01')
def test_training_growth(preds):assert preds.n_train.is_monotonic_increasing
def test_mean_baseline(preds):assert np.isfinite(preds.historical_mean).all()
def test_ridge_matches_fast(panel,preds):assert np.max(np.abs(a._fast_augmented_forecasts(panel)-preds.augmented.to_numpy()))<1e-8
def test_block_reorder_preserves_values(panel):
    rng=np.random.default_rng(2);x=panel.factor.to_numpy();z=a.block_reorder_factor(x,rng)
    assert len(x)==len(z) and np.allclose(np.sort(x),np.sort(z))
def test_ridge_train_only(preds):assert (preds.max_training_target_date<=preds.date).all()
def test_rmse_order(preds):assert a.rmse(preds.target,preds.ar_ridge)<a.rmse(preds.target,preds.augmented)
def test_bootstrap_count(preds):assert len(a.block_bootstrap_gain(preds,draws=25))==25
def test_weight_invariance(raw):
    p=a.make_panel(raw,broiler_weight=.7)
    q=a.make_panel(raw,broiler_weight=.7)
    assert np.array_equal(p.factor,q.factor)
def test_lag_horizon(raw):
    p=a.make_panel(raw,horizon=3,lag=3)
    assert (p.target_date>p.date).all()
def test_sec_sales():
    f=pd.read_csv(a.HERE/'data/tyson_fy2023_sec_fundamentals.csv')
    assert f.query("segment=='Beef' and fiscal_year==2023").sales_usd_millions.iloc[0]==19325
    assert f.query("segment=='Beef' and fiscal_year==2023").operating_income_usd_millions.iloc[0]==-91
def test_summary_no_alpha():
    import json
    s=json.loads((a.RESULTS/'summary.json').read_text())
    assert s['equity_alpha_established'] is False and s['pit_verified'] is False
