import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from analysis import read_raw, make_panel, walk_forward, score, delta, ROOT, HORIZON, PURGE


def test_raw_exact_inherited_snapshot():
    p=ROOT/'data/fred_quarterly_snapshot_2026-10-26.csv'
    assert hashlib.sha256(p.read_bytes()).hexdigest()=='17b99d105505b7c4ef7741012cf65d916bac0b907403474f18cffedcc4a99b2d'
    assert len(read_raw())==107


def test_no_lookahead_in_signal():
    raw=read_raw()
    a=make_panel(raw)
    changed=raw.copy()
    changed.loc[changed.index>=85,'CES4349300001']*=10
    b=make_panel(changed)
    assert np.allclose(a[a.origin_index<85].factor,b[b.origin_index<85].factor)


def test_formation_and_target_math():
    raw=read_raw();p=make_panel(raw)
    row=p.iloc[10];i=int(row.origin_index)
    assert np.isclose(row.target,raw.ECOMPCTSA.iloc[i+HORIZON]-raw.ECOMPCTSA.iloc[i])
    assert np.isclose(row.factor,100*np.log(raw.CES4349300001.iloc[i-1]/raw.CES4349300001.iloc[i-5])-100*np.log(raw.PAYEMS.iloc[i-1]/raw.PAYEMS.iloc[i-5]))


def test_target_release_purge_and_train_only():
    p=walk_forward(make_panel(read_raw()))
    assert len(p)==57
    assert (p.train_last_origin<=p.origin_index-PURGE).all()
    assert p.train_n.min()>=40


def test_saved_scorecard_matches_predictions():
    p=pd.read_csv(ROOT/'results/oos_predictions.csv')
    s=score(p).set_index('model')
    frozen=pd.read_csv(ROOT/'results/model_scorecard.csv').set_index('model')
    assert np.allclose(s.loc[frozen.index,'rmse_pp'],frozen.rmse_pp)
    assert np.isclose(delta(p),json.loads((ROOT/'results/summary.json').read_text())['observed_delta_rmse_pp'])


def test_permutation_bootstrap_counts():
    assert len(pd.read_csv(ROOT/'results/block_permutation.csv'))==1000
    assert len(pd.read_csv(ROOT/'results/block_bootstrap.csv'))==2000
    assert len(pd.read_csv(ROOT/'results/exposure_perturbations.csv'))==1000


def test_no_investable_alpha_claim():
    s=json.loads((ROOT/'results/summary.json').read_text())
    assert s['PIT_verified'] is False and s['equity_returns_tested'] is False and s['firm_fundamentals_tested'] is False


def test_actual_figures_saved():
    assert len(list((ROOT/'figures').glob('*.svg')))>=3
    for p in (ROOT/'figures').glob('*.svg'):
        assert p.stat().st_size>500 and '<svg' in p.read_text()[:500]


def test_source_register_fields():
    s=pd.read_csv(ROOT/'data/source_register.csv')
    assert len(s)>=4
    assert s.exact_source_url.str.startswith('https://').all()
    assert (s.historical_vintages=='NOT RETRIEVED').all()


def test_regime_falsification():
    r=pd.read_csv(ROOT/'results/regime_scores.csv').set_index('regime')
    assert r.loc['pre_2020','delta_rmse_pp']<0
    assert r.loc['post_2021','delta_rmse_pp']<0


def test_qualitative_company_exposure_not_numeric():
    x=pd.read_csv(ROOT/'data/exposure_map.csv')
    assert (x.exact_historical_company_share=='UNKNOWN').all()
