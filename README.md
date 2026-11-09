# SmartRetail Analytics

A Python desktop application for chunked retail transaction ingestion, validation, deduplication, analytics and export.

## Run

```bash
python -m pip install -r requirements.txt
python -m main
```

The analytics engine uses only the Python standard library. GUI charts are presented as detailed analysis tables in this initial desktop shell; exports include CSV data or an HTML report.

## Input and outputs

CSV input follows the 22-column schema in `APP_IMPLEMENTATION_PROMPT.md`. Choose an analysis from the sidebar, then export results or inspect quarantined input in the DLQ window. The engine reads configurable chunks and keeps incremental strategy state rather than retaining transaction rows.
