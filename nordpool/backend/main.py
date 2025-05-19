#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
db_path = os.path.join(data_dir, "nordpool_prices.db")

# Create data directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

# Models
class PriceData(BaseModel):
    hour: int
    price: float
    price_kwh: float

class DayPrices(BaseModel):
    date: str
    prices: List[PriceData]
    min_price: float
    max_price: float
    avg_price: float
    source: str

# Routes
@app.get("/")
def read_root():
    return {"message": "Nord Pool API is running"}

@app.get("/prices/available-dates")
def get_available_dates():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT date FROM prices ORDER BY date DESC")
        dates = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {"dates": dates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prices/date/{date}", response_model=DayPrices)
def get_prices_by_date(date: str):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if date exists
        cursor.execute("SELECT COUNT(*) FROM prices WHERE date = ?", (date,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # If date doesn't exist, try to generate it
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d").date()
                today = datetime.now().date()
                
                # Only generate data for dates within a reasonable range
                if date_obj <= today + timedelta(days=1) and date_obj >= today - timedelta(days=30):
                    # Import the function from the script
                    import sys
                    sys.path.append(os.path.join(base_dir, "scripts"))
                    from nordpool_scraper import generate_prices_for_date
                    
                    # Generate prices for the date
                    generate_prices_for_date(cursor, date_obj)
                    conn.commit()
                else:
                    raise HTTPException(status_code=404, detail=f"No price data available for {date}")
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"No price data available for {date}")
        
        # Get prices for the date
        cursor.execute("SELECT hour, price, source FROM prices WHERE date = ? ORDER BY hour", (date,))
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"No price data available for {date}")
        
        prices = []
        total_price = 0
        min_price = float('inf')
        max_price = float('-inf')
        source = rows[0][2]
        
        for hour, price, _ in rows:
            price_kwh = price * 0.1  # Convert EUR/MWh to ct/kWh
            prices.append(PriceData(hour=hour, price=price, price_kwh=price_kwh))
            
            total_price += price
            min_price = min(min_price, price)
            max_price = max(max_price, price)
        
        avg_price = total_price / len(prices) if prices else 0
        
        conn.close()
        
        return DayPrices(
            date=date,
            prices=prices,
            min_price=min_price,
            max_price=max_price,
            avg_price=avg_price,
            source=source
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
