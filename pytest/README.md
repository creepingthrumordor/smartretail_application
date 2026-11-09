# SmartRetail pytest checks

Install the app dependencies and pytest, then run these checks from the project root:

```bash
python -m pip install -r smartretail/requirements.txt pytest
python -m pytest pytest_tests -v
```

The tests use temporary fixture files and do not need the full retail dataset or a running GUI.
