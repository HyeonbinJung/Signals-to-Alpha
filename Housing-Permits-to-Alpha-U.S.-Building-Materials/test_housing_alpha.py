"""Deterministic checks. Test data are synthetic ONLY for unit tests."""
import numpy as np
import pandas as pd
from housing_alpha import (SERIES, read_snapshot, make_panel,
                           walk_forward, evaluate, predict_ridge)

def test_snapshot_integrity():
    df = read_snapshot("fred_housing_materials_snapshot_2010_2026.csv")
    assert len(df) == 200
    assert tuple(df.columns) == SERIES
    assert str(df.index[-1].date()) == "2026-08-01"

def test_lag_no_future_leakage():
    raw = read_snapshot("fred_housing_materials_snapshot_2010_2026.csv")
    panel = make_panel(raw)
    when = pd.Timestamp("2018-01-01")
    assert np.isclose(panel.loc[when, "permits_lag"],
        100 * np.log(raw.loc["2017-11-01", "PERMIT"] /
                     raw.loc["2016-11-01", "PERMIT"]))
    assert np.isclose(panel.loc[when, "actual"],
        100 * np.log(raw.loc["2018-07-01", "IPG327S"] /
                     raw.loc["2017-07-01", "IPG327S"]))

def test_walk_forward_and_frozen_reference_metrics():
    raw = read_snapshot("fred_housing_materials_snapshot_2010_2026.csv")
    result, oos = evaluate(raw)
    assert len(oos) == 98
    assert oos.index[0] == pd.Timestamp("2018-01-01")
    assert oos.index[-1] == pd.Timestamp("2026-02-01")
    assert np.isclose(result["main"]["mean"]["rmse_pp"], 4.8079, atol=0.00015)
    assert np.isclose(result["main"]["housing"]["rmse_pp"], 5.1094, atol=0.00015)
    assert np.isclose(result["main"]["macro"]["rmse_pp"], 4.8737, atol=0.00015)
    assert result["main"]["housing"]["rmse_pp"] > result["main"]["mean"]["rmse_pp"]

def test_training_scaling_is_local():
    rng = np.random.default_rng(17)
    train = pd.DataFrame({"actual": rng.normal(size=60),
                          "target_lag": rng.normal(size=60)})
    row = pd.Series({"target_lag": 0.3})
    original = predict_ridge(train, row, ["target_lag"])
    altered = train.copy()
    altered.loc[0, "target_lag"] += 100
    changed = predict_ridge(altered, row, ["target_lag"])
    assert np.isfinite(original) and np.isfinite(changed)
    assert abs(original - changed) > 1e-9
