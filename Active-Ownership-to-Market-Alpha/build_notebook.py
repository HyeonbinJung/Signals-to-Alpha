"""Regenerate and EXECUTE the evidence-labeled research notebook without Jupyter.

Uses standard notebook v4.5 JSON, executes each code cell in sequence, captures
stdout and generated figures, and persists verified execution counts/outputs.
Requires only the study's declared numpy/pandas/scipy/matplotlib dependencies.
"""

from __future__ import annotations

import base64
import contextlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "research.ipynb"


def main():
    import os
    os.chdir(ROOT)
    cells = []
    env = {"__name__": "__main__"}
    counter = 0

    def markdown(source):
        cells.append({"cell_type": "markdown", "id": f"cell-{len(cells)+1:03d}",
                      "metadata": {}, "source": source.splitlines(keepends=True)})

    def code(source):
        nonlocal counter
        counter += 1
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(source, f"research cell {counter}", "exec"), env)
        outputs = []
        val = buf.getvalue()
        if val:
            outputs.append({"output_type": "stream", "name": "stdout", "text": val.splitlines(keepends=True)})
        image = env.pop("__notebook_image__", None)
        if image is not None:
            raw = Path(image).read_bytes()
            outputs.append({"output_type": "display_data", "metadata": {},
                            "data": {"image/png": base64.b64encode(raw).decode("ascii")}})
        cells.append({"cell_type": "code", "id": f"cell-{len(cells)+1:03d}",
                      "metadata": {}, "execution_count": counter, "outputs": outputs,
                      "source": source.splitlines(keepends=True)})

    markdown("""# Active Ownership & Market-Wide Information — Reproducibility Notebook

**Evidence level: SYNTHETIC SOFTWARE VALIDATION ONLY.** These cells **execute** a controlled fixture that deliberately embeds a positive lead-lag relation. They do **not** reproduce Chen and Yin (2026)'s reported Sharpe ratio or estimate the structural model. Run locally from this study directory; the saved outputs are generated, not fabricated.""")

    markdown("""## 01. Abstract

Chen and Yin report that active-management ownership-conditioned stock-return spreads forecast next-day S&P 500 futures and ETF returns. We separate close-to-close predictability from next-open executable intraday returns, with conservative ownership publication lags. We present a synthetic code-validation result, not real-market inference.""")
    code("""import sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
from make_synthetic_fixture import generate
from backtest import point_in_time_join, build_daily_signal, run_backtest, hac_ols
print('Python:', sys.version.split()[0])
print('Numpy:', np.__version__, '| Pandas:', pd.__version__)
print('RESEARCH STATUS: SYNTHETIC — EMPIRICAL ALPHA NOT ESTABLISHED')""")

    markdown("""## 02. Research Design & Hypotheses

H1: `S[t]` forecasts `ETF_close_to_close[t+1]`. H2: a day-*t* closing signal can be translated to an *open(t+1) → close(t+1)* position after fees. H3: cost/sector alternatives are robust. The generator intentionally builds H1; passing H1 on synthetic returns is a software test, not a statistical discovery.""")
    code("""generate(Path('data/synthetic'), seed=42, n_days=850, n_stocks=90)
p = pd.read_csv('data/synthetic/prices.csv', parse_dates=['date'])
h = pd.read_csv('data/synthetic/holdings.csv', parse_dates=['report_date','available_date'])
m = pd.read_csv('data/synthetic/market.csv', parse_dates=['date'])
print('Stock-day observations:', len(p), '| Holding snapshots:', len(h), '| ETF sessions:', len(m))
print('Market window:', m.date.min().date(), 'to', m.date.max().date())""")

    markdown("""## 03. Industry Context

The relevant economic problem is cross-asset information aggregation: informed, specialized stock selection versus segmented index investors. S&P 500 futures are liquid, so a true lead-lag claim must confront instantaneous-arbitrage arguments. The synthetic data have **no economic industry, recession, funding or market microstructure realism**.""")
    code("""print('SYNTHETIC sectors:', sorted(p['sector'].unique()))
print('SYNTHETIC owner categories:', sorted(h['owner_type'].unique()))
print('Distinct synthetic securities:', p.security_id.nunique())""")

    markdown("""## 04. Data & Source Integrity

Real sources would include 13F historical filing releases, manager classification, CRSP total/delisting returns and ETF session data. The holdings file here is generated using a stable ranking plus randomized quarterly changes. No real CUSIP/SEC data are represented by synthetic `SEC####` symbols. See `data_sources.csv` for verified publishers and access constraints.""")
    code("""sources = pd.read_csv('data_sources.csv')
print(sources[['source','dataset','access']].to_string(index=False))
print('Missing genuine inputs: historical manager type, amended 13F, survivor-free CRSP, live filing timestamps.')""")

    markdown("""## 05. Point-in-Time Availability

Ownership observations at quarter-end are not tradeable until actually filed. The join uses **strictly earlier** published snapshots, blocking same-day date-only ambiguity. The synthetic fixture places publication 45 days after report date solely to exercise this behavior.""")
    code("""joined = point_in_time_join(p, h, 'all_active')
known = joined.dropna(subset=['active_ownership'])
assert (known.available_date < known.date).all()
assert (known.report_date <= known.available_date).all()
print('PIT joined stock-day observations:', len(known))
print('Maximum calendar lag from release:', (known.date-known.available_date).dt.days.max())
print('Leakage guards: PASS (strict prior publication dates)')""")

    markdown("""## 06. Factor Construction

For each daily cross-section, compare the equal-weight returns of the 20% most versus 20% least active-owned equities. Form a t-close signal, then compute a trailing z-score using days *t−126...t−1* only; this ensures contemporary normalization does not peek into tomorrow's price or return.""")
    code("""signals = build_daily_signal(joined, q=0.2)
print('Available signal sessions:', signals.signal.notna().sum())
print('Average high-minus-low spread:', round(float(signals.signal.mean()),6))
print('Signal standard deviation:', round(float(signals.signal.std()),6))""")
    code("""fig, ax = plt.subplots(figsize=(7.6, 2.5))
ax.plot(signals.index, signals.signal, lw=0.55, color='#2563eb')
ax.axhline(0, color='black', lw=0.55)
ax.set(title='Figure 1 — Daily synthetic high-minus-low ownership return spread', ylabel='Daily return', xlabel='Date')
ax.grid(alpha=.2)
fig.tight_layout(); Path('outputs').mkdir(exist_ok=True)
fig.savefig('outputs/notebook_signal.png', dpi=80); plt.close(fig)
__notebook_image__ = 'outputs/notebook_signal.png'
print('Figure 1: Synthetic signal; not sourced from market data.')""")

    markdown("""## 07. Exposure & Transmission

The generator makes stock returns respond to a latent common variable scaled by active-ownership rank, while next-session index returns respond to the preceding latent state. This deliberately creates a lead-lag; success is an internal consistency check, not identification of the paper's rational-expectations mechanism.""")
    code("""market_indexed = m.set_index('date')
aligned = signals.join(market_indexed)
aligned['future_cc'] = aligned.cc_return.shift(-1)
print('Contemporaneous synthetic correlation:', round(aligned[['signal','cc_return']].corr().iloc[0,1],4))
print('One-day-ahead synthetic correlation:', round(aligned[['signal','future_cc']].corr().iloc[0,1],4))""")

    markdown("""## 08. Outcomes & Baselines

For forecasting, close-to-close t+1 returns can include overnight moves; **do not** credit these to an order placed after the t close. For execution, the rule enters at t+1 *open* and exits at the same day's *close*, incurring a two-sided fee. Buy-and-hold close-close and always-long intraday are both shown but represent different exposures.""")
    code("""daily, metrics = run_backtest(p, h, m)
print('Predictions: NW/HAC(5)', metrics['predictive_hac'])
print('Same-day market control: NW/HAC(5)', metrics['predictive_with_same_day_market_control_hac'])
print('Tradable strategy NET Sharpe:', round(metrics['strategy_net']['sharpe'],4))
print('WARNING: All above values are generated synthetic test results.')""")

    markdown("""## 09. Empirical Findings

**None from real markets.** Synthetic net Sharpe of ~2.89 is intentionally inflated by the data generator. The figure distinguishes gross/no-cost from costs and the two differently exposed market references. A comparison to Chen–Yin's published Sharpe near 1 would be invalid.""")
    code("""summary = pd.DataFrame({k: metrics[k] for k in ['strategy_gross','strategy_net','market_close_to_close_buy_hold','market_intraday_long_no_cost']}).T
print(summary[['cumulative_return','cagr','sharpe','max_drawdown']].round(4).to_string())""")
    code("""fig, ax = plt.subplots(figsize=(7.6, 3.0))
for key,label in [('equity_net','Strategy net intraday'),('equity_gross','Strategy gross intraday'),('equity_cc_benchmark','Market buy-hold close-close'),('equity_intraday_long','Market intraday no-cost')]:
    ax.plot(daily.index,daily[key],label=label,lw=1.0)
ax.set(title='Figure 2 — SYNTHETIC equity curve, different benchmark windows',ylabel='Growth of $1')
ax.legend(fontsize=7); ax.grid(alpha=.2); fig.tight_layout()
fig.savefig('outputs/notebook_equity.png',dpi=80); plt.close(fig)
__notebook_image__='outputs/notebook_equity.png'
print('Figure 2: Positive synthetic P&L results from injected predictability.')""")

    markdown("""## 10. Robustness & Placebos

We predeclare cost stress, 10/20/30% ownership tails, owner categories and sector neutrality. A cost sensitivity plot is a mechanism check: a strategy with frequent round trips should lose performance as fees increase. **True** block-aware placebo p-values and factor-neutral tests require real data and are pending.""")
    code("""cost_rows = []
for bps in [1,2,5,10]:
    _, r = run_backtest(p,h,m,side_cost_bps=bps)
    cost_rows.append((bps,r['strategy_net']['sharpe'],r['strategy_net']['cagr']))
cost_df = pd.DataFrame(cost_rows,columns=['one_side_bps','net_sharpe','net_cagr'])
print(cost_df.round(4).to_string(index=False))""")
    code("""fig, ax = plt.subplots(figsize=(6.8, 2.7))
ax.bar(cost_df.one_side_bps.astype(str),cost_df.net_sharpe,color='#64748b')
ax.set(title='Figure 3 — Synthetic net Sharpe by per-side fee',xlabel='Basis points per side',ylabel='Annualized net Sharpe')
ax.grid(axis='y',alpha=.2); fig.tight_layout()
fig.savefig('outputs/notebook_costs.png',dpi=80); plt.close(fig)
__notebook_image__='outputs/notebook_costs.png'
print('Figure 3: Costs reduce the artificial gross alpha.')""")
    code("""cases=[]
for q in [0.1,0.2,0.3]:
    _,mr=run_backtest(p,h,m,q=q)
    cases.append((q,mr['strategy_net']['sharpe'],mr['predictive_hac']['p_hac']))
print(pd.DataFrame(cases,columns=['tail_fraction','net_sharpe','hac_p_value']).to_string(index=False))""")

    markdown("""## 11. Regime Sensitivity

The synthetic fixture has no recession, VIX, funding-tightness or international regimes. The authors' public abstract reports heterogeneity, but the present simulation does not verify it. A chronological last-30% split below is descriptive, **not a genuinely untouched holdout**, since the code and hyperparameters were designed with synthetic behavior in mind.""")
    code("""print('First 70% net:', metrics['strategy_net_first_70pct'])
print('Last 30% net:', metrics['strategy_net_last_30pct'])
print('Bootstrap 95% net Sharpe interval:', metrics['sharpe_block_bootstrap_95pct'])""")

    markdown("""## 12. Bias Audit & Verdict

Real threats include survival and CUSIP mapping, 13F delayed public availability, manager-type endogeneity, betas/momentum/industry risk, short book invisibility, index-futures arbitrage and true transaction costs. Synthetic certainty does not establish an economic mechanism. **Verdict: reproducible synthetic software validation; investable alpha unproven.**""")
    code("""assert (daily['position_open'] == daily['decision_close'].shift(1).fillna(0)).all()
assert (daily['trading_cost'] >= 0).all()
assert (daily['gross_return'] >= daily['net_return']).all()
print('Execution shift, nonnegative trading costs and gross-net ordering: ALL PASS')""")

    markdown("""## 13. Reproduction

`python -m unittest discover -s tests -v`; `python make_synthetic_fixture.py --out data/synthetic`; `python backtest.py --prices ... --holdings ... --market ... --source-label synthetic`; `python robustness.py ...`. `python build_notebook.py` re-executes and stores cell outputs. All paths are local to this study folder; no vendor data, tokens or credentials are committed.""")
    code("""print('Notebook code cells executed in this regeneration; generated outputs saved in research.ipynb.')
print('Independent unit test command: python -m unittest discover -s tests -v')""")

    markdown("""## 14. Next-Stage Protocol

Obtain SEC/WRDS historical manager-level data with actual filing timestamps, CRSP delisting-inclusive returns and S&P 500 ETF market sessions; read all original empirical tables; replicate exact portfolio construction; freeze parameters on a training period and test a genuinely untouched holdout with factor controls, funding state masks, placebo and effective trading costs. Treat any failure as publishable negative evidence.""")

    markdown("""## 15. Sources & Artifacts

- Chen & Yin (2026), *Between the Bells: Active Management and the Aggregation of Market-Wide Information*: https://ssrn.com/abstract=7367200
- SEC Form 13F datasets: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
- SEC investor guide: https://www.investor.gov/introduction-investing/investing-basics/glossary/form-13f-reports-filed-institutional-investment
- Source register: `data_sources.csv`; full methodology `DETAILS.md`; source code `backtest.py`; tests `tests/test_backtest.py`; synthetic scorecard `results_synthetic/RESULTS.md`.

**Do not quote synthetic metrics as empirical finance results.**""")

    doc = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                          "language_info": {"name": "python", "version": "3.12"}},
           "nbformat": 4, "nbformat_minor": 5}
    NOTEBOOK.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    executed = [c for c in cells if c["cell_type"] == "code" and c["execution_count"] is not None]
    graphics = sum(any("image/png" in output.get("data", {}) for output in c["outputs"]) for c in executed)
    print(f"Wrote {NOTEBOOK}: {len(cells)} cells, {len(executed)} executed code cells, {graphics} embedded figures")


if __name__ == "__main__":
    main()
