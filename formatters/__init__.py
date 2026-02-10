"""Formatters: present data as table (CLI) or chart (matplotlib)."""
from .table_formatter import format_table
from .chart_formatter import format_chart

__all__ = ["format_table", "format_chart"]
