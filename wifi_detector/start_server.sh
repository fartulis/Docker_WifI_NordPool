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
