#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime, timedelta
import random

def create_database():
    """Create the database and tables if they don't exist"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'nordpool_prices.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create prices table - using the exact table name expected by the API
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        hour INTEGER,
        price REAL,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    return conn, cursor

def generate_sample_data(conn, cursor):
    """Generate sample price data for the past 30 days"""
    today = datetime.now()
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM prices")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Database already contains {count} price records. Skipping sample data generation.")
        return
    
    print("Generating sample price data for the past 30 days...")
    
    # Generate data for the past 30 days
    for day_offset in range(30, -1, -1):
        date = (today - timedelta(days=day_offset)).strftime('%Y-%m-%d')
        
        # Base price pattern with morning and evening peaks
        base_prices = [
            45, 42, 40, 38, 39, 45,  # 00:00 - 05:59
            65, 75, 85, 75, 65, 55,  # 06:00 - 11:59
            50, 48, 45, 48, 52, 58,  # 12:00 - 17:59
            75, 85, 80, 70, 60, 50   # 18:00 - 23:59
        ]
        
        # Add some randomness
        prices = [max(10, min(120, p + random.randint(-15, 15))) for p in base_prices]
        
        # Insert hourly prices
        for hour in range(24):
            cursor.execute(
                "INSERT INTO prices (date, hour, price, source) VALUES (?, ?, ?, ?)",
                (date, hour, prices[hour], "sample_data")
            )
    
    # Generate data for tomorrow if it's after 13:00
    current_hour = today.hour
    if current_hour >= 13:
        tomorrow = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Base price pattern with morning and evening peaks
        base_prices = [
            45, 42, 40, 38, 39, 45,  # 00:00 - 05:59
            65, 75, 85, 75, 65, 55,  # 06:00 - 11:59
            50, 48, 45, 48, 52, 58,  # 12:00 - 17:59
            75, 85, 80, 70, 60, 50   # 18:00 - 23:59
        ]
        
        # Add some randomness
        prices = [max(10, min(120, p + random.randint(-15, 15))) for p in base_prices]
        
        # Insert hourly prices
        for hour in range(24):
            cursor.execute(
                "INSERT INTO prices (date, hour, price, source) VALUES (?, ?, ?, ?)",
                (tomorrow, hour, prices[hour], "sample_data")
            )
    
    conn.commit()
    print(f"Generated sample price data for {30 + (1 if current_hour >= 13 else 0)} days")

if __name__ == "__main__":
    conn, cursor = create_database()
    generate_sample_data(conn, cursor)
    conn.close()
    print("Database initialization completed successfully")
