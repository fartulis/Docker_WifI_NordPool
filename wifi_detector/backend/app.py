from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import json
import subprocess
import secrets
from typing import List, Dict, Optional
from datetime import datetime
import time

app = FastAPI()
security = HTTPBasic()

@app.post("/login")
def login(credentials: dict):
    with open("config/credentials.json") as f:
        stored = json.load(f)
    if credentials["username"] == stored["username"] and credentials["password"] == stored["password"]:
        return {"status": "ok"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
DEVICES_FILE = os.path.join(CONFIG_DIR, 'devices.json')
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, 'credentials.json')

# Ensure config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Create default files if they don't exist
if not os.path.exists(DEVICES_FILE):
    with open(DEVICES_FILE, 'w') as f:
        json.dump([], f)

if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump({"username": "admin", "password": "admin"}, f)

# Load credentials
def get_credentials():
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

# Verify credentials
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    stored_credentials = get_credentials()
    correct_username = secrets.compare_digest(credentials.username, stored_credentials["username"])
    correct_password = secrets.compare_digest(credentials.password, stored_credentials["password"])
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Load devices
def get_devices():
    with open(DEVICES_FILE, 'r') as f:
        return json.load(f)

# Save devices
def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=4)

# Get manufacturer from MAC address
def get_manufacturer(mac):
    # This is a simplified version - in a real implementation, 
    # you would use a database of MAC address prefixes
    prefixes = {
        "00:11:22": "Apple",
        "AA:BB:CC": "Samsung",
        "11:22:33": "Google",
        "22:33:44": "Huawei",
        "33:44:55": "Xiaomi",
        "44:55:66": "OnePlus",
        "55:66:77": "Sony",
        "66:77:88": "LG",
        "77:88:99": "Nokia",
        "88:99:AA": "Motorola"
    }
    
    prefix = mac[:8].upper()
    return prefixes.get(prefix, "Unknown")

# Scan for devices
def scan_network():
    # In a real implementation, you would use arp-scan or similar
    # For this example, we'll simulate by checking if devices in our list are "online"
    devices = get_devices()
    online_devices = []
    
    for device in devices:
        # Simulate random online status for demo purposes
        # In a real implementation, you would check if the device is actually online
        device["online"] = device["id"] % 2 == 0  # Even IDs are online
        online_devices.append(device)
    
    return online_devices

# API endpoints
@app.get("/")
def read_root():
    return {"message": "WiFi Detector API"}

@app.get("/devices")
def get_all_devices(username: str = Depends(verify_credentials)):
    return get_devices()

@app.get("/devices/scan")
def scan_devices(username: str = Depends(verify_credentials)):
    return scan_network()

@app.post("/devices")
def add_device(device: dict, username: str = Depends(verify_credentials)):
    devices = get_devices()
    
    # Generate ID
    max_id = 0
    for d in devices:
        if d["id"] > max_id:
            max_id = d["id"]
    
    device["id"] = max_id + 1
    
    # Add manufacturer if not provided
    if "manufacturer" not in device:
        device["manufacturer"] = get_manufacturer(device["mac"])
    
    devices.append(device)
    save_devices(devices)
    
    return device

@app.put("/devices/{device_id}")
def update_device(device_id: int, device: dict, username: str = Depends(verify_credentials)):
    devices = get_devices()
    
    for i, d in enumerate(devices):
        if d["id"] == device_id:
            # Update device
            device["id"] = device_id
            
            # Add manufacturer if not provided
            if "manufacturer" not in device:
                device["manufacturer"] = get_manufacturer(device["mac"])
            
            devices[i] = device
            save_devices(devices)
            return device
    
    raise HTTPException(status_code=404, detail="Device not found")

@app.delete("/devices/{device_id}")
def delete_device(device_id: int, username: str = Depends(verify_credentials)):
    devices = get_devices()
    
    for i, d in enumerate(devices):
        if d["id"] == device_id:
            del devices[i]
            save_devices(devices)
            return {"message": "Device deleted"}
    
    raise HTTPException(status_code=404, detail="Device not found")

@app.put("/credentials")
def update_credentials(credentials: dict, username: str = Depends(verify_credentials)):
    # Validate credentials
    if "username" not in credentials or "password" not in credentials:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    # Save credentials
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f)
    
    return {"message": "Credentials updated"}

@app.get("/network/stats")
def get_network_stats(username: str = Depends(verify_credentials)):
    # In a real implementation, you would get actual network stats
    # For this example, we'll return simulated data
    return {
        "total_devices": len(get_devices()),
        "online_devices": len([d for d in scan_network() if d.get("online", False)]),
        "network_load": "Medium",
        "last_scan": datetime.now().isoformat()
    }
