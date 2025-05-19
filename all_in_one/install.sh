#!/bin/bash

echo "Starting Nord Pool & WiFi Detector Installation at $(date)"

SOURCE_DIR=$(pwd)
NORDPOOL_DIR="/home/dainius/Desktop/nordpool"
WIFI_DIR="/home/dainius/Desktop/wifi_detector"

# Create Desktop directory if it doesn't exist
if [ ! -d "/home/dainius/Desktop" ]; then
    echo "Creating Desktop directory..."
    mkdir -p /home/dainius/Desktop
fi

# Stop any running services
echo "Stopping any running services..."
pkill -f "python.*http.server.*8080" || true
pkill -f "python.*http.server.*8081" || true
pkill -f "uvicorn.*main:app" || true
pkill -f "uvicorn.*app:app" || true
pkill -f "python.*modbus_server.py" || true

# Remove existing installations
echo "Removing existing installations..."
if [ -d "$NORDPOOL_DIR" ]; then
    rm -rf "$NORDPOOL_DIR"
fi
if [ -d "$WIFI_DIR" ]; then
    rm -rf "$WIFI_DIR"
fi

# Install dependencies
echo "Installing required dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-bs4 python3-pandas python3-sqlalchemy python3-requests arp-scan

# Install additional Python packages
echo "Installing additional Python packages..."
sudo pip3 install fastapi==0.95.2 uvicorn==0.22.0

# Create directories
echo "Creating directories..."
mkdir -p "$NORDPOOL_DIR"/{logs,data,backend,frontend,scripts}
mkdir -p "$WIFI_DIR"/{logs,config,backend,frontend,scripts}

# Copy files
echo "Copying Nord Pool files..."
cp -r "$SOURCE_DIR/nordpool/backend"/* "$NORDPOOL_DIR/backend/" 2>/dev/null || true
cp -r "$SOURCE_DIR/nordpool/frontend"/* "$NORDPOOL_DIR/frontend/" 2>/dev/null || true
cp -r "$SOURCE_DIR/nordpool/scripts"/* "$NORDPOOL_DIR/scripts/" 2>/dev/null || true
cp -r "$SOURCE_DIR/nordpool/data"/* "$NORDPOOL_DIR/data/" 2>/dev/null || true

echo "Copying WiFi Detector files..."
cp -r "$SOURCE_DIR/wifi_detector/backend"/* "$WIFI_DIR/backend/" 2>/dev/null || true
cp -r "$SOURCE_DIR/wifi_detector/frontend"/* "$WIFI_DIR/frontend/" 2>/dev/null || true
cp -r "$SOURCE_DIR/wifi_detector/scripts"/* "$WIFI_DIR/scripts/" 2>/dev/null || true
cp -r "$SOURCE_DIR/wifi_detector/config"/* "$WIFI_DIR/config/" 2>/dev/null || true

# Copy Modbus server script to both installations
cp "$SOURCE_DIR/scripts/modbus_server.py" "$NORDPOOL_DIR/scripts/" 2>/dev/null || true

# Make scripts executable
echo "Making scripts executable..."
find "$NORDPOOL_DIR" -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
find "$NORDPOOL_DIR" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
find "$WIFI_DIR" -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
find "$WIFI_DIR" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# Create Nord Pool start script
echo "Creating Nord Pool start script..."
cat > "$NORDPOOL_DIR/start_server.sh" << 'EOFNP'
#!/bin/bash

IP_ADDRESSES=$(hostname -I)
FIRST_IP=$(echo $IP_ADDRESSES | awk '{print $1}')

echo "Starting Nord Pool Electricity Prices System..."
echo "System will be accessible at:"
echo "- Web interface: http://$FIRST_IP:8080/elektra"
echo "- API: http://$FIRST_IP:8000"
echo "- Modbus server: $FIRST_IP:502"
echo ""
echo "You can also access locally at:"
echo "- Web interface: http://localhost:8080/elektra"
echo "- API: http://localhost:8000"
echo "- Modbus server: localhost:502"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 8080 --directory frontend &
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
cd ../scripts
python3 modbus_server.py &
echo "Services started. Press Ctrl+C to stop all services"
wait
EOFNP
chmod +x "$NORDPOOL_DIR/start_server.sh"

# Create WiFi Detector start script
echo "Creating WiFi Detector start script..."
cat > "$WIFI_DIR/start_server.sh" << 'EOFWD'
#!/bin/bash

IP_ADDRESSES=$(hostname -I)
FIRST_IP=$(echo $IP_ADDRESSES | awk '{print $1}')

echo "Starting WiFi Detector System..."
echo "System will be accessible at:"
echo "- Web interface: http://$FIRST_IP:8081"
echo "- API: http://$FIRST_IP:8001"
echo ""
echo "You can also access locally at:"
echo "- Web interface: http://localhost:8081"
echo "- API: http://localhost:8001"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 8081 --directory frontend &
cd backend
python3 -m uvicorn app:app --host 0.0.0.0 --port 8001 &
echo "Services started. Press Ctrl+C to stop all services"
wait
EOFWD
chmod +x "$WIFI_DIR/start_server.sh"

# Create desktop shortcuts
echo "Creating desktop shortcuts..."
cat > "/home/dainius/Desktop/NordPool.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Nord Pool Electricity Prices
Comment=View electricity prices from Nord Pool
Exec=$NORDPOOL_DIR/start_server.sh
Icon=utilities-system-monitor
Terminal=true
Categories=Utility;
