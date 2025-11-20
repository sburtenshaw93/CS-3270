import pytest
from collections.abc import Mapping
from src.data_processor import NumericColumnIterator

# Import whichever name your module provides
try:
    from src.data_processor import summarize_columns as _summarize_columns
except ImportError:
    from src.data_processor import summerize_columns as _summarize_columns  

from src.core import mean, median, mode, data_range

#---------------------------Numeric Column Iterator----------------------------------------
def test_numeric_iterator_skips_non_numbers():
    rows = [
        {"A": "1"},
        {"A": " "},             # skip
        {"A": "3.8"},
        {"A": "pomegranate"},   # skip
        {"A": "2.2"},
    ]
    assert list(NumericColumnIterator(rows, "A")) == [1.0, 3.8, 2.2]


# ---------------- Helpers to normalize summarize_columns----------------
def _col_mapping(result):
    if isinstance(result, Mapping):
        return result

    # Going to a common place where a dict will likely be stored
    if hasattr(result, "as_dict"):
        maybe = result.as_dict()
        if isinstance(maybe, Mapping):
            return maybe

    for attr in ("stats_by_column", "data", "_data", "by_col", "summary", "results"):
        maybe = getattr(result, attr, None)
        if isinstance(maybe, Mapping):
            return maybe

    # Doing a last try to see if the dict(result) works here
    try:
        maybe = dict(result)
        if isinstance(maybe, Mapping):
            return maybe
    except Exception:
        pass

    raise AssertionError(
        f"summarize_columns must return or expose a mapping; got {type(result).__name__}"
    )

# Turn one of the column's stats into a dict
def _to_plain_stats(stats_obj_or_dict):
    if isinstance(stats_obj_or_dict, Mapping):
        d = dict(stats_obj_or_dict)
        if "range" not in d and "data_range" in d:
            d["range"] = d["data_range"]
        return {
            "count": d.get("count"),
            "mean": d.get("mean"),
            "median": d.get("median"),
            "mode": d.get("mode"),
            "range": d.get("range"),
        }

    # Read attributes
    def _get(name):
        return getattr(stats_obj_or_dict, name) if hasattr(stats_obj_or_dict, name) else None

    rng = _get("range")
    if rng is None:
        rng = _get("data_range")

    # If there happens to be a to_dict() then use it
    if hasattr(stats_obj_or_dict, "to_dict"):
        try:
            return _to_plain_stats(stats_obj_or_dict.to_dict())
        except Exception:
            pass

    out = {
        "count": _get("count"),
        "mean": _get("mean"),
        "median": _get("median"),
        "mode": _get("mode"),
        "range": rng,
    }
    
    # Sanity check 🤨
    if all(k in out for k in ("count", "mean", "median", "mode", "range")):
        return out

    raise AssertionError(f"Could not normalize stats object of type {type(stats_obj_or_dict).__name__}")


# -------------------------------- Tests --------------------------------

def test_summarize_columns_populates_stats():
    # Values given are 1, 2, 3 for column X 
    rows = [{"X": "1"}, {"X": "2"}, {"X": "3"}]
    colmap = _col_mapping(_summarize_columns(rows, ["X"]))
    stats = _to_plain_stats(colmap["X"])

    assert stats["count"] == 3
    assert stats["mean"] == pytest.approx(mean([1, 2, 3]))     # 2.0
    assert stats["median"] == median([1, 2, 3])                # 2
    assert stats["mode"] == mode([1, 2, 3])                    # tie -> smallest = 1
    assert stats["range"] == data_range([1, 2, 3])             # 3 - 1 = 2


# No numbers here, all of the stats except "count" which should be None
def test_summarize_columns_all_blank_becomes_none():
    rows = [{"X": ""}, {"X": " "}]
    colmap = _col_mapping(_summarize_columns(rows, ["X"]))
    stats = _to_plain_stats(colmap["X"])
    assert stats == {
        "count": 0,
        "mean": None,
        "median": None,
        "mode": None,
        "range": None,
    }
