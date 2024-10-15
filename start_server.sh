#!/usr/bin/bash

# Path to the virtual environment
VENV_PATH="/home/pi/Desktop/pyvideosync/.venv"

# Path to the Python program
PYTHON_PROGRAM="/home/pi/Desktop/pyvideosync/server.py"
CLIENT_PROGRAM="/home/pi/Desktop/pyvideosync/client.py"

# Open a new terminal window and run the commands
export DISPLAY=:0
lxterminal --command="bash -c 'source $VENV_PATH/bin/activate && sudo python3 $PYTHON_PROGRAM; exec bash'" &

sleep 5
export DISPLAY=:0
lxterminal --command="bash -c 'source $VENV_PATH/bin/activate && python3 $CLIENT_PROGRAM; exec bash'" &
