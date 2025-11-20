import pytest
from pathlib import Path
from src.data_visualizer import (
    filter_hot_days,
    filter_cold_days,
    filter_rainy_days,
    filter_dry_days,
    extract_max_temps,
    extract_min_temps,
    extract_rainfall,
    calculate_average_temp,
    calculate_total_rainfall,
    count_days_above_threshold
)
from src.models import WeatherRecord

#-------------Create sample data for testing---------------------------------------------
@pytest.fixture
def sample_records():

    return [
        WeatherRecord(row={'MaxTemp': '30.0', 'MinTemp': '20.0', "Rainfall": '0.0', 'RainToday': 'No'}),
        WeatherRecord(row={'MaxTemp': '10.0', 'MinTemp': '5.0', "Rainfall": '5.5', 'RainToday': 'Yes'}),
        WeatherRecord(row={'MaxTemp': '28.0', 'MinTemp': '18.0', "Rainfall": '0.0', 'RainToday': 'No'}),
        WeatherRecord(row={'MaxTemp': '8.0', 'MinTemp': '2.0', "Rainfall": '12.3', 'RainToday': 'Yes'}),
        WeatherRecord(row={'MaxTemp': '20.0', 'MinTemp': '12.0', "Rainfall": '0.0', 'RainToday': 'No'}),
    ]

#-------------------test filter functions--------------------------------------------------------------

def test_filter_hot_days(sample_records):
    
    hot_days = filter_hot_days(sample_records, threshold=25.0)
    assert len(hot_days) == 2
    
    temps = [float(record.row['MaxTemp']) for record in hot_days]
    assert 30.0 in temps
    assert 28.0 in temps
    

def test_filter_cold_days(sample_records):
    cold_days = filter_cold_days(sample_records, threshold=15.0)
    assert len(cold_days) == 2
    
    temps = [float(record.row['MaxTemp']) for record in cold_days]
    assert 10.0 in temps
    assert 8.0 in temps
    
def test_filter_rainy_days(sample_records):
    rainy_days = filter_rainy_days(sample_records)
    assert len(rainy_days) == 2
    
    for record in rainy_days:
        assert record.row['RainToday'].strip() == "Yes"
        

def test_filter_dry_days(sample_records):
    dry_days = filter_dry_days(sample_records)
    assert len(dry_days) == 3
    
    for record in dry_days:
        assert record.row['RainToday'].strip() == "No"
        
#----------------------------test map functions-----------------------------------

def test_extract_max_temps(sample_records):
    temps = extract_max_temps(sample_records)
    assert len(temps) == 5
    
    assert temps[0] == 30.0
    assert temps[1] == 10.0
    assert temps[2] == 28.0
    
    assert all(isinstance(t, float) for t in temps)
    
def test_extract_min_temps(sample_records):
    temps = extract_min_temps(sample_records)
    assert len(temps) == 5
    assert temps[0] == 20.0
    assert temps[1] == 5.0
    assert all(isinstance(t, float) for t in temps)
    
def test_extract_rainfall(sample_records):
    rainfall = extract_rainfall(sample_records)
    assert len(rainfall) == 5
    assert rainfall[0] == 0.0
    assert rainfall[1] == 5.5
    assert rainfall[2] == 0.0
    assert rainfall[3] == 12.3
    

#------------------------test reduce functions-----------------------------------------------------

def test_calculate_total_rainfall():
    rainfall = [5.5, 12.3, 0.0, 3.2]
    total = calculate_total_rainfall(rainfall)
    assert total == pytest.approx(21.0, rel=0.01)

def test_calculate_total_rainfall_empty():
    total = calculate_total_rainfall([])
    assert total == 0.0
    
def test_calculate_average_temp():
    temps = [10.0, 20.0, 30.0]
    average = calculate_average_temp(temps)
    assert average == pytest.approx(20.0, rel=0.01)
    
def test_calculate_average_temp_empty():
    average = calculate_average_temp([])
    assert average == 0.0
    
def test_count_days_above_threshold():
    temps = [15.0, 25.0, 30.0, 20.0, 35.0]
    count = count_days_above_threshold(temps, 22.0)
    assert count == 3
    
#----------------Combining map, filter, reduce-----------------------------------------------

def test_functional_pipeline(sample_records):
    hot_days = filter_hot_days(sample_records, threshold=25.0)
    hot_temps = extract_max_temps(hot_days)
    average_hot = calculate_average_temp(hot_temps)
    assert average_hot == pytest.approx(29.0, rel=0.01)
    
def test_missing_data_handling():
    records_with_missing = [
        WeatherRecord(row={'MaxTemp': '', 'MinTemp': '', "Rainfall": '', 'RainToday': 'No'}),
        WeatherRecord(row={'MaxTemp': '25.0', 'MinTemp': '15.0', "Rainfall": '5.0', 'RainToday': 'Yes'}),
    ]
    temps = extract_max_temps(records_with_missing)
    assert temps[0] == 0.0
    assert temps[1] == 25.0
