from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from computer_factor import *

ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(scope='module')
def raw():return load_and_qa(ROOT/'data/frozen_g17_electronics_2026-10-19.csv')
@pytest.fixture(scope='module')
def panel(raw):return make_panel(raw)
@pytest.fixture(scope='module')
def forecasts(panel):return oos(panel)

def test_raw_integrity(raw):assert len(raw)==189 and (raw[RAW]>0).all().all()
def test_source_snapshot_sha(raw):
    import hashlib
    assert hashlib.sha256((ROOT/'data/frozen_g17_electronics_2026-10-19.csv').read_bytes()).hexdigest()=='6a6fca4b29755f0c2cae8ccfae1016a22648e724787cc42e726ac945583c351c'
def test_factor_definition(panel):
    x=panel.dropna(subset=['factor']).iloc[0]
    assert np.isclose(x.factor,x.network_stale-x.chip_stale)
def test_lag_mechanism(panel):
    x=panel.iloc[20]
    assert np.isclose(x.computer_stale,panel.iloc[18].computer_yoy)
def test_target_forward(panel):
    x=panel.iloc[30]
    assert np.isclose(x.target,panel.iloc[33].computer_yoy)
def test_oos_n(forecasts):assert len(forecasts)==117
def test_training_purge(forecasts):
    assert forecasts.n_train.min()>=48
    assert (forecasts.latest_input_month<forecasts.date).all()
    assert (forecasts.target_month>forecasts.date).all()
def test_first_forecast_date(forecasts):assert forecasts.date.iloc[0]==pd.Timestamp('2016-10-01')
def test_control_full_equal_origins(forecasts):assert forecasts[['macro_control','full_network_balance']].notna().all().all()
def test_scores(forecasts):
    s=scorecard(forecasts)
    assert len(s)==7 and s.n.nunique()==1 and (s.rmse_log_pp>0).all()
def test_gain_negative(forecasts):assert subset_gain(forecasts)<0
def test_block_indices():
    rng=np.random.default_rng(1);x=moving_block_indices(117,12,rng)
    assert len(x)==117 and x.min()>=0 and x.max()<117
    assert sum(x[i+1]-x[i]==1 for i in range(len(x)-1))>=105
def test_block_permute_preserves_values(panel):
    rng=np.random.default_rng(5);a=panel.factor.to_numpy();b=block_permute_factor(panel,12,rng)
    assert np.allclose(np.sort(a[np.isfinite(a)]),np.sort(b[np.isfinite(b)]))
def test_bootstrap_count(forecasts):assert len(bootstrap_paired(forecasts,draws=15))==15
def test_perturbation_changes_factor(raw):
    a=make_panel(raw,k=.7);b=make_panel(raw,k=1.3)
    assert not np.allclose(a.factor.dropna(),b.factor.dropna())
def test_fixed_seed_determinism(forecasts):
    a=bootstrap_paired(forecasts,draws=10,seed=9)
    b=bootstrap_paired(forecasts,draws=10,seed=9)
    assert a.equals(b)
def test_ridge_matches_sklearn(panel):
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    cols=FEATURES['full_network_balance'];t=100
    train=panel.iloc[17:95].dropna(subset=cols+['target'])
    row=panel.iloc[[t]]
    scaler=StandardScaler().fit(train[cols]);model=Ridge(alpha=ALPHA).fit(scaler.transform(train[cols]),train.target)
    expected=model.predict(scaler.transform(row[cols]))[0]
    assert abs(fit_predict(train,row,cols)-expected)<1e-9
