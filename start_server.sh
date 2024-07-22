#!/usr/bin/bash

# cd to the directory where the server is located
# cd /path/to/server

source ./venv/bin/activate

# Start the server
echo "Starting the server (in 10 seconds)..."
sleep 10

# Start the server
python3 server.py
