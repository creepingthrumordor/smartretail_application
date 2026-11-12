"""Automated checks mapped to the Task 2 test plan (T02–T14)."""

import csv
import io
import os
import time
import tracemalloc
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from smartretail.adapters.csv_adapter import CsvInputAdapter
from smartretail.adapters.log_adapter import LogInputAdapter
from smartretail.analytics.anomaly_detection import AnomalyDetectionStrategy
from smartretail.analytics.customer_segmentation import CustomerSegmentationStrategy
from smartretail.analytics.peak_sales import PeakSalesStrategy
from smartretail.analytics.product_revenue import ProductRevenueStrategy
from smartretail.analytics.seasonal_demand import SeasonalDemandStrategy
from smartretail.analytics.store_regional import StoreRegionalPerformanceStrategy
from smartretail.config import CSV_FIELDS
from smartretail.core.domain import RawRecord
from smartretail.core.exceptions import ExportError, InputFormatError
from smartretail.exporters.csv_exporter import CsvExporter
from smartretail.exporters.visual_exporter import VisualReportExporter
from smartretail.gui import app as gui_app
from smartretail.pipeline.builder import PipelineBuilder
from smartretail.services.chunk_service import ChunkProcessingService
from smartretail.services.facade import SmartRetailFacade
from smartretail.validation.dead_letter_queue import DeadLetterQueue
from smartretail.validation.validator import RecordValidator


def _make_record(row):
    """Parse fixture values through the production validator for test data."""
    buffer = io.StringIO(newline="")
    csv.writer(buffer).writerow([row[field] for field in CSV_FIELDS])
    record, error = RecordValidator().parse_and_validate(
        RawRecord("fixture.csv", 2, buffer.getvalue().rstrip("\r\n"))
    )
    assert error is None
    return record


def test_log_adapter_returns_valid_and_malformed_lines_with_locations(tmp_path):
    path = tmp_path / "transactions.log"
    path.write_text("valid transaction entry\n{broken json\n", encoding="utf-8")
    adapter = LogInputAdapter()
    adapter.open(str(path))
    try:
        rows = adapter.read_chunk(5)
    finally:
        adapter.close()

    assert [row.data for row in rows] == ["valid transaction entry", "{broken json"]
    assert [row.line_number for row in rows] == [1, 2]
    assert all(row.source == str(path) for row in rows)


@pytest.mark.parametrize(
    ("field", "value", "expected_fragment"),
    [
        ("transaction_id", "", "Missing transaction_id"),
        ("transaction_datetime", "not-a-date", "Invalid transaction record"),
    ],
)
def test_validator_rejects_missing_required_value_and_bad_timestamp(
    transaction_row, field, value, expected_fragment
):
    transaction_row[field] = value
    buffer = io.StringIO(newline="")
    csv.writer(buffer).writerow(
        [transaction_row[column] for column in CSV_FIELDS]
    )

    record, error = RecordValidator().parse_and_validate(
        RawRecord("fixture.csv", 2, buffer.getvalue().rstrip("\r\n"))
    )

    assert record is None
    assert expected_fragment in error


def test_validator_accepts_negative_quantity_return(transaction_row):
    transaction_row.update(transaction_type="Return", quantity="-1")
    record = _make_record(transaction_row)

    assert record.is_return is True
    assert record.quantity == -1


def test_validator_rejects_return_with_positive_quantity(transaction_row):
    transaction_row.update(transaction_type="Return", quantity="1")
    buffer = io.StringIO(newline="")
    csv.writer(buffer).writerow(
        [transaction_row[column] for column in CSV_FIELDS]
    )
    record, error = RecordValidator().parse_and_validate(
        RawRecord("fixture.csv", 2, buffer.getvalue().rstrip("\r\n"))
    )

    assert record is None
    assert "Return quantity must be negative" in error


def test_malformed_record_is_quarantined_and_later_record_is_processed(
    write_transactions, transaction_row
):
    invalid = transaction_row.copy()
    invalid["transaction_datetime"] = "bad timestamp"
    path = write_transactions([invalid, transaction_row.copy()])
    dlq = DeadLetterQueue()
    service = ChunkProcessingService(PeakSalesStrategy(), dlq)

    result = service.run(CsvInputAdapter(), str(path), chunk_size=1)

    assert result.summary["total_rows"] == 2
    assert result.summary["records"] == 1
    assert result.summary["quarantined"] == 1
    rejected = dlq.get_all()[0]
    assert rejected.line_number == 2
    assert rejected.raw_data
    assert "Invalid transaction record" in rejected.reason


