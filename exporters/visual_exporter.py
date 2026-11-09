"""Export printable PDF and HTML analysis reports."""

import html
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from smartretail.core.domain import AnalyticsResult
from smartretail.core.exceptions import ExportError
from .base import IResultExporter


class VisualReportExporter(IResultExporter):
    """Create a concise HTML or PDF summary for an analysis result."""

    def export(self, result: AnalyticsResult, destination: str) -> str:
        try:
            if destination.lower().endswith(".pdf"):
                return self._export_pdf(result, destination)
            return self._export_html(result, destination)
        except (OSError, ImportError, ValueError) as exc:
            raise ExportError(f"Could not create analysis report: {exc}") from exc

    @staticmethod
    def _export_html(result: AnalyticsResult, destination: str) -> str:
        target = (
            destination
            if destination.lower().endswith(".html")
            else f"{destination}.html"
        )
        summary = html.escape(json.dumps(result.summary, indent=2, default=str))
        tables = html.escape(json.dumps(result.tables, indent=2, default=str))
        alerts = html.escape("\n".join(result.alerts))
        body = (
            f"<h1>{html.escape(result.strategy_name)}</h1>"
            f"<h2>Summary</h2><pre>{summary}</pre>"
            f"<h2>Tables</h2><pre>{tables}</pre>"
            f"<h2>Alerts</h2><pre>{alerts}</pre>"
        )
        document = (
            '<!doctype html><meta charset="utf-8">'
            "<title>SmartRetail Report</title>"
            '<body style="font:16px sans-serif;max-width:1000px;margin:3rem auto">'
            f"{body}</body>"
        )
        with open(target, "w", encoding="utf-8") as output:
            output.write(document)
        return target

    def _export_pdf(self, result: AnalyticsResult, destination: str) -> str:
        from matplotlib.backends.backend_pdf import PdfPages
        from matplotlib.figure import Figure
        from matplotlib.patches import FancyBboxPatch

        summary = result.summary
        tables = result.tables
        strategy_name = result.strategy_name.lower()
        paper = "#FBFAF8"
        ink = "#302C27"
        muted = "#77716A"
        accent = "#F99F46"
        teal = "#4ABDAC"
        gold = "#F7B733"

        figure = Figure(figsize=(8.27, 11.69), facecolor=paper)
        header = figure.add_axes([0, 0, 1, 1])
        header.axis("off")
        self._draw_header(header, result, ink, muted, accent)
        self._draw_metrics(header, result, ink, muted)

        chart = figure.add_axes([0.11, 0.405, 0.80, 0.285])
        chart.set_facecolor(paper)
        for spine in chart.spines.values():
            spine.set_visible(False)
        chart.tick_params(colors=muted, labelsize=8)
        chart.grid(axis="y", color="#E8E3DC", linewidth=0.7)
        chart.set_axisbelow(True)
        self._draw_chart(chart, result, strategy_name, tables, paper, ink, muted, accent, teal, gold)

        header.text(0.075, 0.365, "Key results", fontsize=13, weight="bold", color=ink)
        self._draw_key_table(figure, header, tables, strategy_name, ink, muted)
        header.text(0.075, 0.065, "SmartRetail Analytics", fontsize=8, color=muted)
        header.text(
            0.925,
            0.065,
            "CONFIDENTIAL",
            fontsize=8,
            color=muted,
            ha="right",
        )

        with PdfPages(destination) as pdf:
            pdf.savefig(figure)
        figure.clear()
        return destination

    @staticmethod
    def _draw_header(header, result, ink, muted, accent) -> None:
        from matplotlib.patches import FancyBboxPatch

        header.text(
            0.075,
            0.945,
            "SMARTRETAIL  /  ANALYTICS",
            fontsize=9,
            weight="bold",
            color=muted,
        )
        header.text(
            0.075,
            0.902,
            result.strategy_name.replace("Strategy", " Analysis"),
            fontsize=23,
            weight="bold",
            color=ink,
        )
        header.text(
            0.075,
            0.875,
            f"Summary report  ·  {datetime.now():%d %b %Y}",
            fontsize=10,
            color=muted,
        )
        header.add_patch(
            FancyBboxPatch(
                (0.075, 0.851),
                0.85,
                0.004,
                boxstyle="round,pad=0.002",
                facecolor=accent,
                edgecolor="none",
            )
        )

    @staticmethod
    def _draw_metrics(header, result, ink, muted) -> None:
        from matplotlib.patches import FancyBboxPatch

        summary = result.summary
        row_count = summary.get("total_rows", summary.get("records", "—"))
        try:
            row_count = f"{int(row_count):,}"
        except (TypeError, ValueError):
            pass

        revenue = summary.get("net_revenue", "—")
        try:
            revenue = f"LKR {Decimal(str(revenue)):,.2f}"
        except (InvalidOperation, ValueError):
            pass

        quarantined = summary.get("quarantined", "—")
        try:
            quarantined = f"{int(quarantined):,}"
        except (TypeError, ValueError):
            pass

        metrics = [
            ("Rows processed", row_count),
            ("Net revenue", revenue),
            ("Quarantined", quarantined),
            ("Elapsed", f"{result.execution_time_sec:.1f} sec"),
        ]
        for index, (label, value) in enumerate(metrics):
            x_position = 0.075 + index * 0.218
            header.add_patch(
                FancyBboxPatch(
                    (x_position, 0.756),
                    0.198,
                    0.072,
                    boxstyle="round,pad=0.009,rounding_size=0.012",
                    facecolor="#F0EDE8",
                    edgecolor="none",
                )
            )
            header.text(
                x_position + 0.012,
                0.801,
                label.upper(),
                fontsize=7.5,
                weight="bold",
                color=muted,
            )
            header.text(
                x_position + 0.012,
                0.774,
                str(value),
                fontsize=12.5,
                weight="bold",
                color=ink,
            )
        header.text(0.075, 0.718, "At a glance", fontsize=13, weight="bold", color=ink)

    @staticmethod
    def _draw_chart(
        chart, result, strategy_name, tables, paper, ink, muted, accent, teal, gold
    ) -> None:
        if "peak" in strategy_name and result.charts_data.get("heatmap"):
            matrix = result.charts_data["heatmap"]
            hourly_counts = [sum(matrix[hour]) for hour in range(24)]
            chart.bar(range(24), hourly_counts, color=teal, width=0.75)
            chart.set_xticks(range(0, 24, 2))
            chart.set_xlabel("Hour of day", color=muted)
            chart.set_ylabel("Transactions", color=muted)
        elif "customer" in strategy_name and tables.get("segments"):
            rows = tables["segments"]
            chart.pie(
                [row["customers"] for row in rows],
                labels=[row["segment"].replace(" Customers", "") for row in rows],
                autopct="%1.0f%%",
                startangle=90,
                colors=[teal, accent, gold, "#AAA6A0"],
                textprops={"color": ink, "fontsize": 8},
                wedgeprops={"width": 0.38, "edgecolor": paper},
            )
        elif "seasonal" in strategy_name and tables.get("monthly_revenue"):
            rows = tables["monthly_revenue"]
            chart.plot(
                [row["month"] for row in rows],
                [float(row["revenue"]) for row in rows],
                color=teal,
                marker="o",
                markersize=4,
                linewidth=2,
            )
            chart.set_xticks(range(1, 13))
            chart.set_xlabel("Month", color=muted)
            chart.set_ylabel("Net revenue", color=muted)
        elif "product" in strategy_name and tables.get("categories"):
            rows = list(reversed(tables["categories"][:8]))
            chart.barh(
                [row["name"] for row in rows],
                [float(row["revenue"]) for row in rows],
                color=teal,
            )
            chart.set_xlabel("Net revenue", color=muted)
        elif "anomaly" in strategy_name and tables.get("alert_breakdown"):
            rows = list(reversed(tables["alert_breakdown"]))
            chart.barh(
                [row["alert_type"] for row in rows],
                [row["count"] for row in rows],
                color=accent,
            )
            chart.set_xlabel("Alert count", color=muted)
        elif "store" in strategy_name and tables.get("stores"):
            rows = list(reversed(tables["stores"][:8]))
            chart.barh(
                [row["store_id"] for row in rows],
                [float(row["revenue"]) for row in rows],
                color=gold,
            )
            chart.set_xlabel("Net revenue", color=muted)
        else:
            chart.axis("off")
            chart.text(
                0.5,
                0.5,
                "No chart data available",
                ha="center",
                va="center",
                color=muted,
            )

    @staticmethod
    def _draw_key_table(figure, header, tables, strategy_name, ink, muted) -> None:
        primary_tables = {
            "peak": "peak_hours",
            "customer": "segments",
            "seasonal": "monthly_revenue",
            "product": "categories",
            "anomaly": "alert_breakdown",
            "store": "stores",
        }
        table_name = next(
            (
                table
                for keyword, table in primary_tables.items()
                if keyword in strategy_name and tables.get(table)
            ),
            None,
        )
        rows = tables.get(table_name, [])[:6] if table_name else []
        if not rows:
            header.text(
                0.08,
                0.30,
                "No tabular results were returned for this analysis.",
                fontsize=10,
                color=muted,
            )
            return

        table_axis = figure.add_axes([0.075, 0.125, 0.85, 0.215])
        table_axis.axis("off")
        columns = list(rows[0].keys())[:4]
        cells = [
            [str(row.get(column, ""))[:42] for column in columns]
            for row in rows
        ]
        table = table_axis.table(
            cellText=cells,
            colLabels=[column.replace("_", " ").title() for column in columns],
            cellLoc="left",
            colLoc="left",
            bbox=[0, 0, 1, 1],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        for (row_index, _column_index), cell in table.get_celld().items():
            cell.set_linewidth(0)
            if row_index == 0:
                cell.set_facecolor("#E9E4DC")
                cell.set_text_props(weight="bold", color=ink)
            else:
                row_color = "#FFFFFF" if row_index % 2 else "#F4F1EC"
                cell.set_facecolor(row_color)
                cell.set_text_props(color=ink)
