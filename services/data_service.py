"""
Data service: orchestrates API client and processes raw API responses
into structured data for display (table or chart).
"""
from typing import List, Tuple
from datetime import datetime

from api_client import fetch_timeseries, FingridAPIError
from datasets import get_dataset_id, DATASET_CATALOG


def resolve_variable(name_or_id: str) -> str:
    """Resolve user input to a dataset ID. Raises ValueError if unknown."""
    did = get_dataset_id(name_or_id)
    if did is None:
        names = ", ".join(sorted(DATASET_CATALOG.keys())[:8])
        raise ValueError(
            f"Unknown variable: '{name_or_id}'. Use a name (e.g. {names}) or a dataset ID."
        )
    return did


def parse_time(s: str) -> str:
    """
    Normalize time string for Fingrid API.
    Accepts 'YYYY-MM-DD', 'YYYY-MM-DDTHH:MM', or 'YYYY-MM-DD HH:MM'.
    """
    s = s.strip()
    if "T" in s:
        part = s.split("T")[1]
        if len(part) == 5:  # HH:MM
            return s
        if len(part) == 8:  # HH:MM:SS
            return s
        return s
    if " " in s:
        date_part, time_part = s.split(" ", 1)
        return f"{date_part}T{time_part}"
    return f"{s}T00:00"


def fetch_and_process(
    variable: str,
    start_time: str,
    end_time: str,
) -> Tuple[List[dict], str]:
    """
    Fetch data for one variable and return (rows, variable_label).
    Each row is {'start_time': datetime, 'end_time': datetime, 'value': float, 'dataset_id': str}.
    variable_label is a short name for the series (e.g. for chart title).
    """
    dataset_id = resolve_variable(variable)
    # Resolve label from catalog if possible
    variable_label = variable
    for name, did in DATASET_CATALOG.items():
        if did == dataset_id:
            variable_label = name.replace("_", " ").title()
            break

    raw = fetch_timeseries([dataset_id], start_time, end_time)
    rows: List[dict] = []
    for item in raw:
        try:
            st = item.get("startTime")
            et = item.get("endTime")
            value = item.get("value")
            if st is None or value is None:
                continue
            # Parse ISO format e.g. 2024-01-01T00:00:00.000Z
            if isinstance(st, str):
                st = st.replace("Z", "+00:00").replace(".000", "")
                try:
                    dt_start = datetime.fromisoformat(st.replace("+00:00", ""))
                except ValueError:
                    dt_start = datetime.fromisoformat(st)
            else:
                dt_start = st
            if et and isinstance(et, str):
                et = et.replace("Z", "+00:00").replace(".000", "")
                try:
                    dt_end = datetime.fromisoformat(et.replace("+00:00", ""))
                except ValueError:
                    dt_end = datetime.fromisoformat(et)
            else:
                dt_end = dt_start
            rows.append({
                "start_time": dt_start,
                "end_time": dt_end,
                "value": float(value) if value is not None else None,
                "dataset_id": str(item.get("datasetId", dataset_id)),
            })
        except (TypeError, ValueError):
            continue
    rows.sort(key=lambda r: r["start_time"])
    return rows, variable_label