def test_conflicting_duplicate_is_quarantined_without_dropping_other_valid_row(
    write_transactions, transaction_row
):
    first = transaction_row.copy()
    exact_duplicate = transaction_row.copy()
    conflict = transaction_row.copy()
    conflict["unit_price"] = "101.00"
    conflict["total_amount"] = "181.80"
    unrelated = transaction_row.copy()
    unrelated["transaction_id"] = "TX-OTHER"
    path = write_transactions([first, exact_duplicate, conflict, unrelated])
    facade = SmartRetailFacade()

    result = facade.run_analysis(str(path), "csv", "peak_sales", chunk_size=2)

    assert result.summary["total_rows"] == 4
    assert result.summary["duplicates"] == 1
    assert result.summary["quarantined"] == 1
    assert result.summary["records"] == 2
    assert "Conflicting duplicate transaction_id" in facade.get_dlq().get_all()[0].reason


def test_pipeline_filter_enrichment_and_aggregation_match_expected_result(
    transaction_row,
):
    morning = replace(
        _make_record(transaction_row),
        transaction_datetime=datetime(2024, 5, 21, 9, 0),
    )
    afternoon = replace(
        morning,
        transaction_id="TX-AFTERNOON",
        transaction_datetime=datetime(2024, 5, 21, 17, 0),
    )
    pipeline = (
        PipelineBuilder()
        .add_filter(lambda row: row.transaction_datetime.hour >= 12)
        .add_enrichment(lambda row: replace(row, product_name=row.product_name.upper()))
        .add_aggregation(
            lambda rows: [
                replace(
                    rows[0],
                    quantity=sum(row.quantity for row in rows),
                    total_amount=sum(
                        (row.total_amount for row in rows), start=Decimal("0")
                    ),
                )
            ]
            if rows
            else []
        )
        .build()
    )

    result = pipeline.process_chunk([morning, afternoon])

    assert len(result) == 1
    assert result[0].product_name == "RICE"
    assert result[0].quantity == 2
    assert result[0].total_amount == Decimal("180.00")


def test_customer_segmentation_strategy_labels_known_customer_groups(
    transaction_row,
):
    base = _make_record(transaction_row)
    records = [
        replace(base, transaction_id=f"F-{index}", customer_id="frequent")
        for index in range(3)
    ]
    records.extend(
        replace(base, transaction_id=f"O-{index}", customer_id="occasional",
                total_amount=Decimal("100"))
        for index in range(2)
    )
    records.extend(
        [
            replace(base, transaction_id="ONE", customer_id="one-time"),
            replace(base, transaction_id="UNKNOWN", customer_id=None),
        ]
    )
    strategy = CustomerSegmentationStrategy()
    strategy.consume(records)

    result = strategy.build_result()
    segments = result.summary["segments"]

    assert segments["Frequent Customers"] == 1  # Three orders total $540.
    assert segments["Occasional Customers"] == 1
    assert segments["One-Time Customers"] == 1
    assert segments["Unknown Customers"] == 1


def test_seasonal_strategy_totals_revenue_by_month_and_promotion(transaction_row):
    base = _make_record(transaction_row)
    may = replace(base, promotion_name="May Promo", total_amount=Decimal("180"))
    june = replace(
        base,
        transaction_id="JUNE",
        transaction_datetime=datetime(2024, 6, 2, 12, 0),
        promotion_name=None,
        total_amount=Decimal("75"),
    )
    strategy = SeasonalDemandStrategy()
    strategy.consume([may, june])

    result = strategy.build_result()
    months = {row["month"]: row["revenue"] for row in result.tables["monthly_revenue"]}
    promotions = {row["promotion"]: row["revenue"] for row in result.tables["promotions"]}

    assert months[5] == "180"
    assert months[6] == "75"
    assert promotions == {"May Promo": "180", "None": "75"}


def test_product_revenue_strategy_ranks_products_and_categories(transaction_row):
    base = _make_record(transaction_row)
    lower = replace(
        base,
        transaction_id="LOWER",
        product_name="Tea",
        product_category="Beverages",
        total_amount=Decimal("60"),
    )
    strategy = ProductRevenueStrategy()
    strategy.consume([base, lower])

    result = strategy.build_result()

    assert result.tables["products"][0] == {"name": "Rice", "revenue": "180.00"}
    assert result.tables["categories"][0]["name"] == "Groceries"
    assert result.summary["records"] == 2


