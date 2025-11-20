# Module 11 - Final Submission
**Author:** Sarah Burtenshaw

## Overview
This project demonstrates **iterative software development over 11 modules**, evolving from basic CSV data loading to a sophisticated machine learning-powered web application. The final system is a **3-tier web application** with predictive weather forecasting capabilities.

**The Evolution:**
- **Modules 1-2**: Foundation with CSV processing, pandas, and custom Python package (descstats)
- **Modules 3-4**: OOP design, generators, iterators, logging, and error handling
- **Module 5**: Comprehensive testing framework with pytest (36 tests, full coverage)
- **Module 6**: Data visualization and functional programming (map, filter, reduce, lambda)
- **Module 7**: Asynchronous I/O and multiprocessing for concurrent operations
- **Module 8**: Distributed computing with Apache PySpark on Google Colab
- **Module 9**: 3-tier web application with Flask, SQLAlchemy, and browser-based UI
- **Module 10**: Machine Learning integration with Random Forest Classifier (80.74% accuracy)
- **Module 11**: Complete integration with Australia slideshow and final documentation

**Current Architecture (3-Tier):**
1. **Presentation Layer (Tier 1)**: Browser-based UI with HTML/CSS, Jinja2 templates, Australia slideshow
2. **Business Logic (Tier 2)**: Flask web server with routes for statistics, filtering, visualizations, and ML predictions
3. **Data Layer (Tier 3)**: SQLite database with SQLAlchemy ORM, storing 1000 weather records and user queries

**Key Features:**
- Interactive web interface with real-time statistics and filtering
- Data visualizations with matplotlib (charts generated on-demand)
- Machine learning predictions: "Will it rain tomorrow?" based on today's weather
- User query tracking for analytics
- Production-ready code with comprehensive testing and documentation


## Features Implemented
**Module 1 Phase 1**
- Weather data loading using Python's built-in csv module
- Weather data loading using pandas DataFrame
- Basic data preview and row counting
- Demonstrated two approaches to CSV processing

**Module 2 Phase 2**
- Created reusable Python package 'descstats' with statistical functions
- Implemented: mean, median, mode, range, describe()
- Built and published package to TestPyPI
- Loaded real dataset using both csv and pandas methods
- Package installation and usage demonstration

**Module 3 Phase 3**
- OOP refactor with abstraction and interfaces
- BaseFetcher abstract base class with fetch() method
- Encapsulation: separate classes for fetching, processing, storage
- Composition pattern in main.py orchestration
- Data modeling with @dataclass (WeatherRecord, ColumnStats, ResultSummary)
- Files: data_fetcher.py, data_processor.py, data_store.py, models.py

**Module 4 Phase 4**
- Generator: iter_csv_records() streams CSV rows (memory efficient)
- Custom iterator: NumericColumnIterator yields floats, skips invalid values
- summarize_columns() uses iterator for statistics computation
- Logging: configured with console + rotating file handler
- Robust error handling with try/except blocks
- FileStore ensures output folder exists before writing

**Module 5 Phase 5**
- Test framework: pytest with doctest discovery
- Unit tests for: core, models, data_fetcher, data_processor, data_store
- Integration test: runs main() end-to-end using monkeypatch
- Test coverage verification with pytest-cov
- Zero code edits to main.py (tests use monkeypatch for isolation)
- conftest.py for import path management

**Module 6 Phase 6**
- Data visualization with matplotlib (2 line charts)
- Functional programming: map, filter, reduce, lambda
- Pattern analysis: hot vs cold days, rainy vs dry periods
- Automated testing: 14 new tests for visualization functions

**Module 7 Phase 7**
- Asynchronous file I/O (reading CSV, writing JSON, saving charts)
- Multiprocessing for parallel statistics calculation across CPU cores
- Three execution modes: sync, async, and async+parallel
- Performance benchmarking and timing comparisons
- Maintained all previous features (visualization, functional programming)

**Module 8 Phase 8**
- Migrated entire application to Apache PySpark
- Distributed data processing using DataFrames instead of Python lists
- Implemented on Google Colab (virtual PySpark cluster)
- Replaced sequential processing with distributed parallel operations
- Lazy evaluation and distributed aggregations
- Same visualizations using collect() to bring data to driver

**Module 9 Phase 9**
- Built 3-tier web application with Flask
- Browser-based UI with HTML/CSS and Jinja2 templates
- SQLite database storing 1000 weather records
- SQLAlchemy ORM for database operations
- User query tracking (useful application data)
- Interactive filtering and visualizations
- Routes: /, /statistics, /filter, /visualizations, /predict, /api/stats

