"""Housing permits -> U.S. building-materials industrial output: macro alpha-factor falsification.
Public, current-vintage 2010-2026 monthly snapshot. No equity alpha is claimed.
All forecasts are generated from labels mature by forecast time, but the historical
FRED values are revised ex post and are NOT a reconstructed point-in-time tape.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

SERIES = ("PERMIT", "HOUST", "IPG327S", "IPG321S", "IPMAN", "FEDFUNDS")
FEATURE_LAG = 2                  # two complete months for all predictors
LABEL_DELAY = 2                  # two months after target observation for train eligibility
ALPHA = 25.0                     # fixed ridge penalty; no OOS hyperparameter search
TRAIN_START = pd.Timestamp("2012-01-01")
TEST_START = pd.Timestamp("2018-01-01")
MACRO = ["target_lag", "ipman_lag", "fedfunds_lag"]
MODELS = {
    "mean": [],
    "ar": ["target_lag"],
    "macro": MACRO,
    "housing": MACRO + ["permits_lag", "starts_lag"],
    "gap": MACRO + ["housing_gap"],
}

def read_snapshot(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    if df.index.has_duplicates or tuple(df.columns) != SERIES:
        raise ValueError("Expected six official series and unique monthly dates.")
    expected = pd.date_range(df.index.min(), df.index.max(), freq="MS")
    if not df.index.equals(expected) or df.isna().any().any():
        raise ValueError("Snapshot has gaps or missing values.")
    if (df[list(SERIES)] <= 0).any().any():
        raise ValueError("All six raw values must be strictly positive.")
    return df

def log_yoy(series: pd.Series) -> pd.Series:
    return 100.0 * np.log(series / series.shift(12))

def make_panel(raw: pd.DataFrame, target: str = "IPG327S",
               horizon: int = 6, housing_shift: int = 0) -> pd.DataFrame:
    """Origin t features are dated no later than t-2; outcome at t+h.
    housing_shift is a lag-only placebo (no future or circular wrap).
    """
    if target not in ("IPG327S", "IPG321S"):
        raise ValueError("Unexpected target industry.")
    if horizon < 1 or housing_shift < 0:
        raise ValueError("Horizon and lag must be nonnegative.")
    panel = pd.DataFrame(index=raw.index)
    panel["actual"] = log_yoy(raw[target]).shift(-horizon)
    panel["target_lag"] = log_yoy(raw[target]).shift(FEATURE_LAG)
    panel["ipman_lag"] = log_yoy(raw["IPMAN"]).shift(FEATURE_LAG)
    panel["fedfunds_lag"] = raw["FEDFUNDS"].shift(FEATURE_LAG)
    panel["permits_lag"] = log_yoy(raw["PERMIT"]).shift(FEATURE_LAG + housing_shift)
    panel["starts_lag"] = log_yoy(raw["HOUST"]).shift(FEATURE_LAG + housing_shift)
    panel["housing_gap"] = panel["permits_lag"] - panel["starts_lag"]
    return panel.dropna()

def predict_ridge(train: pd.DataFrame, row: pd.Series,
                  features: list[str], alpha: float = ALPHA) -> float:
    y = train["actual"].to_numpy(dtype=float)
    y_mean = float(y.mean())
    if not features:
        return y_mean
    X = train[features].to_numpy(dtype=float)
    mu = X.mean(axis=0)
    sigma = X.std(axis=0, ddof=0)      # training-only scaling
    sigma[sigma < 1e-8] = 1.0
    Z = (X - mu) / sigma
    beta = np.linalg.solve(Z.T @ Z + alpha * np.eye(len(features)),
                           Z.T @ (y - y_mean))
    point = (row[features].to_numpy(dtype=float) - mu) / sigma
    return float(y_mean + point @ beta)

def walk_forward(panel: pd.DataFrame, horizon: int = 6,
                 min_train: int = 35) -> pd.DataFrame:
    """Expanding training. Label at s+h must have aged two months by t."""
    forecasts = []
    for origin, row in panel.iterrows():
        if origin < TEST_START:
            continue
        cutoff = origin - pd.DateOffset(months=horizon + LABEL_DELAY)
        train = panel.loc[(panel.index >= TRAIN_START) & (panel.index <= cutoff)]
        if len(train) < min_train:
            continue
        record = {"formation": origin, "actual": float(row["actual"]),
                  "n_train": int(len(train))}
        for name, features in MODELS.items():
            record[name] = predict_ridge(train, row, features)
        forecasts.append(record)
    if not forecasts:
        raise ValueError("Insufficient mature labels for walk-forward test.")
    return pd.DataFrame(forecasts).set_index("formation")

def summarize_forecasts(oos: pd.DataFrame) -> dict:
    actual = oos["actual"].to_numpy(dtype=float)
    output = {}
    for model in MODELS:
        pred = oos[model].to_numpy(dtype=float)
        output[model] = {
            "rmse_pp": float(np.sqrt(np.mean((pred - actual) ** 2))),
            "mae_pp": float(np.mean(np.abs(pred - actual))),
            "direction_accuracy": float(np.mean(np.sign(pred) == np.sign(actual))),
        }
    return output

def subset_metrics(oos: pd.DataFrame) -> dict:
    subsets = {
        "excluding_covid_2020_03_to_2021_12":
            oos.loc[(oos.index < "2020-03-01") | (oos.index > "2021-12-01")],
        "post_2022": oos.loc[oos.index >= "2022-01-01"],
    }
    return {name: {"n": len(part), "metrics": summarize_forecasts(part)}
            for name, part in subsets.items() if len(part)}

def evaluate(raw: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    panel = make_panel(raw)
    oos = walk_forward(panel)
    placebo = {}
    for months in (12, 24, 36):
        shifted = walk_forward(make_panel(raw, housing_shift=months))
        placebo[str(months)] = {
            "n": len(shifted),
            "housing_rmse_pp": summarize_forecasts(shifted)["housing"]["rmse_pp"],
            "warning": "Lag-only diagnostic; different sample lengths, not a p-value.",
        }
    wood = walk_forward(make_panel(raw, target="IPG321S"))
    three_month = walk_forward(make_panel(raw, horizon=3), horizon=3)
    latest = raw.iloc[-1]
    year_ago = raw.iloc[-13]
    summary = {
        "as_of": "2026-10-19",
        "study": "housing permits and starts -> building materials production",
        "classification": "fixed-vintage macro forecasting association; not investable equity alpha",
        "sample": {"n_months": len(raw), "first": str(raw.index[0].date()),
                   "last": str(raw.index[-1].date())},
        "oos": {"n": len(oos), "first": str(oos.index[0].date()),
                "last": str(oos.index[-1].date()),
                "horizon_months": 6, "label_delay_months": LABEL_DELAY},
        "latest": {
            "PERMIT_2026_08_thousand_SAAR": float(latest["PERMIT"]),
            "HOUST_2026_08_thousand_SAAR": float(latest["HOUST"]),
            "IPG327S_2026_08_index": float(latest["IPG327S"]),
            "IPG327S_2026_08_yoy_log_pct": float(100 * np.log(latest["IPG327S"] / year_ago["IPG327S"])),
        },
        "main": summarize_forecasts(oos),
        "wood_product_negative_control": {"n": len(wood), "metrics": summarize_forecasts(wood)},
        "three_month_horizon": {"n": len(three_month), "metrics": summarize_forecasts(three_month)},
        "lag_only_placebos": placebo,
        "regime_sensitivity": subset_metrics(oos),
        "warnings": [
            "All historic FRED values are latest/revised snapshot, not ALFRED point-in-time vintages.",
            "Two-month lag is a conservative approximation, not a verified release calendar.",
            "Six-month overlapping targets imply strongly dependent forecast errors.",
            "This is an industrial-production nowcast/forecast test, not a securities-return test.",
            "Housing activity is cyclical and nonmetallic mineral output has nonhousing uses.",
            "Fixed hyperparameters are researcher choices, not a pre-registered 2018 design.",
            "Lag-only placebos are diagnostics, not formal randomization inference.",
        ],
    }
    return summary, oos

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default=str(Path(__file__).with_name("fred_housing_materials_snapshot_2010_2026.csv")))
    p.add_argument("--out", default=None, help="Optional output directory; default: script directory")
    args = p.parse_args()
    summary, oos = evaluate(read_snapshot(args.csv))
    out = Path(args.out) if args.out else Path(__file__).parent
    out.mkdir(parents=True, exist_ok=True)
    (out / "results_generated.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    oos.to_csv(out / "oos_forecasts_generated.csv")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
