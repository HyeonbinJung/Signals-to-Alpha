"""PIT active-ownership market-information backtest (inspired by Chen & Yin, 2026).

This is NOT a reproduction of the authors' undisclosed exact empirical specification.
The signal is calculated after day t close; orders are filled at day t+1 OPEN.
Forecasting is evaluated on t+1 close-to-close (non-executable), while trading
P&L is t+1 open-to-close (executable, excluding any overnight move).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

TRADING_DAYS = 252


def _read_csv(path: str | Path, dates: list[str]) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=dates)


def validate_inputs(prices: pd.DataFrame, holdings: pd.DataFrame, market: pd.DataFrame) -> None:
    expected = [
        (prices, {"date", "security_id", "ret"}, "prices"),
        (holdings, {"security_id", "report_date", "available_date", "owner_type", "active_ownership"}, "holdings"),
        (market, {"date", "cc_return", "oc_return"}, "market"),
    ]
    for df, required, name in expected:
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{name}: missing required columns: {sorted(missing)}")
        if df.empty:
            raise ValueError(f"{name}: input is empty")

    if prices.duplicated(["date", "security_id"]).any():
        raise ValueError("prices: duplicate (date, security_id) observations")
    if market.duplicated("date").any():
        raise ValueError("market: duplicate dates")
    if holdings.duplicated(["security_id", "available_date", "owner_type"]).any():
        raise ValueError("holdings: multiple snapshots for security/date/owner_type; aggregate before input")
    if (holdings["report_date"] > holdings["available_date"]).any():
        raise ValueError("holdings: report_date cannot follow available_date")
    if not holdings["active_ownership"].between(0, 1).all():
        raise ValueError("holdings: active_ownership must be a fraction in [0,1]")
    for col in ["ret"]:
        if not np.isfinite(prices[col].dropna().astype(float)).all():
            raise ValueError("prices: non-finite returns")
        if (prices[col].dropna() < -1).any():
            raise ValueError("prices: returns below -100%")
    for col in ["cc_return", "oc_return"]:
        if not np.isfinite(market[col].dropna().astype(float)).all():
            raise ValueError(f"market: non-finite {col}")
        if (market[col].dropna() < -1).any():
            raise ValueError(f"market: {col} below -100%")


def point_in_time_join(prices: pd.DataFrame, holdings: pd.DataFrame,
                       owner_type: str, max_age_days: int = 200) -> pd.DataFrame:
    """As-of join, strictly excluding holdings released on the signal date itself.

    To use data published during date t safely, a timestamp-aware pipeline is
    required; this daily-only implementation waits until date t+1 or later.
    """
    h = holdings.loc[holdings["owner_type"] == owner_type].copy()
    if h.empty:
        raise ValueError(f"No holdings for owner_type={owner_type!r}")
    p = prices.copy()
    p["security_id"] = p["security_id"].astype(str)
    h["security_id"] = h["security_id"].astype(str)
    p = p.sort_values(["date", "security_id"])
    h = h.sort_values(["available_date", "security_id"])
    result = pd.merge_asof(
        p, h[["security_id", "available_date", "report_date", "active_ownership"]],
        by="security_id", left_on="date", right_on="available_date",
        direction="backward", allow_exact_matches=False,
    )
    age = (result["date"] - result["available_date"]).dt.days
    result.loc[age > max_age_days, "active_ownership"] = np.nan
    return result


def _weighted_return(group: pd.DataFrame, weighting: str) -> float:
    if weighting == "value":
        w = group["market_cap"].to_numpy(dtype=float)
        if np.any(~np.isfinite(w)) or np.any(w <= 0):
            raise ValueError("value-weighted mode requires positive market_cap for every eligible security")
        return float(np.average(group["ret"], weights=w))
    return float(group["ret"].mean())


def _spread(x: pd.DataFrame, q: float, min_names: int, weighting: str) -> tuple[float, int]:
    x = x.sort_values(["active_ownership", "security_id"])
    n = len(x)
    k = int(np.floor(n * q))
    if n < min_names or k < 2:
        return float("nan"), n
    low, high = x.iloc[:k], x.iloc[-k:]
    return _weighted_return(high, weighting) - _weighted_return(low, weighting), n


def build_daily_signal(joined: pd.DataFrame, q: float = 0.2,
                       min_names: int = 20, weighting: str = "equal",
                       sector_neutral: bool = False) -> pd.DataFrame:
    if not 0 < q <= 0.5:
        raise ValueError("quantile q must be in (0, 0.5]")
    if weighting not in {"equal", "value"}:
        raise ValueError("weighting must be equal or value")
    if sector_neutral and "sector" not in joined.columns:
        raise ValueError("sector-neutral backtest requires a sector column")
    if weighting == "value" and "market_cap" not in joined.columns:
        raise ValueError("value-weighted backtest requires market_cap")
    x = joined.dropna(subset=["ret", "active_ownership"]).copy()
    if "eligible" in x.columns:
        x = x.loc[x["eligible"].astype(bool)]
    out = []
    for day, daily in x.groupby("date", sort=True):
        if not sector_neutral:
            s, n = _spread(daily, q, min_names, weighting)
        else:
            grouped = []
            for _, sector in daily.dropna(subset=["sector"]).groupby("sector"):
                v, n_sector = _spread(sector, q, max(8, min_names // 4), weighting)
                if np.isfinite(v):
                    grouped.append((v, n_sector))
            # Equal sector weight prevents the largest sector from dominating.
            s = float(np.mean([v for v, _ in grouped])) if len(grouped) >= 2 else float("nan")
            n = len(daily)
        out.append({"date": day, "signal": s, "eligible_names": n})
    return pd.DataFrame(out).set_index("date") if out else pd.DataFrame(columns=["signal", "eligible_names"])


def hac_ols(x: np.ndarray, y: np.ndarray, lag: int = 5) -> dict:
    """OLS with Bartlett/Newey-West HAC; p-values use normal approximation."""
    ok = np.isfinite(x).all(axis=1) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n, k = x.shape
    if n < max(k + 10, 30):
        return {"n": n, "beta_signal": None, "t_hac": None, "p_hac": None, "r2": None}
    X = np.column_stack([np.ones(n), x])
    coefficients, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    if rank < X.shape[1]:
        return {"n": n, "beta_signal": None, "t_hac": None, "p_hac": None, "r2": None}
    residuals = y - X @ coefficients
    inv = np.linalg.pinv(X.T @ X)
    xe = X * residuals[:, None]
    meat = xe.T @ xe
    for ell in range(1, min(lag, n - 1) + 1):
        gamma = xe[ell:].T @ xe[:-ell]
        meat += (1 - ell / (lag + 1)) * (gamma + gamma.T)
    cov = inv @ meat @ inv
    se = math.sqrt(max(0.0, float(cov[1, 1])))
    t = float(coefficients[1] / se) if se > 0 else float("nan")
    p = float(2 * norm.sf(abs(t))) if np.isfinite(t) else None
    sst = np.sum((y - y.mean()) ** 2)
    r2 = float(1 - np.sum(residuals ** 2) / sst) if sst > 0 else None
    return {"n": int(n), "beta_signal": float(coefficients[1]),
            "t_hac": t, "p_hac": p, "r2": r2}


def performance(returns: pd.Series) -> dict:
    r = returns.dropna().astype(float)
    n = len(r)
    if n == 0:
        return {key: None for key in ["days", "cumulative_return", "cagr", "sharpe", "sortino", "max_drawdown", "hit_rate"]}
    equity = (1 + r).cumprod()
    cumulative = float(equity.iloc[-1] - 1)
    cagr = float(equity.iloc[-1] ** (TRADING_DAYS / n) - 1) if equity.iloc[-1] > 0 else -1.0
    vol = float(r.std(ddof=1)) if n > 1 else 0.0
    downside = float(np.sqrt(np.mean(np.minimum(r.to_numpy(), 0) ** 2)))
    dd = equity / equity.cummax().clip(lower=1) - 1
    return {"days": int(n), "cumulative_return": cumulative, "cagr": cagr,
            "sharpe": float(np.sqrt(TRADING_DAYS) * r.mean() / vol) if vol > 0 else None,
            "sortino": float(np.sqrt(TRADING_DAYS) * r.mean() / downside) if downside > 0 else None,
            "max_drawdown": float(dd.min()), "hit_rate": float((r > 0).mean())}


def block_bootstrap_sharpe(returns: pd.Series, repetitions: int = 500,
                           block: int = 5, seed: int = 2036) -> list[float] | None:
    r = returns.dropna().to_numpy(dtype=float)
    n = len(r)
    if n < 50 or np.std(r) == 0:
        return None
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(repetitions):
        starts = rng.integers(0, n, size=int(np.ceil(n / block)))
        sample = np.concatenate([r[np.arange(s, s + block) % n] for s in starts])[:n]
        sd = np.std(sample, ddof=1)
        if sd > 0:
            estimates.append(np.sqrt(TRADING_DAYS) * sample.mean() / sd)
    return [float(z) for z in np.quantile(estimates, [0.025, 0.975])] if estimates else None


def run_backtest(prices: pd.DataFrame, holdings: pd.DataFrame, market: pd.DataFrame,
                 owner_type: str = "all_active", q: float = 0.2, min_names: int = 20,
                 weighting: str = "equal", sector_neutral: bool = False,
                 lookback: int = 126, threshold: float = 0.25,
                 side_cost_bps: float = 2.0, short_borrow_bps_daily: float = 0.0,
                 max_age_days: int = 200) -> tuple[pd.DataFrame, dict]:
    validate_inputs(prices, holdings, market)
    joined = point_in_time_join(prices, holdings, owner_type, max_age_days)
    signals = build_daily_signal(joined, q, min_names, weighting, sector_neutral)
    m = market.set_index("date").sort_index()
    daily = m[["cc_return", "oc_return"]].join(signals).sort_index()
    daily["future_cc_return"] = daily["cc_return"].shift(-1)
    # Signal at close(t); market t+1 open-to-close is the actual tradable payoff.
    min_history = max(20, lookback // 2)
    hist = daily["signal"].shift(1)
    mu = hist.rolling(lookback, min_periods=min_history).mean()
    sigma = hist.rolling(lookback, min_periods=min_history).std()
    daily["zscore"] = (daily["signal"] - mu) / sigma.replace(0, np.nan)
    daily["decision_close"] = np.select(
        [daily["zscore"] >= threshold, daily["zscore"] <= -threshold],
        [1, -1], default=0,
    ).astype(int)
    daily["position_open"] = daily["decision_close"].shift(1).fillna(0).astype(int)
    daily["gross_return"] = daily["position_open"] * daily["oc_return"]
    daily["trading_cost"] = (
        daily["position_open"].abs() * 2 * side_cost_bps / 10000
        + (daily["position_open"] == -1) * short_borrow_bps_daily / 10000
    )
    daily["net_return"] = daily["gross_return"] - daily["trading_cost"]
    # A day is tradable only if next-day market OC prices are available.
    daily.loc[daily["oc_return"].isna(), ["gross_return", "net_return", "trading_cost"]] = np.nan
    daily["equity_net"] = (1 + daily["net_return"].fillna(0)).cumprod()
    daily["equity_gross"] = (1 + daily["gross_return"].fillna(0)).cumprod()
    daily["equity_cc_benchmark"] = (1 + daily["cc_return"].fillna(0)).cumprod()
    daily["equity_intraday_long"] = (1 + daily["oc_return"].fillna(0)).cumprod()
    x = daily["signal"].to_numpy(dtype=float).reshape(-1, 1)
    y = daily["future_cc_return"].to_numpy(dtype=float)
    predictive = hac_ols(x, y)
    controlled = hac_ols(np.column_stack([x, daily["cc_return"].to_numpy(dtype=float)]), y)
    valid_days = daily["signal"].notna()
    eligible = daily.loc[daily["net_return"].notna(), "net_return"]
    split = int(len(eligible) * 0.7)
    metrics = {
        "signal_days": int(valid_days.sum()),
        "signal_coverage": float(valid_days.mean()),
        "n_trading_days": int(daily["net_return"].notna().sum()),
        "active_fraction": float((daily["position_open"] != 0).mean()),
        "trade_days": int((daily["position_open"] != 0).sum()),
        "predictive_hac": predictive,
        "predictive_with_same_day_market_control_hac": controlled,
        "strategy_gross": performance(daily["gross_return"]),
        "strategy_net": performance(daily["net_return"]),
        "strategy_net_first_70pct": performance(eligible.iloc[:split]),
        "strategy_net_last_30pct": performance(eligible.iloc[split:]),
        "market_close_to_close_buy_hold": performance(daily["cc_return"]),
        "market_intraday_long_no_cost": performance(daily["oc_return"]),
        "sharpe_block_bootstrap_95pct": block_bootstrap_sharpe(daily["net_return"]),
        "note": "Split is only descriptive; the threshold/lookback must be prespecified, not optimized on full-sample outcomes.",
    }
    return daily, metrics


def save_report(daily: pd.DataFrame, metrics: dict, outdir: Path,
                source_label: str, args: dict) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    daily.to_csv(outdir / "daily.csv", float_format="%.9g", index_label="date")
    (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding="utf-8")
    (outdir / "config.json").write_text(json.dumps(args, indent=2), encoding="utf-8")
    (outdir / "provenance.json").write_text(json.dumps({
        "source_label": source_label,
        "empirical_reproduction": False,
        "warning": "Paper-inspired implementation, not exact paper replication. Synthetic data is not evidence of alpha.",
    }, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(11, 5))
    for col, name in [("equity_net", "Strategy net (intraday)"),
                      ("equity_gross", "Strategy gross (intraday)"),
                      ("equity_cc_benchmark", "Market buy-and-hold (close-close)"),
                      ("equity_intraday_long", "Always-long intraday (no cost)")]:
        ax.plot(daily.index, daily[col], label=name, linewidth=1.3)
    ax.set_title(f"Active Ownership Market Signal — {source_label.upper()}")
    ax.set_ylabel("Growth of $1 (different exposure windows)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(outdir / "equity.png", dpi=150)
    plt.close(fig)
    m = metrics["strategy_net"]
    h = metrics["predictive_hac"]
    def fmt(v):
        return "n/a" if v is None else f"{v:.4f}"
    report = f"""# Backtest Results — {source_label.upper()}

