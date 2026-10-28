from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import run_analysis as a


def test_raw_hash_and_shape():
    d=a.load_raw();assert len(d)==201;assert hashlib.sha256(a.RAW.read_bytes()).hexdigest()==a.EXPECTED_SHA

def test_dates_are_monthly_unique():
    d=a.load_raw();assert d.date.is_unique and d.date.iloc[-1]==pd.Timestamp('2026-09-01')

def test_nonhome_is_positive():
    d=a.load_raw();assert (d.ambulatory>d.home).all()

def test_panel_factor_formula():
    p=a.make_panel(a.load_raw());r=p.iloc[10]
    assert np.isclose(r.factor,np.tanh((r.g_outpatient_nonhome-r.g_nursing)/5))

def test_target_definition():
    d=a.load_raw();p=a.make_panel(d);r=p.iloc[10]
    assert np.isclose(r.target,100*np.log(d.at[int(r.t)+6,'hospital']/d.at[int(r.t)-6,'hospital']))

def test_factor_never_uses_future():
    d=a.load_raw();p=a.make_panel(d);t=70
    d2=d.copy();d2.loc[d2.index>t-2,['home','nursing','ambulatory','hospital','payroll']]*=1.4
    p2=a.make_panel(d2)
    assert np.isclose(p.loc[p.t==t,'factor'].iloc[0],p2.loc[p2.t==t,'factor'].iloc[0])

def test_matured_labels_only():
    p=a.make_panel(a.load_raw());o=a.walk_forward(p)
    assert len(o)==99 and (o.train_n>=60).all()
    for row in o.itertuples():
        tr=p.loc[p.target_mature_t<=row.t]
        assert len(tr)==row.train_n and (tr.target_mature_t<=row.t).all()

def test_outcome_not_used_in_factor():
    d=a.load_raw();p=a.make_panel(d);assert 'target' not in a.MODELS['full']

def test_ridge_matches_sklearn():
    rng=np.random.default_rng(10);x=rng.normal(size=(100,4));y=rng.normal(size=100);z=rng.normal(size=(1,4))
    s=StandardScaler().fit(x);ref=Ridge(alpha=10).fit(s.transform(x),y).predict(s.transform(z))
    assert np.allclose(a.ridge_forecast(x,y,z),ref,atol=1e-10)

def test_fast_refit_matches_main():
    p=a.make_panel(a.load_raw());o=a.walk_forward(p)
    assert np.allclose(a.fast_full_preds(p,p.factor,o),o.full,atol=1e-10)

def test_block_permutation_preserves_multiset():
    p=a.make_panel(a.load_raw());q=a.block_permute_factor(p,np.random.default_rng(5))
    assert np.allclose(np.sort(p.factor),np.sort(q.factor))

def test_seeded_placebo_deterministic():
    p=a.make_panel(a.load_raw());o=a.walk_forward(p)
    assert np.allclose(a.placebo_draws(p,o,draws=4),a.placebo_draws(p,o,draws=4))

def test_seeded_bootstrap_deterministic():
    o=a.walk_forward(a.make_panel(a.load_raw()))
    assert np.allclose(a.bootstrap_gains(o,draws=20),a.bootstrap_gains(o,draws=20))

def test_weights_deterministic():
    p=a.make_panel(a.load_raw());o=a.walk_forward(p)
    w=a.weight_sensitivity(p,o,draws=4)
    assert np.allclose(w.rmse_gain_log_pp,a.weight_sensitivity(p,o,draws=4).rmse_gain_log_pp)

def test_mean_is_better_than_full():
    o=a.walk_forward(a.make_panel(a.load_raw()));assert a.rmse(o.target,o['mean'])<a.rmse(o.target,o.full)

def test_post_2021_negative_gain():
    o=a.walk_forward(a.make_panel(a.load_raw()));z=o[o.date>='2022-01-01'];assert a.rmse(z.target,z.macro_controls)-a.rmse(z.target,z.full)<0

def test_figure_files_are_computed():
    assert len(list((a.ROOT/'figures').glob('*.png')))>=12
    assert all(p.stat().st_size>5000 for p in (a.ROOT/'figures').glob('*.png'))

def test_results_are_real():
    m=json.loads((a.ROOT/'results'/'metrics.json').read_text())
    assert m['placebo_draws']>=1000 and m['bootstrap_draws']>=2000 and m['weight_draws']>=1000
    assert m['historical_publication_vintages'].startswith('UNKNOWN')

def test_no_equity_claim():
    m=json.loads((a.ROOT/'results'/'metrics.json').read_text());assert 'NOT EQUITY ALPHA' in m['status']

def test_issuer_descriptive_not_backfilled():
    d=pd.read_csv(a.ROOT/'data'/'issuer_exposure_map.csv')
    assert (d['backtest_use']=='NO').all() and (d['historical_revenue_weight']=='UNKNOWN').all()

def test_canonical_readme_sections():
    from pathlib import Path
    r=(a.ROOT/'README.md').read_text()
    headings=[x[3:] for x in r.splitlines() if x.startswith('## ')]
    expected=['01. Abstract','02. Research Design & Hypotheses','03. Industry Context','04. Data & Source Integrity','05. Point-in-Time Availability','06. Factor Construction','07. Exposure & Transmission','08. Outcomes & Baselines','09. Empirical Findings','10. Robustness & Placebos','11. Regime Sensitivity','12. Bias Audit & Verdict','13. Reproduction','14. Next-Stage Protocol','15. Sources & Artifacts']
    assert headings==expected

def test_committed_notebook_has_computed_outputs():
    import nbformat
    n=nbformat.read(a.ROOT/'research.ipynb',as_version=4)
    code=[c for c in n.cells if c.cell_type=='code']
    assert len(n.cells)>=40 and len(code)>=25
    assert all(c.execution_count is not None for c in code)
    assert not any(o.output_type=='error' for c in code for o in c.get('outputs',[]))
    assert sum('image/png' in o.get('data',{}) for c in code for o in c.get('outputs',[]) if o.output_type=='display_data')>=3
