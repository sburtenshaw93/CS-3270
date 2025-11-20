""" 
Module 9 Phase 9
Database models for weather web application
Data Access Layer
Uses SQLALchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

#Base class
Base = declarative_base()

# Creates SQLlite file
engine = create_engine('sqlite:///weather_app.db', echo=False)

# Session factory for the database operations
SessionLocal = sessionmaker(bind=engine)

class WeatherRecord(Base):
    """Stores the weather data from the CSV"""
    __tablename__ = 'weather_records'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(100))
    min_temp = Column(Float)
    max_temp = Column(Float)
    rainfall = Column(Float)
    rain_today = Column(String(10))
    
    def __repr__(self):
        return f"<WeatherRecord(id={self.id}, location={self.location}, max_temp={self.max_temp})>"
    

class UserQuery(Base):
    """ 
    Tracks user searches
    """
    __tablename__ = 'user_queries'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_type = Column(String(50)) # for 'hot_days', 'cold_days'.....
    parameters = Column(Text) # filter
    result_count = Column(Integer) # How many records matched
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserQuery(type={self.query_type}, count={self.result_count})>"
    
def init_database():
    """ 
    Creates all database tables
    """
    Base.metadata.create_all(engine)
    print("✅ Database tables created")

def get_session():
    """Returns a new database session"""
    return SessionLocal()

if __name__ == "__main__":
    """Running this file directly creates the database"""
    print("\nCreating database ---> ")
    init_database()