**EVIDENCE STATUS: {'SYNTHETIC TEST ONLY — NOT EMPIRICAL ALPHA' if source_label == 'synthetic' else 'USER-SUPPLIED DATA — VERIFY PROVENANCE AND PAPER SPECIFICATION'}**

This is an **inspired-by** implementation of Chen & Yin (2026), not an exact replication.
No paper result (including Sharpe ≈ 1) is claimed to have been reproduced.

## Prespecified signal and execution
- Ownership: most recently **published** active-ownership snapshot; same-day publications excluded.
- Signal: end-of-day high-minus-low daily stock return spread.
- Signal normalization: {args['lookback']}-day trailing z-score, past days only.
- Entry/exit: **next open → same-day close**, not an unattainable close-to-close fill.
- Trading costs: {args['side_cost_bps']} basis points per side; one daily round trip when active.
- Strategy: long (+1), short (-1), or flat; unit notional; no leverage.

## Results
| Metric | Result |
| --- | ---: |
| Valid signal days | {metrics['signal_days']} |
| Trading days | {metrics['n_trading_days']} |
| Active fraction | {fmt(metrics['active_fraction'])} |
| Net cumulative return | {fmt(m['cumulative_return'])} |
| Net CAGR | {fmt(m['cagr'])} |
| Net annualized Sharpe | {fmt(m['sharpe'])} |
| Net max drawdown | {fmt(m['max_drawdown'])} |
| Last 30% net Sharpe | {fmt(metrics['strategy_net_last_30pct']['sharpe'])} |
| Predictive beta (next-day close-close) | {fmt(h['beta_signal'])} |
| Predictive HAC t-stat / p-value | {fmt(h['t_hac'])} / {fmt(h['p_hac'])} |
| Block-bootstrap Sharpe CI (95%) | {metrics['sharpe_block_bootstrap_95pct']} |

