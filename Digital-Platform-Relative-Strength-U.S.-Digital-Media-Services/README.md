# Digital-Platform Relative Strength and Subsequent Price Returns — U.S. Digital Advertising & Streaming Services

**Status: REPRODUCED RETROSPECTIVE PRICE-RETURN PILOT — NOT PIT / NOT TOTAL RETURN / NOT INVESTABLE ALPHA.**  
**Frozen dataset:** Plotly 6.5.2 example prices, 2018-01-01–2019-12-30; **data provider and adjustment status UNKNOWN**.  
**Evaluation:** 65 weekly formation dates, 260 security-date observations per model, overlapping 4-week outcomes.

## 01. Abstract

We ask whether a **predeclared, business-exposure-weighted eight-week relative-price-strength signal** improves forecasts of subsequent four-week benchmark-adjusted **price changes** for four digital-advertising/streaming-related U.S. public companies (GOOG, AMZN, FB, NFLX), relative to a two-stock technology comparison basket (AAPL, MSFT). On 65 purged expanding-window origins, the controlled model RMSE was **6.9437 percentage points**, versus **7.0143** with the new factor: a **-0.0706 pp** change (negative means deterioration). The factor does not pass the uncertainty, cross-sectional rank, and robustness tests. This is a deliberately narrow retrospective **price** panel, not a verified total-return or historical point-in-time equity-alpha backtest.

## 02. Research Design & Hypotheses

**Primary question:** Does exposure-weighted relative momentum at weekly close *t* forecast stock *i*'s four-week price return above an AAPL/MSFT technology comparison basket, beyond a train-only linear control model?

- **H1:** The fixed eight-week exposure-weighted signal improves four-week OOS RMSE over historical mean and simple momentum baselines.
- **H2:** The signal improves a multivariate Ridge control after four-week purge, and survives block-aware 1,000-draw feature placebo and 2,000-draw paired block bootstrap.
- **H3:** Improvement survives alternative horizons, a one-week information delay, leave-one-company-out, and 1,000 plausible analyst-weight perturbations.
- **Null:** Conditional predictive information is zero; an apparent spread can be chance, concentration, or regime artifact.

The **counterthesis** is that an eight-week return signal is mostly a nonlinear re-expression of four-week momentum already in the controls; technology factor rotations and retrospective name selection dominate any industry mechanism. Failure means no robust incremental gain over the strongest simple baseline and zero-spanning bootstrap interval.

## 03. Industry Context

The target is **digital advertising and streaming services**, not all technology manufacturing. Alphabet (GOOG) and Facebook (FB) are advertising/platform-heavy; Netflix (NFLX) is streaming subscription-heavy; Amazon (AMZN) is mixed retail/cloud/media with a low analyst digital-media exposure. The six-ticker Plotly teaching basket was selected **after the period**, and AAPL/MSFT are technology comparators rather than a market index. No defensible historical industry market-size series was supplied by this source; **2018 market size and CAGR are UNKNOWN** and not estimated from stock prices. Pre-formation 2017 SEC 10-Ks provide qualitative business-line evidence, not precise revenue-weighted industry exposure.

## 04. Data & Source Integrity

