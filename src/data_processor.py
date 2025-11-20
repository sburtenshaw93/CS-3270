from typing import List, Dict, Iterable, Iterator, Any, Mapping, Sequence, Union, Optional
from statistics import mean, median, mode, StatisticsError
import math
import logging
from multiprocessing import Pool, cpu_count
from functools import partial

try:
    from .models import WeatherRecord, ResultSummary, ColumnStats
except ImportError:
    from models import WeatherRecord, ResultSummary, ColumnStats

def _to_float_or_none(x: str):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

class StatsProcessor:
    def summarize(self, records: List[WeatherRecord]) -> ResultSummary:
        if not records:
            return ResultSummary(stats_by_column={})

        columns = list(records[0].row.keys())
        numeric_data: Dict[str, List[float]] = {c: [] for c in columns}

        for rec in records:
            for c in columns:
                val = _to_float_or_none(rec.row.get(c, ""))
                if val is not None:
                    numeric_data[c].append(val)

        stats_by_column: Dict[str, ColumnStats] = {}
        for col, values in numeric_data.items():
            if not values:
                continue
            values.sort()
            n = len(values)
            try:
                m = mode(values)
            except StatisticsError:
                m = None
            data_range = values[-1] - values[0] if n else None
            stats_by_column[col] = ColumnStats(
                mean=mean(values) if n else None,
                median=median(values) if n else None,
                mode=m,
                data_range=data_range,
                count=n,
            )
        return ResultSummary(stats_by_column=stats_by_column)

# ---------------------------- New --------------------------------------

# Added to the module to handle both dict rows and WeatherRecord rows
log = logging.getLogger(__name__)

class NumericColumnIterator:
    def __init__(self, records: Iterable[Any], column: Union[str, int]):
        self._records = iter(records)
        self._column = column
        self._use_mapping: Optional[bool] = None
        self._index: Optional[int] = None
        self._primed = False
        self._buffer_first: Optional[Any] = None

    def __iter__(self) -> "NumericColumnIterator":
        return self

    # --------------- Helpers ------------------------------
    def _is_mapping_row(self, rec: Any) -> bool:
        if hasattr(rec, "row") and isinstance(getattr(rec, "row"), Mapping):
            return True
        return isinstance(rec, Mapping)

    def _as_mapping_row(self, rec: Any) -> Mapping:
        return rec.row if hasattr(rec, "row") else rec

    def _is_sequence_row(self, rec: Any) -> bool:
        return isinstance(rec, Sequence) and not isinstance(rec, (str, bytes, bytearray))

    def _init_on_first(self, first: Any) -> None:
        if self._is_mapping_row(first):
            self._use_mapping = True
            self._buffer_first = first
            return

        if self._is_sequence_row(first):
            self._use_mapping = False
            if isinstance(self._column, int):
                self._index = max(0, int(self._column))
                self._buffer_first = first
                return

            if isinstance(self._column, str) and self._column in list(first):
                self._index = list(first).index(self._column)
                self._buffer_first = None  # treat first row as a header and skip it
                return

            self._index = 0
            self._buffer_first = first
            return

        self._use_mapping = None
        self._buffer_first = first

    def __next__(self) -> float:
        while True:
            if not self._primed:
                first = next(self._records)
                self._primed = True
                self._init_on_first(first)

            if self._buffer_first is not None:
                rec = self._buffer_first
                self._buffer_first = None
            else:
                rec = next(self._records)

            # Get the value from the record
            if self._use_mapping is True:
                row_map = self._as_mapping_row(rec)
                value = row_map.get(self._column, "")   # FIX: use self._column and the inner dict
            elif self._use_mapping is False and self._is_sequence_row(rec):
                idx = 0 if self._index is None else self._index
                value = rec[idx] if 0 <= idx < len(rec) else ""
            else:
                value = rec

            num = _to_float(value)
            if num is None or (isinstance(num, float) and math.isnan(num)):
                continue
            return num

# created a function to remove ","
def _to_float(v: Any) -> float | None:
    if v is None:
        return None

    if isinstance(v, (int, float)):
        try:
            return float(v)
        except Exception:
            return None

    if isinstance(v, str):
        s = v.strip()
        if s == "" or s.lower() in {"nan", "na", "null"}:
            return None

        s = s.replace(",", "")
        try:
            return float(s)
        except Exception:
            return None
    return None 

# -----------------------------New----------------------------------
# Optional helper that uses the iterator to produce a ResultSummary
def summarize_columns(records: Iterable[Any], numeric_columns: Iterable[Union[str, int]]) -> ResultSummary:
    records_list = list(records) if not isinstance(records, list) else records

    stats_by_column: Dict[str, ColumnStats] = {}
    for col in numeric_columns:
        vals = list(NumericColumnIterator(records_list, col))
        if not vals:
            stats_by_column[col] = ColumnStats(None, None, None, None, 0)
            continue

        vals.sort()
        n = len(vals)
        try:
            m = mode(vals)
        except StatisticsError:
            m = None
        data_rng = vals[-1] - vals[0] if n else None

        stats_by_column[col] = ColumnStats(
            mean=mean(vals) if n else None,
            median=median(vals) if n else None,
            mode=m,
            data_range=data_rng,
            count=n,
        )
    return ResultSummary(stats_by_column=stats_by_column)
#--------------------New helper function phase 7----------------------------------
def _process_single_column(records_list: list, col: Union[str, int]) -> tuple:
    """Processing statistics for a single column"""
    
    # Extract values for this column using the iterator
    vals = list(NumericColumnIterator(records_list, col))
    
    if not vals:
        return (col, ColumnStats(None, None, None, None, 0))
    
    # Calculate statistics
    vals.sort()
    n = len(vals)
    
    try:
        m = mode(vals)
    except StatisticsError:
        m = None
    
    data_rng = vals[-1] - vals[0] if n else None
    
    stats = ColumnStats(
        mean=mean(vals) if n else None,
        median=median(vals) if n else None,
        mode=m,
        data_range=data_rng,
        count=n,
    )
    return (col, stats)

def summarize_columns_parallel(records: Iterable[Any], numeric_columns: Iterable[Union[str, int]]) -> ResultSummary:
    """Parallel version using multiprocessing"""
    
    # Convert to list if needed
    records_list = list(records) if not isinstance(records, list) else records
    numeric_columns_list = list(numeric_columns)
    
    # Determine number of worker processes
    num_workers = max(1, cpu_count() - 1)
    
    print(f"Multiprocessing: Using {num_workers} CPU cores to process {len(numeric_columns_list)} columns")
    
    # Creating a process pool
    with Pool(processes=num_workers) as pool:
        worker_func = partial(_process_single_column, records_list)
        results = pool.map(worker_func, numeric_columns_list)
    
    stats_by_column = {col: stats for col, stats in results}
    
    print(f"Multiprocessing: Completed processing {len(stats_by_column)} columns")

    return ResultSummary(stats_by_column=stats_by_column)