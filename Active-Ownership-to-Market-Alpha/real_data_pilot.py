"""REAL PUBLIC DATA exploratory pilot (not a Chen-Yin exact replication).

Reads SEC original 13F quarterly ZIPs and a third-party, historical S&P-500
price Parquet. A *manually selected* active-manager filing breadth fraction,
NOT active shares / shares outstanding, is used to rank equities.

No price, holding, or payoff values are simulated. The lack of historical
CUSIP crosswalk and definitive active/passive classifications makes this
an exploratory REAL-DATA PROXY, not an investable alpha result.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

import duckdb
import numpy as np
import pandas as pd

from backtest import (TRADING_DAYS, block_bootstrap_sharpe, hac_ols,
                      performance, point_in_time_join, save_report)


# Names are a predeclared, recognizable hedge/quant manager *proxy*.
# Filing names and actual holdings status are verified against SEC COVERPAGE.
MANAGER_PATTERN = re.compile(
    r"AQR CAPITAL MANAGEMENT|CITADEL ADVISORS|RENAISSANCE TECHNOLOGIES|"
    r"MILLENNIUM MANAGEMENT|POINT72 ASSET MANAGEMENT|BRIDGEWATER ASSOCIATES|"
    r"TWO SIGMA INVESTMENTS|TWO SIGMA ADVISERS|TIGER GLOBAL MANAGEMENT|"
    r"COATUE MANAGEMENT|PERSHING SQUARE CAPITAL MANAGEMENT|BAUPOST GROUP|"
    r"VIKING GLOBAL INVESTORS|LONE PINE CAPITAL|FARALLON CAPITAL MANAGEMENT|"
    r"GREENLIGHT CAPITAL|DEERFIELD MANAGEMENT|MARSHALL WACE|"
    r"VERITION FUND MANAGEMENT|JANE STREET GROUP|D. E. SHAW|"
    r"GOLDMAN SACHS ASSET MANAGEMENT|BAMCO INC|APPALOOSA MANAGEMENT|"
    r"SUSQUEHANNA INTERNATIONAL|RUBRIC CAPITAL MANAGEMENT",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_mapping(path: Path) -> tuple[dict, dict]:
    df = pd.read_csv(path, dtype=str, low_memory=False)
    df = df[df["AssetType"].str.upper().eq("EQUITY")].copy()
    df["CUSIP"] = df["CUSIP"].str.upper().str.strip().str.zfill(9)
    df["Symbol"] = df["Symbol"].str.upper().str.strip().str.replace(".", "-", regex=False)
    df = df[df["CUSIP"].str.len().eq(9)]
    # Only one-to-one identifiers are allowed; ambiguous reused symbols excluded.
    count_id = df.groupby("CUSIP")["Symbol"].nunique()
    count_symbol = df.groupby("Symbol")["CUSIP"].nunique()
    df = df[df.CUSIP.isin(count_id[count_id.eq(1)].index) &
            df.Symbol.isin(count_symbol[count_symbol.eq(1)].index)]
    df = df.drop_duplicates(["CUSIP", "Symbol"])
    return dict(zip(df.CUSIP, df.Symbol)), dict(zip(df.Symbol, df.CUSIP))


def read_meta(zip_paths: list[Path]) -> pd.DataFrame:
    tables = []
    for path in zip_paths:
        with ZipFile(path) as archive:
            submissions = pd.read_csv(archive.open("SUBMISSION.tsv"), sep="\t", dtype=str)
            covers = pd.read_csv(archive.open("COVERPAGE.tsv"), sep="\t", dtype=str,
                                 usecols=["ACCESSION_NUMBER", "FILINGMANAGER_NAME", "REPORTTYPE"])
        d = submissions.merge(covers, on="ACCESSION_NUMBER", how="inner")
        d["source_zip"] = str(path)
        d = d[d["FILINGMANAGER_NAME"].fillna("").str.contains(MANAGER_PATTERN)]
        d = d[d["SUBMISSIONTYPE"].eq("13F-HR")]
        d = d[d["REPORTTYPE"].fillna("").str.contains("HOLDINGS|COMBINATION", case=False)]
        d["FILING_DATE"] = pd.to_datetime(d["FILING_DATE"], format="%d-%b-%Y", errors="coerce")
        d["PERIODOFREPORT"] = pd.to_datetime(d["PERIODOFREPORT"], format="%d-%b-%Y", errors="coerce")
        d = d[d.PERIODOFREPORT.between("2023-09-30", "2024-09-30")]
        d = d[d.FILING_DATE.between("2023-10-01", "2024-11-30")]
        tables.append(d)
    meta = pd.concat(tables, ignore_index=True)
    meta = meta.sort_values("FILING_DATE").drop_duplicates(["CIK", "PERIODOFREPORT"], keep="last")
    return meta


def load_positions(meta: pd.DataFrame, mapping: dict, zip_paths: list[Path]):
    wanted = set(meta.ACCESSION_NUMBER)
    observed = {}
    line_count = 0
    mapped = 0
    for path in zip_paths:
        acc_for_zip = wanted & set(meta.loc[meta.source_zip.eq(str(path)), "ACCESSION_NUMBER"])
        if not acc_for_zip:
            continue
        with ZipFile(path) as archive:
            for chunk in pd.read_csv(archive.open("INFOTABLE.tsv"), sep="\t", dtype=str,
                                     usecols=["ACCESSION_NUMBER", "CUSIP", "PUTCALL", "SSHPRNAMTTYPE"],
                                     chunksize=250000, low_memory=False):
                chunk = chunk[chunk.ACCESSION_NUMBER.isin(acc_for_zip)]
                if chunk.empty:
                    continue
                chunk = chunk[chunk.PUTCALL.isna() & chunk.SSHPRNAMTTYPE.eq("SH")]
                chunk["CUSIP"] = chunk.CUSIP.str.upper().str.strip().str.zfill(9)
                line_count += len(chunk)
                chunk["ticker"] = chunk.CUSIP.map(mapping)
                chunk = chunk.dropna(subset=["ticker"])
                mapped += len(chunk)
                for accession, ticker_values in chunk.groupby("ACCESSION_NUMBER")["ticker"]:
                    observed.setdefault(accession, set()).update(ticker_values.tolist())
    return observed, {"selected_13f_line_count": line_count,
                      "mapped_line_count": mapped,
                      "selected_13f_line_mapping_fraction": mapped / line_count if line_count else 0}


def build_breadth_snapshots(meta: pd.DataFrame, positions: dict, universe: list[str],
                           min_managers: int = 8) -> tuple[pd.DataFrame, list]:
    latest = {}
    rows = []
    audits = []
    for date, reports in meta.sort_values("FILING_DATE").groupby("FILING_DATE", sort=True):
        for row in reports.itertuples(index=False):
            latest[row.CIK] = (positions.get(row.ACCESSION_NUMBER, set()), row.PERIODOFREPORT, date)
        available = {cik: item for cik, item in latest.items()
                     if (date - item[2]).days <= 200}
        if len(available) < min_managers:
            continue
        counts = Counter(t for names, _, _ in available.values() for t in names)
        # Each security's zero is explicit; nobody holding it is a true zero in
        # *this selected manager sample*, NOT zero total institutional ownership.
        for ticker in universe:
            rows.append((ticker, max(item[1] for item in available.values()),
                         date, "active_manager_breadth_proxy", counts[ticker] / len(available)))
        audits.append({"date": str(date.date()), "reporting_managers": len(available),
                       "covered_tickers": sum(1 for s in universe if counts[s] > 0)})
    if not rows:
        raise RuntimeError("No filing snapshots reached the predeclared minimum manager count")
    h = pd.DataFrame(rows, columns=["security_id", "report_date", "available_date",
                                     "owner_type", "active_ownership"])
    return h, audits


def load_prices(prices_path: Path, membership_path: Path, allowed: set[str]):
    con = duckdb.connect()
    # Date+membership interval enforces contemporaneous index inclusion.
    sql = """SELECT p.date, p.ticker, p.adj_close, p.open, p.close
        FROM read_parquet(?) p
        JOIN read_parquet(?) m ON p.ticker=m.ticker
        AND p.date>=m.start AND (m.end IS NULL OR p.date < m.end)
        WHERE p.date BETWEEN '2023-10-01' AND '2024-12-10'
        ORDER BY p.ticker, p.date"""
    frame = con.execute(sql, [str(prices_path), str(membership_path)]).df()
    # DuckDB's Parquet DATE arrives as datetime64[us], whereas SEC filing
    # timestamps are datetime64[ns]; pandas merge_asof requires exact dtypes.
    frame["date"] = pd.to_datetime(frame.date).astype("datetime64[ns]")
    # Get SPY from same adjusted/RAW OHLCV source, *outside* membership join.
    spy = con.execute("""SELECT date, adj_close, open, close
        FROM read_parquet(?) WHERE ticker='SPY'
        AND date BETWEEN '2023-10-01' AND '2024-12-10' ORDER BY date""",
        [str(prices_path)]).df()
    spy["date"] = pd.to_datetime(spy.date).astype("datetime64[ns]")
    spy["cc_return"] = spy.adj_close.pct_change(fill_method=None)
    spy["oc_return"] = spy.close / spy.open - 1
    frame = frame[frame.ticker.isin(allowed)].copy()
    frame["ret"] = frame.groupby("ticker")["adj_close"].pct_change(fill_method=None)
    frame = frame.dropna(subset=["ret"])
    frame = frame.rename(columns={"ticker": "security_id"})
    return frame[["date", "security_id", "ret"]], spy[["date", "cc_return", "oc_return"]].dropna()


def tie_aware_spread(joined: pd.DataFrame, q: float = 0.2, min_names: int = 100):
    rows = []
    for date, x in joined.dropna(subset=["ret", "active_ownership"]).groupby("date"):
        if len(x) < min_names:
            continue
        values = x.active_ownership
        low_cut, high_cut = values.quantile(q), values.quantile(1-q)
        if high_cut <= low_cut:
            continue
        low = x.loc[values <= low_cut, "ret"]
        high = x.loc[values >= high_cut, "ret"]
        if len(low) < 15 or len(high) < 15:
            continue
        rows.append((date, float(high.mean()-low.mean()), len(x), len(high), len(low)))
    return pd.DataFrame(rows, columns=["date", "signal", "n", "n_high", "n_low"]).set_index("date")


def evaluate(market: pd.DataFrame, signal: pd.DataFrame, lookback: int = 63,
             threshold: float = 0.25, cost_bps: float = 2.0):
    d = market.set_index("date").join(signal).sort_index()
    d["future_cc_return"] = d.cc_return.shift(-1)
    prior = d.signal.shift(1)
    mu = prior.rolling(lookback, min_periods=40).mean()
    sd = prior.rolling(lookback, min_periods=40).std().replace(0, np.nan)
    d["zscore"] = (d.signal-mu)/sd
    d["decision_close"] = np.select([d.zscore>=threshold, d.zscore<=-threshold], [1,-1], default=0)
    d["position_open"] = d.decision_close.shift(1).fillna(0).astype(int)
    d["gross_return"] = d.position_open * d.oc_return
    d["trading_cost"] = abs(d.position_open) * cost_bps * 2 / 10000
    d["net_return"] = d.gross_return-d.trading_cost
    d["equity_net"] = (1+d.net_return.fillna(0)).cumprod()
    d["equity_gross"] = (1+d.gross_return.fillna(0)).cumprod()
    d["equity_cc_benchmark"] = (1+d.cc_return.fillna(0)).cumprod()
    d["equity_intraday_long"] = (1+d.oc_return.fillna(0)).cumprod()
    reg=hac_ols(d.signal.to_numpy()[:,None], d.future_cc_return.to_numpy())
    control=hac_ols(np.column_stack([d.signal.to_numpy(),d.cc_return.to_numpy()]),
                    d.future_cc_return.to_numpy())
    trades = d.loc[d.position_open.ne(0), "net_return"]
    valid = d.net_return.dropna()
    split=int(len(valid)*0.7)
    m={"signal_days":int(d.signal.notna().sum()),"signal_coverage":float(d.signal.notna().mean()),
       "n_trading_days":len(valid),"active_fraction":float(d.position_open.ne(0).mean()),
       "trade_days":len(trades),"predictive_hac":reg,
       "predictive_with_same_day_market_control_hac":control,
       "strategy_gross":performance(d.gross_return),"strategy_net":performance(d.net_return),
       "strategy_net_first_70pct":performance(valid.iloc[:split]),
       "strategy_net_last_30pct":performance(valid.iloc[split:]),
       "market_close_to_close_buy_hold":performance(d.cc_return),
       "market_intraday_long_no_cost":performance(d.oc_return),
       "sharpe_block_bootstrap_95pct":block_bootstrap_sharpe(d.net_return),
       "note":"Retrospective public-price/13F proxy; no PIT crosswalk or true active ownership. 70/30 descriptive."}
    return d,m


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,default=Path("outputs/real_2024_pilot"))
    a=p.parse_args()
    src=a.source_dir
    paths=[src/f for f in ["13f_2023q4.zip","13f_2024janfeb.zip","13f_2024marmay.zip",
                                "13f_2024junaug.zip","13f_2024sepnov.zip"]]
    for path in paths+[src/"prices_real.parquet",src/"membership_intervals.parquet",
                       src/"ticker_cusip_snapshot.csv"]:
        if not path.is_file(): raise FileNotFoundError(path)
    a.out.mkdir(parents=True,exist_ok=True)
    cusip_map,ticker_map=load_mapping(src/"ticker_cusip_snapshot.csv")
    print("Crosswalk one-to-one mappings:",len(cusip_map),flush=True)
    price,spy=load_prices(src/"prices_real.parquet",src/"membership_intervals.parquet",set(ticker_map))
    universe=sorted(price.security_id.unique())
    print("PIT index universe eligible with 2022/2023 CUSIP snapshot:",len(universe),flush=True)
    metadata=read_meta(paths)
    print("Selected SEC filings:",len(metadata),"distinct managers:",metadata.CIK.nunique(),flush=True)
    positions,mapping_audit=load_positions(metadata,cusip_map,paths)
    print("SEC line mapping audit",mapping_audit,flush=True)
    holdings,snapshot_audit=build_breadth_snapshots(metadata,positions,universe)
    joined=point_in_time_join(price,holdings,"active_manager_breadth_proxy",max_age_days=200)
    nonmissing = joined.loc[joined.active_ownership.notna()]
    if not nonmissing.available_date.lt(nonmissing.date).all():
        raise AssertionError("PIT FAIL: same-day/future filing used in signal")
    if not nonmissing.report_date.le(nonmissing.available_date).all():
        raise AssertionError("PIT FAIL: report period after filing")
    signal=tie_aware_spread(joined)
    market=spy[spy.date.between("2023-11-01","2024-11-29")].copy()
    d,metrics=evaluate(market,signal)
    args={"lookback":63,"side_cost_bps":2.0,"threshold":0.25,"source":"SEC 13F / Johnbrick123 S&P 500 prices",
          "signal":"selected-manager breadth fraction; not ownership of shares outstanding"}
    save_report(d,metrics,a.out,"public",args)
    audit={"evidence_status":"REAL PUBLIC DATA; EXPLORATORY NON-REPLICATING PROXY",
           "source_checksums":{file.name:sha256(file) for file in paths+[src/"prices_real.parquet",
                     src/"membership_intervals.parquet",src/"ticker_cusip_snapshot.csv"]},
           "manager_name_pattern":MANAGER_PATTERN.pattern,
           "selected_managers":metadata[["CIK","FILINGMANAGER_NAME"]].drop_duplicates().to_dict("records"),
           "selected_filing_count":len(metadata),"manager_count":int(metadata.CIK.nunique()),
           "mapped_universe_size":len(universe),"mapping_audit":mapping_audit,
           "snapshot_count":len(snapshot_audit),"snapshot_audit":snapshot_audit,
           "pit_check": {"checked_rows":len(nonmissing),
                         "filing_always_before_signal_date":True,
                         "report_period_never_after_filing_date":True},
           "signal_days":int(signal.shape[0]),"max_ticker_sample":int(price.security_id.nunique()),
           "limitations":["13F CUSIP crosswalk is a retrospective snapshot, not historical verified PIT mapping",
             "Manager list is hand-picked and cannot stand for all active funds",
             "Breadth fraction is NOT institutional shares outstanding ownership",
             "Third-party price dataset is not a licensed point-in-time CRSP feed",
             "Index membership source accuracy is not independently audited here",
             "Related managers (e.g. Susquehanna affiliates) are not consolidated to ultimate parent",
             "No explicit filtering of vendor-flagged halted shares is applied, though the source no_trade_days.csv shows no affected dates in the pilot window",
             "Short selling, futures execution and factor neutrality not fully modeled"]}
    (a.out/"audit.json").write_text(json.dumps(audit,indent=2,default=str),encoding="utf-8")
    (a.out/"managers.csv").write_text(metadata[["CIK","FILINGMANAGER_NAME","PERIODOFREPORT",
            "FILING_DATE"]].to_csv(index=False),encoding="utf-8")
    (a.out/"breadth_daily.csv").write_text(signal.to_csv(index_label="date"),encoding="utf-8")
    (a.out/"REAL_PILOT_RESULTS.md").write_text(
        "# Actual 13F + historical prices pilot (2024)\n\n"
        "**REAL DATA, BUT NOT THE PAPER'S ACTIVE OWNERSHIP STRATEGY.** The variable is the "
        "fraction of selected managers reporting a holding, not shares held divided by shares outstanding. "
        "Historical CUSIP mappings, manager classification and factor controls remain unverified.\n\n"
        f"- Reporting managers: {metadata.CIK.nunique()}\n"
        f"- Filings: {len(metadata)}\n"
        f"- Crosswalk/price universe: {len(universe)} stocks\n"
        f"- Signal days: {metrics['signal_days']}\n"
        f"- Net Sharpe: {metrics['strategy_net']['sharpe']}\n"
        f"- Net CAGR: {metrics['strategy_net']['cagr']}\n"
        f"- Net max drawdown: {metrics['strategy_net']['max_drawdown']}\n"
        f"- HAC forecast beta/t/p: {metrics['predictive_hac']}\n"
        f"- Date range: {d.index.min().date()} to {d.index.max().date()}\n\n"
        "Compare with the synthetic report only to show why a deliberately planted alpha can mislead. "
        "See audit.json for source hashes, selected managers and limitations.\n",
        encoding="utf-8")
    print(json.dumps({"NET_SHARPE":metrics["strategy_net"]["sharpe"],
                      "HAC":metrics["predictive_hac"],"days":len(d),
                      "funds":metadata.CIK.nunique(),"out":str(a.out)},indent=2),flush=True)


if __name__=="__main__": main()
