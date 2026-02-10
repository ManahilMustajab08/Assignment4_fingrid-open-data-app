#!/usr/bin/env python3
"""
Wind power example: fetch dataset metadata and/or time-series from Fingrid API.
Matches the course example style (github.com/miksa007/Sustainable2025_ex).

The API key and other information are obtained from developer-data.fingrid.fi.

- Without arguments: fetches metadata for dataset 75 (Wind power, 15 min) and prints it.
- With --data: fetches time-series for the last 24 hours and plots with matplotlib.

Usage:
  export FINGRID_API_KEY='your_key'   # or API_KEY (from developer-data.fingrid.fi)
  python wind.py                     # metadata only
  python wind.py --data              # fetch wind data and plot
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import urllib.request
import urllib.error

# Dataset IDs: 75 = Wind 15-min, 181 = Wind real-time
WIND_DATASET_15MIN = "75"
WIND_DATASET_RT = "181"
API_BASE = "https://data.fingrid.fi/api"


def get_api_key():
    return (
        os.environ.get("FINGRID_API_KEY")
        or os.environ.get("FINGRID_OPENDATA_API_KEY")
        or os.environ.get("API_KEY")
    )


def fetch_dataset_metadata(dataset_id: str) -> dict:
    """GET /api/datasets/{id} - returns metadata (name, unit, etc.)."""
    api_key = get_api_key()
    if not api_key:
        print("Error: Set FINGRID_API_KEY or API_KEY", file=sys.stderr)
        sys.exit(1)
    url = f"{API_BASE}/datasets/{dataset_id}"
    req = urllib.request.Request(url, headers={"x-api-key": api_key, "Cache-Control": "no-cache"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def fetch_timeseries(dataset_id: str, start_time: str, end_time: str) -> list:
    """GET /api/data?datasets=...&startTime=...&endTime=... - returns time-series."""
    api_key = get_api_key()
    if not api_key:
        print("Error: Set FINGRID_API_KEY or API_KEY", file=sys.stderr)
        sys.exit(1)
    url = (
        f"{API_BASE}/data"
        f"?datasets={dataset_id}&startTime={start_time}&endTime={end_time}"
        f"&pageSize=10000&page=1"
    )
    req = urllib.request.Request(url, headers={"x-api-key": api_key}, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("data") or []


def main():
    parser = argparse.ArgumentParser(description="Wind power example: metadata and/or time-series from Fingrid")
    parser.add_argument("--data", action="store_true", help="Fetch wind time-series and plot (matplotlib)")
    parser.add_argument("--id", default=WIND_DATASET_15MIN, help="Dataset ID (default 75 = wind 15-min)")
    args = parser.parse_args()

    dataset_id = args.id

    # 1) Fetch and print metadata (same as course wind.py)
    print(f"Fetching metadata for dataset {dataset_id}...")
    meta = fetch_dataset_metadata(dataset_id)
    print("Response (metadata):")
    print(json.dumps(meta, indent=2, ensure_ascii=False))

    if not args.data:
        return

    # 2) Optional: fetch time-series and plot
    end = datetime.utcnow()
    start = end - timedelta(hours=24)
    start_str = start.strftime("%Y-%m-%dT%H:%M")
    end_str = end.strftime("%Y-%m-%dT%H:%M")
    print(f"\nFetching time-series from {start_str} to {end_str}...")
    rows = fetch_timeseries(dataset_id, start_str, end_str)
    if not rows:
        print("No data points returned.")
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("Install matplotlib to plot: pip install matplotlib")
        return
    times = [datetime.fromisoformat(r["startTime"].replace("Z", "").replace(".000", "")) for r in rows]
    values = [r["value"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, values, color="steelblue")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("MW")
    ax.set_title(f"Wind power (dataset {dataset_id}) – last 24 h")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    out = "wind_plot.png"
    fig.savefig(out, dpi=100)
    plt.close()
    print(f"Plot saved to {out}")


if __name__ == "__main__":
    main()
