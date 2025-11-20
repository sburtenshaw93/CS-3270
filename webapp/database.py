""" 
Module 9 Phase 9
Load data from CSV into SQLite
"""

import csv
from pathlib import Path
from models import WeatherRecord, UserQuery, get_session, init_database

# Path to the CSV file
CSV_PATH = Path(__file__).parent.parent / "archive" / "Weather Training Data.csv"

def load_weather_data(limit=1000):
    """ 
    Load weather data from the CSV into the database
    """
    print(f"Loading data from: {CSV_PATH}")
    
    if not CSV_PATH.exists():
        print(f"❌ CSV file not found: {CSV_PATH}")
        return
    
    # Database tables
    init_database()
    
    # get database session
    session = get_session()
    
    # Clear existing data
    session.query(WeatherRecord).delete()
    session.commit()
    
    # Read CSV and insert the records
    count = 0
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if count >= limit:
                break
            
            try:
                # Create WeatherRecord from CSV row
                record = WeatherRecord(
                    location=row.get('Location', ''),
                    min_temp=float(row['MinTemp']) if row.get('MinTemp') else None,
                    max_temp=float(row['MaxTemp']) if row.get('MaxTemp') else None,
                    rainfall=float(row['Rainfall']) if row.get('Rainfall') else None,
                    rain_today=row.get('RainToday', '')
                )
                
                session.add(record)
                count += 1
                
                if count % 100 == 0:
                    print(f"   Loaded {count} records --->")
            
            except (ValueError, KeyError) as e:
                # skip over rows with bad data
                continue
    # save all records to database
    session.commit()
    session.close()
    
    print(f"✅ Loaded {count} weather records into database")

def get_statistics():
    """Calculate basic statistics from database"""
    session = get_session()
    
    # Query all records
    records = session.query(WeatherRecord).all()
    
    if not records:
        return None
    
    # Calculate statistics
    max_temps = [r.max_temp for r in records if r.max_temp is not None]
    min_temps = [r.min_temp for r in records if r.min_temp is not None]
    rainfall = [r.rainfall for r in records if r.rainfall is not None]
    
    stats = {
        'total_records': len(records),
        'avg_max_temp': sum(max_temps) / len(max_temps) if max_temps else 0,
        'avg_min_temp': sum(min_temps) / len(min_temps) if min_temps else 0,
        'total_rainfall': sum(rainfall) if rainfall else 0,
        'max_temp_ever': max(max_temps) if max_temps else 0,
        'min_temp_ever': min(min_temps) if min_temps else 0
    }
    session.close()
    return stats

def log_user_query(query_type, parameters, result_count):
    """Save user query to the database"""
    session = get_session()
    
    query = UserQuery(
        query_type=query_type,
        parameters=str(parameters),
        result_count=result_count
    )
    
    session.add(query)
    session.commit()
    session.close()
    
if __name__ == "__main__":
    print("Loading weather data into database --->")
    load_weather_data(limit=1000) # loading the first 1000 records
    
    print("\nTesting statistics calculation --->") 
    stats = get_statistics()
    print(f"Total records: {stats['total_records']}")
    print(f"Average max temp: {stats['avg_max_temp']:.2f}°C")
    print(f"Total rainfall: {stats['total_rainfall']:.2f}mm")   