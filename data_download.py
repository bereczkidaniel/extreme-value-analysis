"""
Download historical daily closing prices for the ten stocks used in the
analysis via yfinance and write them to a single CSV file that the
`stock_analysis.Rmd` R Markdown report can read.

The default configuration downloads ten years of daily prices for a
sector-diversified basket of large-cap US equities (2 stocks per sector,
5 sectors), but the ticker list and date range can be edited below.

Usage
-----
    python data_download.py

Requires:
    - yfinance >= 0.2.0
    - pandas >= 2.0

Output
------
    data/stock_prices.csv     # dates in first column, one ticker per column
"""

from __future__ import annotations

import argparse
import os
import sys

import pandas as pd
import yfinance as yf

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

TICKERS: list[str] = [
    # Technology
    "AAPL", "MSFT",
    # Financials
    "JPM", "BAC",
    # Healthcare
    "JNJ", "PFE",
    # Energy
    "XOM", "CVX",
    # Consumer staples
    "PG", "KO",
]

START = "2015-01-01"
END = "2024-12-31"
OUT_PATH = os.path.join("data", "stock_prices.csv")


# ----------------------------------------------------------------------
# Download
# ----------------------------------------------------------------------

def download(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Download adjusted close prices for the given tickers."""
    print(f"Downloading {len(tickers)} tickers from {start} to {end} ...")
    raw = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,      # returns split/dividend-adjusted prices
        progress=False,
        group_by="column",
    )

    # yf.download returns a MultiIndex with fields Open/High/Low/Close/Volume
    # when multiple tickers are requested; pick the Close columns.
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"].copy()
    else:
        # Single ticker fallback
        prices = raw[["Close"]].copy()
        prices.columns = tickers

    prices = prices.reindex(columns=tickers)
    prices.index.name = "Date"
    return prices


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=START, help="start date YYYY-MM-DD")
    parser.add_argument("--end", default=END, help="end date YYYY-MM-DD")
    parser.add_argument("--out", default=OUT_PATH, help="output CSV path")
    args = parser.parse_args()

    prices = download(TICKERS, args.start, args.end)

    n_all = len(prices)
    n_clean = prices.dropna().shape[0]
    print(f"Downloaded {n_all} rows.  Rows with data for every ticker: {n_clean}.")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    prices.to_csv(args.out, float_format="%.6f")
    print(f"Saved: {args.out}")

    # Small preview so the user sees what came back
    print("\nFirst rows:")
    print(prices.head().to_string())
    print("\nLast rows:")
    print(prices.tail().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
