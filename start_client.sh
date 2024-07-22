#!/usr/bin/bash

# cd to the directory where the server is located
# cd /path/to/server

source ./venv/bin/activate

# Start the server
echo "Starting the client (in 20 seconds)..."
sleep 20

# Start the server
python3 client.py
