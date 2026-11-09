# SmartRetail Analytics

A Python desktop application for chunked retail transaction ingestion, validation, deduplication, analytics and export.

## Run

```bash
python -m pip install -r requirements.txt
python -m main
```

The analytics engine uses Python's standard library. Export a formatted PDF summary report by default, with CSV data and HTML report exports also available.

## Input and outputs

CSV input follows the 22-column schema in `APP_IMPLEMENTATION_PROMPT.md`. Choose an analysis from the sidebar, then export results or inspect quarantined input in the DLQ window. The engine reads configurable chunks and keeps incremental strategy state rather than retaining transaction rows.
