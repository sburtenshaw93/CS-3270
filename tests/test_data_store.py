import json
from pathlib import Path
from src.data_store import FileStore
from src.models import ResultSummary, ColumnStats

def test_filestore_writes_json(tmp_path):
    store = FileStore(tmp_path / "out")
    summary = ResultSummary(stats_by_column={
        "A": ColumnStats(mean=3.2, median=2.8, mode=1.0, data_range=1.0, count=2)
    })
    out_path = store.save_summary(summary)
    assert out_path.exists()
    payload = json.loads(out_path.read_text())
    assert "A" in payload and payload["A"]["count"] == 2