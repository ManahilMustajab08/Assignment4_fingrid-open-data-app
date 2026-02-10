"""
Catalog of Fingrid Open Data dataset IDs and human-readable names.
Used for user-defined variable selection (by name or ID).
Source: https://data.fingrid.fi/en/datasets
"""
from typing import Dict

# Map: display name -> dataset ID (string)
DATASET_CATALOG: Dict[str, str] = {
    "consumption": "193",           # Total power consumption in Finland
    "production": "192",             # Total power production in Finland
    "wind": "181",                  # Wind power production
    "hydro": "191",                 # Hydro power production
    "nuclear": "188",               # Nuclear power production
    "solar_forecast": "248",        # Solar power forecast
    "chp": "201",                   # Combined heat and power
    "industrial_chp": "202",        # Industrial CHP
    "other_production": "205",      # Reserve power plants and small-scale production
    "transmission_estonia": "180",  # Transmission Finland–Estonia
    "transmission_sweden_se1": "87",   # Transmission Finland–Northern Sweden (SE1)
    "transmission_sweden_se3": "89",   # Transmission Finland–Central Sweden (SE3)
    "transmission_norway": "187",   # Transmission Finland–Norway
    "peak_load": "183",            # Peak load power
    "power_system_state": "209",    # Power system state (traffic lights)
    "wind_forecast": "245",        # Wind power generation forecast
    "district_heating": "371",     # Electric boiler consumption sum
}


def get_dataset_id(name_or_id: str):
    """
    Resolve a variable name or raw dataset ID to a Fingrid dataset ID.
    Returns None if not found.
    """
    key = name_or_id.strip().lower().replace(" ", "_")
    if key in DATASET_CATALOG:
        return DATASET_CATALOG[key]
    # Allow raw numeric ID
    if name_or_id.isdigit():
        return name_or_id
    return None


def list_datasets() -> str:
    """Return a formatted string listing available dataset names and IDs."""
    lines = ["Available variables (use name or ID):", ""]
    for name, did in sorted(DATASET_CATALOG.items(), key=lambda x: x[0]):
        lines.append(f"  {name}: dataset ID {did}")
    return "\n".join(lines)
