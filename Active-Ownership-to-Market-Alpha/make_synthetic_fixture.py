"""Deterministic synthetic *code test* data, never usable as empirical evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate(outdir: Path, seed: int = 42, n_days: int = 850,
             n_stocks: int = 90) -> None:
    rng = np.random.default_rng(seed)
    outdir.mkdir(parents=True, exist_ok=True)
    dates = pd.bdate_range("2020-01-02", periods=n_days)
    ids = [f"SEC{i:04d}" for i in range(n_stocks)]
    baseline_ownership = rng.uniform(0.06, 0.80, n_stocks)
    sectors = [f"Sector_{i % 6}" for i in range(n_stocks)]
    market_caps = rng.lognormal(mean=21, sigma=1.3, size=n_stocks)
    latent = rng.normal(size=n_days)
    for t in range(1, n_days):
        latent[t] += 0.25 * latent[t - 1]
    # Deliberately build predictability into the synthetic stock/market process.
    # Resulting Sharpe numbers *must never* be presented as real-world findings.
    market_oc = 0.004 * np.r_[0, latent[:-1]] + rng.normal(0, 0.010, n_days)
    market_cc = market_oc + rng.normal(0, 0.002, n_days)
    market = pd.DataFrame({"date": dates, "cc_return": market_cc, "oc_return": market_oc})
    market.to_csv(outdir / "market.csv", index=False)

    prices = []
    for t, day in enumerate(dates):
        eps = rng.normal(0, 0.018, n_stocks)
        rets = (0.003 + 0.009 * baseline_ownership) * latent[t] + eps
        for i, sid in enumerate(ids):
            prices.append((day, sid, rets[i], sectors[i], market_caps[i], True))
    pd.DataFrame(prices, columns=["date", "security_id", "ret", "sector", "market_cap", "eligible"]).to_csv(
        outdir / "prices.csv", index=False)

    holdings = []
    starts = pd.date_range("2019-09-30", dates[-1] + pd.Timedelta(days=90), freq="QE")
    for qend in starts:
        # 13F-like 45-calendar-day availability; actual filings need true timestamps.
        available = qend + pd.Timedelta(days=45)
        variation = rng.normal(0, 0.015, n_stocks)
        full = np.clip(baseline_ownership + variation, 0.01, 0.95)
        for i, sid in enumerate(ids):
            for owner, weight in [("all_active", 1.0), ("hedge_fund", 0.45),
                                  ("active_mutual_fund", 0.55)]:
                holdings.append((sid, qend, available, owner, float(full[i] * weight)))
    pd.DataFrame(holdings, columns=["security_id", "report_date", "available_date",
                                   "owner_type", "active_ownership"]).to_csv(outdir / "holdings.csv", index=False)
    (outdir / "SYNTHETIC_DATA.txt").write_text(
        "SYNTHETIC: all stock returns, holdings, and market returns are generated "
        "with a deliberately embedded positive predictive relationship. "
        "Never use these to claim paper replication or actual investment alpha.\n",
        encoding="utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("data/synthetic"))
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--days", type=int, default=850)
    p.add_argument("--stocks", type=int, default=90)
    a = p.parse_args()
    generate(a.out, a.seed, a.days, a.stocks)
    print(f"Created SYNTHETIC fixtures in {a.out}")
