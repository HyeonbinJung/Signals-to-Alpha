import numpy as np
import pandas as pd
from ev_charging_alpha import read_data,panel,walk_forward,metrics,per_year_rank_ic


def test_source_integrity():
    d=read_data();assert len(d)==180;assert d.country.nunique()==16
    assert not d.duplicated(['country','year']).any()


def test_no_future_in_features():
    d=read_data();p=panel(d)
    for r in p.itertuples():
        src=d[(d.country==r.country)&(d.year==r.year-1)].iloc[0]
        assert np.isclose(r.share_l1,src.ev_sales_share_pct)
        assert np.isclose(r.fast_mix_l1,src.public_fast_points/(src.public_fast_points+src.public_slow_points))


def test_target_correct():
    d=read_data();p=panel(d)
    for r in p.itertuples():
        actual=d[(d.country==r.country)&(d.year==r.year)].iloc[0].ev_sales_share_pct
        assert np.isclose(r.target_pp,actual-r.share_l1)


def test_oos_and_embargo():
    o=walk_forward(panel(read_data()))
    assert len(o)>50
    assert o.year.min()>=2018 and o.year.max()<=2023
    assert not o.duplicated(['country','year']).any()
    assert o[['actual','controls','full']].notna().all().all()


def test_baseline_and_full():
    o=walk_forward(panel(read_data()));m=metrics(o)
    assert all(np.isfinite(v['rmse_pp']) for v in m.values())
    assert all(v['n']==len(o) for v in m.values())


def test_stale_and_horizon():
    d=read_data()
    a=walk_forward(panel(d,stale=True));b=walk_forward(panel(d,horizon=2),horizon=2)
    assert len(a)>40 and len(b)>40


def test_rank_ic_bounds():
    r=per_year_rank_ic(walk_forward(panel(read_data())))
    assert r.rank_ic.between(-1,1).all()
