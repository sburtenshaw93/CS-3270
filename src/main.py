
from pathlib import Path
import sys, logging
from logging.handlers import RotatingFileHandler
from models import WeatherRecord
import asyncio
import time

#------------------------------------New-----------------------------------------------------

# Imports that work both ways
if __package__:
    from .data_fetcher import iter_csv_records, async_read_csv_records
    from .data_processor import summarize_columns, summarize_columns_parallel
    from .data_store import FileStore
    from .data_visualizer import analyze_and_visualize, async_analyze_and_visualize
else:
    from data_fetcher import iter_csv_records, async_read_csv_records
    from data_processor import summarize_columns, summarize_columns_parallel
    from data_store import FileStore
    from data_visualizer import analyze_and_visualize, async_analyze_and_visualize


def configure_logging(level = logging.INFO):
    root = logging.getLogger()
    root.setLevel(level)
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))
    
    fh = RotatingFileHandler('app.log', maxBytes = 256_000, backupCount = 2)
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    
    root.handlers.clear()
    root.addHandler(ch)
    root.addHandler(fh)
    

# Imports that work both ways
try:
    from .data_fetcher import iter_csv_records
    from .data_processor import summarize_columns
    from .data_store import FileStore
    from .data_visualizer import analyze_and_visualize
except ImportError:
    from data_fetcher import iter_csv_records
    from data_processor import summarize_columns
    from data_store import FileStore
    from data_visualizer import analyze_and_visualize

# Project root path finder
ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "archive" / "Weather Training Data.csv"
OUT_PATH = ROOT / "dist" / "summary.json"

def main_sync() -> None:
    print("Reading CSV, computing stats, and saving JSON…")
    print(f"CSV path: {CSV_PATH}")

    configure_logging()
    log = logging.getLogger(__name__)

    # 1) Read 📚
    try:
        raw_records = list(iter_csv_records(CSV_PATH))  # list so we can iterate multiple times in summarize
        records = [WeatherRecord(row=row) for row in raw_records]
        if not records:
            print("No rows found in the CSV.")
            sys.exit(0)
    except Exception as e:
        log.exception("Failed to read CSV: %s", e)
        print("Could not read the CSV. Check the file path and try again.")
        sys.exit(1)

    NUMERIC_COLS = list(records[0].row.keys())
    
    # 2) Summarize 
    try:
        summary = summarize_columns(records, NUMERIC_COLS)
    except Exception as e:
        log.exception("Failed to summarize: %s", e)
        print("Something went wrong while summarizing.")
        sys.exit(1)

    # 3) Save 💾
    try:
        out_path = FileStore(OUT_PATH).save_summary(summary)
    except Exception as e:
        log.exception("Failed to save summary: %s", e)
        print("Could not save the summary file.")
        sys.exit(1)

    # friendly wrap up
    total = sum(s.count for s in summary.stats_by_column.values())
    cols = ", ".join(summary.stats_by_column.keys()) or "(no numeric columns found)"
    print("\n" + "="*60)
    print("Starting Data Visualization and Pattern Analysis:  ")
    print("="*60)
    try:
        charts_dir = ROOT / "dist"
        charts_dir.mkdir(exist_ok=True)
        
        viz_results = analyze_and_visualize(records, str(charts_dir))
        print("\n Visualization Complete")
    except Exception as e:
        log.exception("Failed to create visualizations: %s", e)
        print(f"\n Warning: Could not create visualizations: {e}")
        print("The summary JSON was still saved successfully")
    
    print("Completed Processing File -->\n")
    print(f"- Numeric values processed: {total}\n")
    print(f"- Columns summarized: {cols}\n")
    print(f"- Saved to: {out_path.resolve()}\n")


#--------------------------New async main function---------------------------------------
async def main_async_parallel() -> None:
    """Async version with multiprocessing"""
    
    print("reading CSV, computing stats, and saving JSON (ASYNC + PARALLEL)...")
    print(f"CSV path: {CSV_PATH}")
    
    configure_logging()
    log = logging.getLogger(__name__)
    
    # read CSV without blocking
    print("\n[1 of 4] Reading CSV file asynchronously...")
    try:
        raw_records = await async_read_csv_records(CSV_PATH)
        records = [WeatherRecord(row=row) for row in raw_records]
        
        if not records:
            print("No rows found in the CSV")
            sys.exit(0)
        print(f"✅ Read {len(records)} records")
        
    except Exception as e:
        log.exception("Failed to read CSV %s, e")
        print("Could not read the CSV. Check the file path and try again")
        sys.exit(1)
    
    NUMERIC_COLS = list(records[0].row.keys())
    
    #process
    print("\n[2 of 4] Computing statistics in parallel using multiprocessing...")
    try:
        loop = asyncio.get_event_loop()
        summary = await loop.run_in_executor(
            None, 
            summarize_columns_parallel,
            records, 
            NUMERIC_COLS
        )
        total = sum(s.count for s in summary.stats_by_column.values())
        print(f"✅ Processed {total} numeric values across {len(summary.stats_by_column)} columns")
        
    except Exception as e:
        log.exception("Failed to summarize: %s", e)
        print("Something went wrong while summarizing")
        sys.exit(1)
    
    # Concurrent
    print("\n[3 of 4] Saving results and creating visualizations concurrently...")
    print("     (JSON save + 2 charts happening at the same time)")
    
    try:
        charts_dir = ROOT / "dist"
        charts_dir.mkdir(exist_ok=True)
        
        file_store = FileStore(OUT_PATH)
        
        out_path, viz_results = await asyncio.gather(
            file_store.async_save_summary(summary),
            async_analyze_and_visualize(records, str(charts_dir))
        )    
        
        print("\n✅ All files saved successfully")
    
    except Exception as e:
        log.exception("Failed during async save operations: %s, e")
        print(f"\nError during save operations: {e}")
        sys.exit(1)
    
    # Summary
    cols = ", ".join(summary.stats_by_column.keys()) or "(no numeric columns found)"
    print("\n" + "="*60)
    print("Async + Multiprocessing Complete")
    print("="*60)
    print(f"✅ Numeric values processed: {total}")
    print(f"✅ Columns summarized: {cols}")
    print(f"✅ JSON saved to: {out_path.resolve()}")
    print(f"✅ Charts saved to: {charts_dir.resolve()}")
    print("="*60 + "\n")


