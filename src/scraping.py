"""
scraping.py — Robust Wayback scraper for AAA Florida metro gas prices

What it does:
- Pulls Wayback capture timestamps for https://gasprices.aaa.com/?state=FL (years 2022–2025 by default)
- Chooses one capture per day (latest capture that day)
- Downloads raw archived HTML (id_ form) with retries + backoff
- Parses each metro block: h3[data-cost] -> next table.table-mob
- Writes results incrementally to CSV so you can stop/restart without losing progress
- Skips days already in the output CSV (resume)

Usage in a notebook:
    from src.scraping import run_scrape
    df = run_scrape(max_days=10)   # small test first
"""

from __future__ import annotations

import os
import re
import time
import random
import hashlib
from datetime import datetime
from typing import Iterable, Optional, List, Dict, Tuple

import requests
import pandas as pd
from bs4 import BeautifulSoup

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# -----------------------------
# Config
# -----------------------------
STATE_URL = "https://gasprices.aaa.com/?state=FL"
CDX = "https://web.archive.org/cdx/search/cdx"

DEFAULT_FROM_YEAR = 2022
DEFAULT_TO_YEAR = 2025

DEFAULT_OUT_CSV = "aaa_fl_metros_wayback_2022_2025.csv"
DEFAULT_ERRORS_CSV = "aaa_fl_wayback_errors.csv"


# -----------------------------
# Networking: session + retries
# -----------------------------
def make_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (compatible; WaybackScraper/1.0; +https://example.com)"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
    )

    retry = Retry(
        total=8,
        connect=8,
        read=8,
        status=8,
        backoff_factor=1.2,  # exponential backoff between retries
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)
    return sess


SESSION = make_session()


# -----------------------------
# Wayback helpers
# -----------------------------
def cdx_timestamps(
    url: str,
    from_year: int,
    to_year: int,
    limit: Optional[int] = None,
) -> List[str]:
    """
    Return all capture timestamps (strings) for url between from_year and to_year inclusive.
    """
    params = {
        "url": url,
        "from": str(from_year),
        "to": str(to_year),
        "output": "json",
        "fl": "timestamp,statuscode,mimetype",
        "filter": "statuscode:200",
    }
    if limit is not None:
        params["limit"] = str(limit)

    r = SESSION.get(CDX, params=params, timeout=(15, 60))
    r.raise_for_status()
    data = r.json()
    rows = data[1:]  # first row is header
    return [row[0] for row in rows]


def choose_latest_capture_per_day(timestamps: Iterable[str]) -> List[str]:
    """
    Deduplicate to one timestamp per day (YYYYMMDD), keeping the latest timestamp that day.
    """
    by_day: Dict[str, str] = {}
    for ts in timestamps:
        day = ts[:8]
        if day not in by_day or ts > by_day[day]:
            by_day[day] = ts
    return [by_day[d] for d in sorted(by_day.keys())]


