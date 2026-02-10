"""
Format time series data as a readable table in the command line.
Uses no external dependencies beyond the standard library.
"""
from typing import List, Dict


def format_table(rows: List[Dict], variable_label: str, max_rows: int = 50) -> str:
    """
    Format rows as a simple ASCII table. If len(rows) > max_rows, show first and last
    rows and a line indicating truncation.
    """
    if not rows:
        return f"No data for '{variable_label}' in the given time range."

    lines = [f"\n--- {variable_label} ---", ""]
    col_start = "Start time (UTC)"
    col_end = "End time (UTC)"
    col_value = "Value"

    def row_to_str(r: Dict) -> str:
        st = r.get("start_time")
        et = r.get("end_time")
        v = r.get("value")
        st_s = str(st)[:19] if st else ""
        et_s = str(et)[:19] if et else ""
        v_s = f"{v:.2f}" if v is not None and isinstance(v, (int, float)) else str(v)
        return f"  {st_s:20}  {et_s:20}  {v_s:>12}"

    lines.append(f"  {col_start:20}  {col_end:20}  {col_value:>12}")
    lines.append("  " + "-" * 56)

    if len(rows) <= max_rows:
        for r in rows:
            lines.append(row_to_str(r))
    else:
        for r in rows[: max_rows // 2]:
            lines.append(row_to_str(r))
        lines.append("  ...")
        lines.append(f"  ({len(rows) - max_rows} rows omitted)")
        lines.append("  ...")
        for r in rows[-(max_rows // 2) :]:
            lines.append(row_to_str(r))

    lines.append("")
    lines.append(f"Total points: {len(rows)}")
    return "\n".join(lines)
