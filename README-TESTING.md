## WOW!!!!!!!😱 😩 😫 🫣 😶
## Module: 5, Phase: 5 Testing Coverage
# Author: Sarah Burtenshaw

# What I implemented
- Test framework: pytest (with doctests discovered by pytest)
- Unit tests for: core, models, data_fetcher, data_processor, data_store
- Integration test: runs main() end-to-end without changing main.py
- Doctest: tiny documentation-style checks
- Coverage: verified with coverage or pytest-cov
- Zero/minimal code edits: tests use monkeypatch to keep main.py intact

# Configuation
``` bash
[pytest]
addopts = -q --doctest-glob="*.txt" --maxfail=1
testpaths = tests
pythonpath = src
```

# Constant trouble with the imports
Added conftest.py. Without this the import for the tests get 
touchy and sometimes will be mad on the imports from other files and their paths
``` bash
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

# allow: from src.core import otherwise it breaks
sys.path.insert(0, str(ROOT))
# allow: from core import otherwise it breaks
sys.path.insert(0, str(SRC))
```

## Run Tests & Coverage
# Setup
cd Module-5-Phase-5
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pytest coverage pytest-cov

# Run Tests
pytest -q

# Coverage
- Option A
coverage run -m pytest -q
coverage report -m

- Option B
pytest --cov=src --cov-report=term-missing -q

# What each test covers
tests/test_core.py
- mean / median / mode / data_range on simple inputs
- Mode tie behavior (accepts either selected mode or StatisticsError depending on Python version)

tests/test_models.py
- ColumnStats + ResultSummary.to_dict() round-trip
- Handles None values (empty column scenarios)

tests/test_fetcher.py
- iter_csv_records(path) yields row objects
- CSVFetcher.fetch() returns a list of rows
- Missing file raises FileNotFoundError
- tests/test_fetcher_errors.py (optional)
- CSV with no header raises ValueError

tests/test_processor.py
- NumericColumnIterator emits floats, skips blanks/words
- summarize_columns() returns counts + realistic means
- tests/test_processor_edge.py (optional)
- Empty or missing column → count == 0 and stats are None

tests/test_store.py
- FileStore(dir) writes summary.json with expected schema
- tests/test_main.py (integration, no edits to main.py)
- Uses monkeypatch to:
- Stub iter_csv_records to return FakeRecord(row=...) (what main() expects)
- Redirect OUT_PATH to a temp dir
- Runs main(), then asserts summary.json exists and is valid

## Command cheat sheet
# Start fresh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pytest coverage pytest-cov

# Run tests
pytest -q

# Coverage --> choose one
coverage run -m pytest -q && coverage report -m
# or
pytest --cov=src --cov-report=term-missing -q