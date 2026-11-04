"""Prespecified quantiles, cost levels, investor types and sector-neutral checks."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import run_backtest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prices", required=True)
    parser.add_argument("--holdings", required=True)
    parser.add_argument("--market", required=True)
    parser.add_argument("--out", default="outputs/robustness.csv")
    a = parser.parse_args()
    p = pd.read_csv(a.prices, parse_dates=["date"])
    h = pd.read_csv(a.holdings, parse_dates=["report_date", "available_date"])
    m = pd.read_csv(a.market, parse_dates=["date"])
    types = list(sorted(h["owner_type"].unique()))
    trials = []
    for q in (0.1, 0.2, 0.3):
        for cost in (1.0, 2.0, 5.0, 10.0):
            trials.append(("all_active", q, cost, False))
    for owner in types:
        trials.append((owner, 0.2, 2.0, False))
    if "sector" in p.columns:
        trials.append(("all_active", 0.2, 2.0, True))
    rows = []
    for owner, q, cost, sector_neutral in trials:
        _, result = run_backtest(p, h, m, owner_type=owner, q=q,
                                 side_cost_bps=cost, sector_neutral=sector_neutral)
        rows.append({"owner_type": owner, "quantile": q, "cost_bps_per_side": cost,
                     "sector_neutral": sector_neutral,
                     "signal_days": result["signal_days"],
                     "net_sharpe": result["strategy_net"]["sharpe"],
                     "net_cagr": result["strategy_net"]["cagr"],
                     "net_max_drawdown": result["strategy_net"]["max_drawdown"],
                     "last_30pct_sharpe": result["strategy_net_last_30pct"]["sharpe"],
                     "hac_p_value": result["predictive_hac"]["p_hac"]})
    output = Path(a.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    print(json.dumps({"robustness_rows": len(rows), "out": str(output)}))


if __name__ == "__main__":
    main()
