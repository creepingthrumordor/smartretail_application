# SmartRetail automated tests

These pytest checks exercise the SmartRetail application and map to test-plan cases T01–T14. Small temporary CSV/log files are used for ordinary checks, so the full assignment dataset and a GUI display are not required for most of the suite.

## Install and run

From the repository root, install the app requirements and pytest:

```bash
python -m pip install -r requirements.txt pytest
```

The test directory is named `pytest`, so run the module from the repository's parent directory to avoid a name collision with the pytest runner:

```bash
cd ..
python -m pytest smartretail/pytest -v
```

Replace `smartretail` with the project directory name if it differs. T13 is skipped unless `SMARTRETAIL_DATASET` points to the supplied large CSV. T14 is skipped when Tk cannot open a display; the assignment also lists the GUI smoke check as manual.

## Coverage notes

The test modules cover CSV/log reading, validation, duplicates and DLQ routing, transformations, all six analytics strategies, chunk-size equivalence, end-to-end processing, exports, error handling, optional large-dataset measurements, and a GUI workflow smoke check. Some plan behavior remains conditional on the dataset or GUI environment; the test output will show these as skipped rather than passed.