def test_store_regional_strategy_ranks_store_and_region_performance(transaction_row):
    base = _make_record(transaction_row)
    lower = replace(
        base,
        transaction_id="OTHER-STORE",
        store_id="STR002",
        region="East",
        total_amount=Decimal("60"),
    )
    strategy = StoreRegionalPerformanceStrategy()
    strategy.consume([base, lower])

    result = strategy.build_result()

    assert result.tables["stores"][0]["store_id"] == "STR001"
    assert result.tables["stores"][0]["revenue"] == "180.00"
    regions = {row["region"]: row["transactions"] for row in result.tables["regions"]}
    assert regions == {"West": 1, "East": 1}


def test_holiday_label_is_added_only_when_enrichment_is_configured(transaction_row):
    base = _make_record(transaction_row)
    strategy_without_calendar = SeasonalDemandStrategy()
    strategy_without_calendar.consume([base])
    without_calendar = strategy_without_calendar.build_result()

    calendar_pipeline = (
        PipelineBuilder()
        .add_enrichment(lambda row: replace(row, promotion_name="New Year Holiday"))
        .build()
    )
    strategy_with_calendar = SeasonalDemandStrategy()
    strategy_with_calendar.consume(calendar_pipeline.process_chunk([base]))
    with_calendar = strategy_with_calendar.build_result()

    assert "New Year Holiday" not in {
        row["promotion"] for row in without_calendar.tables["promotions"]
    }
    assert "New Year Holiday" in {
        row["promotion"] for row in with_calendar.tables["promotions"]
    }


def test_results_are_equivalent_across_chunk_sizes_including_partial_chunk(
    write_transactions, transaction_row
):
    rows = []
    for index in range(5):
        row = transaction_row.copy()
        row["transaction_id"] = f"TX-{index}"
        row["transaction_datetime"] = f"5/21/2024 {9 + index:02d}:00"
        rows.append(row)
    path = write_transactions(rows)

    one_at_a_time = SmartRetailFacade().run_analysis(
        str(path), "csv", "peak_sales", chunk_size=1
    )
    chunks_of_three = SmartRetailFacade().run_analysis(
        str(path), "csv", "peak_sales", chunk_size=3
    )

    assert one_at_a_time.summary == chunks_of_three.summary
    assert one_at_a_time.tables == chunks_of_three.tables
    assert one_at_a_time.charts_data == chunks_of_three.charts_data
    assert chunks_of_three.summary["total_rows"] == 5


def test_full_ingestion_dlq_analysis_and_csv_export(write_transactions, transaction_row, tmp_path):
    invalid = transaction_row.copy()
    invalid["transaction_datetime"] = "not a date"
    valid = transaction_row.copy()
    valid["transaction_id"] = "VALID-AFTER-INVALID"
    path = write_transactions([invalid, valid])
    facade = SmartRetailFacade()

    result = facade.run_analysis(str(path), "csv", "peak_sales", chunk_size=1)
    export_path = tmp_path / "integrated-result.csv"
    facade.export_result(result, "csv", str(export_path))

    assert result.summary["total_rows"] == 2
    assert result.summary["records"] == 1
    assert result.summary["quarantined"] == 1
    assert facade.get_dlq().get_all()[0].raw_data
    exported = export_path.read_text(encoding="utf-8")
    assert "summary" in exported
    assert "total_rows" in exported
    assert "peak_hours" in exported


def test_csv_and_visual_exports_contain_expected_result_content(tmp_path):
    from smartretail.core.domain import AnalyticsResult

    result = AnalyticsResult(
        "PeakSalesStrategy",
        {"records": 2, "net_revenue": "250.50"},
        {"peak_hours": [{"hour": 17, "count": 2}]},
        {"heatmap": [[0] * 7 for _ in range(24)]},
    )
    csv_path = tmp_path / "summary.csv"
    html_path = tmp_path / "summary.html"

    CsvExporter().export(result, str(csv_path))
    VisualReportExporter().export(result, str(html_path))

    csv_text = csv_path.read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")
    assert "section,key,value" in csv_text
    assert "net_revenue" in csv_text
    assert "250.50" in csv_text
    assert "PeakSalesStrategy" in html_text
    assert "peak_hours" in html_text


