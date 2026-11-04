"""Download the exact public input *families* used for the 2024 real-data pilot.

SEC 13F downloads require a descriptive SEC_USER_AGENT, e.g. a real name and
email. The public GitHub data release is mutable; compare local file SHA256
values against outputs/real_2024_pilot/audit.json before expecting identical
numbers. Source content is not redistributed through this research repository.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import time
from urllib.request import Request, urlopen


SEC_BASE = "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/"
RELEASE = "https://github.com/Johnbrick123/sp500-data/releases/download/data/"
FILES = {
    "13f_2023q4.zip": SEC_BASE + "2023q4_form13f.zip",
    "13f_2024janfeb.zip": SEC_BASE + "01jan2024-29feb2024_form13f.zip",
    "13f_2024marmay.zip": SEC_BASE + "01mar2024-31may2024_form13f.zip",
    "13f_2024junaug.zip": SEC_BASE + "01jun2024-31aug2024_form13f.zip",
    "13f_2024sepnov.zip": SEC_BASE + "01sep2024-30nov2024_form13f.zip",
    "prices_real.parquet": RELEASE + "prices.parquet",
    "membership_intervals.parquet": RELEASE + "membership_intervals.parquet",
    "ticker_cusip_snapshot.csv":
        "https://raw.githubusercontent.com/ReAXET/Stock_Data/master/StockCUSIPList.csv",
}


def download(url: str, target: Path, user_agent: str) -> None:
    part = target.with_name(target.name + ".incomplete")
    request = Request(url, headers={"User-Agent": user_agent})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=120) as response, part.open("wb") as output:
                while chunk := response.read(2 * 1024 * 1024):
                    output.write(chunk)
            if part.stat().st_size < 100:
                raise RuntimeError(f"Unexpectedly short response for {url}")
            part.replace(target)
            return
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if not ua or "@" not in ua:
        parser.error("Set SEC_USER_AGENT='Your Real Name your-email@example.org' before downloading")
    args.out.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        target = args.out / name
        if target.exists() and target.stat().st_size > 100:
            print(f"SKIP: {name} ({target.stat().st_size:,} bytes)", flush=True)
            continue
        print(f"FETCH: {name}", flush=True)
        download(url, target, ua if "sec.gov" in url else "ActiveOwnershipResearch/1.0")
        print(f"DONE: {name} ({target.stat().st_size:,} bytes)", flush=True)


if __name__ == "__main__":
    main()
