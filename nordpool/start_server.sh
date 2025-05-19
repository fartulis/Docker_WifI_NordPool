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
