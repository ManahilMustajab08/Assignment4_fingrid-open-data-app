#!/usr/bin/env python3
"""
Fingrid data – CLI entry point.
Open data from the Fingrid Open Data API is fetched and displayed as a table
and/or chart. The API key and other information are obtained from developer-data.fingrid.fi.
"""
import argparse
import sys
from datetime import datetime, timedelta

# Ensure running from package root so local imports work
import os
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != APP_DIR and APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from api_client import (
    FingridAPIError,
    MissingAPIKeyError,
    NetworkError,
    RateLimitError,
    APIResponseError,
)
from datasets import list_datasets
from services.data_service import fetch_and_process, parse_time
from formatters.table_formatter import format_table
from formatters.chart_formatter import format_chart


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch electricity-related data from Fingrid Open Data API and display as table or chart.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Table: consumption for last 2 days (default variable and range)
  python main.py

  # Table: wind production for a custom range
  python main.py --variable wind --start 2024-01-01 --end 2024-01-03

  # Chart only, save to file
  python main.py --variable production --days 7 --chart --output chart.png

  # Both table and chart
  python main.py --variable consumption --days 1 --table --chart

  # List available variables
  python main.py --list-variables
"""
    )
    parser.add_argument(
        "--variable", "-v",
        default="consumption",
        help="Variable/dataset name or ID (default: consumption). Use --list-variables to see options.",
    )
    parser.add_argument(
        "--start",
        metavar="TIME",
        help="Start time (e.g. 2024-01-01 or 2024-01-01T00:00). Default: --end minus --days.",
    )
    parser.add_argument(
        "--end",
        metavar="TIME",
        help="End time. Default: now (or yesterday for some datasets).",
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=2,
        help="Number of days of data when --start/--end not given (default: 2).",
    )
    parser.add_argument(
        "--table", "-t",
        action="store_true",
        default=True,
        help="Print results as a table (default: True unless --chart-only).",
    )
    parser.add_argument(
        "--chart", "-c",
        action="store_true",
        help="Generate a matplotlib chart.",
    )
    parser.add_argument(
        "--chart-only",
        action="store_true",
        help="Only generate chart; do not print table.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save chart to FILE (implies --chart).",
    )
    parser.add_argument(
        "--list-variables",
        action="store_true",
        help="List available variable names and dataset IDs, then exit.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=50,
        help="Max rows to show in table before truncating (default: 50).",
    )
    args = parser.parse_args()
    if args.chart_only:
        args.table = False
    if args.output:
        args.chart = True
    return args


def get_time_range(args) -> tuple[str, str]:
    """Compute start_time and end_time for the API."""
    now = datetime.utcnow()
    if args.end:
        end_str = parse_time(args.end)
        end_dt = datetime.fromisoformat(end_str.replace("Z", ""))
    else:
        end_dt = now
        end_str = end_dt.strftime("%Y-%m-%dT%H:%M")

    if args.start:
        start_str = parse_time(args.start)
    else:
        start_dt = end_dt - timedelta(days=args.days)
        start_str = start_dt.strftime("%Y-%m-%dT%H:%M")

    return start_str, end_str


def main() -> int:
    args = parse_args()

    if args.list_variables:
        print(list_datasets())
        return 0

    start_str, end_str = get_time_range(args)

    try:
        rows, variable_label = fetch_and_process(args.variable, start_str, end_str)
    except FingridAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        if isinstance(e, MissingAPIKeyError):
            print("\nThe API key and other information are obtained from developer-data.fingrid.fi", file=sys.stderr)
            print("  1. Go to https://developer-data.fingrid.fi (or data.fingrid.fi → Developer portal).", file=sys.stderr)
            print("  2. Sign in/register and subscribe to 'Open Data starter'.", file=sys.stderr)
            print("  3. Copy your API key and set: export FINGRID_API_KEY=your_key", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\n" + list_datasets(), file=sys.stderr)
        return 1

    if args.table:
        print(format_table(rows, variable_label, max_rows=args.max_rows))

    if args.chart:
        out_path = args.output if args.output else None
        msg = format_chart(rows, variable_label, output_path=out_path)
        print(msg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
