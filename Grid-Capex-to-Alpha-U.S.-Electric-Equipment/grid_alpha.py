"""U.S. grid-capex demand/supply gap research pilot.

This is an economic-activity *lead-association* test, NOT an equity-alpha backtest.
The bundled CSV is a mixed-vintage FRED snapshot, not a historical PIT archive.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge

HORIZON = 6
DISCLOSURE_LAG = 1  # conservative one-month feature lag; NOT a vintage reconstruction
TRAIN_LABEL_DELAY = HORIZON + DISCLOSURE_LAG
BASELINE = ["equip_yoy_pit", "equip_mom6_pit"]
FULL = BASELINE + ["gap"]


def read_snapshot(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    df = df.rename(columns={
        "utility_power_index_IPG2211S": "load",
        "electrical_equipment_index_IPG3353S": "equip",
    })
    if df.index.has_duplicates or df.isna().any().any():
        raise ValueError("Snapshot requires complete unique monthly observations.")
    expected = pd.date_range(df.index.min(), df.index.max(), freq="MS")
    if not df.index.equals(expected):
        raise ValueError("Missing monthly observations.")
    if (df[["load", "equip"]] <= 0).any().any():
        raise ValueError("Non-positive industrial production index.")
    return df


def make_panel(raw: pd.DataFrame, horizon: int = HORIZON) -> pd.DataFrame:
    x = raw.copy()
    for field in ("load", "equip"):
        x[field + "_yoy"] = 100.0 * (x[field] / x[field].shift(12) - 1.0)
    x["equip_mom6"] = 100.0 * (x["equip"] / x["equip"].shift(6) - 1.0)
    # At month t, assume the latest safely known monthly datapoint is month t-1.
    for field in ("load_yoy", "equip_yoy", "equip_mom6"):
        x[field + "_pit"] = x[field].shift(DISCLOSURE_LAG)
    # Fixed scale, NO full-sample standardization. Economic intuition is
    # electrification-load growth exceeding equipment manufacturing growth.
    x["gap"] = np.tanh((x["load_yoy_pit"] - x["equip_yoy_pit"]) / 10.0)
    # Forecast the next six-month equipment output growth, not stock return.
    x["y"] = 100.0 * (x["equip"].shift(-horizon) / x["equip"] - 1.0)
    return x[["gap", "load_yoy_pit", "equip_yoy_pit",
              "equip_mom6_pit", "y"]].dropna()


def ridge_prediction(train: pd.DataFrame, observation: pd.Series,
                     features: list[str], alpha: float = 20.0) -> float:
    xx = train[features].to_numpy(dtype=float)
    one = observation[features].to_numpy(dtype=float)[None, :]
    mean = xx.mean(axis=0)
    scale = xx.std(axis=0)  # training observations only
    scale[scale < 1e-8] = 1.0
    fit = Ridge(alpha=alpha).fit((xx - mean) / scale, train["y"].to_numpy())
    return float(fit.predict((one - mean) / scale)[0])


def walk_forward(panel: pd.DataFrame, min_train: int = 12,
                 horizon: int = HORIZON) -> pd.DataFrame:
    """Expanding training: only use labels matured >= 1 month before t."""
    rows = []
    for when, obs in panel.iterrows():
        eligible = panel.loc[
            (panel.index + pd.DateOffset(months=horizon + DISCLOSURE_LAG)) <= when
        ]
        if len(eligible) < min_train:
            continue
        rows.append({
            "formation": when,
            "actual": float(obs["y"]),
            "mean": float(eligible["y"].mean()),
            "baseline": ridge_prediction(eligible, obs, BASELINE),
            "with_gap": ridge_prediction(eligible, obs, FULL),
            "n_train": len(eligible),
        })
    return pd.DataFrame(rows).set_index("formation")


def rmse(actual: pd.Series | np.ndarray, pred: pd.Series | np.ndarray) -> float:
    return float(np.sqrt(np.mean((np.asarray(actual) - np.asarray(pred)) ** 2)))


def shifted_placebo(panel: pd.DataFrame, observed_rmse: float) -> dict:
    """Conservative circular-shift pseudo-placebo preserving gap autocorrelation.

    This is NOT a randomization-based exact p-value under a full time-series null;
    and the shifted gap partly shares construction with the unshifted equipment
    controls. Use only as an exploratory falsification diagnostic.
    """
    series = panel["gap"].to_numpy()
    scores = []
    for k in range(7, len(panel) - 6):
        shuffled = panel.copy()
        shuffled["gap"] = np.roll(series, k)
        predicted = walk_forward(shuffled)
        scores.append(rmse(predicted.actual, predicted.with_gap))
    if not scores:
        return {"n_shifts": 0, "placebo_p": None}
    return {
        "n_shifts": len(scores),
        "null_median_rmse": float(np.median(scores)),
        "placebo_p": float((1 + sum(v <= observed_rmse for v in scores)) / (1 + len(scores))),
    }


def block_bootstrap(oos: pd.DataFrame, length: int = 6,
                    repeats: int = 2000, seed: int = 20261019) -> list[float]:
    """Circular moving-block bootstrap of (baseline MSE - gap MSE).

    Illustrative only: 19 OOS origins with overlapping 6-month outcomes are
    far too few for confident interval inference.
    """
    diff = ((oos.actual - oos.baseline) ** 2 -
            (oos.actual - oos.with_gap) ** 2).to_numpy()
    generator = np.random.default_rng(seed)
    means = []
    for _ in range(repeats):
        indices = []
        while len(indices) < len(diff):
            start = int(generator.integers(0, len(diff)))
            indices.extend((start + j) % len(diff) for j in range(length))
        means.append(float(np.mean(diff[indices[:len(diff)]])))
    return [float(x) for x in np.quantile(means, [0.025, 0.975])]


def analyse(data_file: str | Path) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    raw = read_snapshot(data_file)
    panel = make_panel(raw)
    oos = walk_forward(panel)
    rank = spearmanr(panel["gap"], panel["y"])
    comparison = {
        col: {
            "rmse_pct_points": rmse(oos.actual, oos[col]),
            "mae_pct_points": float(np.mean(np.abs(oos.actual - oos[col]))),
            "direction_accuracy": float(np.mean((oos.actual > 0) == (oos[col] > 0))),
        } for col in ("mean", "baseline", "with_gap")
    }
    actual = comparison["with_gap"]["rmse_pct_points"]
    summary = {
        "study_type": "macro leading-association, not investable security alpha",
        "snapshot_period": f"{raw.index.min():%Y-%m} to {raw.index.max():%Y-%m}",
        "snapshot_observations": len(raw),
        "paired_formation_periods": len(panel),
        "oos_forecast_origins": len(oos),
        "horizon_months": HORIZON,
        "outcome": "next 6-month electrical-equipment manufacturing output growth (%)",
        "latest_power_yoy_pct": float(100 * (raw.load.iloc[-1] / raw.load.iloc[-13] - 1)),
        "latest_equipment_yoy_pct": float(100 * (raw.equip.iloc[-1] / raw.equip.iloc[-13] - 1)),
        "full_sample_spearman": float(rank.statistic),
        "naive_nominal_spearman_p": float(rank.pvalue),
        "forecast_metrics": comparison,
        "circular_shift_placebo": shifted_placebo(panel, actual),
        "block_bootstrap_mse_improvement_95pct_exploratory": block_bootstrap(oos),
        "warnings": [
            "Revised fixed-vintage and mixed-vintage historical series, not genuine historical PIT",
            "Source data do not isolate AI data-centre power demand",
            "Only 19 highly overlapping out-of-sample forecast origins",
            "No security-price/total-return or transaction-cost series: no equity-alpha claim",
            "Nominal rank p-value ignores overlapping outcome/autocorrelation",
            "The 2025 forecast narrative is contextual; not used as historical tradable feature",
        ],
    }
    return summary, panel, oos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=str(Path(__file__).with_name("fed_industrial_production_snapshot_2022_2026.csv")))
    args = parser.parse_args()
    result, _, forecasts = analyse(args.csv)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    forecasts.to_csv(Path(args.csv).with_name("oos_forecasts_generated.csv"))