@pytest.mark.parametrize("failure", ["missing", "unsupported", "empty"])
def test_facade_reports_input_failures_clearly(failure, tmp_path):
    facade = SmartRetailFacade()
    if failure == "missing":
        path = tmp_path / "missing.csv"
        with pytest.raises(InputFormatError, match="does not exist"):
            facade.run_analysis(str(path), "csv", "peak_sales")
    elif failure == "unsupported":
        path = tmp_path / "input.csv"
        path.write_text("header\n", encoding="utf-8")
        with pytest.raises(InputFormatError, match="Unsupported input format"):
            facade.run_analysis(str(path), "json", "peak_sales")
    else:
        path = tmp_path / "empty.csv"
        path.write_text("", encoding="utf-8")
        with pytest.raises(InputFormatError, match="no transaction records"):
            facade.run_analysis(str(path), "csv", "peak_sales")


def test_export_to_unwritable_directory_raises_export_error(tmp_path):
    from smartretail.core.domain import AnalyticsResult

    result = AnalyticsResult("TestStrategy", {"records": 0})
    with pytest.raises(ExportError, match="Could not write CSV export"):
        CsvExporter().export(result, str(tmp_path))


def test_large_dataset_processing_reconciles_rows_and_records_measurements(
    record_property,
):
    dataset_value = os.environ.get("SMARTRETAIL_DATASET")
    if not dataset_value:
        pytest.skip("Set SMARTRETAIL_DATASET to the supplied large transaction CSV")
    dataset = Path(dataset_value)
    if not dataset.is_file():
        pytest.skip(f"SMARTRETAIL_DATASET does not point to a file: {dataset}")

    with dataset.open(encoding="utf-8-sig", newline="") as source:
        input_rows = max(0, sum(1 for _ in csv.reader(source)) - 1)

    tracemalloc.start()
    started = time.perf_counter()
    try:
        result = SmartRetailFacade().run_analysis(
            str(dataset), "csv", "peak_sales", chunk_size=5000
        )
        elapsed = time.perf_counter() - started
        _current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    accounted_rows = (
        result.summary["records"]
        + result.summary["duplicates"]
        + result.summary["quarantined"]
    )
    print(
        f"Input rows: {input_rows}; accounted rows: {accounted_rows}; "
        f"elapsed: {elapsed:.2f}s; peak traced memory: "
        f"{peak_bytes / (1024 * 1024):.2f} MiB"
    )
    record_property("dataset", str(dataset))
    record_property("input_rows", input_rows)
    record_property("accounted_rows", accounted_rows)
    record_property("chunk_size", 5000)
    record_property("elapsed_seconds", elapsed)
    record_property("peak_traced_bytes", peak_bytes)

    assert result.summary["total_rows"] == input_rows
    assert accounted_rows == input_rows
    assert elapsed >= 0
    assert peak_bytes > 0


def test_gui_smoke_choose_analyze_display_and_export(
    monkeypatch, write_transactions, transaction_row, tmp_path
):
    """Exercise GUI orchestration; skip where Tk cannot open a display."""

    class ImmediateThread:
        def __init__(self, target, daemon=False):
            self.target = target

        def start(self):
            self.target()

    path = write_transactions([transaction_row.copy()])
    try:
        window = gui_app.DashboardWindow()
    except gui_app.tk.TclError as exc:
        pytest.skip(f"Tk display is unavailable: {exc}")

    destination = tmp_path / "gui-export.csv"
    try:
        status_changes = []
        window.status.trace_add(
            "write", lambda *_args: status_changes.append(window.status.get())
        )
        monkeypatch.setattr(gui_app, "Thread", ImmediateThread)
        monkeypatch.setattr(window, "_start_loader", lambda: None)
        monkeypatch.setattr(
            gui_app.filedialog,
            "askopenfilename",
            lambda **_kwargs: str(path),
        )
        monkeypatch.setattr(
            gui_app.filedialog,
            "asksaveasfilename",
            lambda **_kwargs: str(destination),
        )

        window.choose_input()
        window.analysis_menu.current(0)
        window.run()
        window.root.update()

        assert hasattr(window, "last_result")
        assert "Processing dataset…" in status_changes
        assert "complete" in window.status.get()
        assert window.kpis["rows"].cget("text") == "1"

        window.export()
        assert destination.is_file()
        assert "peak_hours" in destination.read_text(encoding="utf-8")
    finally:
        window.root.destroy()
