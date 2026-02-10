#!/usr/bin/env python3
"""
Fetch metadata for all datasets from the Fingrid Open Data API.
Writes id and name (English) to datasets_info.txt.
Based on the course example: github.com/miksa007/Sustainable2025_ex

The API key and other information are obtained from developer-data.fingrid.fi.

Usage:
  export FINGRID_API_KEY='your_api_key'   # or API_KEY
  python get_datasets.py
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

# Support same env var as course example
API_KEY_ENV_VARS = ("FINGRID_API_KEY", "FINGRID_OPENDATA_API_KEY", "API_KEY")
API_BASE = "https://data.fingrid.fi/api"
RATE_LIMIT_SLEEP = 2  # seconds between requests (API: 10 req/min)
ID_START = 1
ID_END = 251
OUTPUT_FILE = "datasets_info.txt"


def get_api_key():
    for var in API_KEY_ENV_VARS:
        key = os.environ.get(var)
        if key:
            return key
    return None


def main():
    api_key = get_api_key()
    if not api_key:
        print("Error: No API key found. Set one of: FINGRID_API_KEY, API_KEY", file=sys.stderr)
        sys.exit(1)

    headers = {"x-api-key": api_key, "Cache-Control": "no-cache"}
    datasets_info = []
    error_404_ids = []

    for dataset_id in range(ID_START, ID_END):
        try:
            url = f"{API_BASE}/datasets/{dataset_id}"
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
            did = data.get("id")
            name = data.get("nameEn") or data.get("name") or ""
            datasets_info.append({"id": did, "name": name})
        except urllib.error.HTTPError as e:
            if e.code == 404:
                error_404_ids.append(dataset_id)
            else:
                print(f"HTTP {e.code} for dataset {dataset_id}", file=sys.stderr)
        except Exception as e:
            print(f"Error fetching dataset {dataset_id}: {e}", file=sys.stderr)
        time.sleep(RATE_LIMIT_SLEEP)

    print("Dataset information (count):", len(datasets_info))
    print("Dataset IDs with 404:", error_404_ids[:20], "..." if len(error_404_ids) > 20 else "")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(datasets_info, f, indent=2, ensure_ascii=False)
    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
