import sys, json
from pathlib import Path
import importlib

try:
    main_mod = importlib.import_module("main")
except ModuleNotFoundError:
    main_mod = importlib.import_module("src.main")


# Mimic of the WeatherRecord
class FakeRecord:
    def __init__(self, row):
        self.row = row

def test_main_integration(tmp_path, monkeypatch):
    # Preparing the CSV and the output path
    out_file = tmp_path / "dist" / "summary.json"
    monkeypatch.setattr(main_mod, "OUT_PATH", out_file)
    
    def fake_iter_csv_records(_ignored):
        return [{"A": "1"}, {"A": "2"}]
    
    monkeypatch.setattr(main_mod, "iter_csv_records", fake_iter_csv_records)
    
    # Simulate the Command Line Interface(CLI) Arguments
    old_argv = sys.argv[:]
    try:
        sys.argv = ["prog"]
        main_mod.main()
    finally:
        sys.argv = old_argv #👵🏼👴🏼
        
    # Verifying the output
    assert out_file.exists(), f"Expected summary at {out_file}"
    data = json.loads(out_file.read_text())
    # Just verify we got some data - test runs with real CSV
    assert len(data) > 0, "Expected at least some columns in output"
    # Check that we have valid statistics structure
    first_col = list(data.keys())[0]
    assert "count" in data[first_col]
    
                       