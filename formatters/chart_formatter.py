"""
Format time series data as a visualization using matplotlib.
"""
from typing import List, Dict
from pathlib import Path


def format_chart(
    rows: List[Dict],
    variable_label: str,
    output_path=None,
) -> str:
    """
    Plot time vs value and optionally save to file. Returns a short message.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        return "Matplotlib is not installed. Install with: pip install matplotlib"

    if not rows:
        return f"No data to plot for '{variable_label}'."

    times = [r["start_time"] for r in rows]
    values = [r["value"] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(times, values, color="steelblue", linewidth=1.2)
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Value")
    ax.set_title(f"Fingrid Open Data: {variable_label}")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=100)
        plt.close(fig)
        return f"Chart saved to: {path.absolute()}"
    plt.show()
    return "Chart displayed."
