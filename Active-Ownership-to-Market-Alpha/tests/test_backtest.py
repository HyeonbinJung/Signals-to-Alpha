import unittest

import numpy as np
import pandas as pd

from backtest import (
    build_daily_signal, hac_ols, performance, point_in_time_join,
    run_backtest, validate_inputs,
)
from make_synthetic_fixture import generate


class BacktestTests(unittest.TestCase):
    def test_same_day_filing_is_never_used(self):
        dates = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
        prices = pd.DataFrame({"date": dates, "security_id": ["X"] * 3, "ret": [0.01] * 3})
        h = pd.DataFrame({"security_id": ["X"], "report_date": pd.to_datetime(["2023-12-31"]),
                          "available_date": pd.to_datetime(["2024-01-03"]),
                          "owner_type": ["all_active"], "active_ownership": [0.5]})
        matched = point_in_time_join(prices, h, "all_active")
        self.assertTrue(matched.loc[matched["date"] <= pd.Timestamp("2024-01-03"), "active_ownership"].isna().all())
        self.assertEqual(float(matched.loc[matched["date"] == pd.Timestamp("2024-01-04"), "active_ownership"].iloc[0]), 0.5)

    def test_duplicate_market_dates_rejected(self):
        p = pd.DataFrame({"date": pd.to_datetime(["2024-01-01"]), "security_id": ["a"], "ret": [0.]})
        h = pd.DataFrame({"report_date": pd.to_datetime(["2023-12-01"]),
                          "available_date": pd.to_datetime(["2023-12-02"]), "security_id": ["a"],
                          "owner_type": ["all_active"], "active_ownership": [0.2]})
        m = pd.DataFrame({"date": pd.to_datetime(["2024-01-01"] * 2),
                          "cc_return": [0., 0.], "oc_return": [0., 0.]})
        with self.assertRaisesRegex(ValueError, "duplicate dates"):
            validate_inputs(p, h, m)

    def test_signal_sign(self):
        date = pd.Timestamp("2024-01-04")
        x = pd.DataFrame({"date": [date] * 20, "security_id": list(map(str, range(20))),
                          "ret": [0.] * 4 + [0.01] * 12 + [0.03] * 4,
                          "active_ownership": np.arange(20) / 20})
        signal = build_daily_signal(x).loc[date, "signal"]
        self.assertAlmostEqual(float(signal), 0.03)

    def test_no_future_position(self):
        # Decisions are made after close(t), for the OPEN-to-CLOSE payoff on t+1.
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            generate(Path(d), n_days=130, n_stocks=30)
            p = pd.read_csv(Path(d) / "prices.csv", parse_dates=["date"])
            h = pd.read_csv(Path(d) / "holdings.csv", parse_dates=["report_date", "available_date"])
            m = pd.read_csv(Path(d) / "market.csv", parse_dates=["date"])
            daily, _ = run_backtest(p, h, m, min_names=20, lookback=30)
            shifted = daily["decision_close"].shift(1).fillna(0).astype(int)
            pd.testing.assert_series_equal(daily["position_open"], shifted, check_names=False)
            np.testing.assert_allclose(daily["gross_return"], daily["position_open"] * daily["oc_return"])

    def test_cost_monotonicity(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            generate(Path(d), n_days=140, n_stocks=30)
            p = pd.read_csv(Path(d) / "prices.csv", parse_dates=["date"])
            h = pd.read_csv(Path(d) / "holdings.csv", parse_dates=["report_date", "available_date"])
            m = pd.read_csv(Path(d) / "market.csv", parse_dates=["date"])
            a, _ = run_backtest(p, h, m, lookback=30, side_cost_bps=1)
            b, _ = run_backtest(p, h, m, lookback=30, side_cost_bps=10)
            self.assertTrue((a["net_return"] >= b["net_return"]).all())
            self.assertTrue((a["net_return"] > b["net_return"]).any())

    def test_hac_recovers_known_relationship(self):
        rng = np.random.default_rng(9)
        x = rng.normal(size=500)
        y = 0.002 * x + rng.normal(0, 0.002, 500)
        reg = hac_ols(x[:, None], y)
        self.assertGreater(reg["beta_signal"], 0)
        self.assertLess(reg["p_hac"], 0.01)

    def test_constant_returns_no_sharpe(self):
        result = performance(pd.Series([0.0] * 50))
        self.assertIsNone(result["sharpe"])


if __name__ == "__main__":
    unittest.main()