**Module 10 Phase 10**
- Integrated Machine Learning for predictive weather forecasting
- Random Forest Classifier predicting rain tomorrow (Yes/No)
- Model trained on 98,040 weather records with 80.74% accuracy
- Features: Location, MinTemp, MaxTemp, Rainfall, RainToday
- scikit-learn implementation with model persistence (pickle)
- Interactive web form for predictions with confidence scores
- New route: /predict with ML prediction interface
- Files: webapp/ml_model.py, webapp/templates/predict.html

**Module 11 Phase 11**
- Final submission with complete feature integration
- 3-tier web application with ML prediction capability
- Australia slideshow on home page demonstrating presentation layer
- All features working: statistics, filtering, visualizations, ML predictions
- Complete documentation and screenshots


## How to Run Module 8 - PySpark
1. Go to https://colab.research.google.com/drive/1Ndc3m-V3VugX7X5Cbxz-7XpXasmNPQyi?usp=sharing
2. Run all cells (Runtime → Run all)

## PySpark Changes Made

**What Changed:**
- Python lists → PySpark DataFrames (distributed data structure)
- `iter_csv_records()` → `spark.read.csv()` (distributed file reading)
- `summarize_columns()` → `df.describe()` (parallel statistics)
- `filter_hot_days()` → `df.filter(col("MaxTemp") > 25)` (distributed filtering)
- `reduce(sum)` → `df.agg({"Rainfall": "sum"})` (distributed aggregation)
- Added `.collect()` to bring data from workers to driver for visualization

**Why Changed:**
- DataFrames can be split across multiple machines (scalable)
- All operations run in parallel automatically (faster)
- Lazy evaluation - Spark builds execution plan before running
- Can process data larger than memory
- No need for async/multiprocessing - Spark handles it

**Key Difference:** Module 7 uses one machine with manual parallelism. Module 8 uses distributed cluster with automatic parallelism.

## How to Run Module 11 - Final Submission
### Setup

**Prerequisites:**
```bash
pip install -r requirements.txt
```
**Setup (One-time):**
```bash
# Load data into database (first time only)
python3 webapp/database.py
```
**Run the web application:**
```bash
python3 webapp/app.py
```
**Model Training Process:**
```bash
python3 webapp/ml_model.py
```
**Then open your browser:**
```bash
http://127.0.0.1:5000
```

## Test Cases
**Existing tests maintained from previous phases:**
- test_data_fetcher.py - CSV reading functionality (sync version)
- test_data_processor.py - Statistics calculations (sync version)
- test_data_store.py - JSON file writing (sync version)
- test_data_visualizer.py - Chart generation and functional programming
- test_main.py - Main program integration
- test_async_parallel.py - Test sync, async and parallel 

**Phase 7 Tests (tests/test_async_parallel.py):**
- `test_async_csv_reading_matches_sync` - Verifies async CSV reading produces identical results to sync version
- `test_async_json_writing` - Verifies async JSON writing creates valid output files
- `test_parallel_statistics_match_sequential` - Verifies parallel processing produces same statistics as sequential
- `test_parallel_processing_uses_multiple_cores` - Confirms multiprocessing actually uses multiple CPU cores
- `test_all_modes_same_data` - Integration test verifying sync, async, and parallel modes produce identical results
- `test_async_operations_dont_block` - Demonstrates async operations run concurrently, not sequentially

