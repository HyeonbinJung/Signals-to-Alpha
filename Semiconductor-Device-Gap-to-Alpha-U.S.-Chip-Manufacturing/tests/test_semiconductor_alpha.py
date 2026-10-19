import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from semiconductor_alpha import load_data, make_panel, walk_forward, metrics

def test_snapshot():
    d = load_data()
    assert len(d) == 189
    assert d.index.max() == pd.Timestamp("2026-09-01")

def test_no_future_data():
    d = load_data()
    t = pd.Timestamp("2018-01-01")
    original = make_panel(d).loc[t, "gap"]
    modified = d.copy()
    modified.loc[modified.index > t - pd.DateOffset(months=2), :] *= 2
    assert make_panel(modified).loc[t, "gap"] == original

def test_purge():
    oos = walk_forward(make_panel(load_data()))
    assert len(oos) == 108
    for t, row in oos.iterrows():
        assert pd.Timestamp(row.last_training_origin) <= t - pd.DateOffset(months=5)

def test_rmse():
    assert metrics(walk_forward(make_panel(load_data())))["full"]["rmse"] > 0
