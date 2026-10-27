"""Unit and artifact assertions for a deliberately retrospective investment pilot."""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from analysis import (load_raw,prepare,walkforward,metrics,improvement,year_block_bootstrap,
                      block_shuffle_factor,rank_diagnostics,leave_one_company_out,FIRMS)

@pytest.fixture(scope='module')
def raw():return load_raw(ROOT)

@pytest.fixture(scope='module')
def p(raw):return walkforward(prepare(raw))

def test_source_frozen_dimensions_and_positive(raw):
    assert len(raw)==220 and raw.firm.nunique()==11
    assert raw.year.min()==1935 and raw.year.max()==1954
    assert not raw.duplicated(['firm','year']).any()
    assert (raw[['invest','value','capital']]>0).all().all()

def test_documented_1946_ussteel_discrepancy(raw):
    assert raw.query('firm=="US Steel" and year==1946').capital.iloc[0]==132.6
    corrected=prepare(raw,correct_ussteel=True)
    assert corrected.query('firm=="US Steel" and year==1947').log_capital_lag.iloc[0]==pytest.approx(np.log(232.6))

def test_no_lookahead_in_lags(raw):
    d=prepare(raw)
    assert (d.lag_year==d.year-1).all()
    for f,grp in d.groupby('firm'):
        r=raw[raw.firm==f].set_index('year')
        for _,row in grp.iterrows():
            assert row.log_invest_lag==pytest.approx(np.log(r.loc[row.year-1,'invest']))
            assert row.q_proxy==pytest.approx(np.log(r.loc[row.year-1,'value']/r.loc[row.year-1,'capital']))

def test_purged_oos_years(p):
    assert len(p)==110 and p.year.nunique()==10
    assert set(p.year)==set(range(1945,1955))
    assert p.groupby('year').firm.nunique().eq(11).all()
    assert (p.max_train_target_year<=p.year-2).all()
    assert p.train_rows.min()>=77

def test_baselines_and_increment(p):
    m=metrics(p).set_index('model')
    assert m.loc['full','rmse_log']<m.loc['control','rmse_log']
    assert m.loc['persistence','rmse_log']<m.loc['full','rmse_log']
    assert improvement(p)==pytest.approx(m.loc['control','rmse_log']-m.loc['full','rmse_log'])

def test_bootstrap_reproducibility_and_year_cluster(p):
    a=year_block_bootstrap(p,n=5,seed=42)
    b=year_block_bootstrap(p,n=5,seed=42)
    pd.testing.assert_frame_equal(a,b)
    assert a.rmse_improvement.notna().all()

def test_shuffle_preserves_firm_multiset(raw):
    d=prepare(raw)
    x=block_shuffle_factor(d,np.random.default_rng(99))
    for f in FIRMS:
        assert sorted(d[d.firm==f].q_proxy.round(9))==sorted(x[x.firm==f].q_proxy.round(9))

def test_leave_one_company_out(raw):
    x=leave_one_company_out(prepare(raw))
    assert len(x)==11 and x.n.eq(100).all()
    assert set(x.excluded_firm)==set(FIRMS)

def test_rank_diagnostics_not_equity(p):
    d=rank_diagnostics(p)
    assert len(d)==10 and d.n_firms.eq(11).all()
    assert d.fundamental_residual_rank_ic.between(-1,1).all()

def test_saved_resampling_counts():
    for fn,n in [('block_shuffle_placebo.csv',1000),('bootstrap_year_blocks.csv',2000),('exposure_perturbations.csv',1000),('fundamental_rank_yearblock_uncertainty.csv',2000)]:
        assert len(pd.read_csv(ROOT/'results'/fn))==n

def test_saved_scorecard_matches_refit(p):
    actual=metrics(p).sort_values('model').reset_index(drop=True)
    stored=pd.read_csv(ROOT/'results/baseline_scorecard.csv').sort_values('model').reset_index(drop=True)
    pd.testing.assert_frame_equal(actual,stored,rtol=1e-11,atol=1e-11)

def test_no_equity_alpha_claim():
    s=json.loads((ROOT/'results/summary.json').read_text())
    assert s['no_pit'] is True and s['no_equity_returns'] is True
    assert s['oos_firm_years']==110