The frozen CSV is from [Plotly's documented sample dataset](https://plotly.com/python-api-reference/generated/plotly.express.data.html), with exact packaged [v6.5.2 dataset path](https://github.com/plotly/plotly.py/blob/v6.5.2/plotly/package_data/datasets/stocks.csv.gz). It has **105 strictly weekly **sample-grid** dates**, six positive normalized closing-price columns, 2018-01-01 to 2019-12-30. Input SHA-256 is recorded in `data/source_qa.md`. The first label (2018-01-01) falls on a U.S. market holiday, so the sample dates are not verified exchange close timestamps. The original exchange/vendor, adjustment factors, dividend treatment, sample creation date, historical price revisions and trading availability are **UNKNOWN**. Grade **B** applies only to the Plotly-distributed sample snapshot, **C** to unverified upstream market-data provenance, and **A** to SEC company filings. The `data/source_register.csv` contains exact URLs, observation periods, grades, filing dates where known, vintage limitations and permitted analytical roles.

## 05. Point-in-Time Availability

At a weekly formation close *t*, only prices observed through *t* enter the signal. The four-week outcome uses *(t,t+4]* and training samples require **training origin + 4 ≤ test origin**; model means/scales and coefficients are recomputed only on the eligible training rows. All four 2017 SEC 10-K filings were publicly filed by **2018-02-06**, before evaluated OOS dates, but their **analyst exposure priors are reconstructed retrospectively**. Plotly's sample does not document original historical price timestamps, corporate-action adjustments or release vintages; mechanical date ordering is **not** a genuine PIT audit. The entire result remains a fixed-snapshot retrospective falsification pilot.

## 06. Factor Construction

For company *i* at formation week *t*, with log normalized price \(p\) and equal-weight AAPL/MSFT log-price index \(b_t=(p_{AAPL,t}+p_{MSFT,t})/2\):

\[ M_{i,t}=100[(p_{i,t}-p_{i,t-8})-(b_t-b_{t-8})] \]
\[ F_{i,t}=w_i\tanh(M_{i,t}/20),\quad w_{GOOG,AMZN,FB,NFLX}=(.95,.30,1.00,.85). \]

The `20` scale, eight-week lookback and analyst weights are fixed, not fit on the target. The comparator index is an average of **log prices**, not a tradable rebalanced portfolio. The factor is price-derived; it is **not** independent evidence of advertising revenue, subscriptions or audience demand.

## 07. Exposure & Transmission

The pre-evaluation SEC evidence is [Alphabet 2017 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204418000007/0001652044-18-000007-index.htm), [Facebook 2017 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680118000009/0001326801-18-000009-index.html), [Netflix 2017 10-K](https://www.sec.gov/Archives/edgar/data/1065280/000106528018000069/0001065280-18-000069-index.htm) and [Amazon 2017 10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872418000005/0001018724-18-000005-index.htm). These filings establish business categories; the four weights are **analyst scenario priors**, not exact audited segment shares. The hypothesized channel is platform sentiment and demand anticipation → relative stock-price momentum → subsequent relative price changes, with major confounding from market beta, earnings surprises and rotation. `data/exposure_map.csv` preserves each filing URL/date and mapping rationale. There is no independent 2018–2019 fundamental outcome panel; 2017 filings are **descriptive only**, and no fundamental-lead conclusion is made.

## 08. Outcomes & Baselines

The outcome is \(Y_{i,t}=100[(p_{i,t+4}-p_{i,t})-(b_{t+4}-b_t)]\) **percentage points of log-price change**. It is **not total shareholder return**, and AAPL/MSFT is **not the S&P 500**. Models on identical OOS origins: expanding historical mean; last four-week relative return persistence; raw eight-week momentum; factor-only Ridge; controlled Ridge (lag4, lag1, four-week volatility, benchmark eight-week momentum, company fixed dummies); augmented Ridge (+factor). Ridge penalty is fixed at 10, with train-only z-scores and unpenalized intercept. Expanding evaluation has **65** origins × four stocks = **260** correlated security-week predictions; four-week labels overlap, so effective independent temporal information is far smaller than 260.

## 09. Empirical Findings

| Model | OOS predictions | RMSE (pp) | MAE (pp) | Direction accuracy |
|:--|--:|--:|--:|--:|
| mean | 260 | 6.6272 | 4.8347 | 0.646 |
| factor_only | 260 | 6.7417 | 4.9159 | 0.635 |
| control | 260 | 6.9437 | 5.2570 | 0.600 |
| augmented | 260 | 7.0143 | 5.3034 | 0.527 |
| persistence | 260 | 8.5029 | 6.4144 | 0.577 |
| momentum | 260 | 11.7065 | 8.9806 | 0.596 |

Control-minus-augmented RMSE is **-0.0706 pp** (negative = factor worsens). The augmented forecast rank IC averages **-0.160** across only four stocks per week; the top-minus-bottom realized benchmark-adjusted price-change spread averages **-1.509 pp** over overlapping four-week windows. Deducting a purely illustrative **20 basis point round-trip** gives **-1.709 pp**, **not** a backtested portfolio net return because turnover, rebalancing, dividends, financing, slippage and borrow are unverified. Figures 01–06 show raw paths, factor, outcome, RMSE, loss accumulation and IC.

## 10. Robustness & Placebos

A **1,000-refit** within-firm **four-week contiguous block-shuffle** of factor histories yields an exploratory upper-tail fraction **0.5405** for RMSE improvement; **not an exact p-value**, because overlapping targets and nonstationarity invalidate unconditional exchangeability. A **2,000-draw paired four-week moving-block bootstrap** gives a 95% improvement interval **[-0.3527, +0.1911] pp**, including zero. Under **1,000 fixed-prior exposure perturbations**, the fraction of improved forecasts is **0.000**. Leave-one-company-out (retrain/evaluate on the remaining three companies) tests concentration:

| Excluded company | Remaining-universe predictions/model | Improvement (pp) |
|:--|--:|--:|
| GOOG | 195 | -0.0849 |
| AMZN | 195 | -0.0491 |
| FB | 195 | -0.0169 |
| NFLX | 195 | -0.1018 |

Ablations and 40-week rolling training are saved in `results/ablations.csv` and `results/rolling.csv`; rolling improvement is **-0.3995 pp**. All 1,000 + 2,000 + 1,000 draw-level results are committed.

## 11. Regime Sensitivity

| Calendar regime | OOS origins | RMSE improvement (pp) |
|:--|--:|--:|
| 2018 | 17 | -0.0873 |
| 2019H1 | 25 | +0.0462 |
| 2019H2 | 23 | -0.1958 |

Alternative horizons and conservative signal lags are calculated with separate purged training sets:

| Horizon (weeks) | Signal lag (weeks) | OOS origins | Improvement (pp) |
|--:|--:|--:|--:|
| 2 | 0 | 69 | -0.0511 |
| 2 | 1 | 68 | -0.0514 |
| 4 | 0 | 65 | -0.0706 |
| 4 | 1 | 64 | -0.0189 |
| 8 | 0 | 57 | +0.2414 |
| 8 | 1 | 56 | +0.2806 |

The 2018–2019 window is too short to represent rate, pandemic, and AI cycles; results are highly sensitive to market regime and sample choice.

## 12. Bias Audit & Verdict

- **Historical PIT:** original price release/adjustment provenance UNKNOWN; no historical vendor tape.
- **Selection/survivorship:** six Plotly teaching tickers, retrospectively chosen four-company core; delistings and failed platforms excluded.
- **Leakage:** price features and train-only scaling avoid direct future-input leakage, but retrospective weights and source revisions remain unverified.
- **Temporal dependence:** overlapping four-week labels, strong shared market risk, only 65 test origins.
- **Multiple testing:** the predeclared main specification was tested with many robustness variants; no multiple-hypothesis adjusted alpha evidence.
- **Execution/costs:** normalized closing-price series, no total returns, borrow/turnover/market impact audit, and no real benchmark.
- **Fundamentals:** SEC filings used only for qualitative mapping, not independent 2018–2019 revenue/EPS outcome validation.

**Verdict: reject robust incremental predictive power.** The augmented model worsens OOS RMSE and has negative average cross-sectional rank IC. This is a reproduced, narrow, historical **price-return falsification pilot**, not an industry-demand lead, not PIT, and not investable equity alpha.

## 13. Reproduction

From the study directory in a Python environment with declared packages:

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m pytest -q tests
python execute_notebook.py
```

`run_analysis.py` saves full 1,000/2,000/1,000 draw distributions and 12 calculated PNG diagnostics. `execute_notebook.py` executes and saves the notebook with computed table/image outputs. `logs/` contains observed local execution, tests and clean-directory replay; GitHub CI structure checks are a **separate** claim and do not prove PIT or numeric reproduction. `data/plotly_stocks_2018_2019_frozen.csv` is committed; runtime extraction from Plotly is not required to reproduce the analysis.

## 14. Next-Stage Protocol

Acquire **vendor-verified daily unadjusted/adjusted prices, dividends, delisting histories and corporate-action timestamps**, plus the broad 2018-era digital-media universe; freeze actual original-release vintages. Obtain point-in-time quarterly company segment revenue, streaming subscribers and advertising demand from SEC filings with filing timestamps. Pre-register a monthly demand factor using **independent operating signals**, compare against sector ETF and a broad-market total-return benchmark, and enforce realistic turnover, borrow, slippage and false-discovery controls. Re-run a truly untouched post-2019 period before any alpha claim.

## 15. Sources & Artifacts

- Grade B: [Plotly sample stock dataset](https://plotly.com/python-api-reference/generated/plotly.express.data.html) and [exact v6.5.2 packaged source](https://github.com/plotly/plotly.py/blob/v6.5.2/plotly/package_data/datasets/stocks.csv.gz); dataset original publication date **UNKNOWN**.
- Grade A: [GOOG 2017 SEC 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204418000007/0001652044-18-000007-index.htm) (filed 2018-02-06), [FB 2017 SEC 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680118000009/0001326801-18-000009-index.html) (filed 2018-02-01), [NFLX 2017 SEC 10-K](https://www.sec.gov/Archives/edgar/data/1065280/000106528018000069/0001065280-18-000069-index.htm) (filed 2018-01-29), [AMZN 2017 SEC 10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872418000005/0001018724-18-000005-index.htm) (filed 2018-02-02).
- Grade C: original market-price vendor, adjustment history and release vintage **UNKNOWN**.
- Frozen input `data/plotly_stocks_2018_2019_frozen.csv`; derived panel `data/derived_formation_panel.csv`; exposure mapping `data/exposure_map.csv`; full register `data/source_register.csv`; provenance audit `data/source_qa.md`.
- Full tables `results/*.csv`, numeric verdict `results/summary.json`, twelve diagnostics `figures/*.png`, notebook `research.ipynb`, source `analysis.py`, runner `run_analysis.py`, tests `tests/test_digital_media.py`, logs `logs/`.
