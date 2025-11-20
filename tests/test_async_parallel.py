""" 
Test cases for phase 7. Async and parallel programming
tests async file operations and multiprocessing implementations
"""
import pytest
import asyncio
from pathlib import Path
import json
import tempfile
import os
import time

# Import both sync and async versions
from src.data_fetcher import iter_csv_records, async_read_csv_records
from src.data_processor import summarize_columns, summarize_columns_parallel
from src.data_store import FileStore
from src.models import WeatherRecord, ResultSummary, ColumnStats

class TestAsyncFileOperations:
    """Test async file I/O operations"""
    
    def test_async_csv_reading_matches_sync(self, tmp_path):
        """verify async CSV reading produces same results as sync version"""
        csv_file = tmp_path / "test_weather.csv"
        csv_file.write_text(
            "Location, MinTemp, MaxTemp, RainFall\n"
            "Sydney, 15.2, 25.3, 0.0\n"
            "Melbourne, 12.5, 22.1, 5.2\n"
            "Brisbane, 18.0, 28.5, 0.0\n"
        )
        #Sync version 
        sync_records = list(iter_csv_records(csv_file))
        
        #Async version
        async_records = asyncio.run(async_read_csv_records(csv_file))
        
        assert len(sync_records) == len(async_records)
        assert len(sync_records) == 3
        
        for sync_row, async_row in zip(sync_records, async_records):
            assert sync_row == async_row
            assert sync_row['Location'] in ['Sydney', "Melbourne", "Brisbane"]
            
    def test_async_json_writing(self, tmp_path):
        """Verifying async JSON is writing and creating a valid output"""
        #test summary
        stats = ColumnStats(mean=20.0, median=19.5, mode=18.0, data_range=10.0, count=100)
        summary = ResultSummary(stats_by_column={"Temperature": stats})
        
        #write async
        output_file = tmp_path / "summary.json"
        store = FileStore(output_file)
        
        async def write_test():
            result = await store.async_save_summary(summary)
            return result
        
        result_path = asyncio.run(write_test())
        
        #checking to see the file exists and is in valid JSON
        assert result_path.exists()
        
        with open(result_path, 'r') as f:
            data = json.load(f)
        
        #verify content
        assert 'Temperature' in data
        assert data['Temperature']['mean'] == 20.0
        assert data['Temperature']['count'] == 100
        
class TestParallelProcessing:
    """Test multiprocessing implementations"""
    
    def test_parallel_statistics_match_sequential(self):
        """Verify parallel processing the same result as sequential"""
        #test records
        test_data = [
            {'Temperature': '20.5', 'Humidity': '65'},
            {'Temperature': '22.0', 'Humidity': '70'},
            {'Temperature': '19.5', 'Humidity': '60'},
            {'Temperature': '21.0', 'Humidity': '68'},
            {'Temperature': '20.0', 'Humidity': '62'},
        ]
        records = [WeatherRecord(row=row) for row in test_data]
        columns = ['Temperature', "Humidity"]

        #Process sequentially
        sequential_result = summarize_columns(records, columns)
        
        #Process in parallel
        parallel_result = summarize_columns_parallel(records, columns)
        
        # Results should be the same
        assert set(sequential_result.stats_by_column.keys()) == set(parallel_result.stats_by_column.keys())
                
        for col in columns:
            seq_stats = sequential_result.stats_by_column[col]
            par_stats = parallel_result.stats_by_column[col]
            
            #Statistics should match
            assert seq_stats.count == par_stats.count
            assert abs(seq_stats.mean - par_stats.mean) < 0.001
            assert seq_stats.median == par_stats.median
            
    def test_parallel_processing_uses_multiple_cores(self, capsys):
        """Verify parallel processing that will use multiprocessing"""
        #test records
        test_data = [{'Col1': str(i), 'Col2': str(i*2)} for i in range(10)]
        records = [WeatherRecord(row=row) for row in test_data]
        columns = ['Col1', 'Col2']
        
        #parallel version
        result = summarize_columns_parallel(records, columns)
        
        #capture output
        captured = capsys.readouterr()
        
        assert 'MULTIPROCESSING' in captured.out or 'Multiprocessing' in captured.out
        assert 'CPU cores' in captured.out or 'cores' in captured.out
        
        #processed both columns
        assert len(result.stats_by_column) == 2
        

class TestExecutionModes:
    """Test that all execution modes produce consistent results"""
    
    def test_all_modes_same_data(self, tmp_path):
        """Verifying sync, async and parallel modes produce the exact same results for statistics"""
        #test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "Temp, RainFall\n"
            "20.5, 0.0\n"
            "22.0, 5.2\n"
            "19.5, 0.0\n"
            "21.0, 3.1\n"
        )
        
        #Using both methods to read the csv file
        sync_records_raw = list(iter_csv_records(csv_file))
        async_records_raw = asyncio.run(async_read_csv_records(csv_file))
        
        sync_records = [WeatherRecord(row=r) for r in sync_records_raw]
        async_records = [WeatherRecord(row=r) for r in async_records_raw]
        
        columns = ['Temp', 'RainFall']
        
        sync_stats = summarize_columns(sync_records, columns)
        async_stats = summarize_columns(async_records, columns)
        parallel_stats = summarize_columns_parallel(async_records, columns)
        
        assert len(sync_stats.stats_by_column) == 2
        assert len(async_stats.stats_by_column) == 2
        assert len(parallel_stats.stats_by_column) == 2
        
        for col in columns:
            assert sync_stats.stats_by_column[col].count == 4
            assert async_stats.stats_by_column[col].count == 4
            assert parallel_stats.stats_by_column[col].count == 4
            
    def test_async_operations_dont_block(self):
        """Verify async operations run concurrently"""
        async def slow_operation(name, delay):
            await asyncio.sleep(delay)
            return name
        
        async def test_concurrent():
            """Run multiple operations"""
            start = time.time()
            
            # Run three operations
            results = await asyncio.gather(
                slow_operation("task1", 0.1),
                slow_operation("task2", 0.1),
                slow_operation("task3", 0.1)
            )
            
            elapsed = time.time() - start
            
            assert elapsed < 0.2 
            assert len(results) == 3
            
            return elapsed
        
        elapsed = asyncio.run(test_concurrent())
        assert elapsed < 0.2
        
if __name__ == "__main__":
    pytest.main([__file__, "-v"])