def wayback_raw_html(timestamp: str, original_url: str, timeout: Tuple[int, int] = (15, 90)) -> str:
    """
    Fetch raw HTML for a given capture timestamp using id_ form (less rewriting).
    timeout=(connect_timeout, read_timeout)
    """
    wb_url = f"https://web.archive.org/web/{timestamp}id_/{original_url}"
    r = SESSION.get(wb_url, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for {wb_url}")
    return r.text


def ts_to_date(timestamp: str) -> str:
    return datetime.strptime(timestamp[:8], "%Y%m%d").date().isoformat()


# -----------------------------
# Parsing
# -----------------------------
_money = re.compile(r"^\$?\s*([0-9]+(?:\.[0-9]+)?)\s*$")


def parse_price(text: str):
    t = (text or "").strip()
    if not t or t in {"—", "–"}:
        return None
    m = _money.match(t.replace(",", ""))
    return float(m.group(1)) if m else None


def parse_metro_tables(html: str, capture_date: str, wayback_timestamp: str) -> pd.DataFrame:
    """
    Parse metro sections:
        h3[data-cost]  -> next table.table-mob (NOT record-table)
    Rows: Current Avg., Yesterday Avg., Week Ago Avg., Month Ago Avg., Year Ago Avg.
    """
    soup = BeautifulSoup(html, "html.parser")
    out = []

    for h3 in soup.select("h3[data-cost]"):
        metro = h3.get_text(strip=True)
        if not metro:
            continue

        # Only the "table-mob" table after this metro heading
        table = h3.find_next("table", class_="table-mob")
        if table is None:
            continue

        for tr in table.select("tbody tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all("td")]
            if len(cells) < 2:
                continue

            label = cells[0]
            vals = cells[1:5]  # regular, mid, premium, diesel

            out.append(
                {
                    "date": capture_date,
                    "wayback_timestamp": wayback_timestamp,
                    "metro": metro,
                    "label": label,
                    "regular": parse_price(vals[0]) if len(vals) > 0 else None,
                    "mid": parse_price(vals[1]) if len(vals) > 1 else None,
                    "premium": parse_price(vals[2]) if len(vals) > 2 else None,
                    "diesel": parse_price(vals[3]) if len(vals) > 3 else None,
                }
            )

    return pd.DataFrame(out)


# -----------------------------
# Resume + incremental saving
# -----------------------------
def _load_done_dates(out_csv: str) -> set:
    """
    Resume helper: if output exists, skip dates already scraped.
    """
    if not os.path.exists(out_csv):
        return set()
    try:
        df = pd.read_csv(out_csv, usecols=["date"])
        return set(df["date"].dropna().astype(str).unique().tolist())
    except Exception:
        # if file exists but is malformed, don't skip anything
        return set()


def _append_csv(df: pd.DataFrame, path: str):
    if df.empty:
        return
    header = not os.path.exists(path)
    df.to_csv(path, mode="a", header=header, index=False)


def _log_error(errors_csv: str, row: dict):
    header = not os.path.exists(errors_csv)
    pd.DataFrame([row]).to_csv(errors_csv, mode="a", header=header, index=False)


# -----------------------------
# Main runner
# -----------------------------
def run_scrape(
    from_year: int = DEFAULT_FROM_YEAR,
    to_year: int = DEFAULT_TO_YEAR,
    out_csv: str = DEFAULT_OUT_CSV,
    errors_csv: str = DEFAULT_ERRORS_CSV,
    sleep_s: float = 0.6,
    max_days: Optional[int] = None,
    keep_only_current: bool = False,
    verbose_every: int = 25,
) -> pd.DataFrame:
    """
    Scrape AAA FL metro prices from Wayback (embedded HTML).

    Parameters
    ----------
    from_year, to_year : int
        Year range for CDX timestamps.
    out_csv : str
        Incremental output file.
    errors_csv : str
        Incremental error log file.
    sleep_s : float
        Base sleep between requests (add jitter automatically).
    max_days : Optional[int]
        If set, only scrape the first N daily captures (great for testing).
    keep_only_current : bool
        If True, keep only label == "Current Avg."
    verbose_every : int
        Print progress every N days.

    Returns
    -------
    DataFrame of scraped rows from this run (also appended to out_csv).
    """
    print(f"CDX: listing captures for {STATE_URL} from {from_year} to {to_year} ...")
    ts_all = cdx_timestamps(STATE_URL, from_year=from_year, to_year=to_year)

    if not ts_all:
        print("No captures found in that range.")
        return pd.DataFrame()

    ts_daily = choose_latest_capture_per_day(ts_all)
    if max_days is not None:
        ts_daily = ts_daily[:max_days]

    done_dates = _load_done_dates(out_csv)
    total = len(ts_daily)

    print(f"Found {len(ts_all)} captures -> {len(ts_daily)} daily captures.")
    if done_dates:
        print(f"Resuming: {len(done_dates)} dates already in {out_csv} will be skipped.")

    batch = []
    scraped_this_run = []

    for i, ts in enumerate(ts_daily, 1):
        date = ts_to_date(ts)
        if date in done_dates:
            continue

        try:
            html = wayback_raw_html(ts, STATE_URL, timeout=(15, 120))
            df = parse_metro_tables(html, date, ts)

            if keep_only_current and not df.empty:
                df = df[df["label"] == "Current Avg."].copy()

            if not df.empty:
                batch.append(df)
                scraped_this_run.append(df)

        except Exception as e:
            _log_error(
                errors_csv,
                {
                    "date": date,
                    "wayback_timestamp": ts,
                    "error": str(e),
                },
            )

        # Incremental write every few iterations to protect progress
        if i % verbose_every == 0:
            if batch:
                df_batch = pd.concat(batch, ignore_index=True)
                _append_csv(df_batch, out_csv)
                batch = []
            print(f"Progress: {i}/{total} (latest ts={ts}, date={date})")

        # polite delay + jitter (reduces throttling / timeouts)
        time.sleep(max(0.0, sleep_s) + random.uniform(0, 0.35))

    # final flush
    if batch:
        df_batch = pd.concat(batch, ignore_index=True)
        _append_csv(df_batch, out_csv)

    if scraped_this_run:
        result = pd.concat(scraped_this_run, ignore_index=True)
        return result

    return pd.DataFrame()


# -----------------------------
# Script entry point
# -----------------------------
if __name__ == "__main__":
    # Running as a script (not from notebook)
    df = run_scrape(
        from_year=DEFAULT_FROM_YEAR,
        to_year=DEFAULT_TO_YEAR,
        out_csv=DEFAULT_OUT_CSV,
        errors_csv=DEFAULT_ERRORS_CSV,
        sleep_s=0.6,
        max_days=None,            # set e.g. 20 to test quickly
        keep_only_current=False,  # set True if you only want Current Avg.
        verbose_every=25,
    )
    print(df.head())
    print(f"Done. Appended results to {DEFAULT_OUT_CSV}")