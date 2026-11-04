"""Mechanical cost sensitivity on already-frozen REAL-data daily trades.

This is a diagnostic, not a parameter search. No alternative signal/threshold
is selected after observing the outcomes. The input must be the pilot daily.csv.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from backtest import performance


def cost_sensitivity(daily: pd.DataFrame) -> pd.DataFrame:
    results = []
    for bps in (0, 1, 2, 5, 10):
        net = daily.gross_return - (daily.position_open.abs() * bps * 2 / 10_000)
        result = performance(net)
        results.append({"cost_bps_per_side": bps, **result})
    return pd.DataFrame(results)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args()
    daily = pd.read_csv(a.daily, parse_dates=["date"])
    needed = {"position_open", "gross_return"}
    if needed.difference(daily.columns):
        raise ValueError("Expected daily.csv from the frozen real-data pilot")
    table = cost_sensitivity(daily)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(a.out, index=False, float_format="%.9g")
    print(table[["cost_bps_per_side", "cumulative_return", "sharpe"]].to_string(index=False))


if __name__ == "__main__":
    main()
