from src.models import ColumnStats, ResultSummary

def test_models_to_dict_roundtrip():
    stats = ColumnStats(mean=2.5, median=3.1, mode=1.0, data_range=2.0, count=3)
    summary = ResultSummary(stats_by_column={"A": stats})
    d = summary.to_dict()
    assert "A" in d
    assert d["A"]["count"] == 3
    
    
def test_models_to_dict_with_none_values():
    stats = ColumnStats(mean=None, median=None, mode=None, data_range=None, count=0)
    summary = ResultSummary(stats_by_column={"Empty": stats})
    d = summary.to_dict()
    assert d["Empty"]["count"] == 0
    assert d["Empty"]["mean"] is None    