#!/usr/bin/env python3
import os
import sqlite3
import json
import random
from datetime import datetime, timedelta

def init_nordpool_database():
    """Initialize the Nord Pool database with sample data"""
    print("Initializing Nord Pool database...")
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nordpool_dir = os.path.join(base_dir, "nordpool")
    data_dir = os.path.join(nordpool_dir, "data")
    db_path = os.path.join(data_dir, "nordpool_prices.db")
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create prices table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        hour INTEGER,
        price REAL,
        source TEXT
    )
    ''')
    
    # Generate prices for the past 30 days
    today = datetime.now().date()
    
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        # Check if prices already exist for this date
        cursor.execute("SELECT COUNT(*) FROM prices WHERE date = ?", (date_str,))
        count = cursor.fetchone()[0]
        
        if count < 24:
            print(f"Generating prices for {date_str}")
            generate_prices_for_date(cursor, date)
    
    # Generate prices for tomorrow
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    cursor.execute("SELECT COUNT(*) FROM prices WHERE date = ?", (tomorrow_str,))
    count = cursor.fetchone()[0]
    
    if count < 24:
        print(f"Generating prices for tomorrow ({tomorrow_str})")
        generate_prices_for_date(cursor, tomorrow)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Nord Pool database initialization completed")

def generate_prices_for_date(cursor, date):
    """Generate realistic price patterns for a specific date"""
    date_str = date.strftime('%Y-%m-%d')
    
    # Delete any existing prices for this date
    cursor.execute("DELETE FROM prices WHERE date = ?", (date_str,))
    
    # Generate a base price between 40 and 80 EUR/MWh
    base_price = random.uniform(40, 80)
    
    # Generate hourly prices with realistic patterns
    for hour in range(24):
        # Morning peak (7-9 AM)
        if 7 <= hour <= 9:
            price = base_price + random.uniform(20, 40)
        # Evening peak (17-21 PM)
        elif 17 <= hour <= 21:
            price = base_price + random.uniform(15, 35)
        # Night low (0-5 AM)
        elif 0 <= hour <= 5:
            price = base_price - random.uniform(15, 25)
        # Midday (10-16)
        elif 10 <= hour <= 16:
            price = base_price + random.uniform(-10, 10)
        # Late night (22-23)
        else:
            price = base_price - random.uniform(5, 15)
        
        # Ensure price is not negative
        price = max(price, 5)
        
        # Round to 2 decimal places
        price = round(price, 2)
        
        # Insert into database
        cursor.execute(
            "INSERT INTO prices (date, hour, price, source) VALUES (?, ?, ?, ?)",
            (date_str, hour, price, "Nord Pool")
        )

def init_wifi_detector_database():
    """Initialize the WiFi Detector database with sample data"""
    print("Initializing WiFi Detector database...")
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    wifi_dir = os.path.join(base_dir, "wifi_detector")
    config_dir = os.path.join(wifi_dir, "config")
    
    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    # Create credentials.json
    credentials = {
        "username": "admin",
        "password": "admin"
    }
    
    with open(os.path.join(config_dir, "credentials.json"), "w") as f:
        json.dump(credentials, f, indent=4)
    
    # Create devices.json with sample devices
    devices = []
    
    # Sample MAC address prefixes for different manufacturers
    mac_prefixes = {
        "Apple": ["00:1E:52", "00:17:F2", "00:3E:E1", "00:0D:93", "00:26:BB"],
        "Samsung": ["00:07:AB", "00:12:47", "00:15:99", "00:17:D5", "00:21:19"],
        "Google": ["00:1A:11", "00:1A:11", "00:1A:11", "00:1A:11", "00:1A:11"],
        "Xiaomi": ["00:9E:C8", "00:EC:0A", "00:EC:0A", "00:EC:0A", "00:EC:0A"],
        "Huawei": ["00:18:82", "00:25:68", "00:25:9E", "00:34:FE", "00:46:4B"],
        "Sony": ["00:01:4A", "00:13:A9", "00:1A:80", "00:1D:0D", "00:24:BE"],
        "LG": ["00:1C:62", "00:1E:75", "00:1F:6B", "00:1F:E3", "00:21:FB"],
        "HTC": ["00:09:2D", "00:23:76", "00:EE:BD", "18:87:96", "38:E7:D8"],
        "OnePlus": ["00:C0:EE", "94:65:2D", "94:65:2D", "94:65:2D", "94:65:2D"],
        "Motorola": ["00:0E:C7", "00:1C:C1", "00:24:37", "00:24:92", "00:24:95"]
    }
    
    # Generate 10 sample devices
    for i in range(1, 11):
        # Select a random manufacturer
        manufacturer = random.choice(list(mac_prefixes.keys()))
        
        # Generate a random MAC address with the manufacturer's prefix
        prefix = random.choice(mac_prefixes[manufacturer])
        suffix = ":".join([f"{random.randint(0, 255):02X}" for _ in range(3)])
        mac = f"{prefix}:{suffix}"
        
        # Create a device name based on manufacturer
        device = {
            "id": i,
            "name": f"{manufacturer} Device {i}",
            "mac": mac,
            "manufacturer": manufacturer,
            "online": random.choice([True, False])
        }
        
        devices.append(device)
    
    with open(os.path.join(config_dir, "devices.json"), "w") as f:
        json.dump({"devices": devices}, f, indent=4)
    
    print("WiFi Detector database initialization completed")

if __name__ == "__main__":
    init_nordpool_database()
    init_wifi_detector_database()
