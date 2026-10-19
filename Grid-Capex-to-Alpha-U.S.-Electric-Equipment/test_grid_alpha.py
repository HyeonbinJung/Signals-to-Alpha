from pathlib import Path
import numpy as np
import pandas as pd
from grid_alpha import analyse, make_panel, read_snapshot, walk_forward

CSV = Path(__file__).resolve().parent / "fed_industrial_production_snapshot_2022_2026.csv"

def test_source_values_and_monthly_continuity():
    raw = read_snapshot(CSV)
    assert len(raw) == 56
    assert np.isclose(raw["load"].iloc[-1], 113.069)
    assert np.isclose(raw["equip"].iloc[-1], 100.0704)

def test_no_contemporaneous_feature_lookahead():
    raw = read_snapshot(CSV)
    panel = make_panel(raw)
    # 2023-02 at formation can use Jan 2023 observations only.
    t = pd.Timestamp("2023-02-01")
    expected = 100 * (raw.loc["2023-01-01", "load"] /
                      raw.loc["2022-01-01", "load"] - 1)
    assert np.isclose(panel.loc[t, "load_yoy_pit"], expected)

def test_training_labels_are_matured_before_forecast():
    _, panel, oos = analyse(CSV)
    assert len(panel) == 37
    assert len(oos) == 19
    first = oos.index[0]
    assert first - pd.DateOffset(months=7) >= panel.index[11]

def test_snapshot_results_reproduce():
    result, _, _ = analyse(CSV)
    assert np.isclose(result["forecast_metrics"]["with_gap"]["rmse_pct_points"], 4.124139466455229, atol=1e-6)
    assert np.isclose(result["forecast_metrics"]["mean"]["rmse_pct_points"], 3.5238000575312283, atol=1e-6)
    assert result["circular_shift_placebo"]["n_shifts"] == 24