![Equity curves](equity.png)

## Critical limitations
1. The authors' complete paper specification was not available for verification, so quintile definitions, adjustments, and universes may differ.
2. 13F holdings are delayed, long-only and incompletely reveal economic exposure; historical fund classification is essential.
3. Backtest quality depends on survivor-free, delisting-inclusive daily returns, security IDs and CUSIP crosswalks.
4. Predictive close-close returns are **not** credited as executable P&L; intraday P&L excludes the following overnight return.
5. This backtest does not estimate the paper's rational-expectations model or reproduce its structural 20% share.
6. For genuine out-of-sample evaluation, freeze thresholds on a training period before reviewing test results.
"""
    (outdir / "RESULTS.md").write_text(report, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prices", required=True)
    ap.add_argument("--holdings", required=True)
    ap.add_argument("--market", required=True)
    ap.add_argument("--out", default="outputs/latest")
    ap.add_argument("--source-label", choices=["synthetic", "licensed", "public"], required=True)
    ap.add_argument("--owner-type", default="all_active")
    ap.add_argument("--quantile", type=float, default=0.2)
    ap.add_argument("--min-names", type=int, default=20)
    ap.add_argument("--weighting", choices=["equal", "value"], default="equal")
    ap.add_argument("--sector-neutral", action="store_true")
    ap.add_argument("--lookback", type=int, default=126)
    ap.add_argument("--threshold", type=float, default=0.25)
    ap.add_argument("--side-cost-bps", type=float, default=2.0)
    ap.add_argument("--short-borrow-bps-daily", type=float, default=0)
    ap.add_argument("--max-age-days", type=int, default=200)
    args = ap.parse_args()
    kwargs = vars(args)
    prices = _read_csv(args.prices, ["date"])
    holdings = _read_csv(args.holdings, ["report_date", "available_date"])
    market = _read_csv(args.market, ["date"])
    daily, metrics = run_backtest(prices, holdings, market,
        owner_type=args.owner_type, q=args.quantile, min_names=args.min_names,
        weighting=args.weighting, sector_neutral=args.sector_neutral,
        lookback=args.lookback, threshold=args.threshold,
        side_cost_bps=args.side_cost_bps,
        short_borrow_bps_daily=args.short_borrow_bps_daily,
        max_age_days=args.max_age_days)
    save_report(daily, metrics, Path(args.out), args.source_label, kwargs)
    print(json.dumps({"result": str(Path(args.out) / "RESULTS.md"),
                      "net_sharpe": metrics["strategy_net"]["sharpe"],
                      "predictive_hac": metrics["predictive_hac"]}, indent=2))


if __name__ == "__main__":
    main()