async def main_async() -> None:
    """Async version of amin that demonstrates concurrent I/O operations"""
    
    print("reading CSV, computing stats, and saving JSON (ASYNC)...")
    print(f"CSV path: {CSV_PATH}")
    
    configure_logging()
    log = logging.getLogger(__name__)
    
    # read CSV without blocking
    print("\n[1 of 4] Reading CSV file asynchronously...")
    try:
        raw_records = await async_read_csv_records(CSV_PATH)
        records = [WeatherRecord(row=row) for row in raw_records]
        
        if not records:
            print("No rows found in the CSV")
            sys.exit(0)
        print(f"✅ Read {len(records)} records")
        
    except Exception as e:
        log.exception("Failed to read CSV %s, e")
        print("Could not read the CSV. Check the file path and try again")
        sys.exit(1)
    
    NUMERIC_COLS = list(records[0].row.keys())
    
    #process
    print("\n[2 of 4] Computing statistics...")
    try:
        summary = summarize_columns(records, NUMERIC_COLS)
        total = sum(s.count for s in summary.stats_by_column.values())
        print(f"✅ Processed {total} numeric values across {len(summary.stats_by_column)} columns")
        
    except Exception as e:
        log.exception("Failed to summarize: %s", e)
        print("Something went wrong while summarizing")
        sys.exit(1)
    
    # Concurrent
    print("\n[3 of 4] Saving results and creating visualizations concurrently...")
    print("          (JSON save + 2 charts happening at the same time)")
    
    try:
        charts_dir = ROOT / "dist"
        charts_dir.mkdir(exist_ok=True)
        
        file_store = FileStore(OUT_PATH)
        
        out_path, viz_results = await asyncio.gather(
            file_store.async_save_summary(summary),
            async_analyze_and_visualize(records, str(charts_dir))
        )    
        
        print("\n✅ All files saved successfully")
    
    except Exception as e:
        log.exception("Failed during async save operations: %s, e")
        print(f"\nError during save operations: {e}")
        sys.exit(1)
    
    # Summary
    cols = ", ".join(summary.stats_by_column.keys()) or "(no numeric columns found)"
    print("\n" + "="*60)
    print("Async Processing Complete")
    print("="*60)
    print(f"✅ Numeric values processed: {total}")
    print(f"✅ Columns summarized: {cols}")
    print(f"✅ JSON saved to: {out_path.resolve()}")
    print(f"✅ Charts saved to: {charts_dir.resolve()}")
    print("="*60 + "\n")


def main() -> None:
    """
    Changed main() to run the normal sync and new async versions
    """
    if len(sys.argv) > 1 and sys.argv[1] == '--sync':
        # Run synchronous version
        print("\n" + "="*60)
        print("MODE: SYNCHRONOUS")
        print("="*60 + "\n")
        start_time = time.time()
        
        main_sync()
        
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"   SYNC execution time: {elapsed:.2f} seconds")
        print(f"{'='*60}\n")
    
    elif len(sys.argv) > 1 and sys.argv[1] == '--parallel':
        # Run async and multiprocessing
        print("\n" + "="*60)
        print("MODE: ASYNC I/O + MULTIPROCESSING")
        print("Demonstrates parallel CPU processing")
        print("="*60 + "\n")
        start_time = time.time()
        
        asyncio.run(main_async_parallel())
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"   ASYNC + PARALLEL execution time: {elapsed:.2f} seconds")
        print(f"{'='*60}\n")
        
    else:
        # Run asynchronous version (default)
        print("\n" + "="*60)
        print("Running ASYNCHRONOUS version...")
        print("="*60 + "\n")
        start_time = time.time()
        
        asyncio.run(main_async())
        
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"   ASYNC execution time: {elapsed:.2f} seconds")
        print(f"{'='*60}\n")
    


if __name__ == "__main__":
    main()