```markdown
## Module 9 - 3-Tier Architecture

**TIER 1: Presentation Layer (UI)**
- HTML templates with Jinja2
- CSS styling (gradients, responsive design)
- Browser-based interface
- Files: `webapp/templates/*.html`

**TIER 2: Business Logic (Backend)**
- Flask web framework
- Route handlers: `@app.route('/')`
- Data processing and filtering
- File: `webapp/app.py`
- Routes:
  - `/` - Home page
  - `/statistics` - Database stats
  - `/filter` - Filter weather data
  - `/visualizations` - Generate charts
  - `/api/stats` - JSON API

**TIER 3: Data Access Layer (Database)**
- SQLite database (`weather_app.db`)
- SQLAlchemy ORM
- Models: WeatherRecord, UserQuery
- Files: `webapp/models.py`, `webapp/database.py`

**Useful Application Data Stored:**
1. **WeatherRecord** - 1000 weather observations
   - Location, temperatures, rainfall
2. **UserQuery** - Tracks user searches
   - Query type, parameters, timestamp, result count
   - Example of analytics/usage tracking

**How the 3 Tiers Interact:**

## Asynchronous Programming Features
**ASYNC I/O - Concurrent file operations**

**Where: src/data_fetcher.py, src/data_store.py, src/data_visualizer.py**
- async_read_csv_records() - Reads CSV without blocking
    - Uses aiofiles for async file operations
    - WHY: File reading waits for disk, async lets other tasks run

- async_save_summary() - Writes JSON asynchronously
    - Prevents blocking during file writes
    - WHY: Disk I/O is slow, async enables concurrent operations

- async_save_plot() - Saves charts without blocking
    - Uses asyncio.to_thread() to wrap matplotlib's blocking savefig()
    - WHY: Multiple charts can save simultaneously

- asyncio.gather() - Coordinates concurrent operations
    - Saves JSON + Chart 1 + Chart 2 all at the same time
    - WHY: Sequential would be: save JSON (wait) → chart 1 (wait) → chart 2 (wait)
    - With async: all three happen concurrently!

## Performance Results
``` bash
Mode	        Time	vs Baseline	Description
Sync	        2.84s	-	Sequential, no optimization
Async	        2.76s	2.8% faster ✅	Concurrent I/O (WINNER)
Async+Parallel	8.16s	187% slower	Demonstrates parallelism
```

# Functional Programming Features Used
## Multiprocessing Features

**Where: src/data_processor.py**
- summarize_columns_parallel() - Processes columns in parallel
    - Uses multiprocessing.Pool with 9 CPU cores
    - Each worker calculates statistics for different columns simultaneously
    - WHY: Statistics (mean, median, mode) are CPU-intensive, columns are independent
### How it works:
1. User enters today's weather conditions in web form
2. Flask route `/predict` receives form data
3. `predict_rain()` function loads trained model
4. Model makes prediction with probability scores
5. Results displayed with confidence percentages


## FILTER - Selecting specific records
- filter_hot_days() - Finds days where MaxTemp > 25°C
- filter_cold_days() - Finds days where MaxTemp < 15°C
- filter_rainy_days() - Uses lambda to find rainy days
- filter_dry_days() - Uses lambda to find dry days

## MAP - Transforming data
- extract_max_temps() - Extracts max temperatures from records
- extract_min_temps() - Extracts min temperatures from records
- extract_rainfall() - Extracts rainfall amounts from records

## REDUCE - Combining values
- calculate_total_rainfall() - Sums all rainfall using reduce
- calculate_average_temp() - Calculates average using reduce
- count_days_above_threshold() - Counts days using reduce

## LAMBDA - Quick inline functions
- Used throughout filter and map operations for concise function definitions.

## Charts Created
1. Hot vs Cold Days Comparison (dist/hot_vs_cold.png)
Line chart showing temperature patterns for hot days (>25°C) vs cold days (<15°C) with average reference lines.
2. Rainy vs Dry Days Analysis (dist/rainy_vs_dry.png)
Dual chart showing rainfall amounts and temperature comparison between rainy and dry days.

## Key Findings
- Analyzed 99,516 weather records
- 38,056 hot days vs 11,603 cold days
- 22,056 rainy days (22% of dataset)
- Total rainfall: 226,055mm

## Average temp similar on rainy vs dry days (~24°C)
- Test Cases Automated (14 tests)
- test_filter_hot_days - Verify FILTER finds hot days
- test_filter_cold_days - Verify FILTER finds cold days
- test_filter_rainy_days - Verify FILTER with LAMBDA
- test_filter_dry_days - Verify FILTER with LAMBDA
- test_extract_max_temps - Verify MAP extracts temperatures
- test_extract_min_temps - Verify MAP extracts temperatures
- test_extract_rainfall - Verify MAP extracts rainfall
- test_calculate_total_rainfall - Verify REDUCE sums values
- test_calculate_average_temp - Verify REDUCE calculates average
- test_count_days_above_threshold - Verify REDUCE counts
- test_functional_pipeline - Verify filter→map→reduce integration
- test_missing_data_handling - Verify edge case handling
- Plus 22 tests from previous phases (36 total, all passing)

## Files Modified/Created
- src/main.py - Added async_main() and main_async_parallel() functions
- src/data_fetcher.py - Added async_read_csv_records()
- src/data_store.py - Added async_save_summary()
- src/data_visualizer.py - Added async_save_plot(), async chart functions
- `webapp/ml_model.py` - Model training, loading, and prediction functions
- `webapp/templates/predict.html` - ML prediction interface
- `webapp/rain_predictor_model.pkl` - Trained model (saved with pickle)
- `webapp/location_encoder.pkl` - Location label encoder

**Updated**
- src/data_processor.py - Added summarize_columns_parallel()
- pyproject.toml - Added aiofiles dependency

## Libraries Used
- matplotlib (visualization)
- functools.reduce (functional programming)
- pytest (testing)
- aiofiles (async file I/O)
- asyncio (async coordination)
- multiprocessing (parallel CPU processing)