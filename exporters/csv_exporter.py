"""CSV exporter for analysis summaries and result tables."""

import csv
import json

from smartretail.core.domain import AnalyticsResult
from smartretail.core.exceptions import ExportError
from .base import IResultExporter


class CsvExporter(IResultExporter):
    """Write summary values followed by each result table to a CSV file."""

    def export(self, result: AnalyticsResult, destination: str) -> str:
        try:
            with open(destination, "w", newline="", encoding="utf-8") as output:
                writer = csv.writer(output)
                writer.writerow(["section", "key", "value"])
                writer.writerows(
                    ("summary", key, json.dumps(value, default=str))
                    for key, value in result.summary.items()
                )

                for section, rows in result.tables.items():
                    writer.writerow([section])
                    if not rows:
                        continue
                    table_writer = csv.DictWriter(
                        output, fieldnames=list(rows[0].keys())
                    )
                    table_writer.writeheader()
                    table_writer.writerows(rows)
            return destination
        except OSError as exc:
            raise ExportError(f"Could not write CSV export: {exc}") from exc
