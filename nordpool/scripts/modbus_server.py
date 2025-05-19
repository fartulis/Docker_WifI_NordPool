#!/usr/bin/env python3
import time
import json
import os
import sqlite3
from datetime import datetime, timedelta

class ModbusServer:
    def __init__(self, host='0.0.0.0', port=502):
        self.host = host
        self.port = port
        self.registers = {}
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'nordpool_prices.db')
        
        for i in range(1000, 1024):
            self.registers[i] = 0  # Today's prices EUR/MWh
        for i in range(1100, 1124):
            self.registers[i] = 0  # Today's prices ct/kWh
        for i in range(2000, 2024):
            self.registers[i] = 0  # Tomorrow's prices EUR/MWh
        for i in range(2100, 2124):
            self.registers[i] = 0  # Tomorrow's prices ct/kWh
        for i in range(3000, 3030):
            self.registers[i] = 0  # WiFi device presence status
        
        self.load_data()
        
        print(f"Modbus TCP server started on {self.host}:{self.port}")
        print("Register mapping:")
        print("- Registers 1000-1023: Today's hourly prices (EUR/MWh)")
        print("- Registers 1100-1123: Today's hourly prices (ct/kWh)")
        print("- Registers 2000-2023: Tomorrow's hourly prices (EUR/MWh)")
        print("- Registers 2100-2123: Tomorrow's hourly prices (ct/kWh)")
        print("- Registers 3000-3029: WiFi device presence status (1=present, 0=absent)")
        
        self.update_loop()
    
    def load_data(self):
        """Load price data from the database and update registers"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            cursor.execute("SELECT hour, price FROM prices WHERE date = ?", (today,))
            today_prices = cursor.fetchall()
            
            cursor.execute("SELECT hour, price FROM prices WHERE date = ?", (tomorrow,))
            tomorrow_prices = cursor.fetchall()
            
            for hour, price in today_prices:
                if 0 <= hour < 24:
                    self.registers[1000 + hour] = int(price)  # EUR/MWh
                    self.registers[1100 + hour] = int(price * 0.1)  # ct/kWh
            
            for hour, price in tomorrow_prices:
                if 0 <= hour < 24:
                    self.registers[2000 + hour] = int(price)  # EUR/MWh
                    self.registers[2100 + hour] = int(price * 0.1)  # ct/kWh
            
            conn.close()
            print(f"Loaded price data from database: {len(today_prices)} hours for today, {len(tomorrow_prices)} hours for tomorrow")
        except Exception as e:
            print(f"Error loading data from database: {e}")
    
    def update_loop(self):
        """Continuously update the registers with the latest data"""
        while True:
            self.load_data()
            time.sleep(300)  # Update every 5 minutes

if __name__ == "__main__":
    server = ModbusServer()
